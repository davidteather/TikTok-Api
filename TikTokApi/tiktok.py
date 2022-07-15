import asyncio
import json
import logging
import os
import random
import string
import threading
import time
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlencode

import requests

from .api.comment import Comment
from .api.hashtag import Hashtag
from .api.search import Search
from .api.sound import Sound
from .api.trending import Trending
from .api.user import User
from .api.video import Video
from .browser_utilities.browser import browser
from .exceptions import *
from .utilities import LOGGER_NAME

os.environ["no_proxy"] = "127.0.0.1,localhost"

BASE_URL = "https://m.tiktok.com/"
DESKTOP_BASE_URL = "https://www.tiktok.com/"

_thread_lock = threading.Lock()

ERROR_CODES = {
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


class TikTokApi:
    _is_context_manager = False
    user = User
    search = Search
    sound = Sound
    hashtag = Hashtag
    video = Video
    trending = Trending
    comment = Comment
    logger = logging.getLogger(LOGGER_NAME)

    def __init__(
            self,
            logging_level: int = logging.WARNING,
            request_delay: Optional[int] = None,
            custom_device_id: Optional[str] = None,
            generate_static_device_id: Optional[bool] = False,
            custom_verify_fp: Optional[str] = None,
            use_test_endpoints: Optional[bool] = False,
            proxy: Optional[str] = None,
            executable_path: Optional[str] = None,
            *args,
            **kwargs,
    ):
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

        * custom_verify_fp: A TikTok parameter needed to work most of the time, optional
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
            in the future, however currently basically any custom_verify_fp will
            work here which is helpful.

        * proxy: A string containing your proxy address, optional
            If you want to do a lot of scraping of TikTok endpoints you'll likely
            need a proxy.

            Ex: "https://0.0.0.0:8080"

            All the methods take this as a optional parameter, however it's cleaner code
            to store this at the instance level. You can override this at the specific
            methods.

        * executable_path: The location of the driver, optional
            This shouldn't be needed if you're using playwright

        * **kwargs
            Parameters that are passed on to basically every module and methods
            that interact with this main class. These may or may not be documented
            in other places.
        """

        self.logger.setLevel(logging_level)

        with _thread_lock:
            self._initialize(
                request_delay=request_delay,
                custom_device_id=custom_device_id,
                generate_static_device_id=generate_static_device_id,
                custom_verify_fp=custom_verify_fp,
                use_test_endpoints=use_test_endpoints,
                proxy=proxy,
                executable_path=executable_path,
                *args,
                **kwargs,
            )

    def _initialize(self, **kwargs):
        # Add classes from the api folder
        User.parent = self
        Search.parent = self
        Sound.parent = self
        Hashtag.parent = self
        Video.parent = self
        Trending.parent = self
        Comment.parent = self

        # Some Instance Vars
        self._executable_path = kwargs.get("executable_path", None)
        self.cookie_jar = None

        if kwargs.get("custom_did") != None:
            raise Exception("Please use 'custom_device_id' instead of 'custom_did'")
        self._custom_device_id = kwargs.get("custom_device_id", None)
        self._user_agent = "5.0 (iPhone; CPU iPhone OS 14_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1"  # TODO: Randomly generate agents
        self._proxy = kwargs.get("proxy", None)
        self._custom_verify_fp = kwargs.get("custom_verify_fp")
        self._signer_url = kwargs.get("external_signer", None)
        self._request_delay = kwargs.get("request_delay", None)
        self._requests_extra_kwargs = kwargs.get("requests_extra_kwargs", {})

        if kwargs.get("use_test_endpoints", False):
            global BASE_URL
            BASE_URL = "https://t.tiktok.com/"

        if kwargs.get("generate_static_device_id", False):
            self._custom_device_id = "".join(
                random.choice(string.digits) for num in range(19)
            )

        if self._signer_url is None:
            self._browser = asyncio.get_event_loop().run_until_complete(
                asyncio.gather(browser.create(**kwargs))
            )[0]

            self._user_agent = self._browser.user_agent

        try:
            self._timezone_name = self._browser.timezone_name
            self._browser_language = self._browser.browser_language
            self._width = self._browser.width
            self._height = self._browser.height
            self._region = self._browser.region
            self._language = self._browser.language
        except Exception as e:
            self.logger.exception(
                "An error occurred while opening your browser, but it was ignored\n",
                "Are you sure you ran python -m playwright install?",
            )

            self._timezone_name = ""
            self._browser_language = ""
            self._width = "1920"
            self._height = "1080"
            self._region = "US"
            self._language = "en"
            raise e from e

    def get_data(self, path, subdomain="m", **kwargs) -> dict:
        """Makes requests to TikTok and returns their JSON.

        This is all handled by the package so it's unlikely
        you will need to use this.
        """
        processed = self._process_kwargs(kwargs)
        kwargs["custom_device_id"] = processed.device_id
        if self._request_delay is not None:
            time.sleep(self._request_delay)

        if self._proxy is not None:
            proxy = self._proxy

        if kwargs.get("custom_verify_fp") == None:
            if self._custom_verify_fp != None:
                verifyFp = self._custom_verify_fp
            else:
                verifyFp = "verify_khr3jabg_V7ucdslq_Vrw9_4KPb_AJ1b_Ks706M8zIJTq"
        else:
            verifyFp = kwargs.get("custom_verify_fp")

        tt_params = None
        send_tt_params = kwargs.get("send_tt_params", False)

        full_url = f"https://{subdomain}.tiktok.com/" + path

        if self._signer_url is None:
            kwargs["custom_verify_fp"] = verifyFp
            (
                verify_fp,
                device_id,
                signature,
                tt_params,
            ) = asyncio.get_event_loop().run_until_complete(
                asyncio.gather(
                    self._browser.sign_url(
                        full_url, calc_tt_params=send_tt_params, **kwargs
                    )
                )
            )[
                0
            ]

            user_agent = self._browser.user_agent
            referrer = self._browser.referrer
        else:
            (
                verify_fp,
                device_id,
                signature,
                user_agent,
                referrer,
            ) = self.external_signer(
                full_url,
                custom_device_id=kwargs.get("custom_device_id"),
                verifyFp=kwargs.get("custom_verify_fp", verifyFp),
            )

        if not kwargs.get("send_tt_params", False):
            tt_params = None

        query = {"verifyFp": verify_fp, "device_id": device_id, "_signature": signature}
        url = "{}&{}".format(full_url, urlencode(query))

        h = requests.head(
            url,
            headers={"x-secsdk-csrf-version": "1.2.5", "x-secsdk-csrf-request": "1"},
            proxies=self._format_proxy(processed.proxy),
            **self._requests_extra_kwargs,
        )

        csrf_token = None
        if subdomain == "m":
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

        self.logger.debug(f"GET: %s\n\theaders: %s", url, headers)
        r = requests.get(
            url,
            headers=headers,
            cookies=self._get_cookies(**kwargs),
            proxies=self._format_proxy(processed.proxy),
            **self._requests_extra_kwargs,
        )

        self.cookie_jar = r.cookies

        try:
            parsed_data = r.json()
            if (
                    parsed_data.get("type") == "verify"
                    or parsed_data.get("verifyConfig", {}).get("type", "") == "verify"
            ):
                self.logger.error(
                    "Tiktok wants to display a captcha.\nResponse:\n%s\nCookies:\n%s\nURL:\n%s",
                    r.text,
                    self._get_cookies(**kwargs),
                    url,
                )
                raise CaptchaException(0, None,
                    "TikTok blocks this request displaying a Captcha \nTip: Consider using a proxy or a custom_verify_fp as method parameters"
                )

            # statusCode from props->pageProps->statusCode thanks @adiantek on #403

            statusCode = parsed_data.get("statusCode", 0)
            self.logger.debug(f"TikTok Returned: %s", json)
            if statusCode == 10201:
                # Invalid Entity
                raise NotFoundException(10201, r,
                                        "TikTok returned a response indicating the entity is invalid"
                                        )
            elif statusCode == 10219:
                # Not available in this region
                raise NotAvailableException(10219, r, "Content not available for this region")
            elif statusCode != 0 and statusCode != -1:
                raise TikTokException(statusCode, r,
                                      ERROR_CODES.get(statusCode, f"TikTok sent an unknown StatusCode of {statusCode}")
                                      )

            return r.json()
        except ValueError as e:
            text = r.text
            self.logger.debug("TikTok response: %s", text)
            if len(text) == 0:
                raise EmptyResponseException(0, None,
                    "Empty response from Tiktok to " + url
                ) from None
            else:
                raise InvalidJSONException(0, r, "TikTok sent invalid JSON") from e

    def get_data_no_sig(self, path, subdomain="m", **kwargs) -> dict:
        processed = self._process_kwargs(kwargs)
        full_url = f"https://{subdomain}.tiktok.com/" + path
        referrer = self._browser.referrer
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:101.0) Gecko/20100101 Firefox/101.0",
            "authority": "m.tiktok.com",
            "method": "GET",
            "path": full_url.split("tiktok.com")[1],
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
        }
        self.logger.debug(f"GET: %s\n\theaders: %s", full_url, headers)

        r = requests.get(
            full_url,
            headers=headers,
            cookies=self._get_cookies(**kwargs),
            proxies=self._format_proxy(processed.proxy),
            **self._requests_extra_kwargs,
        )
        return r.json()

    def __del__(self):
        """A basic cleanup method, called automatically from the code"""
        if not self._is_context_manager:
            self.logger.debug(
                "TikTokAPI was shutdown improperlly. Ensure the instance is terminated with .shutdown()"
            )
            self.shutdown()
        return

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

        * custom_verify_fp: A TikTok parameter needed to work most of the time,
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
            self._signer_url + "?{}".format(urlencode(query)),
            **self._requests_extra_kwargs,
        )
        parsed_data = data.json()

        return (
            parsed_data["verifyFp"],
            parsed_data["device_id"],
            parsed_data["_signature"],
            parsed_data["user_agent"],
            parsed_data["referrer"],
        )

    def _get_cookies(self, **kwargs):
        """Extracts cookies from the kwargs passed to the function for get_data"""
        device_id = kwargs.get(
            "custom_device_id",
            "".join(random.choice(string.digits) for num in range(19)),
        )
        if kwargs.get("custom_verify_fp") is None:
            if self._custom_verify_fp is not None:
                verifyFp = self._custom_verify_fp
            else:
                verifyFp = None
        else:
            verifyFp = kwargs.get("custom_verify_fp")

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
        processed = self._process_kwargs(kwargs)
        kwargs["custom_device_id"] = processed.device_id
        if self._signer_url is None:
            (
                verify_fp,
                device_id,
                signature,
                _,
            ) = asyncio.get_event_loop().run_until_complete(
                asyncio.gather(self._browser.sign_url(calc_tt_params=False, **kwargs))
            )[
                0
            ]
            user_agent = self._browser.user_agent
            referrer = self._browser.referrer
        else:
            (
                verify_fp,
                device_id,
                signature,
                user_agent,
                referrer,
            ) = self.external_signer(
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
            proxies=self._format_proxy(processed.proxy),
            cookies=self._get_cookies(**kwargs),
        )
        return r.content

    @staticmethod
    def generate_device_id():
        """Generates a valid device_id for other methods. Pass this as the custom_device_id field to download videos"""
        return "".join([random.choice(string.digits) for num in range(19)])

    #
    # PRIVATE METHODS
    #

    def _format_proxy(self, proxy) -> Optional[dict]:
        """
        Formats the proxy object
        """
        if proxy is None and self._proxy is not None:
            proxy = self._proxy
        if proxy is not None:
            return {"http": proxy, "https": proxy}
        else:
            return None

    # Process the kwargs
    def _process_kwargs(self, kwargs):
        region = kwargs.get("region", "US")
        language = kwargs.get("language", "en")
        proxy = kwargs.get("proxy", None)

        if kwargs.get("custom_device_id", None) != None:
            device_id = kwargs.get("custom_device_id")
        else:
            if self._custom_device_id != None:
                device_id = self._custom_device_id
            else:
                device_id = "".join(random.choice(string.digits) for num in range(19))

        @dataclass
        class ProcessedKwargs:
            region: str
            language: str
            proxy: str
            device_id: str

        return ProcessedKwargs(
            region=region, language=language, proxy=proxy, device_id=device_id
        )

    def _add_url_params(self) -> str:
        try:
            region = self._region
            browser_language = self._browser_language.lower()
            timezone = self._timezone_name
            language = self._language
        except AttributeError as e:
            self.logger.debug("Attribute Error on add_url_params", exc_info=e)
            region = "US"
            browser_language = "en-us"
            timezone = "America/Chicago"
            language = "en"
        query = {
            "aid": 1988,
            "app_name": "tiktok_web",
            "device_platform": "web_mobile",
            "region": region,
            "priority_region": "",
            "os": "ios",
            "referer": "",
            "cookie_enabled": "true",
            "screen_width": self._width,
            "screen_height": self._height,
            "browser_language": browser_language,
            "browser_platform": "iPhone",
            "browser_name": "Mozilla",
            "browser_version": self._user_agent,
            "browser_online": "true",
            "timezone_name": timezone,
            "is_page_visible": "true",
            "focus_state": "true",
            "is_fullscreen": "false",
            "history_len": random.randint(1, 5),
            "language": language,
        }

        return urlencode(query)

    def shutdown(self) -> None:
        with _thread_lock:
            self.logger.debug("Shutting down Playwright")
            asyncio.get_event_loop().run_until_complete(self._browser._clean_up())

    def __enter__(self):
        with _thread_lock:
            self._is_context_manager = True
            return self

    def __exit__(self, type, value, traceback):
        self.shutdown()
