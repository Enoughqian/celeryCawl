import secrets

from dotenv import load_dotenv
import os

from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, BaseSettings, EmailStr, HttpUrl, AnyUrl, validator
from loguru import logger
import requests
from collections import defaultdict
import sys

load_dotenv()

class Config(BaseSettings):
    MYSQLDATABASE = os.getenv('MYSQLDATABASE')
    REDIS_HOST = os.getenv('REDIS_HOST')
    REDIS_PORT = os.getenv('REDIS_PORT')
    CELERY_BROKER_DB = os.getenv('CELERY_BROKER_DB')
    CELERY_BACKEND_DB = os.getenv('CELERY_BACKEND_DB')
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
settings = Config()
