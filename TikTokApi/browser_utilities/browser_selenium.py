import random
import time
import requests
import logging
from threading import Thread
import time
import re
import random
import json
from .browser_interface import BrowserInterface
from selenium_stealth import stealth
from selenium import webdriver
from .get_acrawler import get_acrawler, get_tt_params_script
from urllib.parse import splitquery, parse_qs, parse_qsl

from ..utilities import LOGGER_NAME

log = logging.getLogger(LOGGER_NAME)


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
        self.executablePath = kwargs.get("executablePath", "chromedriver")
        self.device_id = kwargs.get("custom_device_id", None)

        args = kwargs.get("browser_args", [])
        options = kwargs.get("browser_options", {})

        if len(args) == 0:
            self.args = []
        else:
            self.args = args

        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("log-level=2")
        self.options = {
            "headless": True,
            "handleSIGINT": True,
            "handleSIGTERM": True,
            "handleSIGHUP": True,
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

        # self.options.update(options)

        if self.executablePath is not None:
            self.options["executablePath"] = self.executablePath

        try:
            self.browser = webdriver.Chrome(
                executable_path=self.executablePath, chrome_options=options
            )
        except Exception as e:
            raise e

        # Page avoidance
        self.setup_browser()
        # page.close()

    def setup_browser(self):
        stealth(
            self.browser,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )

        self.get_params(self.browser)
        # NOTE: Slower than playwright at loading this because playwright can ignore unneeded files.
        self.browser.get("https://www.tiktok.com/@redbull")
        self.browser.execute_script(get_acrawler())
        self.browser.execute_script(get_tt_params_script())

    def get_params(self, page) -> None:
        self.userAgent = page.execute_script("""return navigator.userAgent""")
        self.browser_language = self.kwargs.get(
            "browser_language", ("""return navigator.language""")
        )
        self.browser_version = """return window.navigator.appVersion"""

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
            ("""return Intl.DateTimeFormat().resolvedOptions().timeZone"""),
        )
        self.width = """return screen.width"""
        self.height = """return screen.height"""

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

    def sign_url(self, calc_tt_params=False, **kwargs):
        url = kwargs.get("url", None)
        if url is None:
            raise Exception("sign_url required a url parameter")

        tt_params = None
        if kwargs.get("gen_new_verifyFp", False):
            verifyFp = self.gen_verifyFp()
        else:
            verifyFp = kwargs.get(
                "custom_verifyFp",
                "verify_khgp4f49_V12d4mRX_MdCO_4Wzt_Ar0k_z4RCQC9pUDpX",
            )

        if kwargs.get("custom_device_id") is not None:
            device_id = kwargs.get("custom_device_id", None)
        elif self.device_id is None:
            device_id = str(random.randint(10000, 999999999))
        else:
            device_id = self.device_id

        url = "{}&verifyFp={}&device_id={}".format(url, verifyFp, device_id)
        # self.browser.execute_script(content=get_acrawler())
        # Should be covered by an earlier addition of get_acrawler.
        evaluatedPage = (
            self.browser.execute_script(
                '''
        var url = "'''
                + url
                + """"
        var token = window.byted_acrawler.sign({url: url});
        return token;
        """
            ),
        )

        url = "{}&_signature={}".format(url, evaluatedPage)
        # self.browser.execute_script(content=get_tt_params_script())
        # Should be covered by an earlier addition of get_acrawler.

        tt_params = self.browser.execute_script(
            """() => {
                return window.genXTTParams("""
            + json.dumps(dict(parse_qsl(splitquery(url)[1])))
            + """);
        
            }"""
        )

        return (verifyFp, device_id, evaluatedPage, tt_params)

    def clean_up(self):
        try:
            self.browser.close()
        except Exception:
            log.warning("cleanup of browser failed", exc_info=True)

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
