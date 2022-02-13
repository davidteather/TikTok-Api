import random
import time
import string
import requests
import logging
import time
import random
import json
import re
from .browser_interface import BrowserInterface
from urllib.parse import parse_qsl, urlparse

from ..utilities import LOGGER_NAME
from .get_acrawler import _get_acrawler, _get_tt_params_script
from playwright.sync_api import sync_playwright

playwright = None

logger = logging.getLogger(LOGGER_NAME)


def get_playwright():
    global playwright
    if playwright is None:
        try:
            playwright = sync_playwright().start()
        except Exception as e:
            raise e

    return playwright


class browser(BrowserInterface):
    def __init__(
        self,
        **kwargs,
    ):
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

        try:
            self.browser = get_playwright().webkit.launch(
                args=self.args, **self.options
            )
        except Exception as e:
            logger.critical("Webkit launch failed", exc_info=True)
            raise e

        context = self._create_context(set_useragent=True)
        page = context.new_page()
        self.get_params(page)
        context.close()

    def get_params(self, page) -> None:
        self.browser_language = self.kwargs.get(
            "browser_language",
            page.evaluate("""() => { return navigator.language; }"""),
        )
        self.browser_version = page.evaluate(
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
            page.evaluate(
                """() => { return Intl.DateTimeFormat().resolvedOptions().timeZone; }"""
            ),
        )
        self.width = page.evaluate("""() => { return screen.width; }""")
        self.height = page.evaluate("""() => { return screen.height; }""")

    def _create_context(self, set_useragent=False):
        iphone = playwright.devices["iPhone 11 Pro"]
        iphone["viewport"] = {
            "width": random.randint(320, 1920),
            "height": random.randint(320, 1920),
        }
        iphone["device_scale_factor"] = random.randint(1, 3)
        iphone["is_mobile"] = random.randint(1, 2) == 1
        iphone["has_touch"] = random.randint(1, 2) == 1

        iphone["bypass_csp"] = True

        context = self.browser.new_context(**iphone)
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

    def sign_url(self, url, calc_tt_params=False, **kwargs):
        def process(route):
            route.abort()

        tt_params = None
        context = self._create_context()
        page = context.new_page()

        if calc_tt_params:
            page.route(re.compile(r"(\.png)|(\.jpeg)|(\.mp4)|(x-expire)"), process)
            page.goto(
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

        page.add_script_tag(content=_get_acrawler())
        evaluatedPage = page.evaluate(
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
            page.add_script_tag(content=_get_tt_params_script())

            tt_params = page.evaluate(
                """() => {
                    return window.genXTTParams("""
                + json.dumps(dict(parse_qsl(urlparse(url).query)))
                + """);
            
                }"""
            )

        context.close()
        return (verifyFp, device_id, evaluatedPage, tt_params)

    def _clean_up(self):
        try:
            self.browser.close()
        except Exception:
            logger.exception("cleanup failed")
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
