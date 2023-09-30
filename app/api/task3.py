from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright
import time
import re
from loguru import logger
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse, JSONResponse
import asyncio
import sys
import json
from loguru import logger
from sqlmodel import Session, select, update, func, or_
from datetime import datetime
from sqlmodel import SQLModel, Field
from datetime import datetime
from sqlmodel import SQLModel, create_engine, Session
import os
from fastapi import APIRouter, Depends, HTTPException
import ctypes
import threading
import requests
import random
import aiohttp
from celery import Celery
from app.core.config import settings

# 连接参数
broker_params = 'redis://:{}@{}:{}/{}'.format(
    settings.REDIS_PASSWORD,
    settings.REDIS_HOST,
    settings.REDIS_PORT,
    settings.CELERY_BROKER_DB
)

backend_params = 'redis://:{}@{}:{}/{}'.format(
    settings.REDIS_PASSWORD,
    settings.REDIS_HOST,
    settings.REDIS_PORT,
    settings.CELERY_BACKEND_DB
)
print(broker_params)

# 创建Celery应用实例
app = Celery('crawl_page', broker=broker_params)

# 配置Celery应用
app.conf.update(
    result_backend = backend_params
)

# 异步接口
def afetch_product_info(url: str, browser, context):
    """
    获取异步接口数据
    """
    target_url_pattern = 'https://life.scsjsd.com/aweme/v2/poi/user/trade/product/info/'
    
    total_bytes = 0
    
    def check_blocked_patterns(string, blocked_patterns):
        for pattern in blocked_patterns:
            if re.search(pattern, string):
                return True
        return False

    def filter_requests(route, request):
        resource_type = request.resource_type
        blocked_pattern = ['namek/user/goods/agreement/info', 'user/trade/product/decision/update/', 
                           'slardar/fe/sdk-web/plugins/common-monitors', 'rc-client-security/secsdk-captcha']
        
        blocked_rc_type = ['image', 'stylesheet', 'xhr']
        
        if resource_type in blocked_rc_type:
            route.abort()
        elif check_blocked_patterns(request.url, blocked_pattern):
            route.abort()
        else:
            logger.debug(f"{request.resource_type}, {request.url}")
            route.continue_()
        pass
    
    def handle_response(response, responses):
        nonlocal total_bytes
        if response.status == 200:
            # 计算流量大小
            length = response.headers.get('content-length')
            length = int(length) if length else 0
            total_bytes += length
        
        if response.status == 200 and response.url.startswith(target_url_pattern):
            responses.append(response.json())

    with sync_playwright() as playwright:
        # 读取有头无头的配置
        if_headless = False
        
        # 调用火狐浏览器
        browser = playwright.firefox.launch(headless = if_headless)
        logger.info("调用火狐浏览器成功")

        # 获取异步响应
        async_responses = []
        async_start_time = time.time()
        page = browser.new_page()
        page.on('response', lambda response: handle_response(response, async_responses))

        # 启用请求拦截
        page.route('**/*', filter_requests)
        
        # 异步加载
        page.goto(url)
        page.wait_for_load_state('networkidle')

        # 计算时长
        async_time = time.time() - async_start_time

        logger.debug("异步加载结果：")

        logger.debug(f"异步加载总流量：{total_bytes}  bytes")
        logger.debug(f"异步加载耗时：{async_time} seconds")
        browser.close()
        
        return async_responses
    
# 传入product_id抓取，绑定异步任务
@app.task
def search_product(product_id):
    url = f'https://life.scsjsd.com/falcon/poi_mwa/trade_detail?source=groupbuy&trans_status_bar=1&is_share_page=1&hide_nav_bar=1&enter_from=link&activity_id={product_id}&should_full_screen=1&detail_enter_page=link&schema_type=45&utm_campaign=client_share&app=aweme&utm_medium=ios&tt_from=copy&utm_source=copy&utm_campaign=client_share&app=aweme&utm_medium=ios&tt_from=copy&utm_source=copy'

    result = afetch_product_info(url, None, None)
    if result:
        result = result[0]['ProductSerializationData']
    else:
        result = None
    return result

# 导入任务模块
# app.autodiscover_tasks()

if __name__ == "__main__":
    product_id = "1776275820963868"
    search_product(product_id)