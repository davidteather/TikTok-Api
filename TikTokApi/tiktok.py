
import pyppeteer
import random
import requests
from .browser import browser
import time
from selenium import webdriver


class TikTokApi:
    def __init__(self, debug=False, request_delay=None):
        """The TikTokApi class. Used to interact with TikTok.

          :param debug: If you want debugging to be enabled.
          :param request_delay: The amount of time to wait before making a request.
        """
        self.debug = debug
        if debug:
            print("Class initialized")

        self.userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36"

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

    def getData(self, api_url, b, language='en', proxy=None):
        """Returns a dictionary of a response from TikTok.

          :param api_url: the base string without a signature

          :param b: The browser object that contains the signature

          :param language: The two digit language code to make requests to TikTok with.
                           Note: This doesn't seem to actually change things from the API.
            
          :param proxy: The IP address of a proxy server to request from.
        """
        if self.request_delay != None:
            time.sleep(self.request_delay)
        url = b.url + \
            "&verifyFp=" + b.verifyFp + \
            "&_signature=" + b.signature
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
            "user-agent": b.userAgent



        }, proxies=self.__format_proxy(proxy))
        try:
            return r.json()
        except:
            print(r.request.headers)
            print("Converting response to JSON failed response is below (probably empty)")
            print(r.text)

            raise Exception('Invalid Response')

    def getBytes(self, api_url, b, proxy=None):
        """Returns bytes of a response from TikTok.

          :param api_url: the base string without a signature

          :param b: The browser object that contains the signature

          :param language: The two digit language code to make requests to TikTok with.
                           Note: This doesn't seem to actually change things from the API.
            
          :param proxy: The IP address of a proxy server to request from.
        """
        url = api_url + \
            "&_verifyFp=" + b.verifyFp + \
            "&_signature=" + b.signature
        r = requests.get(url, headers={"method": "GET",
                                       "accept-encoding": "gzip, deflate, br",
                                       "referrer": b.referrer,
                                       "user-agent": b.userAgent,
                                       }, proxies=self.__format_proxy(proxy))
        return r.content

    def trending(self, count=30, language='en', region='US', proxy=None):
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
            api_url = "https://m.tiktok.com/api/item_list/?{}&count={}&id=1&type=5&secUid=&maxCursor={}&minCursor=0&sourceType=12&appId=1233&region={}&language={}".format(
                self.__add_new_params__() ,str(realCount), str(maxCursor), str(region), str(language))
            b = browser(api_url, language=language, proxy=proxy)
            res = self.getData(api_url, b, proxy=proxy)

            if 'items' in res.keys():
                for t in res['items']:
                    response.append(t)

            if not res['hasMore'] and not first:
                if self.debug:
                    print("TikTok isn't sending more TikToks beyond this point.")
                return response

            realCount = count-len(response)
            maxCursor = res['maxCursor']

            first = False

        return response[:count]

    def userPosts(self, userID, secUID, count=30, language='en', region='US', proxy=None):
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
            api_url = "https://m.tiktok.com/api/item_list/?{}&count={}&id={}&type=1&secUid={}&maxCursor={}&minCursor=0&sourceType=8&appId=1233&region={}&language={}".format(
                self.__add_new_params__(), str(realCount), str(userID), str(secUID), str(maxCursor), str(region), str(language))
            b = browser(api_url, proxy=proxy)
            res = self.getData(api_url, b, proxy=proxy)

            if 'items' in res.keys():
                for t in res['items']:
                    response.append(t)

            if not res['hasMore'] and not first:
                print("TikTok isn't sending more TikToks beyond this point.")
                return response

            realCount = count-len(response)
            maxCursor = res['maxCursor']

            first = False

        return response[:count]

    def byUsername(self, username, count=30, proxy=None, language='en', region='US'):
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

    def userLiked(self, userID, secUID, count=30, language='en', region='US', proxy=None):
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

            api_url = "https://m.tiktok.com/api/item_list/?{}&count={}&id={}&type=2&secUid={}&maxCursor={}&minCursor=0&sourceType=9&appId=1233&region={}&language={}&verifyFp=".format(
                self.__add_new_params__(), str(realCount), str(userID), str(secUID), str(maxCursor), str(region), str(language))
            b = browser(api_url, proxy=proxy)
            res = self.getData(api_url, b, proxy=proxy)

            try:
                res['items']
            except:
                if self.debug:
                    print("Most Likely User's List is Empty")
                return []

            if 'items' in res.keys():
                for t in res['items']:
                    response.append(t)

            if not res['hasMore'] and not first:
                print("TikTok isn't sending more TikToks beyond this point.")
                return response

            realCount = count-len(response)
            maxCursor = res['maxCursor']

            first = False

        return response[:count]

    def userLikedbyUsername(self, username, count=30, proxy=None, language='en', region='US'):
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

    def bySound(self, id, count=30, language='en', proxy=None):
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

            api_url = "https://m.tiktok.com/share/item/list?{}&secUid=&id={}&type=4&count={}&minCursor=0&maxCursor={}&shareUid=&lang={}&verifyFp=".format(
                self.__add_new_params__(),str(id), str(realCount), str(maxCursor), str(language))
            b = browser(api_url, proxy=proxy)
            res = self.getData(api_url, b, proxy=proxy)

            for t in res['body']['itemListData']:
                response.append(t)

            if not res['body']['hasMore']:
                print("TikTok isn't sending more TikToks beyond this point.")
                return response

            realCount = count-len(response)
            maxCursor = res['body']['maxCursor']

        return response[:count]

    def getMusicObject(self, id, language='en', proxy=None):
        """Returns a music object for a specific sound id.

          :param id: The sound id to search by.
          :param language: The 2 letter code of the language to return.
                           Note: Doesn't seem to have an affect.
          :param proxy: The IP address of a proxy to make requests from. 
        """
        api_url = "https://m.tiktok.com/api/music/detail/?{}&musicId={}&language={}&verifyFp=".format(
            self.__add_new_params__(), str(id), language)
        b = browser(api_url, proxy=proxy)
        return self.getData(api_url, b, proxy=proxy)

    def byHashtag(self, hashtag, count=30, language='en', proxy=None, region='US'):
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
        maxCount = 50
        maxCursor = 0

        while len(response) < count:
            if count < maxCount:
                realCount = count
            else:
                realCount = maxCount

            api_url = "https://m.tiktok.com/share/item/list?{}&region={}&secUid=&id={}&type=3&count={}&minCursor=0&maxCursor={}&shareUid=&recType=&lang={}".format(
                self.__add_new_params__(), region, str(
                    id), str(count), str(maxCursor), language
            )
            b = browser(api_url, proxy=proxy)
            res = self.getData(api_url, b, proxy=proxy, language=language)

            for t in res['body']['itemListData']:
                response.append(t)

            if not res['body']['hasMore']:
                print("TikTok isn't sending more TikToks beyond this point.")
                return response

            realCount = count-len(response)
            maxCursor = res['body']['maxCursor']

        return response[:count]

    def getHashtagObject(self, hashtag, language='en', proxy=None):
        """Returns a hashtag object.

          :param hashtag: The hashtag to search by.
          :param language: The 2 letter code of the language to return.
                           Note: Doesn't seem to have an affect.
          :param proxy: The IP address of a proxy to make requests from. 
        """
        api_url = "https://m.tiktok.com/api/challenge/detail/?{}&challengeName={}&language={}".format(
            self.__add_new_params__(), str(hashtag.encode('utf-8'))[2:-1].replace("\\x", "%").upper(), language)
        b = browser(api_url, proxy=proxy)
        return self.getData(api_url, b, proxy=proxy)

    def getRecommendedTikToksByVideoID(self, id, language='en', proxy=None):
        """Returns a dictionary listing reccomended TikToks for a specific TikTok video.

          :param id: The id of the video to get suggestions for.
          :param language: The 2 letter code of the language to return.
                           Note: Doesn't seem to have an affect.
          :param proxy: The IP address of a proxy to make requests from. 
        """
        api_url = "https://m.tiktok.com/share/item/list?{}&secUid=&id={}&type=0&count=24&minCursor=0&maxCursor=0&shareUid=&recType=3&lang={}&verifyFp=".format(
            self.__add_new_params__(), id, language)
        b = browser(api_url, proxy=proxy)
        return self.getData(api_url, b, proxy=proxy)['body']

    def getTikTokById(self, id, language='en', proxy=None):
        """Returns a dictionary of a specific TikTok.

          :param id: The id of the TikTok you want to get the object for.
          :param language: The 2 letter code of the language to return.
                           Note: Doesn't seem to have an affect.
          :param proxy: The IP address of a proxy to make requests from. 
        """
        api_url = "https://m.tiktok.com/api/item/detail/?{}&itemId={}&language={}&verifyFp=".format(
            self.__add_new_params__(), id, language)
        b = browser(api_url, proxy=proxy)
        return self.getData(api_url, b, proxy=proxy)

    def getTikTokByUrl(self, url, language='en', proxy=None):
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
                "URL format not supported. Below is an example of a supported url.\nhttps://www.tiktok.com/@therock/video/6829267836783971589")

        return self.getTikTokById(post_id, language=language, proxy=proxy)

    def discoverHashtags(self, proxy=None):
        """Discover page, consists challenges (hashtags)

          :param proxy: The IP address of a proxy server.
        """
        api_url = "https://m.tiktok.com/node/share/discover?{}&noUser=1&userCount=30&scene=0&verifyFp=".format(self.__add_new_params__())
        b = browser(api_url, proxy=proxy)
        return self.getData(api_url, b, proxy=proxy)['body'][1]['exploreList']

    def discoverMusic(self, proxy=None):
        """Discover page, consists of music

          :param proxy: The IP address of a proxy server.
        """
        api_url = "https://m.tiktok.com/node/share/discover?{}&noUser=1&userCount=30&scene=0&verifyFp=".format(self.__add_new_params__())
        b = browser(api_url, proxy=proxy)
        return self.getData(api_url, b, proxy=proxy)['body'][2]['exploreList']

    def getUserObject(self, username, language='en', proxy=None):
        """Gets a user object (dictionary)

          :param username: The username of the user.
          :param language: The 2 letter code of the language to return.
                           Note: Doesn't seem to have an affect.
          :param proxy: The IP address of a proxy to make requests from. 
        """
        return self.getUser(username, language, proxy=proxy)['userInfo']['user']

    def getUser(self, username, language='en', proxy=None):
        """Gets the full exposed user object

          :param username: The username of the user.
          :param language: The 2 letter code of the language to return.
                           Note: Doesn't seem to have an affect.
          :param proxy: The IP address of a proxy to make requests from. 
        """
        api_url = "https://m.tiktok.com/api/user/detail/?{}&uniqueId={}&language={}".format(
            self.__add_new_params__(), username, language)
        b = browser(api_url, proxy=proxy)
        return self.getData(api_url, b, proxy=proxy)

    def getSuggestedUsersbyID(self, userId='6745191554350760966', count=30 ,language='en', proxy=None):
        """Returns suggested users given a different TikTok user.

          :param userId: The id of the user to get suggestions for.
          :param count: The amount of users to return.
          :param proxy: The IP address of a proxy to make requests from. 
        """
        api_url = "https://m.tiktok.com/node/share/discover?{}&noUser=0&pageId={}&userId={}&userCount={}&scene=15&verifyFp=".format(
            self.__add_new_params__(), userId, userId, str(count))
        b = browser(api_url, proxy=proxy)

        res = []
        for x in self.getData(api_url, b, proxy=proxy)['body'][0]['exploreList']:
            res.append(x['cardItem'])
        return res[:count]

    def getSuggestedUsersbyIDCrawler(self, count=30, startingId='6745191554350760966', language='en', proxy=None):
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

    def getSuggestedHashtagsbyID(self, count=30, userId='6745191554350760966', language='en', proxy=None):
        """Returns suggested hashtags given a TikTok user.

          :param userId: The id of the user to get suggestions for.
          :param count: The amount of users to return.
          :param proxy: The IP address of a proxy to make requests from. 
        """
        api_url = "https://m.tiktok.com/node/share/discover?{}&noUser=0&pageId={}&userId={}&userCount={}&scene=15&verifyFp=".format(
            self.__add_new_params__(), userId, userId, str(count))
        b = browser(api_url, proxy=proxy)

        res = []
        for x in self.getData(api_url, b, proxy=proxy)['body'][1]['exploreList']:
            res.append(x['cardItem'])
        return res[:count]

    def getSuggestedHashtagsbyIDCrawler(self, count=30, startingId='6745191554350760966', language='en', proxy=None):
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

    def getSuggestedMusicbyID(self, count=30, userId='6745191554350760966', language='en', proxy=None):
        """Returns suggested music given a TikTok user.

          :param userId: The id of the user to get suggestions for.
          :param count: The amount of users to return.
          :param proxy: The IP address of a proxy to make requests from. 
        """
        api_url = "https://m.tiktok.com/node/share/discover?{}&noUser=0&pageId={}&userId={}&userCount={}&scene=15&verifyFp=".format(
            self.__add_new_params__(), userId, userId, str(count))
        b = browser(api_url, proxy=proxy)

        res = []
        for x in self.getData(api_url, b, proxy=proxy)['body'][2]['exploreList']:
            res.append(x['cardItem'])
        return res[:count]

    def getSuggestedMusicIDCrawler(self, count=30, startingId='6745191554350760966', language='en', proxy=None):
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

    def get_Video_By_TikTok(self, data, proxy=None):
        """Downloads video from TikTok using a TikTok object

          :param data: A TikTok object
          :param proxy: The IP address of your proxy.
        """
        api_url = data['video']['downloadAddr']
        return self.get_Video_By_DownloadURL(api_url, proxy=proxy)

    def get_Video_By_DownloadURL(self, download_url, proxy=None):
        """Downloads video from TikTok using download url in a TikTok object

          :param download_url: The download url key value in a TikTok object.
          :param proxy: The IP for your proxy.
        """
        b = browser(download_url, proxy=proxy)
        return self.getBytes(download_url, b, proxy=proxy)

    def get_Video_By_Url(self, video_url, return_bytes=0, chromedriver_path=None):
        """(DEPRECRATED)
            Gets the source url of a given url for a tiktok

            video_url - the url of the video
            return_bytes - 0 is just the url, 1 is the actual video bytes
            chromedriver_path - path to your chrome driver executable 
        """
        raise Exception("Deprecated. Other Methods Work Better.")

    def get_Video_No_Watermark_ID(self, video_id, return_bytes=0, proxy=None):
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
        video_url_no_wm = "https://api2-16-h2.musical.ly/aweme/v1/play/?video_id={" \
                          "}&vr_type=0&is_play_url=1&source=PackSourceEnum_PUBLISH&media_type=4" \
            .format(video_data[pos+4:pos+36])
        if return_bytes == 0:
            return video_url_no_wm
        else:
            headers = {"User-Agent": "okhttp"}
            video_data_no_wm = requests.get(
                video_url_no_wm, params=None, headers=headers)
            return video_data_no_wm.content

    def get_Video_No_Watermark_Faster(self, video_url, return_bytes=0, proxy=None):
        """No Water Mark method, but may be faster

          :param video_url: The url of the video you want to download
          :param return_bytes: Set this to 1 if you want bytes, set it to 0 for url.
          :param proxy: The IP of your proxy.
        """
        video_id = video_url.split("/video/")[1].split("?")[0]
        return self.get_Video_No_Watermark_ID(video_id, return_bytes, proxy=proxy)

    def get_Video_No_Watermark(self, video_url, return_bytes=0, proxy=None):
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
            r = requests.get(contentURL, headers={"method": "GET",
                                                  "accept-encoding": "gzip, deflate, br",
                                                  'accept-Language': 'en-US,en;q=0.9',
                                                  'Range': 'bytes=0-200000',
                                                  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
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

            cleanVideo = "https://api2-16-h2.musical.ly/aweme/v1/play/?video_id=" + \
                key + "&line=0&ratio=default&media_type=4&vr_type=0"

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

    def __format_proxy(self, proxy):
        """
          Formats the proxy object
        """
        if proxy != None:
            return {
                'http': proxy,
                'https': proxy
            }
        else:
            return None

    def __get_js(self, proxy=None):
        return requests.get("https://sf16-muse-va.ibytedtos.com/obj/rc-web-sdk-gcs/acrawler.js", proxies=self.__format_proxy(proxy)).text

    def __format_new_params__(self, parm):
        return parm.replace("/", "%2F").replace(" ", "+").replace(";", "%3B")

    def __add_new_params__(self):
        return "aid=1988&app_name=tiktok_web&device_platform=web&referer=&user_agent={}&cookie_enabled=true".format(self.__format_new_params__(self.userAgent)) + \
            "&screen_width={}&screen_height={}&browser_language={}&browser_platform={}&browser_name={}&browser_version={}".format(self.width, self.height, self.browser_language, self.browser_platform, self.browser_name, self.browser_version) + \
            "&browser_online=true&timezone_name={}&priority_region=&appId=1233&appType=m&isAndroid=false&isMobile=false".format(self.timezone_name) + \
            "&isIOS=false&OS=windows&did=" + \
            str(random.randint(10000, 999999999))

