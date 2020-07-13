import asyncio
import pyppeteer
import random
import time
import json
import string
import atexit
import requests

# Import Detection From Stealth
from .stealth import stealth

class signer:
    def __init__(self, language='en', proxy=None, debug=False, keep_open=False):
        self.debug = debug
        self.proxy = proxy

        self.referrer = "https://www.tiktok.com/"
        self.userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.0 Safari/537.36)"
        self.args = [
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-infobars",
            "--window-position=0,0",
            "--ignore-certifcate-errors",
            "--ignore-certifcate-errors-spki-list",
             "--user-agent=" + self.userAgent,
        ]

        #self.args = []
        # "--user-agent=" + self.userAgent,

        if proxy != None:
            if "@" in proxy:
                self.args.append("--proxy-server=" + proxy.split(":")[0] + "://" + proxy.split(
                    "://")[1].split(":")[1].split("@")[1] + ":" + proxy.split("://")[1].split(":")[2])
            else:
                self.args.append("--proxy-server=" + proxy)
        self.options = {
            'args': self.args,
            'headless': False,
            'ignoreHTTPSErrors': True,
            'userDataDir': "./tmp",
            'handleSIGINT': False,
            'handleSIGTERM': False,
            'handleSIGHUP': False
        }

        if keep_open:
            self.loop = asyncio.new_event_loop()
            # self.loop.create_task(self.start())
            self.loop.run_forever(self.test())

    async def start(self):
        self.browser = await pyppeteer.launch(self.options)

    async def test(self):
        await self.loop.create_task(self.start())

    async def sign_url(self, url):

        self.page = await self.browser.newPage()

        await self.page.evaluateOnNewDocument("""() => {
            delete navigator.__proto__.webdriver;
           }""")

        # Check for user:pass proxy
        if self.proxy != None:
            if "@" in self.proxy:
                await self.page.authenticate({
                    'username': self.proxy.split("://")[1].split(":")[0],
                    'password': self.proxy.split("://")[1].split(":")[1].split("@")[0]
                })

        await stealth(self.page)

        # might have to switch to a tiktok url if they improve security
        await self.page.goto("https://www.bing.com/")

        self.userAgent = await self.page.evaluate("""() => {return navigator.userAgent; }""")

        await self.page.evaluate("() => { " + self.__get_js(proxy=self.proxy) + " }")


        verifyFp = await self.get_cookie()
        signature = await self.page.evaluate('''() => {
            var url = "''' + url + "&verifyFp=" + verifyFp + '''"
            var token = window.byted_acrawler.sign({url: url});
            return token;
            }''')

        await self.page.close() 
        return verifyFp, signature

    async def get_cookie(self):
        key = ''
        for i in range(16):
            key += random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits)
        return key

    async def close_browser(self):
        await self.browser.close()
        await self.loop.close()

    def __format_proxy(self, proxy):
        if proxy != None:
            return {
                'http': proxy,
                'https': proxy
            }
        else:
            return None

    def __get_js(self, proxy=None):
        return requests.get("https://sf16-muse-va.ibytedtos.com/obj/rc-web-sdk-gcs/acrawler.js", proxies=self.__format_proxy(proxy)).text