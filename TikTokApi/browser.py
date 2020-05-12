import asyncio
import pyppeteer
import random
class browser:
    def __init__(self, url):
        self.url = url
        self.userAgent = "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1"
        self.args = [
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-infobars",
            "--window-position=0,0",
            "--ignore-certifcate-errors",
            "--ignore-certifcate-errors-spki-list",
            "--user-agent=" + self.userAgent
        ]

        self.options = {
        'args': self.args,
        'headless': True,
        'ignoreHTTPSErrors': True,
        'userDataDir': "./tmp"
        }

        asyncio.get_event_loop().run_until_complete(self.start())

    async def start(self):
        self.browser = await pyppeteer.launch(self.options)
        self.page = await self.browser.newPage()

        await self.page.emulate({'viewport': {
            'width':random.randint(320, 1920),
            'height':random.randint(320, 1920),
            'deviceScaleFactor':random.randint(1, 3),
            'isMobile':random.random() > 0.5,
            'hasTouch': random.random() > 0.5
        }})

        await self.page.setUserAgent(self.userAgent)

        await self.page.goto("https://www.tiktok.com/trending?lang=en", {
        'waitUntil': "load"
        })

        await self.page.evaluate('''() => {
          var b = {};
          for (let x of window.webpackJsonp) {
            if (typeof x[1]["duD4"] === "function") {
              x[1]["duD4"](null, b);
              break;
            }
          }

          if (typeof b.sign !== "function") {
            throw "No function found";
          }

          window.generateSignature = function generateSignature(url) {
              return b.sign({ url: url });
          };
          }''')
        
        self.signature = await self.sign(self.url)
        await self.browser.close()

    async def sign(self, string):
        res = await self.page.evaluate("generateSignature('" + string + "')")
        return res
