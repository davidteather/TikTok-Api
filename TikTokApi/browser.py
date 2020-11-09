import random
import time
import string
import requests
import logging
from threading import Thread

# Import Detection From Stealth
from .stealth import stealth

from .get_acrawler import get_acrawler

async_support = False
from playwright import sync_playwright

def set_async():
    global async_support
    async_support = True


options = {}


def custom_options(to_add):
    global options
    options = to_add


args = []


def custom_args(to_add):
    global args
    args = to_add


try:
    playwright = sync_playwright().start()
except Exception as e:
    raise e

def get_playwright():
    return playwright

class browser:
    def __init__(
        self,
        **kwargs,
    ):
        self.debug = kwargs.get("debug", False)
        self.proxy = kwargs.get("proxy", None)
        self.api_url = kwargs.get("api_url", None)
        self.referrer = kwargs.get("referer", "https://www.tiktok.com/")
        self.language = kwargs.get("language", "en")
        self.executablePath = kwargs.get("executablePath", None)
        self.did = kwargs.get("custom_did", None)
        find_redirect = kwargs.get("find_redirect", False)

        self.userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36"

        global args
        global options

        if len(args) == 0:
            self.args = [
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-infobars",
                "--window-position=0,0",
                "--ignore-certifcate-errors",
                "--ignore-certifcate-errors-spki-list",
            ]
        else:
            self.args = args
            
        self.args.append("--user-agent=" + self.userAgent)

        self.options = {
            "headless": True,
            "handleSIGINT": False,
            "handleSIGTERM": False,
            "handleSIGHUP": False,
        }
        
        if self.proxy != None:
            if "@" in self.proxy:
                server_prefix = self.proxy.split("://")[0]
                address = self.proxy.split("@")[1]
                self.options['proxy'] = {
                    "server": server_prefix + "://" + address,
                    "username": self.proxy.split("://")[1].split(":")[0],
                    "password": self.proxy.split("://")[1].split("@")[0].split(":")[1],
                }
            else:
                self.options['proxy'] = {
                    "server": self.proxy
                }

        self.options.update(options)

        if self.executablePath != None:
            self.options["executablePath"] = self.executablePath

        try:
            self.browser = playwright.chromium.launch(args=self.args, **self.options)
        except Exception as e:
            logging.critical(e)
        
        self.page = self.create_page()
        self.get_params(self.page)

    def get_params(self, page) -> None:
        # self.browser_language = await self.page.evaluate("""() => { return navigator.language || navigator.userLanguage; }""")
        self.browser_language = ""
        # self.timezone_name = await self.page.evaluate("""() => { return Intl.DateTimeFormat().resolvedOptions().timeZone; }""")
        self.timezone_name = ""
        # self.browser_platform = await self.page.evaluate("""() => { return window.navigator.platform; }""")
        self.browser_platform = ""
        # self.browser_name = await self.page.evaluate("""() => { return window.navigator.appCodeName; }""")
        self.browser_name = ""
        # self.browser_version = await self.page.evaluate("""() => { return window.navigator.appVersion; }""")
        self.browser_version = ""

        self.width = page.evaluate("""() => { return screen.width; }""")
        self.height = page.evaluate("""() => { return screen.height; }""")

    def create_page(self):
        
        page = self.browser.newPage()
        page.evaluate(
            """() => {
        delete navigator.__proto__.webdriver;
        }"""
        )

        stealth(page)
        page.goto("about:blank")

        return page
    

    def sign_url(self, url):
        page = self.page
        verifyFp = "".join(
            random.choice(
                string.ascii_lowercase + string.ascii_uppercase + string.digits
            )
            for i in range(16)
        )

        if self.did == None:
            did = str(random.randint(10000, 999999999))
        else:
            did = self.did

        page.evaluate("() => { " + get_acrawler() + " }")
        return verifyFp, did, page.evaluate(
            '''() => {
        var url = "'''
            + url
            + "&verifyFp="
            + verifyFp
            + """&did="""
            + did
            + """"
        var token = window.byted_acrawler.sign({url: url});
        return token;
        }"""
        )
        

    def clean_up(self):
        self.browser.close()

    def find_redirect(self, url):
        self.page.goto(url, {"waitUntil": "load"})
        self.redirect_url = self.page.url

    def __format_proxy(self, proxy):
        if proxy != None:
            return {"http": proxy, "https": proxy}
        else:
            return None

    def __get_js(self):
        return requests.get(
            "https://sf16-muse-va.ibytedtos.com/obj/rc-web-sdk-gcs/acrawler.js",
            proxies=self.__format_proxy(self.proxy),
        ).text
