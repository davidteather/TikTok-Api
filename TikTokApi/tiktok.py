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

        self.referrer = "https://www.tiktok.com/@ondymikula/video/6756762109670477061"

    #
    # Method that retrives data from the api
    #
    def getData(self, api_url, signature, userAgent):
        url = api_url + \
            "&_signature=" + signature
        r = requests.get(url, headers={"method": "GET",
                                    "accept-encoding": "gzip, deflate, br",
                                    "Referer": self.referrer,
                                    "user-agent": userAgent,
                                    })           
        return r.json()


    #
    # Gets trending Tiktoks
    #
    def trending(self, count=30):
        api_url = "https://m.tiktok.com/api/item_list/?count={}&id=1&type=5&secUid=&maxCursor=1&minCursor=0&sourceType=12&appId=1233&verifyFp=".format(str(count))
        b = browser(api_url)

        return self.getData(api_url, b.signature, b.userAgent)['items']
        
    #
    # Gets a specific user's tiktoks
    #
    def userPosts(self, userID, secUID, count=30):
        api_url = "https://m.tiktok.com/api/item_list/?count={}&id={}&type=1&secUid={}&maxCursor=0&minCursor=0&sourceType=8&appId=1233&region=US&language=en&verifyFp=".format(str(count), str(userID), str(secUID))
        b = browser(api_url)
        return self.getData(api_url, b.signature, b.userAgent)['items']


    #
    # Gets tiktoks by music ID
    #
    # Note: not working for whatever reason. 
    #
    def bySound(self, id, count=30):
        api_url = "https://m.tiktok.com/share/item/list?secUid=&id={}&type=4&count={}&minCursor=0&maxCursor=0&shareUid=&lang=&verifyFp=".format(str(id), str(count))
        b = browser(api_url)
        return self.getData(api_url, b.signature, b.userAgent)['items']

    # 
    # Gets a user object for id and secUid
    #
    # Note: not working for whatever reason. 
    #
    def getUserObject(self, username):
        api_url = "https://m.tiktok.com/api/user/detail/?uniqueId={}&language=en&verifyFp=".format(username)
        b = browser(api_url)
        return self.getData(api_url, b.signature, b.userAgent)['userInfo']['user']

    
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
        data = json.loads(soup.find_all('script', attrs={"id": "videoObject"})[0].text)

        if return_bytes == 0:
            return data['contentUrl']
        else:
            r = requests.get(data['contentUrl'])
            return r.content