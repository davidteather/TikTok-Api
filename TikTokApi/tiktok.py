import json
import logging
import os
import random
import string
import time
from urllib.parse import quote, urlencode

import requests
from TikTokApi.api import user, music, search, hashtag, video, trending
from playwright.sync_api import sync_playwright

from .exceptions import *
from .utilities import update_messager

os.environ["no_proxy"] = "127.0.0.1,localhost"

BASE_URL = "https://m.tiktok.com/"
DESKTOP_BASE_URL = "https://www.tiktok.com/"


class TikTokApi:
    _instance = None

    @staticmethod
    def __new__(cls, *args, **kwargs):
        """The TikTokApi class. Used to interact with TikTok. This is a singleton
            class to prevent issues from arising with playwright

        ##### Parameters
        * logging_level: The logging level you want the program to run at, optional
            These are the standard python logging module's levels.

        * request_delay: The amount of time in seconds to wait before making a request, optional
            This is used to throttle your own requests as you may end up making too
            many requests to TikTok for your IP.

        * custom_device_id: A TikTok parameter needed to download videos, optional
            The code generates these and handles these pretty well itself, however
            for some things such as video download you will need to set a consistent
            one of these. All the methods take this as a optional parameter, however
            it's cleaner code to store this at the instance level. You can override
            this at the specific methods.

        * generate_static_device_id: A parameter that generates a custom_device_id at the instance level
            Use this if you want to download videos from a script but don't want to generate
            your own custom_device_id parameter.

        * custom_verifyFp: A TikTok parameter needed to work most of the time, optional
            To get this parameter look at [this video](https://youtu.be/zwLmLfVI-VQ?t=117)
            I recommend watching the entire thing, as it will help setup this package. All
            the methods take this as a optional parameter, however it's cleaner code
            to store this at the instance level. You can override this at the specific
            methods.

            You can use the following to generate `"".join(random.choice(string.digits)
            for num in range(19))`

        * use_test_endpoints: Send requests to TikTok's test endpoints, optional
            This parameter when set to true will make requests to TikTok's testing
            endpoints instead of the live site. I can't guarantee this will work
            in the future, however currently basically any custom_verifyFp will
            work here which is helpful.

        * proxy: A string containing your proxy address, optional
            If you want to do a lot of scraping of TikTok endpoints you'll likely
            need a proxy.

            Ex: "https://0.0.0.0:8080"

            All the methods take this as a optional parameter, however it's cleaner code
            to store this at the instance level. You can override this at the specific
            methods.

        * use_selenium: Option to use selenium over playwright, optional
            Playwright is selected by default and is the one that I'm designing the
            package to be compatable for, however if playwright doesn't work on
            your machine feel free to set this to True.

        * executablePath: The location of the driver, optional
            This shouldn't be needed if you're using playwright

        * **kwargs
            Parameters that are passed on to basically every module and methods
            that interact with this main class. These may or may not be documented
            in other places.
        """

        if cls._instance is None:
            cls._instance = super(TikTokApi, cls).__new__(cls)
            cls._instance._initialize(*args, **kwargs)
        return cls._instance

    def _initialize(self, **kwargs):
        # Add classes from the api folder
        user.User.parent = self
        self.user = user.User

        self.search = search.Search(self)

        music.Music.parent = self
        self.music = music.Music

        hashtag.Hashtag.parent = self
        self.hashtag = hashtag.Hashtag

        video.Video.parent = self
        self.video = video.Video
        
        trending.Trending.parent = self
        self.trending = trending.Trending

        logging.basicConfig(level=kwargs.get("logging_level", logging.WARNING))
        logging.info("Class initalized")

        # Some Instance Vars
        self.executablePath = kwargs.get("executablePath", None)

        if kwargs.get("custom_did") != None:
            raise Exception("Please use custom_device_id instead of custom_device_id")
        self.custom_device_id = kwargs.get("custom_device_id", None)
        self.user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/86.0.4240.111 Safari/537.36"
        )
        self.proxy = kwargs.get("proxy", None)
        self.custom_verifyFp = kwargs.get("custom_verifyFp")
        self.signer_url = kwargs.get("external_signer", None)
        self.request_delay = kwargs.get("request_delay", None)
        self.requests_extra_kwargs = kwargs.get("requests_extra_kwargs", {})

        if kwargs.get("use_test_endpoints", False):
            global BASE_URL
            BASE_URL = "https://t.tiktok.com/"
        if kwargs.get("use_selenium", False):
            from .browser_utilities.browser_selenium import browser
        else:
            from .browser_utilities.browser import browser

        if kwargs.get("generate_static_device_id", False):
            self.custom_device_id = "".join(
                random.choice(string.digits) for num in range(19)
            )

        if self.signer_url is None:
            self.browser = browser(**kwargs)
            self.user_agent = self.browser.user_agent

        try:
            self.timezone_name = self.__format_new_params(self.browser.timezone_name)
            self.browser_language = self.__format_new_params(
                self.browser.browser_language
            )
            self.width = self.browser.width
            self.height = self.browser.height
            self.region = self.browser.region
            self.language = self.browser.language
        except Exception as e:
            logging.exception(e)
            logging.warning(
                "An error ocurred while opening your browser but it was ignored."
            )
            logging.warning("Are you sure you ran python -m playwright install")

            self.timezone_name = ""
            self.browser_language = ""
            self.width = "1920"
            self.height = "1080"
            self.region = "US"
            self.language = "en"

    def get_data(self, path, use_desktop_base_url=False, **kwargs) -> dict:
        """Makes requests to TikTok and returns their JSON.

        This is all handled by the package so it's unlikely
        you will need to use this.
        """
        (
            region,
            language,
            proxy,
            maxCount,
            device_id,
        ) = self._process_kwargs(kwargs)
        kwargs["custom_device_id"] = device_id
        if self.request_delay is not None:
            time.sleep(self.request_delay)

        if self.proxy is not None:
            proxy = self.proxy

        if kwargs.get("custom_verifyFp") == None:
            if self.custom_verifyFp != None:
                verifyFp = self.custom_verifyFp
            else:
                verifyFp = "verify_khr3jabg_V7ucdslq_Vrw9_4KPb_AJ1b_Ks706M8zIJTq"
        else:
            verifyFp = kwargs.get("custom_verifyFp")

        tt_params = None
        send_tt_params = kwargs.get("send_tt_params", False)

        if use_desktop_base_url:
            full_url = DESKTOP_BASE_URL + path
        else:
            full_url = BASE_URL + path

        if self.signer_url is None:
            kwargs["custom_verifyFp"] = verifyFp
            verify_fp, device_id, signature, tt_params = self.browser.sign_url(
                full_url, calc_tt_params=send_tt_params, **kwargs
            )
            user_agent = self.browser.user_agent
            referrer = self.browser.referrer
        else:
            verify_fp, device_id, signature, user_agent, referrer = self.external_signer(
                full_url,
                custom_device_id=kwargs.get("custom_device_id"),
                verifyFp=kwargs.get("custom_verifyFp", verifyFp),
            )

        if not kwargs.get("send_tt_params", False):
            tt_params = None

        query = {"verifyFp": verify_fp, "device_id": device_id, "_signature": signature}
        url = "{}&{}".format(full_url, urlencode(query))

        h = requests.head(
            url,
            headers={"x-secsdk-csrf-version": "1.2.5", "x-secsdk-csrf-request": "1"},
            proxies=self._format_proxy(proxy),
            **self.requests_extra_kwargs,
        )

        csrf_token = None
        if not use_desktop_base_url:
            csrf_session_id = h.cookies["csrf_session_id"]
            csrf_token = h.headers["X-Ware-Csrf-Token"].split(",")[1]
            kwargs["csrf_session_id"] = csrf_session_id

        headers = {
            "authority": "m.tiktok.com",
            "method": "GET",
            "path": url.split("tiktok.com")[1],
            "scheme": "https",
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip",
            "accept-language": "en-US,en;q=0.9",
            "origin": referrer,
            "referer": referrer,
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "none",
            "sec-gpc": "1",
            "user-agent": user_agent,
            "x-secsdk-csrf-token": csrf_token,
            "x-tt-params": tt_params,
        }

        logging.info(f"GET: {url}\n\theaders: {headers}")
        r = requests.get(
            url,
            headers=headers,
            cookies=self.get_cookies(**kwargs),
            proxies=self._format_proxy(proxy),
            **self.requests_extra_kwargs,
        )

        try:
            json = r.json()
            if (
                json.get("type") == "verify"
                or json.get("verifyConfig", {}).get("type", "") == "verify"
            ):
                logging.error(
                    "Tiktok wants to display a catcha. Response is:\n" + r.text
                )
                logging.error(self.get_cookies(**kwargs))
                raise TikTokCaptchaError()

            # statusCode from props->pageProps->statusCode thanks @adiantek on #403
            error_codes = {
                "0": "OK",
                "450": "CLIENT_PAGE_ERROR",
                "10000": "VERIFY_CODE",
                "10101": "SERVER_ERROR_NOT_500",
                "10102": "USER_NOT_LOGIN",
                "10111": "NET_ERROR",
                "10113": "SHARK_SLIDE",
                "10114": "SHARK_BLOCK",
                "10119": "LIVE_NEED_LOGIN",
                "10202": "USER_NOT_EXIST",
                "10203": "MUSIC_NOT_EXIST",
                "10204": "VIDEO_NOT_EXIST",
                "10205": "HASHTAG_NOT_EXIST",
                "10208": "EFFECT_NOT_EXIST",
                "10209": "HASHTAG_BLACK_LIST",
                "10210": "LIVE_NOT_EXIST",
                "10211": "HASHTAG_SENSITIVITY_WORD",
                "10212": "HASHTAG_UNSHELVE",
                "10213": "VIDEO_LOW_AGE_M",
                "10214": "VIDEO_LOW_AGE_T",
                "10215": "VIDEO_ABNORMAL",
                "10216": "VIDEO_PRIVATE_BY_USER",
                "10217": "VIDEO_FIRST_REVIEW_UNSHELVE",
                "10218": "MUSIC_UNSHELVE",
                "10219": "MUSIC_NO_COPYRIGHT",
                "10220": "VIDEO_UNSHELVE_BY_MUSIC",
                "10221": "USER_BAN",
                "10222": "USER_PRIVATE",
                "10223": "USER_FTC",
                "10224": "GAME_NOT_EXIST",
                "10225": "USER_UNIQUE_SENSITIVITY",
                "10227": "VIDEO_NEED_RECHECK",
                "10228": "VIDEO_RISK",
                "10229": "VIDEO_R_MASK",
                "10230": "VIDEO_RISK_MASK",
                "10231": "VIDEO_GEOFENCE_BLOCK",
                "10404": "FYP_VIDEO_LIST_LIMIT",
                "undefined": "MEDIA_ERROR",
            }
            statusCode = json.get("statusCode", 0)
            logging.info(f"TikTok Returned: {json}")
            if statusCode == 10201:
                # Invalid Entity
                raise TikTokNotFoundError(
                    "TikTok returned a response indicating the entity is invalid"
                )
            elif statusCode == 10219:
                # not available in this region
                raise TikTokNotAvailableError("Content not available for this region")
            elif statusCode != 0 and statusCode != -1:
                raise GenericTikTokError(
                    error_codes.get(
                        statusCode, f"TikTok sent an unknown StatusCode of {statusCode}"
                    )
                )

            return r.json()
        except ValueError as e:
            text = r.text
            logging.error("TikTok response: " + text)
            if len(text) == 0:
                raise EmptyResponseError(
                    "Empty response from Tiktok to " + url
                ) from None
            else:
                logging.error("Converting response to JSON failed")
                logging.error(e)
                raise JSONDecodeFailure() from e

    def clean_up(self):
        """A basic cleanup method, called automatically from the code"""
        self.__del__()

    def __del__(self):
        """A basic cleanup method, called automatically from the code"""
        try:
            self.browser.clean_up()
        except Exception:
            pass
        try:
            get_playwright().stop()
        except Exception:
            pass
        TikTokApi._instance = None

    def external_signer(self, url, custom_device_id=None, verifyFp=None):
        """Makes requests to an external signer instead of using a browser.

        ##### Parameters
        * url: The server to make requests to
            This server is designed to sign requests. You can find an example
            of this signature server in the examples folder.

        * custom_device_id: A TikTok parameter needed to download videos
            The code generates these and handles these pretty well itself, however
            for some things such as video download you will need to set a consistent
            one of these.

        * custom_verifyFp: A TikTok parameter needed to work most of the time,
            To get this parameter look at [this video](https://youtu.be/zwLmLfVI-VQ?t=117)
            I recommend watching the entire thing, as it will help setup this package.
        """
        if custom_device_id is not None:
            query = {
                "url": url,
                "custom_device_id": custom_device_id,
                "verifyFp": verifyFp,
            }
        else:
            query = {"url": url, "verifyFp": verifyFp}
        data = requests.get(
            self.signer_url + "?{}".format(urlencode(query)),
            **self.requests_extra_kwargs,
        )
        parsed_data = data.json()

        return (
            parsed_data["verifyFp"],
            parsed_data["device_id"],
            parsed_data["_signature"],
            parsed_data["user_agent"],
            parsed_data["referrer"],
        )

    def get_cookies(self, **kwargs):
        """Extracts cookies from the kwargs passed to the function for get_data"""
        device_id = kwargs.get(
            "custom_device_id",
            "".join(random.choice(string.digits) for num in range(19)),
        )
        if kwargs.get("custom_verifyFp") == None:
            if self.custom_verifyFp != None:
                verifyFp = self.custom_verifyFp
            else:
                verifyFp = "verify_khr3jabg_V7ucdslq_Vrw9_4KPb_AJ1b_Ks706M8zIJTq"
        else:
            verifyFp = kwargs.get("custom_verifyFp")

        if kwargs.get("force_verify_fp_on_cookie_header", False):
            return {
                "tt_webid": device_id,
                "tt_webid_v2": device_id,
                "csrf_session_id": kwargs.get("csrf_session_id"),
                "tt_csrf_token": "".join(
                    random.choice(string.ascii_uppercase + string.ascii_lowercase)
                    for i in range(16)
                ),
                "s_v_web_id": verifyFp,
                "ttwid": kwargs.get("ttwid"),
            }
        else:
            return {
                "tt_webid": device_id,
                "tt_webid_v2": device_id,
                "csrf_session_id": kwargs.get("csrf_session_id"),
                "tt_csrf_token": "".join(
                    random.choice(string.ascii_uppercase + string.ascii_lowercase)
                    for i in range(16)
                ),
                "ttwid": kwargs.get("ttwid"),
            }

    def get_bytes(self, **kwargs) -> bytes:
        """Returns TikTok's response as bytes, similar to get_data"""
        (
            region,
            language,
            proxy,
            maxCount,
            device_id,
        ) = self._process_kwargs(kwargs)
        kwargs["custom_device_id"] = device_id
        if self.signer_url is None:
            verify_fp, device_id, signature, _ = self.browser.sign_url(
                calc_tt_params=False, **kwargs
            )
            user_agent = self.browser.user_agent
            referrer = self.browser.referrer
        else:
            verify_fp, device_id, signature, user_agent, referrer = self.external_signer(
                kwargs["url"], custom_device_id=kwargs.get("custom_device_id", None)
            )
        query = {"verifyFp": verify_fp, "_signature": signature}
        url = "{}&{}".format(kwargs["url"], urlencode(query))
        r = requests.get(
            url,
            headers={
                "Accept": "*/*",
                "Accept-Encoding": "identity;q=1, *;q=0",
                "Accept-Language": "en-US;en;q=0.9",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Host": url.split("/")[2],
                "Pragma": "no-cache",
                "Range": "bytes=0-",
                "Referer": "https://www.tiktok.com/",
                "User-Agent": user_agent,
            },
            proxies=self._format_proxy(proxy),
            cookies=self.get_cookies(**kwargs),
        )
        return r.content

    @staticmethod
    def generate_device_id():
        """Generates a valid device_id for other methods. Pass this as the custom_device_id field to download videos"""
        return "".join([random.choice(string.digits) for num in range(19)])

    #
    # PRIVATE METHODS
    #

    def _format_proxy(self, proxy) -> dict:
        """
        Formats the proxy object
        """
        if proxy is None and self.proxy is not None:
            proxy = self.proxy
        if proxy is not None:
            return {"http": proxy, "https": proxy}
        else:
            return None

    # Process the kwargs
    def _process_kwargs(self, kwargs):
        region = kwargs.get("region", "US")
        language = kwargs.get("language", "en")
        proxy = kwargs.get("proxy", None)
        maxCount = kwargs.get("maxCount", 35)

        if kwargs.get("custom_device_id", None) != None:
            device_id = kwargs.get("custom_device_id")
        else:
            if self.custom_device_id != None:
                device_id = self.custom_device_id
            else:
                device_id = "".join(random.choice(string.digits) for num in range(19))
        return region, language, proxy, maxCount, device_id


    def __get_js(self, proxy=None) -> str:
        return requests.get(
            "https://sf16-muse-va.ibytedtos.com/obj/rc-web-sdk-gcs/acrawler.js",
            proxies=self._format_proxy(proxy),
            **self.requests_extra_kwargs,
        ).text

    def __format_new_params(self, parm) -> str:
        # TODO: Maybe try not doing this? It should be handled by the urlencode.
        return parm.replace("/", "%2F").replace(" ", "+").replace(";", "%3B")

    def _add_url_params(self) -> str:
        query = {
            "aid": 1988,
            "app_name": "tiktok_web",
            "device_platform": "web_mobile",
            "region": self.region or "US",
            "priority_region": "",
            "os": "ios",
            "referer": "",
            "root_referer": "",
            "cookie_enabled": "true",
            "screen_width": self.width,
            "screen_height": self.height,
            "browser_language": self.browser_language.lower() or "en-us",
            "browser_platform": "iPhone",
            "browser_name": "Mozilla",
            "browser_version": self.__format_new_params(self.user_agent),
            "browser_online": "true",
            "timezone_name": self.timezone_name or "America/Chicago",
            "is_page_visible": "true",
            "focus_state": "true",
            "is_fullscreen": "false",
            "history_len": random.randint(0, 30),
            "language": self.language or "en",
        }
        return urlencode(query)
