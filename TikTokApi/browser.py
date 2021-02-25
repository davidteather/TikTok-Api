import random
import time
import string
import requests
import logging
from threading import Thread
import time
import datetime
import random


# Import Detection From Stealth
from .stealth import stealth
from .get_acrawler import get_acrawler
from playwright.sync_api import sync_playwright

playwright = None


def get_playwright():
    global playwright
    if playwright is None:
        try:
            playwright = sync_playwright().start()
        except Exception as e:
            raise e

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

        args = kwargs.get("browser_args", [])
        options = kwargs.get("browser_options", {})

        if len(args) == 0:
            self.args = []
        else:
            self.args = args

        self.options = {
            "headless": True,
            "handle_sigint": True,
            "handle_sigterm": True,
            "handle_sighup": True,
        }

        if self.proxy is not None:
            if "@" in self.proxy:
                server_prefix = self.proxy.split("://")[0]
                address = self.proxy.split("@")[1]
                self.options["proxy"] = {
                    "server": server_prefix + "://" + address,
                    "username": self.proxy.split("://")[1].split(":")[0],
                    "password": self.proxy.split("://")[1].split("@")[0].split(":")[1],
                }
            else:
                self.options["proxy"] = {"server": self.proxy}

        self.options.update(options)

        if self.executablePath is not None:
            self.options["executablePath"] = self.executablePath

        try:
            self.browser = get_playwright().webkit.launch(
                args=self.args, **self.options
            )
        except Exception as e:
            raise e
            logging.critical(e)

        context = self.create_context(set_useragent=True)
        page = context.new_page()
        self.get_params(page)
        context.close()

    def get_params(self, page) -> None:
        # self.browser_language = await self.page.evaluate("""() => { return
        # navigator.language || navigator.userLanguage; }""")
        self.browser_language = ""
        # self.timezone_name = await self.page.evaluate("""() => { return
        # Intl.DateTimeFormat().resolvedOptions().timeZone; }""")
        self.timezone_name = ""
        # self.browser_platform = await self.page.evaluate("""() => { return window.navigator.platform; }""")
        self.browser_platform = ""
        # self.browser_name = await self.page.evaluate("""() => { return window.navigator.appCodeName; }""")
        self.browser_name = ""
        # self.browser_version = await self.page.evaluate("""() => { return window.navigator.appVersion; }""")
        self.browser_version = ""

        self.width = page.evaluate("""() => { return screen.width; }""")
        self.height = page.evaluate("""() => { return screen.height; }""")

    def create_context(self, set_useragent=False):
        iphone = playwright.devices["iPhone 11 Pro"]
        iphone["viewport"] = {
            "width": random.randint(320, 1920),
            "height": random.randint(320, 1920),
        }
        iphone["device_scale_factor"] = random.randint(1, 3)
        iphone["is_mobile"] = random.randint(1, 2) == 1
        iphone["has_touch"] = random.randint(1, 2) == 1

        context = self.browser.new_context(**iphone)
        if set_useragent:
            self.userAgent = iphone["user_agent"]

        return context

    def base36encode(self, number, alphabet="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        """Converts an integer to a base36 string."""
        base36 = ""
        sign = ""

        if number < 0:
            sign = "-"
            number = -number

        if 0 <= number < len(alphabet):
            return sign + alphabet[number]

        while number != 0:
            number, i = divmod(number, len(alphabet))
            base36 = alphabet[i] + base36

        return sign + base36

    def gen_verifyFp(self):
        chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"[:]
        chars_len = len(chars)
        scenario_title = self.base36encode(int(time.time() * 1000))
        uuid = [0] * 36
        uuid[8] = "_"
        uuid[13] = "_"
        uuid[18] = "_"
        uuid[23] = "_"
        uuid[14] = "4"

        for i in range(36):
            if uuid[i] != 0:
                continue
            r = int(random.random() * chars_len)
            uuid[i] = chars[int((3 & r) | 8 if i == 19 else r)]

        return f'verify_{scenario_title.lower()}_{"".join(uuid)}'

    def sign_url(self, **kwargs):
        url = kwargs.get("url", None)
        if url is None:
            raise Exception("sign_url required a url parameter")
        context = self.create_context()
        page = context.new_page()
        verifyFp = "".join(
            random.choice(
                string.ascii_lowercase + string.ascii_uppercase + string.digits
            )
            for i in range(16)
        )
        if kwargs.get("gen_new_verifyFp", False):
            verifyFp = self.gen_verifyFp()
        else:
            verifyFp = kwargs.get(
                "custom_verifyFp",
                "verify_khgp4f49_V12d4mRX_MdCO_4Wzt_Ar0k_z4RCQC9pUDpX",
            )

        if kwargs.get("custom_did") is not None:
            did = kwargs.get("custom_did", None)
        elif self.did is None:
            did = str(random.randint(10000, 999999999))
        else:
            did = self.did

        page.set_content("<script> " + get_acrawler() + " </script>")
        evaluatedPage = page.evaluate(
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
        context.close()
        return (
            verifyFp,
            did,
            evaluatedPage,
        )

    def clean_up(self):
        try:
            self.browser.close()
        except Exception:
            logging.info("cleanup failed")
        # playwright.stop()

    def find_redirect(self, url):
        self.page.goto(url, {"waitUntil": "load"})
        self.redirect_url = self.page.url

    def __format_proxy(self, proxy):
        if proxy is not None:
            return {"http": proxy, "https": proxy}
        else:
            return None

    def __get_js(self):
        return requests.get(
            "https://sf16-muse-va.ibytedtos.com/obj/rc-web-sdk-gcs/acrawler.js",
            proxies=self.__format_proxy(self.proxy),
        ).text
