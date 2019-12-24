class TikTokapi:
    #
    # The TikTokapi class initial function
    #
    def __init__(self, browsermobDirectory, headless=False):
        # Imports
        self.referer = "https://www.tiktok.com/@ondymikula/video/6757762109670477061"
        from browsermobproxy import Server
        import psutil
        import json
        import time
        import json
        from selenium import webdriver

        self.browsermobDirectory = browsermobDirectory
        # Kills any browsermob-proxy
        for proc in psutil.process_iter():
            # check whether the process name matches
            if proc.name() == "browsermob-proxy":
                proc.kill()

        dictf = {'port': 8090}
        self.server = Server(
            path=browsermobDirectory, options=dictf)
        # "browsermob-proxy/bin/browsermob-proxy"
        self.server.start()
        time.sleep(1)
        self.proxy = self.server.create_proxy()
        time.sleep(1)

        # Creates FF profile

        chromeProfile = webdriver.ChromeOptions()
        chromeProfile.add_argument("--disable-automation")
        chromeProfile.add_argument("--no-sandbox")
        chromeProfile.add_argument('--disable-extensions')
        chromeProfile.add_argument('--profile-directory=Default')
        chromeProfile.add_argument("--incognito")
        chromeProfile.add_argument("--disable-plugins-discovery")
        chromeProfile.add_argument("--start-maximized")
        chromeProfile.add_argument("--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1")
        chromeProfile.add_experimental_option('useAutomationExtension', False)
        chromeProfile.add_experimental_option(
            "excludeSwitches", ["enable-automation"])
        chromeProfile.add_argument(
            "--proxy-server={0}".format(self.proxy.proxy))
        # chromeProfile.add_experimental_option("mobileEmulation", {"deviceName": "Galaxy S5"})

        if headless == True:
            chromeProfile.add_argument('headless')
        self.driver = webdriver.Chrome(chrome_options=chromeProfile)
        self.driver.set_window_size(1920, 1080)

        # Records FF Har
        self.proxy.new_har("list")
        self.driver.delete_all_cookies()
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => false});")
        self.driver.get("https://www.tiktok.com/en/trending")
        data = self.proxy.har
        self.signature = "VIm6dAAgEBardkWLNbDzilSJDWAAAlc"

        # Get Trending hashtags
        hashtags = self.driver.find_elements_by_xpath(
            '//h3[@class="_list_item_title"]/a')
        hashtagArray = []
        for hashtag in hashtags:
            hashtagArray.append(hashtag.get_attribute('title'))

        self.hashtag = hashtagArray
        self.headless = headless
        self.browsermobDirectory = browsermobDirectory


    # Quits the browser
    def quit_browser(self):
        self.driver.quit()


    #
    # Show the user the trending hashtags
    #
    def get_trending_hashtags(self):
        # Returns the trending hashtags from /en/trending
        return self.hashtag

    #
    # Allows the user to search by a specific hashtag
    #
    # hastag - the hashtag you want to search by
    # count - the amount of results you want
    #

    def search_by_hashtag(self, hashtag, count=10, verbose=0):
        import requests
        from browsermobproxy import Server
        import psutil
        import json
        import time
        import json
        from selenium import webdriver
        from selenium.webdriver.firefox.options import Options

        import string

        import random

        hashtagId = None
        tries = 0

        while hashtagId == None:
            if tries >= 10:
                raise Exception("Could not locate hashtag ID: Tried " + str(tries) + " times")
            # Browsermob-capture
            time.sleep(2)
            self.proxy.new_har("list")
            self.driver.get("https://www.tiktok.com/tag/" + hashtag + "?langCountry=en")
            data = self.proxy.har


            for element in data['log']['entries']:
                if hashtagId != None:
                    break
                elif "https://m.tiktok.com/share/item/list?" in element['request']['url'] or "https://www.tiktok.com/share/item/list?" in element['request']['url']:
                    for name in element['request']['queryString']:
                        if name['name'] == "id" and name['value'] != "":
                            hashtagId = name['value']
                            break

            tries += 1

        response = []
        if hashtagId != None:
            while True:
                hashtagSignature = "yZ-7VgAgEBu8bjAI0DLgHMmfukAAJRs"
                url = "https://m.tiktok.com/share/item/list?secUid=&id=" + hashtagId + "&type=3&count=30&minCursor=0&maxCursor=0&shareUid=&_signature=" + hashtagSignature
                headers = {"method": "GET",
                           "accept-encoding": "gzip, deflate, br",
                           "Referer": self.referer,
                           "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1"}
                r = requests.get(url, headers=headers)

                data = r.json()

                if data["statusCode"] == 0:
                    maxCursor = data['body']['maxCursor']
                    for tiktok in data["body"]["itemListData"]:
                        if count > len(response):
                            response.append(tiktok)
                        else:
                            return response

                    if len(response) == count:
                        return response

                    raise Exception('Rate Limit: This function only currently supports 30 TikToks.')

                    while True:
                        try:
                            if count > len(response):
                                data['body']['hasMore'] == True
                                url = "https://m.tiktok.com/share/item/list?secUid=&id=" + hashtagId + "&type=3&count=30&minCursor=0&maxCursor=" + str(maxCursor) + "&shareUid=&_signature=" + hashtagSignature

                                headers = {"method": "GET",
                                           "accept-encoding": "gzip, deflate, br",
                                           "Referer": self.referer,
                                           "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1"}

                                r = requests.get(url, headers=headers)

                                data = r.json()

                                if data["statusCode"] == 0:
                                    maxCursor = data['body']['maxCursor']
                                    for tiktok in data["body"]["itemListData"]:
                                        if count > len(response):
                                            response.append(tiktok)
                                        else:
                                            return response

                            else:
                                return response

                        except:

                            url = "https://m.tiktok.com/share/item/list?secUid=&id=" + hashtagId + "&type=3&count=30&minCursor=0&maxCursor=" + str(maxCursor) + "&shareUid=&_signature=" + hashtagSignature

                            headers = {"method": "GET",
                                       "accept-encoding": "gzip, deflate, br",
                                       "Referer": self.referer,
                                       "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1"}

                            r = requests.get(url, headers=headers)

                            data = r.json()
                            continue

        else:
            raise Exception('Unable to locate the hashtag ID')

    #
    # Gets trending results
    #
    # count - the number of results to display
    # verbose - 0 or 1, 1 is intense logging
    #

    def trending(self, count=10, verbose=0):
        import requests

        while True:
            url = "https://www.tiktok.com/share/item/list?secUid=&id=&type=5&count=30&minCursor=0&maxCursor=0&shareUid=&_signature=" + self.signature
            r = requests.get(url, headers={"method": "GET",
                                           "accept-encoding": "gzip, deflate, br",
                                           "Referer": self.referer,
                                           "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1"}
                             )

            data = r.json()
            response = []
            if data["statusCode"] == 0:
                maxCursor = data['body']['maxCursor']
                for tiktok in data["body"]["itemListData"]:
                    if count > len(response):
                        response.append(tiktok)
                    else:
                        return response
                while True:
                    try:
                        if count > len(response):
                            var = data['body']['hasMore']
                            maxCursor = data['body']['maxCursor']

                            url = "https://www.tiktok.com/share/item/list?secUid=&id=&type=5&count=30&minCursor=0&maxCursor=" + str(maxCursor) + "&shareUid=&_signature=" + self.signature

                            r = requests.get(url, headers={"method": "GET",
                                                           "accept-encoding": "gzip, deflate, br",
                                                           "Referer": self.referer,
                                                           "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1"})
                            data = r.json()
                            if data["statusCode"] == 0:
                                for tiktok in data["body"]["itemListData"]:
                                    if count > len(response):
                                        response.append(tiktok)
                                    else:
                                        return response
                        else:
                            return response
                    except:
                        url = "https://www.tiktok.com/share/item/list?secUid=&id=&type=5&count=30&minCursor=0&maxCursor=" + str(maxCursor) + "&shareUid=&_signature=" + self.signature

                        r = requests.get(url, headers={"method": "GET",
                                                       "accept-encoding": "gzip, deflate, br",
                                                       "Referer": self.referer,
                                                       "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1"})

                        data = r.json()
                        continue

    #
    # Gets a user's post
    #
    # count - the count of results
    # verbose - 1 is high logging
    #

    def userPosts(self, id, secUid, count=10, verbose=0):
        import requests
        while True:

            # I feel like this signature won't work in a few hours
            userpostSig = "T.EPYAAgEBM6AIQ-UrnWvU.xDnAABIP"


            url = "https://m.tiktok.com/share/item/list?secUid=" + str(secUid) + "&id=" + str(id) + "&type=1&count=30&minCursor=0&maxCursor=0&shareUid=&_signature=" + userpostSig
            r = requests.get(url, headers={"method": "GET",
                                           "accept-encoding": "gzip, deflate, br",
                                           "Referer": self.referer,
                                           "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1"})

            data = r.json()
            response = []

            if data["statusCode"] != 0:
                if verbose == 1:
                    print("Invalid Signature Retrying")
            else:
                maxCursor = data['body']['maxCursor']
                for tiktok in data["body"]["itemListData"]:
                    if count > len(response):
                        response.append(tiktok)
                    else:
                        return response
                
                if len(response) == count:
                    return response

                raise Exception('Rate Limit: This function only currently supports 30 TikToks.')
                while True:
                    try:
                        if count > len(response) and str(data['body']['hasMore']) == "True":
                            url = "https://m.tiktok.com/share/item/list?id=" + str(id) + "&type=1&count=" + \
                                str(count - len(response)) + "&minCursor=0&maxCursor=" + maxCursor + "&_signature=" + \
                                userpostSig
                            maxCursor = data['body']['maxCursor']

                            r = requests.get(url, headers={"method": "GET",
                                                           "accept-encoding": "gzip, deflate, br",
                                                           "Referer": self.referer,
                                                           "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1"})

                            data = r.json()

                            if data["statusCode"] == 0:
                                for tiktok in data["body"]["itemListData"]:
                                    response.append(tiktok)

                            else:
                                if verbose == 1:
                                    print(
                                        "Invalid Signature Retrying")

                        else:
                            return response

                    except:
                        url = "https://m.tiktok.com/share/item/list?id=" + str(id) + "&type=1&count=" + \
                            str(count - len(response)) + "&minCursor=0&maxCursor=" + maxCursor + "&_signature=" + \
                            self.signature

                        r = requests.get(url, headers={"method": "GET",
                                                       "accept-encoding": "gzip, deflate, br",
                                                       "Referer": self.referer,
                                                       "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1"})

                        data = r.json()

                        continue

    #
    # Gets the source url of a given url for a tiktok
    #
    # video_url - the url of the video
    # return_bytes - 0 is just the url, 1 is the actual video bytes
    #

    def get_Video_By_Url(self, video_url, return_bytes=0):
        # Imports
        import requests
        import time
        import browsermobproxy
        from browsermobproxy import Server
        import psutil
        import json
        from bs4 import BeautifulSoup

        self.driver.get(video_url)
        time.sleep(5)
        
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        data = json.loads(soup.find_all('script', attrs={"id": "videoObject"})[0].text)

        if return_bytes == 0:
            return data['contentUrl']
        else:
            r = requests.get(data['contentUrl'])
            return r.content

    #
    # returns videos related to given video
    #

    def get_Related_Videos(self, video_url):
        # Imports
        import requests
        import time
        import browsermobproxy
        from browsermobproxy import Server
        import psutil
        import json
        from selenium import webdriver
        from selenium.webdriver.firefox.options import Options

        videoID = video_url.split("/")[5]
        found = False
        tries = 0
        while not found:
            if tries >= 50:
                raise Exception("Tried 50 times could not find video JSON.")
            else:
                url = "https://m.tiktok.com/share/item/list?secUid=&id=" + videoID + "&type=0&count=10&minCursor=0&maxCursor=0&shareUid=&_signature=" + self.signature

                r = requests.get(url, headers={"method": "GET",
                                                "accept-encoding": "gzip, deflate, br",
                                                "Referer": self.referer,
                                                "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1"})

                data = r.json()
                if data['statusCode'] == 0:
                    found = True
                    break
                tries += 1

        return data['body']['itemListData']