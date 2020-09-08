import random
import requests
import time
from urllib.parse import urlencode

from .browser import browser


BASE_URL = "https://m.tiktok.com/"


class TikTokApi:
    def __init__(self, debug=False, request_delay=None):
        """The TikTokApi class. Used to interact with TikTok.

          :param debug: If you want debugging to be enabled.
          :param request_delay: The amount of time to wait before making a request.
        """
        self.debug = debug
        if debug:
            print("Class initialized")

        self.userAgent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/84.0.4147.125 Safari/537.36"
        )

        # Get Browser Params
        b = browser('newParam', newParams=True)

        try:
            self.timezone_name = self.__format_new_params__(b.timezone_name)
            self.browser_language = self.__format_new_params__(b.browser_language)
            self.browser_platform = self.__format_new_params__(b.browser_platform)
            self.browser_name = self.__format_new_params__(b.browser_name)
            self.browser_version = self.__format_new_params__(b.browser_version)
            self.width = b.width
            self.height = b.height
        except Exception as e:
            if debug:
                print("The following error occurred, but it was ignored.")
                print(e)

            self.timezone_name = ""
            self.browser_language = ""
            self.browser_platform = ""
            self.browser_name = ""
            self.browser_version = ""
            self.width = "1920"
            self.height = "1080"

        self.request_delay = request_delay

    def getData(self, b, language='en', proxy=None) -> dict:
        """Returns a dictionary of a response from TikTok.

          :param api_url: the base string without a signature

          :param b: The browser object that contains the signature

          :param language: The two digit language code to make requests to TikTok with.
                           Note: This doesn't seem to actually change things from the API.

          :param proxy: The IP address of a proxy server to request from.
        """
        if self.request_delay is not None:
            time.sleep(self.request_delay)

        query = {'verifyFp': b.verifyFp, 'did': b.did, '_signature': b.signature}
        url = "{}&{}".format(b.url, urlencode(query))
        r = requests.get(url, headers={
            'authority': 'm.tiktok.com',
            "method": "GET",
            'path': url.split("tiktok.com")[1],
            'scheme': 'https',
            'accept': 'application/json, text/plain, */*',
            "accept-encoding": "gzip, deflate, br",
            'accept-language': 'en-US,en;q=0.9',
            "referrer": b.referrer,
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            "user-agent": b.userAgent,
            'cookie': 'tt_webid_v2=' + b.did
        }, proxies=self.__format_proxy(proxy))
        try:
            return r.json()
        except Exception as e:
            if self.debug:
                print(e)
            print(r.request.headers)
            print("Converting response to JSON failed response is below (probably empty)")
            print(r.text)

            raise Exception('Invalid Response')

    def getBytes(self, b, proxy=None) -> bytes:
        """Returns bytes of a response from TikTok.

          :param api_url: the base string without a signature

          :param b: The browser object that contains the signature

          :param language: The two digit language code to make requests to TikTok with.
                           Note: This doesn't seem to actually change things from the API.

          :param proxy: The IP address of a proxy server to request from.
        """
        query = {'verifyFp': b.verifyFp, '_signature': b.signature}
        url = "{}&{}".format(b.url, urlencode(query))
        r = requests.get(url, headers={"method": "GET",
                                       "accept-encoding": "gzip, deflate, br",
                                       "referrer": b.referrer,
                                       "user-agent": b.userAgent,
                                       }, proxies=self.__format_proxy(proxy))
        return r.content

    def trending(self, count=30, language='en', region='US', proxy=None) -> dict:
        """
          Gets trending TikToks
        """
        response = []
        maxCount = 50
        maxCursor = 0
        first = True

        while len(response) < count:
            if count < maxCount:
                realCount = count
            else:
                realCount = maxCount

            query = {
                'count': realCount,
                'id': 1,
                'type': 5,
                'secUid': '',
                'maxCursor': maxCursor,
                'minCursor': 0,
                'sourceType': 12,
                'appId': 1233,
                'region': region,
                'priority_region': region,
                'language': language
            }
            api_url = "{}api/item_list/?{}&{}".format(
                BASE_URL, self.__add_new_params__(), urlencode(query)
            )
            b = browser(api_url, language=language, proxy=proxy)
            res = self.getData(b, proxy=proxy)

            if 'items' in res.keys():
                for t in res['items']:
                    response.append(t)

            if not res['hasMore'] and not first:
                if self.debug:
                    print("TikTok isn't sending more TikToks beyond this point.")
                return response

            realCount = count - len(response)
            maxCursor = res['maxCursor']

            first = False

        return response[:count]

    def userPosts(self, userID, secUID, count=30, language='en', region='US', proxy=None) -> dict:
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
        response = []
        maxCount = 50
        maxCursor = 0
        first = True

        while len(response) < count:
            if count < maxCount:
                realCount = count
            else:
                realCount = maxCount

            query = {
                'count': realCount,
                'id': userID,
                'type': 1,
                'secUid': secUID,
                'maxCursor': maxCursor,
                'minCursor': 0,
                'sourceType': 8,
                'appId': 1233,
                'region': region,
                'priority_region': region,
                'language': language
            }
            api_url = "{}api/item_list/?{}&{}".format(
                BASE_URL, self.__add_new_params__(), urlencode(query)
            )
            b = browser(api_url, proxy=proxy)
            res = self.getData(b, proxy=proxy)

            if 'items' in res.keys():
                for t in res['items']:
                    response.append(t)

            if not res['hasMore'] and not first:
                print("TikTok isn't sending more TikToks beyond this point.")
                return response

            realCount = count - len(response)
            maxCursor = res['maxCursor']

            first = False

        return response[:count]

    def byUsername(self, username, count=30, proxy=None, language='en', region='US') -> dict:
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
        data = self.getUserObject(username, proxy=proxy)
        return self.userPosts(data['id'], data['secUid'], count=count, proxy=proxy, language=language, region=region)

    def userPage(
        self, userID, secUID, page_size=30, before=0, after=0, language='en',
        region='US', proxy=None
    ) -> dict:
        """Returns a dictionary listing of one page of TikToks given a user's ID and secUID

          :param userID: The userID of the user, which TikTok assigns.
          :param secUID: The secUID of the user, which TikTok assigns.
          :param page_size: The number of posts to return per page.
          :param after: time stamp for the earliest TikTok to retrieve
          :param before: time stamp for the latest TikTok to retrieve
          :param language: The 2 letter code of the language to return.
                           Note: Doesn't seem to have an affect.
          :param region: The 2 letter region code.
                         Note: Doesn't seem to have an affect.
          :param proxy: The IP address of a proxy to make requests from.
        """
        api_url = (
            "https://m.tiktok.com/api/item_list/?{}&count={}&id={}&type=1&secUid={}"
            "&minCursor={}&maxCursor={}&sourceType=8&appId=1233&region={}&language={}".format(
                self.__add_new_params__(), page_size, str(userID), str(secUID),
                after, before, region, language
            )
        )
        b = browser(api_url, proxy=proxy)
        return self.getData(b, proxy=proxy)

    def getUserPager(self, username, page_size=30, before=0, after=0, proxy=None, language='en', region='US'):
        """Returns a generator to page through a user's feed

          :param username: The username of the user.
          :param page_size: The number of posts to return in a page.
          :param after: time stamp for the earliest TikTok to retrieve
          :param before: time stamp for the latest TikTok to retrieve
          :param language: The 2 letter code of the language to return.
                           Note: Doesn't seem to have an affect.
          :param region: The 2 letter region code.
                         Note: Doesn't seem to have an affect.
          :param proxy: The IP address of a proxy to make requests from.
        """
        data = self.getUserObject(username, proxy=proxy)

        while True:
            resp = self.userPage(
                data['id'], data['secUid'], page_size=page_size,
                before=before, after=after, proxy=proxy, language=language, region=region
            )

            try:
                page = resp['items']
            except KeyError:
                # No mo results
                return

            before = resp['maxCursor']

            yield page

            if not resp['hasMore']:
                return  # all done

    def userLiked(self, userID, secUID, count=30, language='en', region='US', proxy=None) -> dict:
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
        response = []
        maxCount = 50
        maxCursor = 0
        first = True

        while len(response) < count:
            if count < maxCount:
                realCount = count
            else:
                realCount = maxCount

            query = {
                'count': realCount,
                'id': userID,
                'type': 2,
                'secUid': secUID,
                'maxCursor': maxCursor,
                'minCursor': 0,
                'sourceType': 9,
                'appId': 1233,
                'region': region,
                'priority_region': region,
                'language': language
            }
            api_url = "{}api/item_list/?{}&{}".format(
                BASE_URL, self.__add_new_params__(), urlencode(query)
            )
            b = browser(api_url, proxy=proxy)
            res = self.getData(b, proxy=proxy)

            try:
                res['items']
            except Exception:
                if self.debug:
                    print("Most Likely User's List is Empty")
                return []

            if 'items' in res.keys():
                for t in res['items']:
                    response.append(t)

            if not res['hasMore'] and not first:
                print("TikTok isn't sending more TikToks beyond this point.")
                return response

            realCount = count - len(response)
            maxCursor = res['maxCursor']

            first = False

        return response[:count]

    def userLikedbyUsername(self, username, count=30, proxy=None, language='en', region='US') -> dict:
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
        data = self.getUserObject(username, proxy=proxy)
        return self.userLiked(data['id'], data['secUid'], count=count, proxy=proxy, language=language, region=region)

    def bySound(self, id, count=30, language='en', proxy=None) -> dict:
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
        response = []
        maxCount = 50
        maxCursor = 0

        while len(response) < count:
            if count < maxCount:
                realCount = count
            else:
                realCount = maxCount

            query = {
                'count': realCount,
                'id': id,
                'type': 4,
                'secUid': '',
                'maxCursor': maxCursor,
                'minCursor': 0,
                'shareUid': '',
                'lang': language
            }
            api_url = "{}share/item/list?{}&{}".format(
                BASE_URL, self.__add_new_params__(), urlencode(query)
            )
            b = browser(api_url, proxy=proxy)
            res = self.getData(b, proxy=proxy)

            for t in res['body']['itemListData']:
                response.append(t)

            if not res['body']['hasMore']:
                print("TikTok isn't sending more TikToks beyond this point.")
                return response

            realCount = count - len(response)
            maxCursor = res['body']['maxCursor']

        return response[:count]

    def getMusicObject(self, id, language='en', proxy=None) -> dict:
        """Returns a music object for a specific sound id.

          :param id: The sound id to search by.
          :param language: The 2 letter code of the language to return.
                           Note: Doesn't seem to have an affect.
          :param proxy: The IP address of a proxy to make requests from.
        """
        query = {
            'musicId': id,
            'lang': language
        }
        api_url = "{}api/music/detail/?{}&{}".format(
            BASE_URL, self.__add_new_params__(), urlencode(query)
        )
        b = browser(api_url, proxy=proxy)
        return self.getData(b, proxy=proxy)

    def byHashtag(self, hashtag, count=30, language='en', proxy=None, region='') -> dict:
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
        id = self.getHashtagObject(hashtag)['challengeInfo']['challenge']['id']
        response = []
        maxCursor = 0

        while len(response) < count:
            query = {
                'count': count,
                'id': id,
                'type': 3,
                'secUid': '',
                'maxCursor': maxCursor,
                'minCursor': 0,
                'shareUid': '',
                'recType': '',
                'priority_region': region,
                'lang': language,
            }
            api_url = "{}share/item/list?{}&{}".format(
                BASE_URL, self.__add_new_params__(), urlencode(query)
            )
            b = browser(api_url, proxy=proxy)
            res = self.getData(b, proxy=proxy, language=language)

            for t in res['body']['itemListData']:
                response.append(t)

            if not res['body']['hasMore']:
                print("TikTok isn't sending more TikToks beyond this point.")
                return response

            maxCursor = res['body']['maxCursor']

        return response[:count]

    def getHashtagObject(self, hashtag, language='en', proxy=None) -> dict:
        """Returns a hashtag object.

          :param hashtag: The hashtag to search by.
          :param language: The 2 letter code of the language to return.
                           Note: Doesn't seem to have an affect.
          :param proxy: The IP address of a proxy to make requests from.
        """
        query = {
            'challengeName': str(hashtag.encode('utf-8'))[2:-1].replace("\\x", "%").upper(),
            'language': language
        }
        api_url = "{}api/challenge/detail/?{}&{}".format(
            BASE_URL, self.__add_new_params__(), urlencode(query)
        )
        b = browser(api_url, proxy=proxy)
        return self.getData(b, proxy=proxy)

    def getRecommendedTikToksByVideoID(self, id, language='en', proxy=None) -> dict:
        """Returns a dictionary listing reccomended TikToks for a specific TikTok video.

          :param id: The id of the video to get suggestions for.
          :param language: The 2 letter code of the language to return.
                           Note: Doesn't seem to have an affect.
          :param proxy: The IP address of a proxy to make requests from.
        """
        query = {
            'count': 24,
            'id': id,
            'type': 0,
            'secUid': '',
            'maxCursor': 0,
            'minCursor': 0,
            'shareUid': '',
            'recType': 3,
            'lang': language,
        }
        api_url = "{}share/item/list?{}&{}".format(
            BASE_URL, self.__add_new_params__(), urlencode(query)
        )
        b = browser(api_url, proxy=proxy)
        return self.getData(b, proxy=proxy)['body']

    def getTikTokById(self, id, language='en', proxy=None) -> dict:
        """Returns a dictionary of a specific TikTok.

          :param id: The id of the TikTok you want to get the object for.
          :param language: The 2 letter code of the language to return.
                           Note: Doesn't seem to have an affect.
          :param proxy: The IP address of a proxy to make requests from.
        """

        query = {
            'itemId': id,
            'lang': language,
        }
        api_url = "{}api/item/detail/?{}&{}".format(
            BASE_URL, self.__add_new_params__(), urlencode(query)
        )
        b = browser(api_url, proxy=proxy)
        return self.getData(b, proxy=proxy)

    def getTikTokByUrl(self, url, language='en', proxy=None) -> dict:
        """Returns a dictionary of a TikTok object by url.

          :param url: The TikTok url you want to retrieve.
          :param language: The 2 letter code of the language to return.
                           Note: Doesn't seem to have an affect.
          :param proxy: The IP address of a proxy to make requests from.
        """
        if "@" in url and "/video/" in url:
            post_id = url.split("/video/")[1].split("?")[0]
        else:
            raise Exception(
                "URL format not supported. Below is an example of a supported url.\n"
                "https://www.tiktok.com/@therock/video/6829267836783971589"
            )

        return self.getTikTokById(post_id, language=language, proxy=proxy)

    def discoverHashtags(self, proxy=None) -> dict:
        """Discover page, consists challenges (hashtags)

          :param proxy: The IP address of a proxy server.
        """
        query = {
            'noUser': 1,
            'userCount': 30,
            'scene': 0
        }
        api_url = "{}node/share/discover?{}&{}".format(
            BASE_URL, self.__add_new_params__(), urlencode(query)
        )
        b = browser(api_url, proxy=proxy)
        return self.getData(b, proxy=proxy)['body'][1]['exploreList']

    def discoverMusic(self, proxy=None) -> dict:
        """Discover page, consists of music

          :param proxy: The IP address of a proxy server.
        """
        query = {
            'noUser': 1,
            'userCount': 30,
            'scene': 0
        }
        api_url = "{}node/share/discover?{}&{}".format(
            BASE_URL, self.__add_new_params__(), urlencode(query)
        )
        b = browser(api_url, proxy=proxy)
        return self.getData(b, proxy=proxy)['body'][2]['exploreList']

    def getUserObject(self, username, language='en', proxy=None) -> dict:
        """Gets a user object (dictionary)

          :param username: The username of the user.
          :param language: The 2 letter code of the language to return.
                           Note: Doesn't seem to have an affect.
          :param proxy: The IP address of a proxy to make requests from.
        """
        return self.getUser(username, language, proxy=proxy)['userInfo']['user']

    def getUser(self, username, language='en', proxy=None) -> dict:
        """Gets the full exposed user object

          :param username: The username of the user.
          :param language: The 2 letter code of the language to return.
                           Note: Doesn't seem to have an affect.
          :param proxy: The IP address of a proxy to make requests from.
        """
        query = {
            'uniqueId': username,
            'language': language
        }
        api_url = "{}api/user/detail/?{}&{}".format(
            BASE_URL, self.__add_new_params__(), urlencode(query)
        )
        b = browser(api_url, proxy=proxy)
        return self.getData(b, proxy=proxy)

    def getSuggestedUsersbyID(self, userId='6745191554350760966', count=30, language='en', proxy=None) -> list:
        """Returns suggested users given a different TikTok user.

          :param userId: The id of the user to get suggestions for.
          :param count: The amount of users to return.
          :param proxy: The IP address of a proxy to make requests from.
        """
        query = {
            'noUser': 0,
            'pageId': userId,
            'userId': userId,
            'userCount': count,
            'scene': 15
        }
        api_url = "{}node/share/discover?{}&{}".format(
            BASE_URL, self.__add_new_params__(), urlencode(query)
        )
        b = browser(api_url, proxy=proxy)

        res = []
        for x in self.getData(b, proxy=proxy)['body'][0]['exploreList']:
            res.append(x['cardItem'])
        return res[:count]

    def getSuggestedUsersbyIDCrawler(
        self, count=30, startingId='6745191554350760966', language='en', proxy=None
    ) -> list:
        """Crawls for listing of all user objects it can find.

          :param count: The amount of users to crawl for.
          :param startingId: The ID of a TikTok user to start at.
          :param language: The language parameter.
          :param proxy: The IP address of a proxy to make requests from.
        """
        users = []
        unusedIDS = [startingId]
        while len(users) < count:
            userId = random.choice(unusedIDS)
            newUsers = self.getSuggestedUsersbyID(
                userId=userId, language=language, proxy=proxy)
            unusedIDS.remove(userId)

            for user in newUsers:
                if user not in users:
                    users.append(user)
                    unusedIDS.append(user['id'])

        return users[:count]

    def getSuggestedHashtagsbyID(self, count=30, userId='6745191554350760966', language='en', proxy=None) -> list:
        """Returns suggested hashtags given a TikTok user.

          :param userId: The id of the user to get suggestions for.
          :param count: The amount of users to return.
          :param proxy: The IP address of a proxy to make requests from.
        """
        query = {
            'noUser': 0,
            'pageId': userId,
            'userId': userId,
            'userCount': count,
            'scene': 15
        }
        api_url = "{}node/share/discover?{}&{}".format(
            BASE_URL, self.__add_new_params__(), urlencode(query)
        )
        b = browser(api_url, proxy=proxy)

        res = []
        for x in self.getData(b, proxy=proxy)['body'][1]['exploreList']:
            res.append(x['cardItem'])
        return res[:count]

    def getSuggestedHashtagsbyIDCrawler(
        self, count=30, startingId='6745191554350760966', language='en', proxy=None
    ) -> list:
        """Crawls for as many hashtags as it can find.

          :param count: The amount of users to crawl for.
          :param startingId: The ID of a TikTok user to start at.
          :param language: The language parameter.
          :param proxy: The IP address of a proxy to make requests from.
        """
        hashtags = []
        ids = self.getSuggestedUsersbyIDCrawler(
            count=count, startingId=startingId, language=language, proxy=proxy)
        while len(hashtags) < count and len(ids) != 0:
            userId = random.choice(ids)
            newTags = self.getSuggestedHashtagsbyID(
                userId=userId['id'], language=language, proxy=proxy)
            ids.remove(userId)

            for hashtag in newTags:
                if hashtag not in hashtags:
                    hashtags.append(hashtag)

        return hashtags[:count]

    def getSuggestedMusicbyID(self, count=30, userId='6745191554350760966', language='en', proxy=None) -> list:
        """Returns suggested music given a TikTok user.

          :param userId: The id of the user to get suggestions for.
          :param count: The amount of users to return.
          :param proxy: The IP address of a proxy to make requests from.
        """
        query = {
            'noUser': 0,
            'pageId': userId,
            'userId': userId,
            'userCount': count,
            'scene': 15
        }
        api_url = "{}node/share/discover?{}&{}".format(
            BASE_URL, self.__add_new_params__(), urlencode(query)
        )
        b = browser(api_url, proxy=proxy)

        res = []
        for x in self.getData(b, proxy=proxy)['body'][2]['exploreList']:
            res.append(x['cardItem'])
        return res[:count]

    def getSuggestedMusicIDCrawler(self, count=30, startingId='6745191554350760966', language='en', proxy=None) -> list:
        """Crawls for hashtags.

          :param count: The amount of users to crawl for.
          :param startingId: The ID of a TikTok user to start at.
          :param language: The language parameter.
          :param proxy: The IP address of a proxy to make requests from.
        """
        musics = []
        ids = self.getSuggestedUsersbyIDCrawler(
            count=count, startingId=startingId, language=language, proxy=proxy)
        while len(musics) < count and len(ids) != 0:
            userId = random.choice(ids)
            newTags = self.getSuggestedMusicbyID(
                userId=userId['id'], language=language, proxy=proxy)
            ids.remove(userId)

            for music in newTags:
                if music not in musics:
                    musics.append(music)

        return musics[:count]

    def get_Video_By_TikTok(self, data, proxy=None) -> bytes:
        """Downloads video from TikTok using a TikTok object

          :param data: A TikTok object
          :param proxy: The IP address of your proxy.
        """
        try:
            api_url = data['video']['downloadAddr']
        except Exception:
            api_url = data['itemInfos']['video']['urls'][0]
        return self.get_Video_By_DownloadURL(api_url, proxy=proxy)

    def get_Video_By_DownloadURL(self, download_url, proxy=None) -> bytes:
        """Downloads video from TikTok using download url in a TikTok object

          :param download_url: The download url key value in a TikTok object.
          :param proxy: The IP for your proxy.
        """
        b = browser(download_url, proxy=proxy)
        return self.getBytes(b, proxy=proxy)

    def get_Video_By_Url(self, video_url, return_bytes=0, chromedriver_path=None) -> bytes:
        """(DEPRECRATED)
            Gets the source url of a given url for a tiktok

            video_url - the url of the video
            return_bytes - 0 is just the url, 1 is the actual video bytes
            chromedriver_path - path to your chrome driver executable
        """
        raise Exception("Deprecated. Other Methods Work Better.")

    def get_Video_No_Watermark_ID(self, video_id, return_bytes=0, proxy=None) -> bytes:
        """Returns a TikTok video with no water mark

          :param video_id: The ID of the TikTok you want to download
          :param return_bytes: Set this to 1 if you want bytes, 0 if you want url.
          :param proxy: The IP address of your proxy.
        """
        video_info = self.getTikTokById(video_id)
        video_url = video_info["itemInfo"]["itemStruct"]["video"]["downloadAddr"]
        headers = {"User-Agent": "okhttp", "Range": "bytes=1000-80000"}
        video_data = requests.get(video_url, params=None, headers=headers).text
        pos = video_data.find("vid:")
        if pos == -1:
            return None
        video_url_no_wm = (
            "https://api2-16-h2.musical.ly/aweme/v1/play/?video_id={}&vr_type=0&is_play_url=1"
            "&source=PackSourceEnum_PUBLISH&media_type=4"
            .format(video_data[pos + 4:pos + 36])
        )
        if return_bytes == 0:
            return video_url_no_wm
        else:
            headers = {"User-Agent": "okhttp"}
            video_data_no_wm = requests.get(
                video_url_no_wm, params=None, headers=headers)
            return video_data_no_wm.content

    def get_Video_No_Watermark_Faster(self, video_url, return_bytes=0, proxy=None) -> bytes:
        """No Water Mark method, but may be faster

          :param video_url: The url of the video you want to download
          :param return_bytes: Set this to 1 if you want bytes, set it to 0 for url.
          :param proxy: The IP of your proxy.
        """
        video_id = video_url.split("/video/")[1].split("?")[0]
        return self.get_Video_No_Watermark_ID(video_id, return_bytes, proxy=proxy)

    def get_Video_No_Watermark(self, video_url, return_bytes=0, proxy=None) -> bytes:
        """Gets the video with no watermark

          :param video_url: The url of the video you want to download
          :param return_bytes: Set this to 0 if you want url, 1 if you want bytes.
          :param proxy: The IP address of your proxy.
        """
        r = requests.get(video_url, headers={"method": "GET",
                                             "accept-encoding": "utf-8",
                                             "user-agent": self.userAgent
                                             }, proxies=self.__format_proxy(proxy))

        data = r.text

        check = data.split('video":{"urls":["')
        if len(check) > 1:
            contentURL = check[1].split("\"")[0]
            r = requests.get(contentURL, headers={
                "method": "GET",
                "accept-encoding": "gzip, deflate, br",
                'accept-Language': 'en-US,en;q=0.9',
                'Range': 'bytes=0-200000',
                'Accept':
                    'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                    'q=0.8,application/signed-exchange;v=b3;q=0.9',
                "user-agent": self.userAgent,
            }, proxies=self.__format_proxy(proxy))

            tmp = r.text.split("vid:")
            if len(tmp) > 1:
                key = tmp[1].split("%")[0]
                print(key)

                if key[-1:] == ' ':
                    key = key[1:]

                if key[:1] == ' ':
                    key = key[:-1]

            else:
                key = ""

            cleanVideo = (
                "https://api2-16-h2.musical.ly/aweme/v1/play/?video_id={}&line=0&ratio=default"
                "&media_type=4&vr_type=0"
            ).format(key)

            b = browser(cleanVideo, find_redirect=True, proxy=proxy)
            print(b.redirect_url)
            if return_bytes == 0:
                return b.redirect_url
            else:
                r = requests.get(
                    b.redirect_url, proxies=self.__format_proxy(proxy))
                return r.content
    #
    # PRIVATE METHODS
    #

    def __format_proxy(self, proxy) -> dict:
        """
          Formats the proxy object
        """
        if proxy is not None:
            return {
                'http': proxy,
                'https': proxy
            }
        else:
            return None

    def __get_js(self, proxy=None) -> str:
        return requests.get(
            "https://sf16-muse-va.ibytedtos.com/obj/rc-web-sdk-gcs/acrawler.js",
            proxies=self.__format_proxy(proxy)
        ).text

    def __format_new_params__(self, parm) -> str:
        return parm.replace("/", "%2F").replace(" ", "+").replace(";", "%3B")

    def __add_new_params__(self) -> str:
        query = {
            'aid': 1988,
            'app_name': 'tiktok_web',
            'device_platform': 'web',
            'Referer': '',
            'user_agent': self.__format_new_params__(self.userAgent),
            'cookie_enabled': 'true',
            'screen_width': self.width,
            'screen_height': self.height,
            'browser_language': self.browser_language,
            'browser_platform': self.browser_platform,
            'browser_name': self.browser_name,
            'browser_version': self.browser_version,
            'browser_online': 'true',
            'ac': '4g',
            'timezone_name': self.timezone_name,
            'appId': 1233,
            'appType': 'm',
            'isAndroid': False,
            'isMobile': False,
            'isIOS': False,
            'OS': 'windows'
        }
        return urlencode(query)
