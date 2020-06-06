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
        if debug:
            print("Class initialized")

        self.userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36"
        self.referrer = "https://www.tiktok.com/trending?lang="
        #self.referrer = "https://www.tiktok.com/@ondymikula/video/6757762109670477061"

    #
    # Method that retrives data from the api
    #
    def getData(self, api_url, signature, userAgent, language='en'):
        url = api_url + \
            "&_signature=" + signature
        r = requests.get(url, headers={"method": "GET",
                                       "accept-encoding": "gzip, deflate, br",
                                       "referrer": self.referrer + language,
                                       "user-agent": userAgent,
                                       'accept': 'application/json, text/plain, */*',
                                       'dnt': '1',
                                       'cache-control': 'no-cache',
                                       'scheme': 'https',
                                       'authority': 'm.tiktok.com',
                                       'origin': 'https://www.tiktok.com',
                                       'pragma': 'no-cache',
                                       'sec-fetch-dest': 'empty',
                                       'sec-fetch-mode': 'cors',
                                       'sec-fetch-site': 'same-site',
                                       'path': url.split("tiktok.com")[1],
                                       'accept-language': 'en-US,en;q=0.9'
                                       })
        try:
            return r.json()
        except:
            print("Converting response to JSON failed response is below (probably empty)")
            print(r.text)
            raise Exception('Invalid Response')

    #
    # Method that retrives data from the api
    #

    def getBytes(self, api_url, signature, userAgent):
        url = api_url + \
            "&_signature=" + signature
        r = requests.get(url, headers={"method": "GET",
                                       "accept-encoding": "gzip, deflate, br",
                                       "referrer": self.referrer,
                                       "user-agent": userAgent,
                                       })
        return r.content

    #
    # Gets trending Tiktoks
    #

    def trending(self, count=30, language='en'):
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
            b = browser(api_url, language=language)
            res = self.getData(api_url, b.signature,
                               b.userAgent, language=language)

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
    def userPosts(self, userID, secUID, count=30, language='en'):
        response = []
        maxCount = 99
        maxCursor = 0

        while len(response) < count:
            if count < maxCount:
                realCount = count
            else:
                realCount = maxCount

            api_url = "https://m.tiktok.com/api/item_list/?count={}&id={}&type=1&secUid={}&maxCursor={}&minCursor=0&sourceType=8&appId=1233&region=US&language={}&verifyFp=".format(
                str(realCount), str(userID), str(secUID), str(maxCursor), str(language))
            b = browser(api_url)
            res = self.getData(api_url, b.signature, b.userAgent)

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

    def byUsername(self, username, count=30):
        data = self.getUserObject(username)
        return self.userPosts(data['id'], data['secUid'], count=count)

    #
    # Gets tiktoks by music ID
    #
    # id - the sound ID
    #

    def bySound(self, id, count=30, language='en'):
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
            b = browser(api_url)
            res = self.getData(api_url, b.signature, b.userAgent)

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
    def getMusicObject(self, id, language='en'):
        api_url = "https://m.tiktok.com/api/music/detail/?musicId={}&language={}&verifyFp=".format(
            str(id), language)
        b = browser(api_url)
        return self.getData(api_url, b.signature, b.userAgent)

    #
    # Gets tiktoks by hashtag
    #

    def byHashtag(self, hashtag, count=30, language='en'):
        id = self.getHashtagObject(hashtag)['challengeInfo']['challenge']['id']
        response = []
        maxCount = 99
        maxCursor = 0

        while len(response) < count:
            if count < maxCount:
                realCount = count
            else:
                realCount = maxCount

            api_url = "https://m.tiktok.com/share/item/list?secUid=&id={}&type=3&count={}&minCursor=0&maxCursor={}&shareUid=&lang={}&verifyFp=".format(
                str(id), str(realCount), str(maxCursor), language)
            b = browser(api_url)
            res = self.getData(api_url, b.signature, b.userAgent)

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

    def getHashtagObject(self, hashtag, language='en'):
        api_url = "https://m.tiktok.com/api/challenge/detail/?verifyFP=&challengeName={}&language={}".format(
            str(hashtag.encode('utf-8'))[2:-1].replace("\\x", "%").upper(), language)
        b = browser(api_url)
        return self.getData(api_url, b.signature, b.userAgent)

    #
    # Discover page, consists challenges (hashtags)
    #

    def discoverHashtags(self):
        api_url = "https://m.tiktok.com/node/share/discover?noUser=1&userCount=30&scene=0&verifyFp="
        b = browser(api_url)
        return self.getData(api_url, b.signature, b.userAgent)['body'][1]['exploreList']

    #
    # Discover page, consists of music
    #

    def discoverMusic(self):
        api_url = "https://m.tiktok.com/node/share/discover?noUser=1&userCount=30&scene=0&verifyFp="
        b = browser(api_url)
        return self.getData(api_url, b.signature, b.userAgent)['body'][2]['exploreList']
    #
    # Gets a user object for id and secUid
    #

    def getUserObject(self, username, language='en'):
        return self.getUser(username, language)['userInfo']['user']

    def getUser(self, username, language='en'):
        api_url = "https://m.tiktok.com/api/user/detail/?uniqueId={}&language={}&verifyFp=".format(
            username, language)
        b = browser(api_url)
        return self.getData(api_url, b.signature, b.userAgent)

    #
    # Downloads video from TikTok using a TikTok object
    #

    def get_Video_By_TikTok(self, data):
        api_url = data['video']['downloadAddr']
        return self.get_Video_By_DownloadURL(api_url)

    #
    # Downloads video from TikTok using download url in a tiktok object
    #
    def get_Video_By_DownloadURL(self, download_url):
        b = browser(download_url)
        return self.getBytes(download_url, b.signature, b.userAgent)

    #
    # Gets the source url of a given url for a tiktok
    #
    # video_url - the url of the video
    # return_bytes - 0 is just the url, 1 is the actual video bytes
    # chromedriver_path - path to your chrome driver executible
    #

    def get_Video_By_Url(self, video_url, return_bytes=0, chromedriver_path=None):
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
    def get_Video_No_Watermark(self, video_url, return_bytes=1):
        r = requests.get(video_url, headers={"method": "GET",
                                             "accept-encoding": "utf-8",
                                             "user-agent": self.userAgent
                                             })

        data = r.text.split("\"contentUrl\":\"")
        if len(data) > 1:
            contentURL = data[1].split("\"")[0]

            r = requests.get(contentURL, headers={"method": "GET",
                                                  "accept-encoding": "gzip, deflate, br",
                                                  'accept-Language': 'en-US,en;q=0.9',
                                                  'Range': 'bytes=0-200000',
                                                  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                                                  "user-agent": self.userAgent
                                                  })

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

            b = browser(cleanVideo, find_redirect=True)
            
            if return_bytes == 0:
                return b.redirect_url
            else:
                r = requests.get(b.redirect_url)
                return r.content