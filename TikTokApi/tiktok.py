import random
import requests
import time
import logging
from urllib.parse import urlencode, quote
from .browser import browser, get_playwright
from playwright import sync_playwright
import logging
import os
from .utilities import update_messager
os.environ['no_proxy'] = '127.0.0.1,localhost'

BASE_URL = "https://m.tiktok.com/"

class TikTokApi:
    __instance = None
    def __init__(self, **kwargs):
        """The TikTokApi class. Used to interact with TikTok.

        :param logging_level: The logging level you want the program to run at
        :param request_delay: The amount of time to wait before making a request.
        :param executablePath: The location of the chromedriver.exe
        """
        # Forces Singleton
        if TikTokApi.__instance is None:
            TikTokApi.__instance = self
        else:
            raise Exception("Only one TikTokApi object is allowed")
        logging.basicConfig(level=kwargs.get("logging_level", logging.CRITICAL))
        logging.info("Class initalized")
        self.executablePath = kwargs.get("executablePath", None)

        self.userAgent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/86.0.4240.111 Safari/537.36"
        )
        self.proxy = kwargs.get("proxy", None)

        self.signer_url = kwargs.get("external_signer", None)
        if self.signer_url == None:
            self.browser = browser(**kwargs)
            self.userAgent = self.browser.userAgent
        

        try:
            self.timezone_name = self.__format_new_params__(self.browser.timezone_name)
            self.browser_language = self.__format_new_params__(
                self.browser.browser_language
            )
            self.browser_platform = self.__format_new_params__(
                self.browser.browser_platform
            )
            self.browser_name = self.__format_new_params__(self.browser.browser_name)
            self.browser_version = self.__format_new_params__(
                self.browser.browser_version
            )
            self.width = self.browser.width
            self.height = self.browser.height
        except Exception as e:
            logging.warning("An error occured but it was ignored.")

            self.timezone_name = ""
            self.browser_language = ""
            self.browser_platform = ""
            self.browser_name = ""
            self.browser_version = ""
            self.width = "1920"
            self.height = "1080"

        self.request_delay = kwargs.get("request_delay", None)

    @staticmethod
    def get_instance(**kwargs):
        if not TikTokApi.__instance:
            TikTokApi(**kwargs)
        return TikTokApi.__instance

    def clean_up(self):
        self.__del__()

    def __del__(self):
        try:
            self.browser.clean_up()
        except:
            pass
        try:
            get_playwright().stop()
        except:
            pass
        TikTokApi.__instance = None

    def external_signer(self, url, custom_did=None):
        if custom_did != None:
            query = {
                    "url": url,
                    "custom_did": custom_did
            }
        else:
            query = {
                    "url": url,
            }
        data = requests.get(self.signer_url + "?{}".format(urlencode(query)))
        parsed_data = data.json()

        return parsed_data['verifyFp'], parsed_data['did'], parsed_data['_signature'], parsed_data['userAgent'], parsed_data['referrer']

    def getData(self, **kwargs) -> dict:
        """Returns a dictionary of a response from TikTok.

        :param api_url: the base string without a signature

        :param b: The browser object that contains the signature

        :param language: The two digit language code to make requests to TikTok with.
                         Note: This doesn't seem to actually change things from the API.

        :param proxy: The IP address of a proxy server to request from.
        """
        (
            region,
            language,
            proxy,
            maxCount,
            did,
        ) = self.__process_kwargs__(kwargs)
        kwargs['custom_did'] = did
        if self.request_delay is not None:
            time.sleep(self.request_delay)

        if self.proxy != None:
            proxy = self.proxy

        if self.signer_url == None:
            verify_fp, did, signature = self.browser.sign_url(**kwargs)
            userAgent = self.browser.userAgent
            referrer = self.browser.referrer
        else:
            verify_fp, did, signature, userAgent, referrer = self.external_signer(kwargs['url'], custom_did=kwargs.get('custom_did', None))
        query = {"verifyFp": verify_fp, "did": did, "_signature": signature}
        url = "{}&{}".format(kwargs["url"], urlencode(query))
        r = requests.get(
            url,
            headers={
                "authority": "m.tiktok.com",
                "method": "GET",
                "path": url.split("tiktok.com")[1],
                "scheme": "https",
                "accept": "application/json, text/plain, */*",
                "accept-encoding": "gzip, deflate, br",
                "accept-language": "en-US,en;q=0.9",
                "referer": referrer,
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site",
                "user-agent": userAgent,
                "cookie": "tt_webid_v2=" + did,
            },
            proxies=self.__format_proxy(proxy),
        )
        try:
            return r.json()
        except Exception as e:
            logging.error(e)
            logging.error(
                "Converting response to JSON failed response is below (probably empty)"
            )
            logging.info(r.text)
            raise Exception("Invalid Response")

    def getBytes(self, **kwargs) -> bytes:
        """Returns bytes of a response from TikTok.

        :param api_url: the base string without a signature

        :param b: The browser object that contains the signature

        :param language: The two digit language code to make requests to TikTok with.
                         Note: This doesn't seem to actually change things from the API.

        :param proxy: The IP address of a proxy server to request from.
        """
        (
            region,
            language,
            proxy,
            maxCount,
            did,
        ) = self.__process_kwargs__(kwargs)
        kwargs['custom_did'] = did
        if self.signer_url == None:
            verify_fp, did, signature = self.browser.sign_url(**kwargs)
            userAgent = self.browser.userAgent
            referrer = self.browser.referrer
        else:
            verify_fp, did, signature, userAgent, referrer = self.external_signer(kwargs['url'], custom_did=kwargs.get('custom_did', None))
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
                "cookie": "tt_webid_v2=" + did,
                "Host": url.split("/")[2],
                "Pragma": "no-cache",
                "Range": "bytes=0-",
                "Referer": "https://www.tiktok.com/",
                "User-Agent": userAgent,
            },
            proxies=self.__format_proxy(proxy),
        )
        return r.content

    def trending(self, count=30, minCursor=0, maxCursor=0, **kwargs) -> dict:
        """
        Gets trending TikToks
        """
        (
            region,
            language,
            proxy,
            maxCount,
            did,
        ) = self.__process_kwargs__(kwargs)
        kwargs['custom_did'] = did

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
                "maxCursor": maxCursor,
                "minCursor": minCursor,
                "sourceType": 12,
                "appId": 1233,
                "region": region,
                "priority_region": region,
                "language": language,
            }
            api_url = "{}api/item_list/?{}&{}".format(
                BASE_URL, self.__add_new_params__(), urlencode(query)
            )
            res = self.getData(url=api_url, **kwargs)

            for t in res.get("items", []):
                response.append(t)

            if not res["hasMore"] and not first:
                logging.info("TikTok isn't sending more TikToks beyond this point.")
                return response[:count]

            realCount = count - len(response)
            maxCursor = res["maxCursor"]
            minCursor = res['minCursor']

            first = False

        return response[:count]

    def search_for_users(self, search_term, count=28, **kwargs) -> list:
        """Returns a list of users that match the search_term

        :param search_term: The string to search by.
        :param count: The number of posts to return.
        :param proxy: The IP address of a proxy to make requests from.
        """
        return self.discover_type(search_term, prefix="user", count=count, **kwargs)

    def search_for_music(self, search_term, count=28, **kwargs) -> list:
        """Returns a list of music that match the search_term

        :param search_term: The string to search by.
        :param count: The number of posts to return.
        :param proxy: The IP address of a proxy to make requests from.
        """
        return self.discover_type(search_term, prefix="music", count=count, **kwargs)

    def search_for_hashtags(self, search_term, count=28, **kwargs) -> list:
        """Returns a list of hashtags that match the search_term

        :param search_term: The string to search by.
        :param count: The number of posts to return.
        :param proxy: The IP address of a proxy to make requests from.
        """
        return self.discover_type(
            search_term, prefix="challenge", count=count, **kwargs
        )

    def discover_type(self, search_term, prefix, count=28, **kwargs) -> list:
        """Returns a list of whatever the prefix type you pass in

        :param search_term: The string to search by.
        :param prefix: The type of post to search by user/music/challenge.
        :param count: The number of posts to return.
        :param proxy: The IP address of a proxy to make requests from.
        """
        (
            region,
            language,
            proxy,
            maxCount,
            did,
        ) = self.__process_kwargs__(kwargs)
        kwargs['custom_did'] = did

        response = []
        offsetCount = 0
        while len(response) < count:
            query = {
                "discoverType": count,
                "needItemList": False,
                "keyWord": search_term,
                "offset": offsetCount,
                "count": 99,
                "useRecommend": False,
                "language": "en",
            }
            api_url = "{}api/discover/{}/?{}&{}".format(
                BASE_URL, prefix, self.__add_new_params__(), urlencode(query)
            )
            data = self.getData(url=api_url, **kwargs)

            if "userInfoList" in data.keys():
                for x in data["userInfoList"]:
                    response.append(x)
            elif "musicInfoList" in data.keys():
                for x in data["musicInfoList"]:
                    response.append(x)
            elif "challengeInfoList" in data.keys():
                for x in data["challengeInfoList"]:
                    response.append(x)
            else:
                logging.info("TikTok is not sending videos beyond this point.")
                break

            offsetCount = len(response)

        return response[:count]

    def userPosts(
        self, userID, secUID, count=30, minCursor=0, maxCursor=0, **kwargs
    ) -> dict:
        """Returns a dictionary listing TikToks given a user's ID and secUID

        :param userID: The userID of the user, which TikTok assigns.
        :param secUID: The secUID of the user, which TikTok assigns.
        :param count: The number of posts to return.
                      Note: seems to only support up to ~2,000
        :param language: The 2 letter code of the language to return.
                         Note: Doesn't seem to have an affect.
        :param region: The 2 letter region code.
                       Note: Doesn't seem to have an affect.
        :param proxy: The IP address of a proxy to make requests from.
        """
        (
            region,
            language,
            proxy,
            maxCount,
            did,
        ) = self.__process_kwargs__(kwargs)
        kwargs['custom_did'] = did

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
                "type": 1,
                "secUid": secUID,
                "maxCursor": maxCursor,
                "minCursor": minCursor,
                "sourceType": 8,
                "appId": 1233,
                "region": region,
                "priority_region": region,
                "language": language,
            }
            api_url = "{}api/item_list/?{}&{}".format(
                BASE_URL, self.__add_new_params__(), urlencode(query)
            )

            res = self.getData(url=api_url, **kwargs)
            if "items" in res.keys():
                for t in res["items"]:
                    response.append(t)

            if not res["hasMore"] and not first:
                logging.info("TikTok isn't sending more TikToks beyond this point.")
                return response

            realCount = count - len(response)
            maxCursor = res["maxCursor"]

            first = False

        return response[:count]

    def byUsername(self, username, count=30, **kwargs) -> dict:
        """Returns a dictionary listing TikToks given a user's username.

        :param username: The username of the user.
        :param count: The number of posts to return.
                      Note: seems to only support up to ~2,000
        :param language: The 2 letter code of the language to return.
                         Note: Doesn't seem to have an affect.
        :param region: The 2 letter region code.
                       Note: Doesn't seem to have an affect.
        :param proxy: The IP address of a proxy to make requests from.
        """
        (
            region,
            language,
            proxy,
            maxCount,
            did,
        ) = self.__process_kwargs__(kwargs)
        kwargs['custom_did'] = did
        data = self.getUserObject(username, **kwargs)
        return self.userPosts(
            data["id"],
            data["secUid"],
            count=count,
            **kwargs,
        )

    def userPage(
        self, userID, secUID, page_size=30, minCursor=0, maxCursor=0, **kwargs
    ) -> dict:
        """Returns a dictionary listing of one page of TikToks given a user's ID and secUID

        :param userID: The userID of the user, which TikTok assigns.
        :param secUID: The secUID of the user, which TikTok assigns.
        :param page_size: The number of posts to return per page.
        :param minCursor: time stamp for the earliest TikTok to retrieve
        :param maxCursor: time stamp for the latest TikTok to retrieve
        :param language: The 2 letter code of the language to return.
                         Note: Doesn't seem to have an affect.
        :param region: The 2 letter region code.
                       Note: Doesn't seem to have an affect.
        :param proxy: The IP address of a proxy to make requests from.
        """
        (
            region,
            language,
            proxy,
            maxCount,
            did,
        ) = self.__process_kwargs__(kwargs)
        kwargs['custom_did'] = did

        api_url = "https://m.tiktok.com/api/item_list/?{}&count={}&id={}&type=1&secUid={}" "&minCursor={}&maxCursor={}&sourceType=8&appId=1233&region={}&language={}".format(
            self.__add_new_params__(),
            page_size,
            str(userID),
            str(secUID),
            minCursor,
            maxCursor,
            region,
            language,
        )

        return self.getData(url=api_url, **kwargs)

    def getUserPager(self, username, page_size=30, minCursor=0, maxCursor=0, **kwargs):
        """Returns a generator to page through a user's feed

        :param username: The username of the user.
        :param page_size: The number of posts to return in a page.
        :param minCursor: time stamp for the earliest TikTok to retrieve
        :param maxCursor: time stamp for the latest TikTok to retrieve
        :param language: The 2 letter code of the language to return.
                         Note: Doesn't seem to have an affect.
        :param region: The 2 letter region code.
                       Note: Doesn't seem to have an affect.
        :param proxy: The IP address of a proxy to make requests from.
        """
        (
            region,
            language,
            proxy,
            maxCount,
            did,
        ) = self.__process_kwargs__(kwargs)
        kwargs['custom_did'] = did
        data = self.getUserObject(username, **kwargs)

        while True:
            resp = self.userPage(
                data["id"],
                data["secUid"],
                page_size=page_size,
                maxCursor=maxCursor,
                minCursor=minCursor,
                **kwargs,
            )

            try:
                page = resp["items"]
            except KeyError:
                # No mo results
                return

            maxCursor = resp["maxCursor"]

            yield page

            if not resp["hasMore"]:
                return  # all done

    def userLiked(
        self, userID, secUID, count=30, minCursor=0, maxCursor=0, **kwargs
    ) -> dict:
        """Returns a dictionary listing TikToks that a given a user has liked.
           Note: The user's likes must be public

        :param userID: The userID of the user, which TikTok assigns.
        :param secUID: The secUID of the user, which TikTok assigns.
        :param count: The number of posts to return.
                      Note: seems to only support up to ~2,000
        :param language: The 2 letter code of the language to return.
                         Note: Doesn't seem to have an affect.
        :param region: The 2 letter region code.
                       Note: Doesn't seem to have an affect.
        :param proxy: The IP address of a proxy to make requests from.
        """
        (
            region,
            language,
            proxy,
            maxCount,
            did,
        ) = self.__process_kwargs__(kwargs)
        kwargs['custom_did'] = did
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
                "maxCursor": maxCursor,
                "minCursor": minCursor,
                "sourceType": 9,
                "appId": 1233,
                "region": region,
                "priority_region": region,
                "language": language,
            }
            api_url = "{}api/item_list/?{}&{}".format(
                BASE_URL, self.__add_new_params__(), urlencode(query)
            )

            res = self.getData(url=api_url, **kwargs)

            try:
                res["items"]
            except Exception:
                logging.error("User's likes are most likely private")
                return []

            if "items" in res.keys():
                for t in res["items"]:
                    response.append(t)

            if not res["hasMore"] and not first:
                logging.info("TikTok isn't sending more TikToks beyond this point.")
                return response

            realCount = count - len(response)
            maxCursor = res["maxCursor"]

            first = False

        return response[:count]

    def userLikedbyUsername(self, username, count=30, **kwargs) -> dict:
        """Returns a dictionary listing TikToks a user has liked by username.
           Note: The user's likes must be public

        :param username: The username of the user.
        :param count: The number of posts to return.
                      Note: seems to only support up to ~2,000
        :param language: The 2 letter code of the language to return.
                         Note: Doesn't seem to have an affect.
        :param region: The 2 letter region code.
                       Note: Doesn't seem to have an affect.
        :param proxy: The IP address of a proxy to make requests from.
        """
        (
            region,
            language,
            proxy,
            maxCount,
            did,
        ) = self.__process_kwargs__(kwargs)
        kwargs['custom_did'] = did
        data = self.getUserObject(username, **kwargs)
        return self.userLiked(
            data["id"],
            data["secUid"],
            count=count,
            **kwargs,
        )

    def bySound(self, id, count=30, offset=0, **kwargs) -> dict:
        """Returns a dictionary listing TikToks with a specific sound.

        :param id: The sound id to search by.
                   Note: Can be found in the URL of the sound specific page or with other methods.
        :param count: The number of posts to return.
                      Note: seems to only support up to ~2,000
        :param language: The 2 letter code of the language to return.
                         Note: Doesn't seem to have an affect.
        :param region: The 2 letter region code.
                       Note: Doesn't seem to have an affect.
        :param proxy: The IP address of a proxy to make requests from.
        """
        (
            region,
            language,
            proxy,
            maxCount,
            did,
        ) = self.__process_kwargs__(kwargs)
        kwargs['custom_did'] = did
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
                "cursor": str(offset),
                "shareUid": "",
                "language": language,
            }
            api_url = "{}api/music/item_list/?{}&{}".format(
                BASE_URL, self.__add_new_params__(), urlencode(query)
            )

            res = self.getData(url=api_url, **kwargs)

            for t in res.get("itemList", []):
                response.append(t)

            if not res["hasMore"]:
                logging.info("TikTok isn't sending more TikToks beyond this point.")
                return response

            realCount = count - len(response)
            offset = res["cursor"]

        return response[:count]

    def getMusicObject(self, id, **kwargs) -> dict:
        """Returns a music object for a specific sound id.

        :param id: The sound id to search by.
        :param language: The 2 letter code of the language to return.
                         Note: Doesn't seem to have an affect.
        :param proxy: The IP address of a proxy to make requests from.
        """
        (
            region,
            language,
            proxy,
            maxCount,
            did,
        ) = self.__process_kwargs__(kwargs)
        kwargs['custom_did'] = did

        query = {"musicId": id, "language": language}
        api_url = "{}api/music/detail/?{}&{}".format(
            BASE_URL, self.__add_new_params__(), urlencode(query)
        )

        return self.getData(url=api_url, **kwargs)

    def byHashtag(self, hashtag, count=30, offset=0, **kwargs) -> dict:
        """Returns a dictionary listing TikToks with a specific hashtag.

        :param hashtag: The hashtag to search by.
        :param count: The number of posts to return.
                      Note: seems to only support up to ~2,000
        :param language: The 2 letter code of the language to return.
                         Note: Doesn't seem to have an affect.
        :param region: The 2 letter region code.
                       Note: Doesn't seem to have an affect.
        :param proxy: The IP address of a proxy to make requests from.
        """
        (
            region,
            language,
            proxy,
            maxCount,
            did,
        ) = self.__process_kwargs__(kwargs)
        kwargs['custom_did'] = did
        id = self.getHashtagObject(hashtag)["challengeInfo"]["challenge"]["id"]
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
                "sourceType": "8",
                "language": language,
            }
            api_url = "{}api/challenge/item_list/?{}&{}".format(
                BASE_URL, self.__add_new_params__(), urlencode(query)
            )
            res = self.getData(url=api_url, **kwargs)

            for t in res["itemList"]:
                response.append(t)

            if not res["hasMore"]:
                logging.info("TikTok isn't sending more TikToks beyond this point.")
                return response

            offset += maxCount

        return response[:required_count]

    def getHashtagObject(self, hashtag, **kwargs) -> dict:
        """Returns a hashtag object.

        :param hashtag: The hashtag to search by.
        :param language: The 2 letter code of the language to return.
                         Note: Doesn't seem to have an affect.
        :param proxy: The IP address of a proxy to make requests from.
        """
        (
            region,
            language,
            proxy,
            maxCount,
            did,
        ) = self.__process_kwargs__(kwargs)
        kwargs['custom_did'] = did
        query = {"challengeName": hashtag, "language": language}
        api_url = "{}api/challenge/detail/?{}&{}".format(
            BASE_URL, self.__add_new_params__(), urlencode(query)
        )
        return self.getData(url=api_url, **kwargs)

    def getHashtagDetails(self, hashtag, **kwargs) -> dict:
        """Returns a hashtag object.

        :param hashtag: The hashtag to search by.
        :param language: The 2 letter code of the language to return.
                         Note: Doesn't seem to have an affect.
        :param proxy: The IP address of a proxy to make requests from.
        """
        (
            region,
            language,
            proxy,
            maxCount,
            did,
        ) = self.__process_kwargs__(kwargs)
        kwargs['custom_did'] = did
        query = {"language": language}
        api_url = "{}node/share/tag/{}?{}&{}".format(
            BASE_URL, quote(hashtag), self.__add_new_params__(), urlencode(query)
        )

        return self.getData(url=api_url, **kwargs)

    def getRecommendedTikToksByVideoID(
        self, id, count=30, minCursor=0, maxCursor=0, **kwargs
    ) -> dict:
        """Returns a dictionary listing reccomended TikToks for a specific TikTok video.

        :param id: The id of the video to get suggestions for.
        :param language: The 2 letter code of the language to return.
                         Note: Doesn't seem to have an affect.
        :param proxy: The IP address of a proxy to make requests from.
        """
        (
            region,
            language,
            proxy,
            maxCount,
            did,
        ) = self.__process_kwargs__(kwargs)
        kwargs['custom_did'] = did

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
                "maxCursor": maxCursor,
                "minCursor": minCursor,
                "sourceType": 12,
                "appId": 1233,
                "region": region,
                "priority_region": region,
                "language": language,
            }
            api_url = "{}api/recommend/item_list/?{}&{}".format(
                BASE_URL, self.__add_new_params__(), urlencode(query)
            )

            res = self.getData(url=api_url, **kwargs)

            for t in res.get("items", []):
                response.append(t)

            if not res["hasMore"] and not first:
                logging.info("TikTok isn't sending more TikToks beyond this point.")
                return response[:count]

            realCount = count - len(response)
            maxCursor = res["maxCursor"]

            first = False

        return response[:count]

    def getTikTokById(self, id, **kwargs) -> dict:
        """Returns a dictionary of a specific TikTok.

        :param id: The id of the TikTok you want to get the object for.
        :param language: The 2 letter code of the language to return.
                         Note: Doesn't seem to have an affect.
        :param proxy: The IP address of a proxy to make requests from.
        """
        (
            region,
            language,
            proxy,
            maxCount,
            did,
        ) = self.__process_kwargs__(kwargs)
        kwargs['custom_did'] = did
        did = kwargs.get("custom_did", None)
        query = {
            "itemId": id,
            "language": language,
        }
        api_url = "{}api/item/detail/?{}&{}".format(
            BASE_URL, self.__add_new_params__(), urlencode(query)
        )

        return self.getData(url=api_url, **kwargs)

    def getTikTokByUrl(self, url, **kwargs) -> dict:
        """Returns a dictionary of a TikTok object by url.

        :param url: The TikTok url you want to retrieve.
        :param language: The 2 letter code of the language to return.
                         Note: Doesn't seem to have an affect.
        :param proxy: The IP address of a proxy to make requests from.
        """
        (
            region,
            language,
            proxy,
            maxCount,
            did,
        ) = self.__process_kwargs__(kwargs)
        kwargs['custom_did'] = did
        custom_did = kwargs.get("custom_did", None)
        if "@" in url and "/video/" in url:
            post_id = url.split("/video/")[1].split("?")[0]
        else:
            raise Exception(
                "URL format not supported. Below is an example of a supported url.\n"
                "https://www.tiktok.com/@therock/video/6829267836783971589"
            )

        return self.getTikTokById(
            post_id,
            **kwargs,
        )

    def discoverHashtags(self, **kwargs) -> dict:
        """Discover page, consists challenges (hashtags)

        :param proxy: The IP address of a proxy server.
        """
        (
            region,
            language,
            proxy,
            maxCount,
            did,
        ) = self.__process_kwargs__(kwargs)
        kwargs['custom_did'] = did
        query = {"noUser": 1, "userCount": 30, "scene": 0}
        api_url = "{}node/share/discover?{}&{}".format(
            BASE_URL, self.__add_new_params__(), urlencode(query)
        )

        return self.getData(url=api_url, **kwargs)["body"][1][
            "exploreList"
        ]

    def discoverMusic(self, **kwargs) -> dict:
        """Discover page, consists of music

        :param proxy: The IP address of a proxy server.
        """
        (
            region,
            language,
            proxy,
            maxCount,
            did,
        ) = self.__process_kwargs__(kwargs)
        kwargs['custom_did'] = did
        query = {"noUser": 1, "userCount": 30, "scene": 0}
        api_url = "{}node/share/discover?{}&{}".format(
            BASE_URL, self.__add_new_params__(), urlencode(query)
        )

        return self.getData(url=api_url, **kwargs)["body"][2][
            "exploreList"
        ]

    def getUserObject(self, username, **kwargs) -> dict:
        """Gets a user object (dictionary)

        :param username: The username of the user.
        :param language: The 2 letter code of the language to return.
                         Note: Doesn't seem to have an affect.
        :param proxy: The IP address of a proxy to make requests from.
        """
        (
            region,
            language,
            proxy,
            maxCount,
            did,
        ) = self.__process_kwargs__(kwargs)
        kwargs['custom_did'] = did
        return self.getUser(username, **kwargs)["user"]

    def getUser(self, username, **kwargs) -> dict:
        """Gets the full exposed user object

        :param username: The username of the user.
        :param language: The 2 letter code of the language to return.
                         Note: Doesn't seem to have an affect.
        :param proxy: The IP address of a proxy to make requests from.
        """
        (
            region,
            language,
            proxy,
            maxCount,
            did,
        ) = self.__process_kwargs__(kwargs)
        kwargs['custom_did'] = did
        query = {"uniqueId": username, "language": language}
        api_url = "{}api/user/detail/?{}&{}".format(
            BASE_URL, self.__add_new_params__(), urlencode(query)
        )

        return self.getData(url=api_url, **kwargs)["userInfo"]

    def getSuggestedUsersbyID(
        self, userId="6745191554350760966", count=30, **kwargs
    ) -> list:
        """Returns suggested users given a different TikTok user.

        :param userId: The id of the user to get suggestions for.
        :param count: The amount of users to return.
        :param proxy: The IP address of a proxy to make requests from.
        """
        (
            region,
            language,
            proxy,
            maxCount,
            did,
        ) = self.__process_kwargs__(kwargs)
        kwargs['custom_did'] = did
        query = {
            "noUser": 0,
            "pageId": userId,
            "userId": userId,
            "userCount": count,
            "scene": 15,
        }
        api_url = "{}node/share/discover?{}&{}".format(
            BASE_URL, self.__add_new_params__(), urlencode(query)
        )

        res = []
        for x in self.getData(url=api_url, **kwargs)["body"][0][
            "exploreList"
        ]:
            res.append(x["cardItem"])
        return res[:count]

    def getSuggestedUsersbyIDCrawler(
        self, count=30, startingId="6745191554350760966", **kwargs
    ) -> list:
        """Crawls for listing of all user objects it can find.

        :param count: The amount of users to crawl for.
        :param startingId: The ID of a TikTok user to start at.
        :param language: The language parameter.
        :param proxy: The IP address of a proxy to make requests from.
        """
        (
            region,
            language,
            proxy,
            maxCount,
            did,
        ) = self.__process_kwargs__(kwargs)
        kwargs['custom_did'] = did
        users = []
        unusedIDS = [startingId]
        while len(users) < count:
            userId = random.choice(unusedIDS)
            newUsers = self.getSuggestedUsersbyID(userId=userId, **kwargs)
            unusedIDS.remove(userId)

            for user in newUsers:
                if user not in users:
                    users.append(user)
                    unusedIDS.append(user["id"])

        return users[:count]

    def getSuggestedHashtagsbyID(
        self, count=30, userId="6745191554350760966", **kwargs
    ) -> list:
        """Returns suggested hashtags given a TikTok user.

        :param userId: The id of the user to get suggestions for.
        :param count: The amount of users to return.
        :param proxy: The IP address of a proxy to make requests from.
        """
        (
            region,
            language,
            proxy,
            maxCount,
            did,
        ) = self.__process_kwargs__(kwargs)
        kwargs['custom_did'] = did
        query = {
            "noUser": 0,
            "pageId": userId,
            "userId": userId,
            "userCount": count,
            "scene": 15,
        }
        api_url = "{}node/share/discover?{}&{}".format(
            BASE_URL, self.__add_new_params__(), urlencode(query)
        )

        res = []
        for x in self.getData(url=api_url, **kwargs)["body"][1][
            "exploreList"
        ]:
            res.append(x["cardItem"])
        return res[:count]

    def getSuggestedHashtagsbyIDCrawler(
        self, count=30, startingId="6745191554350760966", **kwargs
    ) -> list:
        """Crawls for as many hashtags as it can find.

        :param count: The amount of users to crawl for.
        :param startingId: The ID of a TikTok user to start at.
        :param language: The language parameter.
        :param proxy: The IP address of a proxy to make requests from.
        """
        (
            region,
            language,
            proxy,
            maxCount,
            did,
        ) = self.__process_kwargs__(kwargs)
        kwargs['custom_did'] = did
        hashtags = []
        ids = self.getSuggestedUsersbyIDCrawler(
            count=count, startingId=startingId, **kwargs
        )
        while len(hashtags) < count and len(ids) != 0:
            userId = random.choice(ids)
            newTags = self.getSuggestedHashtagsbyID(userId=userId["id"], **kwargs)
            ids.remove(userId)

            for hashtag in newTags:
                if hashtag not in hashtags:
                    hashtags.append(hashtag)

        return hashtags[:count]

    def getSuggestedMusicbyID(
        self, count=30, userId="6745191554350760966", **kwargs
    ) -> list:
        """Returns suggested music given a TikTok user.

        :param userId: The id of the user to get suggestions for.
        :param count: The amount of users to return.
        :param proxy: The IP address of a proxy to make requests from.
        """
        (
            region,
            language,
            proxy,
            maxCount,
            did,
        ) = self.__process_kwargs__(kwargs)
        kwargs['custom_did'] = did
        query = {
            "noUser": 0,
            "pageId": userId,
            "userId": userId,
            "userCount": count,
            "scene": 15,
        }
        api_url = "{}node/share/discover?{}&{}".format(
            BASE_URL, self.__add_new_params__(), urlencode(query)
        )

        res = []
        for x in self.getData(url=api_url, **kwargs)["body"][2][
            "exploreList"
        ]:
            res.append(x["cardItem"])
        return res[:count]

    def getSuggestedMusicIDCrawler(
        self, count=30, startingId="6745191554350760966", **kwargs
    ) -> list:
        """Crawls for hashtags.

        :param count: The amount of users to crawl for.
        :param startingId: The ID of a TikTok user to start at.
        :param language: The language parameter.
        :param proxy: The IP address of a proxy to make requests from.
        """
        (
            region,
            language,
            proxy,
            maxCount,
            did,
        ) = self.__process_kwargs__(kwargs)
        kwargs['custom_did'] = did
        musics = []
        ids = self.getSuggestedUsersbyIDCrawler(
            count=count, startingId=startingId, **kwargs
        )
        while len(musics) < count and len(ids) != 0:
            userId = random.choice(ids)
            newTags = self.getSuggestedMusicbyID(userId=userId["id"], **kwargs)
            ids.remove(userId)

            for music in newTags:
                if music not in musics:
                    musics.append(music)

        return musics[:count]

    def get_Video_By_TikTok(self, data, **kwargs) -> bytes:
        """Downloads video from TikTok using a TikTok object

        :param data: A TikTok object
        :param proxy: The IP address of your proxy.
        """
        (
            region,
            language,
            proxy,
            maxCount,
            did,
        ) = self.__process_kwargs__(kwargs)
        kwargs['custom_did'] = did
        try:
            api_url = data["video"]["downloadAddr"]
        except Exception:
            try:
                api_url = data["itemInfos"]["video"]["urls"][0]
            except Exception:
                api_url = data["itemInfo"]["itemStruct"]["video"]["playAddr"]
        return self.get_Video_By_DownloadURL(api_url, **kwargs)

    def get_Video_By_DownloadURL(self, download_url, **kwargs) -> bytes:
        """Downloads video from TikTok using download url in a TikTok object

        :param download_url: The download url key value in a TikTok object.
        :param proxy: The IP for your proxy.
        """
        (
            region,
            language,
            proxy,
            maxCount,
            did,
        ) = self.__process_kwargs__(kwargs)
        kwargs['custom_did'] = did
        return self.getBytes(url=download_url, **kwargs)

    def get_Video_By_Url(self, video_url, **kwargs) -> bytes:
        (
            region,
            language,
            proxy,
            maxCount,
            did,
        ) = self.__process_kwargs__(kwargs)
        kwargs['custom_did'] = did

        tiktok_schema = self.getTikTokByUrl(video_url, **kwargs)
        download_url = tiktok_schema["itemInfo"]["itemStruct"]["video"]["downloadAddr"]

        return self.getBytes(url=download_url, **kwargs)

    def get_Video_No_Watermark(self, video_url, return_bytes=0, **kwargs) -> bytes:
        """Gets the video with no watermark

        :param video_url: The url of the video you want to download
        :param return_bytes: Set this to 0 if you want url, 1 if you want bytes.
        :param proxy: The IP address of your proxy.
        """
        (
            region,
            language,
            proxy,
            maxCount,
            did,
        ) = self.__process_kwargs__(kwargs)
        kwargs['custom_did'] = did
        r = requests.get(
            video_url,
            headers={
                "method": "GET",
                "accept-encoding": "utf-8",
                "user-agent": self.userAgent,
            },
            proxies=self.__format_proxy(proxy),
        )

        data = r.text

        check = data.split('video":{"urls":["')
        if len(check) > 1:
            contentURL = check[1].split('"')[0]
            r = requests.get(
                contentURL,
                headers={
                    "method": "GET",
                    "accept-encoding": "gzip, deflate, br",
                    "accept-Language": "en-US,en;q=0.9",
                    "Range": "bytes=0-200000",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;"
                    "q=0.8,application/signed-exchange;v=b3;q=0.9",
                    "user-agent": self.userAgent,
                },
                proxies=self.__format_proxy(proxy),
            )

            tmp = r.text.split("vid:")
            if len(tmp) > 1:
                key = tmp[1].split("%")[0]
                if key[-1:] == " ":
                    key = key[1:]

                if key[:1] == " ":
                    key = key[:-1]

            else:
                key = ""

            cleanVideo = (
                "https://api2-16-h2.musical.ly/aweme/v1/play/?video_id={}&line=0&ratio=default"
                "&media_type=4&vr_type=0"
            ).format(key)

            b = browser(cleanVideo, **kwargs)
            if return_bytes == 0:
                return b.redirect_url
            else:
                r = requests.get(b.redirect_url, proxies=self.__format_proxy(proxy))
                return r.content

    #
    # PRIVATE METHODS
    #

    def __format_proxy(self, proxy) -> dict:
        """
        Formats the proxy object
        """
        if proxy is not None:
            return {"http": proxy, "https": proxy}
        else:
            return None

    def __get_js(self, proxy=None) -> str:
        return requests.get(
            "https://sf16-muse-va.ibytedtos.com/obj/rc-web-sdk-gcs/acrawler.js",
            proxies=self.__format_proxy(proxy),
        ).text

    def __format_new_params__(self, parm) -> str:
        return parm.replace("/", "%2F").replace(" ", "+").replace(";", "%3B")

    def __add_new_params__(self) -> str:
        query = {
            "aid": 1988,
            "app_name": "tiktok_web",
            "device_platform": "web",
            "referer": "https://www.tiktok.com/",
            "user_agent": self.__format_new_params__(self.userAgent),
            "cookie_enabled": "true",
            "screen_width": self.width,
            "screen_height": self.height,
            "browser_language": self.browser_language,
            "browser_platform": self.browser_platform,
            "browser_name": self.browser_name,
            "browser_version": self.browser_version,
            "browser_online": "true",
            "ac": "4g",
            "timezone_name": self.timezone_name,
            "appId": 1233,
            "appType": "m",
            "isAndroid": False,
            "isMobile": False,
            "isIOS": False,
            "OS": "windows",
        }
        return urlencode(query)

    # Process the kwargs
    def __process_kwargs__(self, kwargs):
        region = kwargs.get("region", "US")
        language = kwargs.get("language", "en")
        proxy = kwargs.get("proxy", None)
        maxCount = kwargs.get("maxCount", 35)
        did = kwargs.get("did", str(random.randint(10000, 999999999)))
        kwargs['did'] = did

        return region, language, proxy, maxCount, did
