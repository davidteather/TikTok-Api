import asyncio
import pyppeteer
import random
import requests
from .browser import browser
from bs4 import BeautifulSoup
import time
import json
from selenium import webdriver


class TikTokApi:
    #
    # The TikTokapi class constructor
    #
    def __init__(self, debug=False):
        self.debug = debug
        if debug:
            print("Class initialized")

        self.userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.0 Safari/537.36)"
        # self.referrer = "https://www.tiktok.com/@ondymikula/video/6757762109670477061"

    #
    # Method that retrives data from the api
    #
    def getData(self, api_url, b, language='en', proxy=None):
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

    #
    # Method that retrives data from the api
    #

    def getBytes(self, api_url, b, proxy=None):
        url = api_url + \
            "&_verifyFp=" + b.verifyFp + \
            "&_signature=" + b.signature
        r = requests.get(url, headers={"method": "GET",
                                       "accept-encoding": "gzip, deflate, br",
                                       "referrer": b.referrer,
                                       "user-agent": b.userAgent,
                                       }, proxies=self.__format_proxy(proxy))
        return r.content

    #
    # Gets trending Tiktoks
    #

    def trending(self, count=30, language='en', proxy=None):
        response = []
        maxCount = 99
        maxCursor = 0

        while len(response) < count:
            if count < maxCount:
                realCount = count
            else:
                realCount = maxCount
            api_url = "https://m.tiktok.com/api/item_list/?count={}&id=1&type=5&secUid=&maxCursor={}&minCursor=0&sourceType=12&appId=1233&region=US&language={}&verifyFp=".format(
                str(realCount), str(maxCursor), str(language))
            b = browser(api_url, language=language, proxy=proxy)
            res = self.getData(api_url, b, proxy=proxy)

            for t in res['items']:
                response.append(t)

            if not res['hasMore']:
                print("TikTok isn't sending more TikToks beyond this point.")
                return response

            realCount = count-len(response)
            maxCursor = res['maxCursor']

        return response[:count]

    #
    # Gets a specific user's tiktoks
    #

    def userPosts(self, userID, secUID, count=30, language='en', region='US', proxy=None):
        response = []
        maxCount = 99
        maxCursor = 0

        while len(response) < count:
            if count < maxCount:
                realCount = count
            else:
                realCount = maxCount
            api_url = "https://m.tiktok.com/api/item_list/?count={}&id={}&type=1&secUid={}&maxCursor={}&minCursor=0&sourceType=8&appId=1233&region={}&language={}".format(
                str(realCount), str(userID), str(secUID), str(maxCursor), str(region), str(language))
            b = browser(api_url, proxy=proxy)
            res = self.getData(api_url, b, proxy=proxy)

            for t in res['items']:
                response.append(t)

            if not res['hasMore']:
                print("TikTok isn't sending more TikToks beyond this point.")
                return response

            realCount = count-len(response)
            maxCursor = res['maxCursor']

        return response[:count]

    #
    # Gets a specific user's tiktoks by username
    #

    def byUsername(self, username, count=30, proxy=None, language='en', region='US'):
        data = self.getUserObject(username, proxy=proxy)
        return self.userPosts(data['id'], data['secUid'], count=count, proxy=proxy, language=language, region=region)

    #
    # Gets a user's liked posts
    #
    def userLiked(self, userID, secUID, count=30, language='en', region='US', proxy=None):
        response = []
        maxCount = 99
        maxCursor = 0

        while len(response) < count:
            if count < maxCount:
                realCount = count
            else:
                realCount = maxCount

            api_url = "https://m.tiktok.com/api/item_list/?count={}&id={}&type=2&secUid={}&maxCursor={}&minCursor=0&sourceType=9&appId=1233&region={}&language={}&verifyFp=".format(
                str(realCount), str(userID), str(secUID), str(maxCursor), str(region), str(language))
            b = browser(api_url, proxy=proxy)
            res = self.getData(api_url, b, proxy=proxy)

            try:
                res['items']
            except:
                if self.debug:
                    print("Most Likely User's List is Empty")
                return []

            for t in res['items']:
                response.append(t)

            if not res['hasMore']:
                print("TikTok isn't sending more TikToks beyond this point.")
                return response

            realCount = count-len(response)
            maxCursor = res['maxCursor']

        return response[:count]

    #
    # Gets a specific user's likes by username
    #

    def userLikedbyUsername(self, username, count=30, proxy=None, language='en', region='US'):
        data = self.getUserObject(username, proxy=proxy)
        return self.userLiked(data['id'], data['secUid'], count=count, proxy=proxy, language=language, region=region)

    #
    # Gets tiktoks by music ID
    #
    # id - the sound ID
    #

    def bySound(self, id, count=30, language='en', proxy=None):
        response = []
        maxCount = 99
        maxCursor = 0

        while len(response) < count:
            if count < maxCount:
                realCount = count
            else:
                realCount = maxCount

            api_url = "https://m.tiktok.com/share/item/list?secUid=&id={}&type=4&count={}&minCursor=0&maxCursor={}&shareUid=&lang={}&verifyFp=".format(
                str(id), str(realCount), str(maxCursor), str(language))
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

    #
    # Gets the music object
    #
    def getMusicObject(self, id, language='en', proxy=None):
        api_url = "https://m.tiktok.com/api/music/detail/?musicId={}&language={}&verifyFp=".format(
            str(id), language)
        b = browser(api_url, proxy=proxy)
        return self.getData(api_url, b, proxy=proxy)

    #
    # Gets tiktoks by hashtag
    #

    def byHashtag(self, hashtag, count=30, language='en', proxy=None):
        id = self.getHashtagObject(hashtag)['challengeInfo']['challenge']['id']
        response = []
        maxCount = 99
        maxCursor = 0

        while len(response) < count:
            if count < maxCount:
                realCount = count
            else:
                realCount = maxCount

            api_url = "https://m.tiktok.com/share/item/list?secUid=&id={}&type=3&count={}&minCursor=0&maxCursor={}&shareUid=&lang={}".format(
                str(id), str(realCount), str(maxCursor), language)
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

    #
    # Gets tiktoks by hashtag (for use in byHashtag)
    #

    def getHashtagObject(self, hashtag, language='en', proxy=None):
        api_url = "https://m.tiktok.com/api/challenge/detail/?challengeName={}&language={}".format(
            str(hashtag.encode('utf-8'))[2:-1].replace("\\x", "%").upper(), language)
        b = browser(api_url, proxy=proxy)
        return self.getData(api_url, b, proxy=proxy)

    #
    # Get a tiktok object with another tiktok's id
    #
    def getRecommendedTikToksByVideoID(self, id, language='en', proxy=None):
        api_url = "https://m.tiktok.com/share/item/list?secUid=&id={}&type=0&count=24&minCursor=0&maxCursor=0&shareUid=&recType=3&lang={}&verifyFp=".format(
            id, language)
        b = browser(api_url, proxy=proxy)
        return self.getData(api_url, b, proxy=proxy)['body']

    #
    # Gets a tiktok object by ID
    #
    def getTikTokById(self, id, language='en', proxy=None):
        api_url = "https://m.tiktok.com/api/item/detail/?itemId={}&language={}&verifyFp=".format(
            id, language)
        b = browser(api_url, proxy=proxy)
        return self.getData(api_url, b, proxy=proxy)

    #
    # Get a tiktok object by url
    #
    def getTikTokByUrl(self, url, language='en', proxy=None):
        if "@" in url and "/video/" in url:
            post_id = url.split("/video/")[1].split("?")[0]
        else:
            raise Exception(
                "URL format not supported. Below is an example of a supported url.\nhttps://www.tiktok.com/@therock/video/6829267836783971589")

        return self.getTikTokById(post_id, language=language, proxy=proxy)

    #
    # Discover page, consists challenges (hashtags)
    #

    def discoverHashtags(self, proxy=None):
        api_url = "https://m.tiktok.com/node/share/discover?noUser=1&userCount=30&scene=0&verifyFp="
        b = browser(api_url, proxy=proxy)
        return self.getData(api_url, b, proxy=proxy)['body'][1]['exploreList']

    #
    # Discover page, consists of music
    #

    def discoverMusic(self, proxy=None):
        api_url = "https://m.tiktok.com/node/share/discover?noUser=1&userCount=30&scene=0&verifyFp="
        b = browser(api_url, proxy=proxy)
        return self.getData(api_url, b, proxy=proxy)['body'][2]['exploreList']
    #
    # Gets a user object for id and secUid
    #

    def getUserObject(self, username, language='en', proxy=None):
        return self.getUser(username, language, proxy=proxy)['userInfo']['user']

    #
    # Gets the full exposed user object
    #
    def getUser(self, username, language='en', proxy=None):
        api_url = "https://m.tiktok.com/api/user/detail/?uniqueId={}&language={}".format(
            username, language)
        b = browser(api_url, proxy=proxy)
        return self.getData(api_url, b, proxy=proxy)

    #
    # Get Suggested Users for given userID
    #
    def getSuggestedUsersbyID(self, count=30, userId='6745191554350760966', language='en', proxy=None):
        api_url = "https://m.tiktok.com/node/share/discover?noUser=0&pageId={}&userId={}&userCount={}&scene=15&verifyFp=".format(
            userId, userId, str(count))
        b = browser(api_url, proxy=proxy)

        res = []
        for x in self.getData(api_url, b, proxy=proxy)['body'][0]['exploreList']:
            res.append(x['cardItem'])
        return res[:count]

    #
    # Crawler for Suggested Users
    #
    def getSuggestedUsersbyIDCrawler(self, count=30, startingId='6745191554350760966', language='en', proxy=None):
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

    #
    # Get suggested hashtags given userID
    #
    def getSuggestedHashtagsbyID(self, count=30, userId='6745191554350760966', language='en', proxy=None):
        api_url = "https://m.tiktok.com/node/share/discover?noUser=0&pageId={}&userId={}&userCount={}&scene=15&verifyFp=".format(
            userId, userId, str(count))
        b = browser(api_url, proxy=proxy)

        res = []
        for x in self.getData(api_url, b, proxy=proxy)['body'][1]['exploreList']:
            res.append(x['cardItem'])
        return res[:count]

    #
    # Crawler for Suggested Hashtags
    #
    def getSuggestedHashtagsbyIDCrawler(self, count=30, startingId='6745191554350760966', language='en', proxy=None):
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

    #
    # Get suggested music by given userID
    #
    def getSuggestedMusicbyID(self, count=30, userId='6745191554350760966', language='en', proxy=None):
        api_url = "https://m.tiktok.com/node/share/discover?noUser=0&pageId={}&userId={}&userCount={}&scene=15&verifyFp=".format(
            userId, userId, str(count))
        b = browser(api_url, proxy=proxy)

        res = []
        for x in self.getData(api_url, b, proxy=proxy)['body'][2]['exploreList']:
            res.append(x['cardItem'])
        return res[:count]

    #
    # Crawler for Suggested Music
    #
    def getSuggestedMusicIDCrawler(self, count=30, startingId='6745191554350760966', language='en', proxy=None):
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

    #
    # Downloads video from TikTok using a TikTok object
    #

    def get_Video_By_TikTok(self, data, proxy=None):
        api_url = data['video']['downloadAddr']
        return self.get_Video_By_DownloadURL(api_url, proxy=proxy)

    #
    # Downloads video from TikTok using download url in a tiktok object
    #
    def get_Video_By_DownloadURL(self, download_url, proxy=None):
        b = browser(download_url, proxy=proxy)
        return self.getBytes(download_url, b, proxy=proxy)

    #
    # Gets the source url of a given url for a tiktok
    #
    # video_url - the url of the video
    # return_bytes - 0 is just the url, 1 is the actual video bytes
    # chromedriver_path - path to your chrome driver executible
    #

    def get_Video_By_Url(self, video_url, return_bytes=0, chromedriver_path=None):
        raise Exception("Deprecated. Other Methods Work Better.")
        if chromedriver_path != None:
            driver = webdriver.Chrome(executable_path=chromedriver_path)
        else:
            driver = webdriver.Chrome()
        driver.get(video_url)
        time.sleep(5)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        data = json.loads(soup.find_all(
            'script', attrs={"id": "videoObject"})[0].text)

        if return_bytes == 0:
            return data['contentUrl']
        else:
            r = requests.get(data['contentUrl'])
            return r.content

    #
    # No Water Mark
    #
    # TikTok Deprecated it see https://github.com/TufayelLUS/TikTok-Video-Downloader-PHP/issues/4
    #
    def get_Video_No_Watermark(self, video_url, return_bytes=1, proxy=None):
        r = requests.get(video_url, headers={"method": "GET",
                                             "accept-encoding": "utf-8",
                                             "user-agent": self.userAgent
                                             }, proxies=self.__format_proxy(proxy))

        data = r.text.split("\"contentUrl\":\"")
        if len(data) > 1:
            contentURL = data[1].split("\"")[0]

            r = requests.get(contentURL, headers={"method": "GET",
                                                  "accept-encoding": "gzip, deflate, br",
                                                  'accept-Language': 'en-US,en;q=0.9',
                                                  'Range': 'bytes=0-200000',
                                                  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                                                  "user-agent": self.userAgent
                                                  }, proxies=self.__format_proxy(proxy))

            tmp = r.text.split("vid:")
            if len(tmp) > 1:
                key = tmp[1].split("%")[0]

                if key[-1:] == ' ':
                    key = key[1:]

                if key[:1] == ' ':
                    key = key[:-1]

            else:
                key = ""

            cleanVideo = "https://api2.musical.ly/aweme/v1/playwm/?video_id=" + key

            b = browser(cleanVideo, find_redirect=True, proxy=proxy)

            if return_bytes == 0:
                return b.redirect_url
            else:
                r = requests.get(
                    b.redirect_url, proxies=self.__format_proxy(proxy))
                return r.content

    #
    # PRIVATE METHODS
    #

    #
    # Formats the proxy object
    #
    def __format_proxy(self, proxy):
        if proxy != None:
            return {
                'http': proxy,
                'https': proxy
            }
        else:
            return None
