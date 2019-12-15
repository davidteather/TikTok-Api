class TikTokapi:
    #
    # The TikTokapi class initial function
    #
    def __init__(self, browsermobDirectory, headless=False):
        # Imports
        print("New class reference, finding valid signature. This might take a minute.")
        self.referer = "https://www.tiktok.com/@ondymikula/video/6757762109670477061"
        from browsermobproxy import Server
        import psutil
        import json
        import time
        import json
        from selenium import webdriver
        from selenium.webdriver.firefox.options import Options

        # Kills any browsermob-proxy
        for proc in psutil.process_iter():
            # check whether the process name matches
            if proc.name() == "browsermob-proxy":
                proc.kill()

        dict = {'port': 8090}
        server = Server(
            path=browsermobDirectory, options=dict)
        # "browsermob-proxy/bin/browsermob-proxy"
        server.start()
        time.sleep(1)
        proxy = server.create_proxy()
        time.sleep(1)

        # Creates FF profile
        profile = webdriver.FirefoxProfile()
        selenium_proxy = proxy.selenium_proxy()
        profile.set_proxy(selenium_proxy)
        options = Options()
        if headless == True:
            options.headless = True
        driver = webdriver.Firefox(firefox_profile=profile, options=options)

        # Records FF Har
        proxy.new_har("list")
        driver.get("https://www.tiktok.com/en/trending")
        data = proxy.har
        self.signature = "VIm6dAAgEBardkWLNbDzilSJDWAAAlc"

        # Get Trending hashtags
        hashtags = driver.find_elements_by_xpath(
            '//h3[@class="_list_item_title"]/a')
        hashtagArray = []
        for hashtag in hashtags:
            hashtagArray.append(hashtag.get_attribute('title'))

        self.hashtag = hashtagArray
        self.headless = headless
        self.browsermobDirectory = browsermobDirectory

        server.stop()
        driver.quit()

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

        for proc in psutil.process_iter():
            # check whether the process name matches
            if proc.name() == "browsermob-proxy":
                proc.kill()

        dict = {'port': 8090}
        server = Server(
            path=self.browsermobDirectory, options=dict)
        # "browsermob-proxy/bin/browsermob-proxy"
        server.start()
        time.sleep(1)
        proxy = server.create_proxy()
        time.sleep(1)

        # Firefox selenium stuff
        profile = webdriver.FirefoxProfile()
        selenium_proxy = proxy.selenium_proxy()
        profile.set_proxy(selenium_proxy)
        options = Options()
        if self.headless == True:
            options.headless = True
        driver = webdriver.Firefox(firefox_profile=profile, options=options)

        # Browsermob-capture
        proxy.new_har("list")
        driver.get("https://www.tiktok.com/tag/" + hashtag + "?langCountry=en")
        data = proxy.har

        hashtagId = None

        for element in data['log']['entries']:
            if "https://m.tiktok.com/share/item/list?" in element['request']['url'] or "https://www.tiktok.com/share/item/list?" in element['request']['url']:
                for name in element['request']['queryString']:
                    if name['name'] == "id":
                        hashtagId = name['value']

                        print(hashtagId)
                    if name['name'] == "_signature":
                        self.signature = name['value'] 
                        print(self.signature)

        driver.quit()

        response = []

        if hashtagId != None:
            while True:
                url = "https://www.tiktok.com/share/item/list?secUid=&id=" + hashtagId + "&type=3&count=30&minCursor=0&maxCursor=0&shareUid=&_signature" + self.signature
                headers = {"method": "GET",
                           "accept-encoding": "gzip, deflate, br",
                           "Referer": self.referer,
                           "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1"}
                r = requests.get(url, headers=headers)

                data = r.json()
                print(data)

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
                                data['body']['hasMore'] == True
                                cookie = ''.join(random.choice(
                                    string.ascii_uppercase + string.digits) for _ in range(40))

                                url = "https://www.tiktok.com/share/item/list?secUid=&id=" + hashtagId + "&type=3&count=30&minCursor=0&maxCursor=" + str(maxCursor) + "&shareUid=&_signature" + self.signature

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
                            cookie = ''.join(random.choice(
                                string.ascii_uppercase + string.digits) for _ in range(40))

                            url = "https://www.tiktok.com/share/item/list?secUid=&id=" + hashtagId + "&type=3&count=30&minCursor=0&maxCursor=" + str(maxCursor) + "&shareUid=&_signature" + self.signature

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

    def userPosts(self, id, count=10, verbose=0):
        import requests
        while True:
            url = "https://m.tiktok.com/share/item/list?id=" + str(id) + "&type=1&count=" + \
                str(count) + "&minCursor=0&maxCursor=0&_signature=" + \
                self.signature
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
                    response.append(tiktok)
                while True:
                    try:
                        if count > len(response) and str(data['body']['hasMore']) == "True":
                            url = "https://m.tiktok.com/share/item/list?id=" + str(id) + "&type=1&count=" + \
                                str(count - len(response)) + "&minCursor=0&maxCursor=" + maxCursor + "&_signature=" + \
                                self.signature
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
        import json
        from selenium import webdriver
        from selenium.webdriver.firefox.options import Options

        # Gets the VideoID
        videoID = video_url.split("/video/")[1].split("?")[0]

        # Checks if they should determine the return_bytes
        if return_bytes == 0:
            # Creates FF profile
            profile = webdriver.FirefoxProfile()
            options = Options()
            profile.set_preference("media.volume_scale", "0.0")
            if self.headless == True:
                options.headless = True

            driver = webdriver.Firefox(
                firefox_profile=profile, options=options)

            driver.get("https://www.tiktok.com/node/video/playwm?id=" + videoID)
            time.sleep(3)

            url = driver.current_url
            driver.quit()

            return url
        else:
            # Creates FF profile
            profile = webdriver.FirefoxProfile()
            options = Options()
            profile.set_preference("media.volume_scale", "0.0")
            if self.headless == True:
                options.headless = True

            driver = webdriver.Firefox(
                firefox_profile=profile, options=options)

            driver.get("https://www.tiktok.com/node/video/playwm?id=" + videoID)
            time.sleep(3)

            url = driver.current_url
            driver.quit()

            r = requests.get(url)

            return r.content
