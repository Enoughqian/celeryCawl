from playwright.sync_api import sync_playwright
from app.core.config import settings
import redis

def connect_redis():
    r = redis.StrictRedis(host=settings.REDIS_HOST, port=int(settings.REDIS_PORT), password=settings.REDIS_PASSWORD, db=0)
    r.set('mykey', 'myvalue')
    value = r.get('mykey')
    print(value)

def run_playwright():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        context = browser.new_context()
        page = context.new_page()

        # 在页面上加载 URL
        page.goto('https://www.baidu.com')

        # # 执行一些操作，例如点击按钮或填写表单
        # page.click('button')
        # page.fill('input[name="username"]', 'myusername')

        # 获取页面
        content = page.content()
        print(content)

        # 截屏保存为文件
        page.screenshot(path='screenshot.png')

        # 关闭浏览器
        context.close()
        browser.close()

if __name__ == "__main__":
    connect_redis()