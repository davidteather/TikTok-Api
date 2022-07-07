import random
import time
import string
from typing import Any, Optional
import requests
import logging
import time
import random
import json
import re
from .browser_interface import BrowserInterface
from urllib.parse import parse_qsl, urlparse
import threading
from ..utilities import LOGGER_NAME
from .get_acrawler import _get_acrawler, _get_tt_params_script
from playwright.async_api import async_playwright
import asyncio

logger = logging.getLogger(LOGGER_NAME)


class browser(BrowserInterface):

    def __init__(self, **kwargs):
        pass

    @staticmethod
    async def create(
        **kwargs,
    ):
        self = browser()
        self.kwargs = kwargs
        self.debug = kwargs.get("debug", False)
        self.proxy = kwargs.get("proxy", None)
        self.api_url = kwargs.get("api_url", None)
        self.referrer = kwargs.get("referer", "https://www.tiktok.com/")
        self.language = kwargs.get("language", "en")
        self.executable_path = kwargs.get("executable_path", None)
        self.device_id = kwargs.get("custom_device_id", None)

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

        if self.executable_path is not None:
            self.options["executable_path"] = self.executable_path

        self._thread_locals = threading.local()
        self._thread_locals.playwright = await async_playwright().start()
        self.playwright = self._thread_locals.playwright
        self.browser = await self.playwright.webkit.launch(
            args=self.args, **self.options
        )
        context = await self._create_context(set_useragent=True)
        page = await context.new_page()
        await self.get_params(page)
        await context.close()

        return self

    async def get_params(self, page) -> None:
        self.browser_language = self.kwargs.get(
            "browser_language",
            await page.evaluate("""() => { return navigator.language; }"""),
        )
        self.browser_version = await page.evaluate(
            """() => { return window.navigator.appVersion; }"""
        )

        if len(self.browser_language.split("-")) == 0:
            self.region = self.kwargs.get("region", "US")
            self.language = self.kwargs.get("language", "en")
        elif len(self.browser_language.split("-")) == 1:
            self.region = self.kwargs.get("region", "US")
            self.language = self.browser_language.split("-")[0]
        else:
            self.region = self.kwargs.get("region", self.browser_language.split("-")[1])
            self.language = self.kwargs.get(
                "language", self.browser_language.split("-")[0]
            )

        self.timezone_name = self.kwargs.get(
            "timezone_name",
            await page.evaluate(
                """() => { return Intl.DateTimeFormat().resolvedOptions().timeZone; }"""
            ),
        )
        self.width = await page.evaluate("""() => { return screen.width; }""")
        self.height = await page.evaluate("""() => { return screen.height; }""")

    async def _create_context(self, set_useragent=False):
        iphone = self.playwright.devices["iPhone 11 Pro"]
        iphone["viewport"] = {
            "width": random.randint(320, 1920),
            "height": random.randint(320, 1920),
        }
        iphone["device_scale_factor"] = random.randint(1, 3)
        iphone["is_mobile"] = random.randint(1, 2) == 1
        iphone["has_touch"] = random.randint(1, 2) == 1

        iphone["bypass_csp"] = True

        context = await self.browser.new_context(**iphone)
        if set_useragent:
            self.user_agent = iphone["user_agent"]

        return context

    def _base36encode(self, number, alphabet="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
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
        scenario_title = self._base36encode(int(time.time() * 1000))
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

    async def sign_url(self, url, calc_tt_params=False, **kwargs):
        async def process(route):
            await route.abort()

        tt_params = None
        context = await self._create_context()
        page = await context.new_page()

        if calc_tt_params:
            await page.route(
                re.compile(r"(\.png)|(\.jpeg)|(\.mp4)|(x-expire)"), process
            )
            await page.goto(
                kwargs.get("default_url", "https://www.tiktok.com/@redbull"),
                wait_until="load",
            )

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
                "custom_verify_fp",
                "verify_khgp4f49_V12d4mRX_MdCO_4Wzt_Ar0k_z4RCQC9pUDpX",
            )

        if kwargs.get("custom_device_id") is not None:
            device_id = kwargs.get("custom_device_id", None)
        elif self.device_id is None:
            device_id = str(random.randint(10000, 999999999))
        else:
            device_id = self.device_id

        url = "{}&verifyFp={}&device_id={}".format(url, verifyFp, device_id)

        await page.add_script_tag(content=_get_acrawler())
        evaluatedPage = await page.evaluate(
            '''() => {
            var url = "'''
            + url
            + """"
            var token = window.byted_acrawler.sign({url: url});
            
            return token;
            }"""
        )

        url = "{}&_signature={}".format(url, evaluatedPage)

        if calc_tt_params:
            await page.add_script_tag(content=_get_tt_params_script())

            tt_params = await page.evaluate(
                """() => {
                    return window.genXTTParams("""
                + json.dumps(dict(parse_qsl(urlparse(url).query)))
                + """);
            
                }"""
            )

        await context.close()
        return (verifyFp, device_id, evaluatedPage, tt_params)

    async def _clean_up(self):
        await self.browser.close()
        await self.playwright.stop()

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
