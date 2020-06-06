import asyncio
import pyppeteer
import random
import time
from pyppeteer_stealth import stealth


class browser:
    def __init__(self, url, language='en', proxy=None, find_redirect=False):
        self.url = url
        self.language = language
        self.userAgent = "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1"
        self.args = [
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-infobars",
            "--window-position=0,0",
            "--ignore-certifcate-errors",
            "--ignore-certifcate-errors-spki-list",
            "--user-agent=" + self.userAgent,
        ]

        self.options = {
            'args': self.args,
            'headless': True,
            'ignoreHTTPSErrors': True,
            'userDataDir': "./tmp",
            'handleSIGINT': False,
            'handleSIGTERM': False,
            'handleSIGHUP': False
        }

        loop = asyncio.new_event_loop()

        if find_redirect:
            loop.run_until_complete(self.find_redirect())
        else:
            loop.run_until_complete(self.start())

    async def start(self):
        self.browser = await pyppeteer.launch(self.options)
        self.page = await self.browser.newPage()

        await stealth(self.page)

        await self.page.emulate({'viewport': {
            'width': random.randint(320, 1920),
            'height': random.randint(320, 1920),
            'deviceScaleFactor': random.randint(1, 3),
            'isMobile': random.random() > 0.5,
            'hasTouch': random.random() > 0.5
        }})

        await self.page.setUserAgent(self.userAgent)

        await self.page.setExtraHTTPHeaders({
            'Accept-Language': self.language
        })

        await self.page.goto("https://www.tiktok.com/trending?lang=" + self.language, {
            'waitUntil': "load"
        })

        self.signature = await self.page.evaluate('''() => {
          var url = "''' + self.url + '''"
          var token = window.byted_acrawler.sign({url: url});
          return token;
          }''')
        await self.browser.close()

    
    async def find_redirect(self):
        self.browser = await pyppeteer.launch(self.options)
        self.page = await self.browser.newPage()

        await stealth(self.page)

        await self.page.emulate({'viewport': {
            'width': random.randint(320, 1920),
            'height': random.randint(320, 1920),
            'deviceScaleFactor': random.randint(1, 3),
            'isMobile': random.random() > 0.5,
            'hasTouch': random.random() > 0.5
        }})

        await self.page.setUserAgent(self.userAgent)

        await self.page.setExtraHTTPHeaders({
            'Accept-Language': self.language
        })

        await self.page.goto(self.url, {
            'waitUntil': "load"
        })

        self.redirect_url = self.page.url