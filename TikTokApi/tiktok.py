import json
import logging
import os
import random
import string
import time
from urllib.parse import quote, urlencode

import requests
from TikTokApi.api import search
from playwright.sync_api import sync_playwright

from .exceptions import *
from .utilities import update_messager

from .api import user

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


        logging.basicConfig(level=kwargs.get("logging_level", logging.WARNING))
        logging.info("Class initalized")

        # Some Instance Vars
        self.executablePath = kwargs.get("executablePath", None)

        if kwargs.get("custom_did") != None:
            raise Exception("Please use custom_device_id instead of custom_device_id")
        self.custom_device_id = kwargs.get("custom_device_id", None)
        self.userAgent = (
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
            self.userAgent = self.browser.userAgent

        try:
            self.timezone_name = self.__format_new_params__(self.browser.timezone_name)
            self.browser_language = self.__format_new_params__(
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
            userAgent = self.browser.userAgent
            referrer = self.browser.referrer
        else:
            verify_fp, device_id, signature, userAgent, referrer = self.external_signer(
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
            "user-agent": userAgent,
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
            parsed_data["userAgent"],
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
            userAgent = self.browser.userAgent
            referrer = self.browser.referrer
        else:
            verify_fp, device_id, signature, userAgent, referrer = self.external_signer(
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
                "User-Agent": userAgent,
            },
            proxies=self._format_proxy(proxy),
            cookies=self.get_cookies(**kwargs),
        )
        return r.content

    def by_trending(self, count=30, **kwargs) -> dict:
        """
        Gets trending TikToks

        ##### Parameters
        * count: The amount of TikToks you want returned, optional

            Note: TikTok seems to only support at MOST ~2000 TikToks
            from a single endpoint.
        """
        (
            region,
            language,
            proxy,
            maxCount,
            device_id,
        ) = self._process_kwargs(kwargs)
        kwargs["custom_device_id"] = device_id

        spawn = requests.head(
            "https://www.tiktok.com",
            proxies=self._format_proxy(proxy),
            **self.requests_extra_kwargs,
        )
        ttwid = spawn.cookies["ttwid"]

        response = []
        first = True

        while len(response) < count:
            if count < maxCount:
                realCount = count
            else:
                realCount = maxCount

            query = {
                "count": realCount,
                "id": 1,
                "sourceType": 12,
                "itemID": 1,
                "insertedItemID": "",
                "region": region,
                "priority_region": region,
                "language": language,
            }
            api_url = "{}api/recommend/item_list/?{}&{}".format(
                BASE_URL, self.__add_url_params__(), urlencode(query)
            )
            res = self.get_data(url=api_url, ttwid=ttwid, **kwargs)
            for t in res.get("itemList", []):
                response.append(t)

            if not res.get("hasMore", False) and not first:
                logging.info("TikTok isn't sending more TikToks beyond this point.")
                return response[:count]

            realCount = count - len(response)

            first = False

        return response[:count]

    def by_username(self, username, count=30, **kwargs) -> dict:
        """Returns a dictionary listing TikToks given a user's username.

        ##### Parameters
        * username: The username of the TikTok user to get TikToks from

        * count: The number of posts to return

            Note: seems to only support up to ~2,000
        """
        (
            region,
            language,
            proxy,
            maxCount,
            device_id,
        ) = self._process_kwargs(kwargs)
        kwargs["custom_device_id"] = device_id
        data = self.get_user_object(username, **kwargs)
        return self.user_posts(
            data["id"],
            data["secUid"],
            count=count,
            **kwargs,
        )

    def user_liked(self, userID, secUID, count=30, cursor=0, **kwargs) -> dict:
        """Returns a dictionary listing TikToks that a given a user has liked.
            Note: The user's likes must be public

        ##### Parameters
        * userID: The userID of the user, which TikTok assigns

        * secUID: The secUID of the user, which TikTok assigns

        * count: The number of posts to return

            Note: seems to only support up to ~2,000
        * cursor: The offset of a page

            The offset to return new videos from
        """
        (
            region,
            language,
            proxy,
            maxCount,
            device_id,
        ) = self._process_kwargs(kwargs)
        kwargs["custom_device_id"] = device_id
        response = []
        first = True

        while len(response) < count:
            if count < maxCount:
                realCount = count
            else:
                realCount = maxCount

            query = {
                "count": realCount,
                "id": userID,
                "type": 2,
                "secUid": secUID,
                "cursor": cursor,
                "sourceType": 9,
                "appId": 1233,
                "region": region,
                "priority_region": region,
                "language": language,
            }
            api_url = "{}api/favorite/item_list/?{}&{}".format(
                BASE_URL, self.__add_url_params__(), urlencode(query)
            )

            res = self.get_data(url=api_url, **kwargs)

            try:
                res["itemList"]
            except Exception:
                logging.error("User's likes are most likely private")
                return []

            for t in res.get("itemList", []):
                response.append(t)

            if not res.get("hasMore", False) and not first:
                logging.info("TikTok isn't sending more TikToks beyond this point.")
                return response

            realCount = count - len(response)
            cursor = res["cursor"]

            first = False

        return response[:count]

    def user_liked_by_username(self, username, count=30, **kwargs) -> dict:
        """Returns a dictionary listing TikToks a user has liked by username.
            Note: The user's likes must be public

        ##### Parameters
        * username: The username of the user

        * count: The number of posts to return

            Note: seems to only support up to ~2,000
        """
        (
            region,
            language,
            proxy,
            maxCount,
            device_id,
        ) = self._process_kwargs(kwargs)
        kwargs["custom_device_id"] = device_id
        data = self.get_user_object(username, **kwargs)
        return self.user_liked(
            data["id"],
            data["secUid"],
            count=count,
            **kwargs,
        )

    def by_sound(self, id, count=30, offset=0, **kwargs) -> dict:
        """Returns a dictionary listing TikToks with a specific sound.

        ##### Parameters
        * id: The sound id to search by

            Note: Can be found in the URL of the sound specific page or with other methods.
        * count: The number of posts to return

            Note: seems to only support up to ~2,000
        """
        (
            region,
            language,
            proxy,
            maxCount,
            device_id,
        ) = self._process_kwargs(kwargs)
        kwargs["custom_device_id"] = device_id
        response = []

        while len(response) < count:
            if count < maxCount:
                realCount = count
            else:
                realCount = maxCount

            query = {
                "secUid": "",
                "musicID": str(id),
                "count": str(realCount),
                "cursor": offset,
                "shareUid": "",
                "language": language,
            }
            api_url = "{}api/music/item_list/?{}&{}".format(
                BASE_URL, self.__add_url_params__(), urlencode(query)
            )

            res = self.get_data(url=api_url, send_tt_params=True, **kwargs)

            try:
                for t in res["items"]:
                    response.append(t)
            except KeyError:
                for t in res.get("itemList", []):
                    response.append(t)

            if not res.get("hasMore", False):
                logging.info("TikTok isn't sending more TikToks beyond this point.")
                return response

            realCount = count - len(response)
            offset = res["cursor"]

        return response[:count]

    def by_sound_page(self, id, page_size=30, cursor=0, **kwargs) -> dict:
        """Returns a page of tiktoks with a specific sound.

        Parameters
        ----------
        id: The sound id to search by
            Note: Can be found in the URL of the sound specific page or with other methods.
        cursor: offset for pagination
        page_size: The number of posts to return
        """
        (
            region,
            language,
            proxy,
            maxCount,
            device_id,
        ) = self._process_kwargs(kwargs)
        kwargs["custom_device_id"] = device_id

        query = {
            "musicID": str(id),
            "count": str(page_size),
            "cursor": cursor,
            "language": language,
        }
        api_url = "{}api/music/item_list/?{}&{}".format(
            BASE_URL, self.__add_url_params__(), urlencode(query)
        )

        return self.get_data(url=api_url, send_tt_params=True, **kwargs)

    def get_music_object(self, id, **kwargs) -> dict:
        """Returns a music object for a specific sound id.

        ##### Parameters
        * id: The sound id to get the object for

            This can be found by using other methods.
        """
        return self.get_music_object_full(id, **kwargs)["music"]

    def get_music_object_full(self, id, **kwargs):
        """Returns a music object for a specific sound id.

        ##### Parameters
        * id: The sound id to get the object for

            This can be found by using other methods.
        """
        (
            region,
            language,
            proxy,
            maxCount,
            device_id,
        ) = self._process_kwargs(kwargs)
        r = requests.get(
            "https://www.tiktok.com/music/-{}".format(id),
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "User-Agent": self.userAgent,
            },
            proxies=self._format_proxy(kwargs.get("proxy", None)),
            cookies=self.get_cookies(**kwargs),
            **self.requests_extra_kwargs,
        )

        j_raw = self.__extract_tag_contents(r.text)
        return json.loads(j_raw)["props"]["pageProps"]["musicInfo"]

    def get_music_object_full_by_api(self, id, **kwargs):
        """Returns a music object for a specific sound id, but using the API rather than HTML requests.

        ##### Parameters
        * id: The sound id to get the object for

            This can be found by using other methods.
        """
        (
            region,
            language,
            proxy,
            maxCount,
            device_id,
        ) = self._process_kwargs(kwargs)
        kwargs["custom_device_id"] = device_id

        api_url = "{}node/share/music/-{}?{}".format(
            BASE_URL, id, self.__add_url_params__()
        )
        res = self.get_data(url=api_url, **kwargs)

        if res.get("statusCode", 200) == 10203:
            raise TikTokNotFoundError()

        return res["musicInfo"]

    def by_hashtag(self, hashtag, count=30, offset=0, **kwargs) -> dict:
        """Returns a dictionary listing TikToks with a specific hashtag.

        ##### Parameters
        * hashtag: The hashtag to search by

            Without the # symbol

            A valid string is "funny"
        * count: The number of posts to return
            Note: seems to only support up to ~2,000
        """
        (
            region,
            language,
            proxy,
            maxCount,
            device_id,
        ) = self._process_kwargs(kwargs)
        kwargs["custom_device_id"] = device_id
        id = self.get_hashtag_object(hashtag)["challengeInfo"]["challenge"]["id"]
        response = []

        required_count = count

        while len(response) < required_count:
            if count > maxCount:
                count = maxCount
            query = {
                "count": count,
                "challengeID": id,
                "type": 3,
                "secUid": "",
                "cursor": offset,
                "priority_region": "",
            }
            api_url = "{}api/challenge/item_list/?{}&{}".format(
                BASE_URL, self.__add_url_params__(), urlencode(query)
            )
            res = self.get_data(url=api_url, **kwargs)

            for t in res.get("itemList", []):
                response.append(t)

            if not res.get("hasMore", False):
                logging.info("TikTok isn't sending more TikToks beyond this point.")
                return response

            offset += maxCount

        return response[:required_count]

    def get_hashtag_object(self, hashtag, **kwargs) -> dict:
        """Returns a hashtag object.

        ##### Parameters
        * hashtag: The hashtag to search by

            Without the # symbol
        """
        (
            region,
            language,
            proxy,
            maxCount,
            device_id,
        ) = self._process_kwargs(kwargs)
        kwargs["custom_device_id"] = device_id
        query = {"name": hashtag, "isName": True, "lang": language}
        api_url = "{}node/share/tag/{}?{}&{}".format(
            BASE_URL, quote(hashtag), self.__add_url_params__(), urlencode(query)
        )
        data = self.get_data(url=api_url, **kwargs)
        if data["challengeInfo"].get("challenge") is None:
            raise TikTokNotFoundError("Challenge {} does not exist".format(hashtag))
        return data

    def get_recommended_tiktoks_by_video_id(self, id, count=30, **kwargs) -> dict:
        """Returns a dictionary listing reccomended TikToks for a specific TikTok video.


        ##### Parameters
        * id: The id of the video to get suggestions for

            Can be found using other methods
        * count: The count of results you want to return
        """
        (
            region,
            language,
            proxy,
            maxCount,
            device_id,
        ) = self._process_kwargs(kwargs)
        kwargs["custom_device_id"] = device_id

        response = []
        first = True

        while len(response) < count:
            if count < maxCount:
                realCount = count
            else:
                realCount = maxCount

            query = {
                "count": realCount,
                "id": 1,
                "secUid": "",
                "sourceType": 12,
                "appId": 1233,
                "region": region,
                "priority_region": region,
                "language": language,
            }
            api_url = "{}api/recommend/item_list/?{}&{}".format(
                BASE_URL, self.__add_url_params__(), urlencode(query)
            )

            res = self.get_data(url=api_url, **kwargs)

            for t in res.get("itemList", []):
                response.append(t)

            if not res.get("hasMore", False) and not first:
                logging.info("TikTok isn't sending more TikToks beyond this point.")
                return response[:count]

            realCount = count - len(response)

            first = False

        return response[:count]

    def get_tiktok_by_id(self, id, **kwargs) -> dict:
        """Returns a dictionary of a specific TikTok.

        ##### Parameters
        * id: The id of the TikTok you want to get the object for
        """
        (
            region,
            language,
            proxy,
            maxCount,
            device_id,
        ) = self._process_kwargs(kwargs)
        kwargs["custom_device_id"] = device_id
        device_id = kwargs.get("custom_device_id", None)
        query = {
            "itemId": id,
            "language": language,
        }
        api_url = "{}api/item/detail/?{}&{}".format(
            BASE_URL, self.__add_url_params__(), urlencode(query)
        )

        return self.get_data(url=api_url, **kwargs)

    def get_tiktok_by_url(self, url, **kwargs) -> dict:
        """Returns a dictionary of a TikTok object by url.


        ##### Parameters
        * url: The TikTok url you want to retrieve

        """

        url = requests.head(url=url, allow_redirects=True).url

        (
            region,
            language,
            proxy,
            maxCount,
            device_id,
        ) = self._process_kwargs(kwargs)
        kwargs["custom_device_id"] = device_id
        custom_device_id = kwargs.get("custom_device_id", None)
        if "@" in url and "/video/" in url:
            post_id = url.split("/video/")[1].split("?")[0]
        else:
            raise Exception(
                "URL format not supported. Below is an example of a supported url.\n"
                "https://www.tiktok.com/@therock/video/6829267836783971589"
            )

        return self.get_tiktok_by_id(
            post_id,
            **kwargs,
        )

    def get_tiktok_by_html(self, url, **kwargs) -> dict:
        """This method retrieves a TikTok using the html
        endpoints rather than the API based ones.

        ##### Parameters
        * url: The url of the TikTok to get
        """
        (
            region,
            language,
            proxy,
            maxCount,
            device_id,
        ) = self._process_kwargs(kwargs)

        r = requests.get(
            url,
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "path": url.split("tiktok.com")[1],
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
            },
            proxies=self._format_proxy(kwargs.get("proxy", None)),
            cookies=self.get_cookies(**kwargs),
            **self.requests_extra_kwargs,
        )

        t = r.text
        try:
            j_raw = self.__extract_tag_contents(r.text)
        except IndexError:
            if not t:
                logging.error("TikTok response is empty")
            else:
                logging.error("TikTok response: \n " + t)
            raise TikTokCaptchaError()

        data = json.loads(j_raw)["props"]["pageProps"]

        if data["serverCode"] == 404:
            raise TikTokNotFoundError("TikTok with that url doesn't exist")

        return data

    def get_user_object(self, username, **kwargs) -> dict:
        """Gets a user object (dictionary)

        ##### Parameters
        * username: The username of the user
        """
        (
            region,
            language,
            proxy,
            maxCount,
            device_id,
        ) = self._process_kwargs(kwargs)
        kwargs["custom_device_id"] = device_id
        return self.get_user(username, **kwargs)["userInfo"]["user"]

    

    def get_video_by_tiktok(self, data, **kwargs) -> bytes:
        """Downloads video from TikTok using a TikTok object.

        You will need to set a custom_device_id to do this for anything but trending.
        To do this, this is pretty simple you can either generate one yourself or,
        you can pass the generate_static_device_id=True into the constructor of the
        TikTokApi class.

        ##### Parameters
        * data: A TikTok object

            A TikTok JSON object from any other method.
        """
        (
            region,
            language,
            proxy,
            maxCount,
            device_id,
        ) = self._process_kwargs(kwargs)
        kwargs["custom_device_id"] = device_id
        try:
            api_url = data["video"]["downloadAddr"]
        except Exception:
            try:
                api_url = data["itemInfos"]["video"]["urls"][0]
            except Exception:
                api_url = data["itemInfo"]["itemStruct"]["video"]["playAddr"]
        return self.get_video_by_download_url(api_url, **kwargs)

    def get_video_by_download_url(self, download_url, **kwargs) -> bytes:
        """Downloads video from TikTok using download url in a TikTok object

        ##### Parameters
        * download_url: The download url key value in a TikTok object
        """
        (
            region,
            language,
            proxy,
            maxCount,
            device_id,
        ) = self._process_kwargs(kwargs)
        kwargs["custom_device_id"] = device_id
        return self.get_bytes(url=download_url, **kwargs)

    def get_video_by_url(self, video_url, **kwargs) -> bytes:
        """Downloads a TikTok video by a URL

        ##### Parameters
        * video_url: The TikTok url to download the video from
        """
        (
            region,
            language,
            proxy,
            maxCount,
            device_id,
        ) = self._process_kwargs(kwargs)
        kwargs["custom_device_id"] = device_id

        tiktok_schema = self.get_tiktok_by_url(video_url, **kwargs)
        download_url = tiktok_schema["itemInfo"]["itemStruct"]["video"]["downloadAddr"]

        return self.get_bytes(url=download_url, **kwargs)

    def get_video_no_watermark(self, video_url, return_bytes=1, **kwargs) -> bytes:
        """Gets the video with no watermark
        .. deprecated::

        Deprecated due to TikTok fixing this

        ##### Parameters
        * video_url: The url of the video you want to download

        * return_bytes: Set this to 0 if you want url, 1 if you want bytes
        """
        (
            region,
            language,
            proxy,
            maxCount,
            device_id,
        ) = self._process_kwargs(kwargs)
        raise Exception("Deprecated method, TikTok fixed this.")

    def get_music_title(self, id, **kwargs):
        """Retrieves a music title given an ID

        ##### Parameters
        * id: The music id to get the title for
        """
        r = requests.get(
            "https://www.tiktok.com/music/-{}".format(id),
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
            },
            proxies=self._format_proxy(kwargs.get("proxy", None)),
            cookies=self.get_cookies(**kwargs),
            **self.requests_extra_kwargs,
        )
        t = r.text
        j_raw = self.__extract_tag_contents(r.text)

        music_object = json.loads(j_raw)["props"]["pageProps"]["musicInfo"]
        if not music_object.get("title", None):
            raise TikTokNotFoundError("Song of {} id does not exist".format(str(id)))

        return music_object["title"]

    def get_secuid(self, username, **kwargs):
        """Gets the secUid for a specific username

        ##### Parameters
        * username: The username to get the secUid for
        """
        r = requests.get(
            "https://tiktok.com/@{}?lang=en".format(quote(username)),
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "path": "/@{}".format(quote(username)),
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
            },
            proxies=self._format_proxy(
                kwargs.get("proxy", None), cookies=self.get_cookies(**kwargs)
            ),
            **self.requests_extra_kwargs,
        )
        try:
            return r.text.split('"secUid":"')[1].split('","secret":')[0]
        except IndexError as e:
            logging.info(r.text)
            logging.error(e)
            raise Exception(
                "Retrieving the user secUid failed. Likely due to TikTok wanting captcha validation. Try to use a proxy."
            )

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

    def __format_new_params__(self, parm) -> str:
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
            "browser_version": self.__format_new_params__(self.userAgent),
            "browser_online": "true",
            "timezone_name": self.timezone_name or "America/Chicago",
            "is_page_visible": "true",
            "focus_state": "true",
            "is_fullscreen": "false",
            "history_len": random.randint(0, 30),
            "language": self.language or "en",
        }
        return urlencode(query)
