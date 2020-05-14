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

        self.referrer = "https://www.tiktok.com/tag/jakefromstate?lang=en"

    #
    # Method that retrives data from the api
    #
    def getData(self, api_url, signature, userAgent):
        url = api_url + \
            "&_signature=" + signature
        r = requests.get(url, headers={"method": "GET",
                                       "accept-encoding": "gzip, deflate, br",
                                       "referrer": self.referrer,
                                       "user-agent": userAgent,
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

    def trending(self, count=30):
        response = []
        maxCount = 99
        maxCursor = 0

        while len(response) < count:
            if count < maxCount:
                realCount = count
            else:
                realCount = maxCount

            api_url = "https://m.tiktok.com/api/item_list/?count={}&id=1&type=5&secUid=&maxCursor={}&minCursor=0&sourceType=12&appId=1233&verifyFp=".format(
            str(realCount), str(maxCursor))
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
    # Gets a specific user's tiktoks
    #
    def userPosts(self, userID, secUID, count=30):
        response = []
        maxCount = 99
        maxCursor = 0

        while len(response) < count:
            if count < maxCount:
                realCount = count
            else:
                realCount = maxCount

            api_url = "https://m.tiktok.com/api/item_list/?count={}&id={}&type=1&secUid={}&maxCursor={}&minCursor=0&sourceType=8&appId=1233&region=US&language=en&verifyFp=".format(
            str(realCount), str(userID), str(secUID), str(maxCursor))
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

    def bySound(self, id, count=30):
        response = []
        maxCount = 99
        maxCursor = 0

        while len(response) < count:
            if count < maxCount:
                realCount = count
            else:
                realCount = maxCount

            api_url = "https://m.tiktok.com/share/item/list?secUid=&id={}&type=4&count={}&minCursor=0&maxCursor={}&shareUid=&lang=en&verifyFp=".format(
            str(id), str(realCount), str(maxCursor))
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
    def getMusicObject(self, id):
        api_url = "https://m.tiktok.com/api/music/detail/?musicId={}&language=en&verifyFp=".format(
            str(id))
        b = browser(api_url)
        return self.getData(api_url, b.signature, b.userAgent)

    #
    # Gets tiktoks by hashtag
    #

    def byHashtag(self, hashtag, count=30):
        id = self.getHashtagObject(hashtag)['challengeInfo']['challenge']['id']
        response = []
        maxCount = 99
        maxCursor = 0

        while len(response) < count:
            if count < maxCount:
                realCount = count
            else:
                realCount = maxCount

            api_url = "https://m.tiktok.com/share/item/list?secUid=&id={}&type=3&count={}&minCursor=0&maxCursor={}&shareUid=&lang=en&verifyFp=".format(
                str(id), str(realCount), str(maxCursor))
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

    def getHashtagObject(self, hashtag):
        api_url = "https://m.tiktok.com/api/challenge/detail/?verifyFP=&challengeName={}&language=en".format(
            str(hashtag))
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

    def getUserObject(self, username):
        api_url = "https://m.tiktok.com/api/user/detail/?uniqueId={}&language=en&verifyFp=".format(
            username)
        b = browser(api_url)
        return self.getData(api_url, b.signature, b.userAgent)['userInfo']['user']

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