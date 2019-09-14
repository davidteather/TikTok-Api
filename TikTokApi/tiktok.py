class TikTokapi:

    def __init__(self, browsermobDirectory, headless=False):
        # Imports
        print("New class reference, finding valid signature. This might take a minute.")
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
        for element in data['log']['entries']:
            if "https://m.tiktok.com/share/item/list?" in element['request']['url'] or "https://www.tiktok.com/share/item/list?" in element['request']['url']:
                print("Found signature, continuing.")
                self.signature = element['request']['queryString'][6]['value']

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

    # Show the user the trending hashtags

    def get_trending_hashtags(self):
        # Returns the trending hashtags from /en/trending
        return self.hashtag

    # Allows the user to search by a specific hashtag
    def search_by_hashtag(self, hashtag, count=10):
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

        # Assigns signature and hashtagID
        for element in data['log']['entries']:
            if "https://m.tiktok.com/share/item/list?" in element['request']['url'] or "https://www.tiktok.com/share/item/list?" in element['request']['url']:
                hashtagId = element['request']['queryString'][1]['value']
                self.signature = element['request']['queryString'][6]['value']

        driver.quit()

        response = []

        if hashtagId != None:
            while True:
                try:
                    var = data['body']['hasMore']
                    hasMore = True
                except:
                    hasMore = False
                    cookie = ''.join(random.choice(
                        string.ascii_uppercase + string.digits) for _ in range(40))

                    url = "https://www.tiktok.com/share/item/list?secUid=&id=" + hashtagId + "&type=3&count=" + \
                            str(count - len(response)) + "&minCursor=-1&maxCursor=0&_signature=" + \
                            self.signature + "&shareUid="

                    headers = {"authority": "www.tiktok.com",
                               "method": "GET",
                               "path": url.split("https://www.tiktok.com")[1],
                               "scheme": "https",
                               "accept": "application/json, text/plain, */*",
                               "accept-encoding": "gzip, deflate, br",
                               "accept-language": "en-US,en;q=0.9",
                               "cache-control": "no-cache",
                               "cookie": cookie,
                               "referer": "https://www.tiktok.com/tag/" + hashtag + "?langCountry=en",
                               "sec-fetch-mode": "cors",
                               "sec-fetch-site": "same-origin",
                               "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"}

                    r = requests.get(url, headers=headers)

                    data = r.json()
                    if data["statusCode"] == 0:
                        for tiktok in data["body"]["itemListData"]:
                            response.append(tiktok)

                if hasMore == True:
                    if count > len(response) and str(data['body']['hasMore']) == "True":
                        cookie = ''.join(random.choice(
                            string.ascii_uppercase + string.digits) for _ in range(40))

                        url = "https://www.tiktok.com/share/item/list?secUid=&id=" + hashtagId + "&type=3&count=" + \
                            str(count - len(response)) + "&minCursor=-1&maxCursor=" + data['body']['maxCursor'] + "&_signature=" + \
                            self.signature + "&shareUid="

                        headers = {"authority": "www.tiktok.com",
                                   "method": "GET",
                                   "path": url.split("https://www.tiktok.com")[1],
                                   "scheme": "https",
                                   "accept": "application/json, text/plain, */*",
                                   "accept-encoding": "gzip, deflate, br",
                                   "accept-language": "en-US,en;q=0.9",
                                   "cache-control": "no-cache",
                                   "cookie": cookie,
                                   "referer": "https://www.tiktok.com/tag/" + hashtag + "?langCountry=en",
                                   "sec-fetch-mode": "cors",
                                   "sec-fetch-site": "same-origin",
                                   "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"}
                        r = requests.get(url, headers=headers)

                        data = r.json()

                        if data["statusCode"] == 0:
                            for tiktok in data["body"]["itemListData"]:
                                response.append(tiktok)

                    else:
                        return response

        else:
            raise Exception('Unable to locate the hashtag ID')

    # Gets trending
    def trending(self, count=10, verbose=0):
        import requests

        while True:
            url = "https://m.tiktok.com/share/item/list?id=&type=5&count=" + \
                str(count) + "&minCursor=0&maxCursor=0&_signature=" + \
                self.signature
            r = requests.get(url, headers={"authority": "m.tiktok.com", "method": "GET", "path": url.split("https://m.tiktok.com")[0], "scheme": "https", "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
                                           "accept-encoding": "gzip, deflate, br", "accept-language": "en-US,en;q=0.9", "cache-control": "max-age=0", "upgrade-insecure-requests": "1",
                                           "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"})

            data = r.json()
            response = []

            if data["statusCode"] != 0:
                if verbose == 1:
                    print("Invalid Signature Retrying")
            else:
                for tiktok in data["body"]["itemListData"]:
                    response.append(tiktok)
                while True:
                    if count > len(response) and str(data['body']['hasMore']) == "True":
                        url = "https://m.tiktok.com/share/item/list?id=&type=5&count=" + \
                            str(count - len(response)) + "&minCursor=0&maxCursor=" + \
                            data['body']['maxCursor'] + \
                            "&_signature=" + self.signature

                        r = requests.get(url, headers={"authority": "m.tiktok.com", "method": "GET", "path": url.split("https://m.tiktok.com")[0], "scheme": "https", "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
                                                       "accept-encoding": "gzip, deflate, br", "accept-language": "en-US,en;q=0.9", "cache-control": "max-age=0", "upgrade-insecure-requests": "1",
                                                       "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"})
                        data = r.json()
                        if data["statusCode"] == 0:
                            for tiktok in data["body"]["itemListData"]:
                                response.append(tiktok)
                    else:
                        return response

    # Gets a user's post
    def userPosts(self, id, count=10, verbose=0):
        import requests
        while True:
            url = "https://m.tiktok.com/share/item/list?id=" + str(id) + "&type=1&count=" + \
                str(count) + "&minCursor=0&maxCursor=0&_signature=" + \
                self.signature
            r = requests.get(url, headers={"authority": "m.tiktok.com", "method": "GET", "path": url.split("https://m.tiktok.com")[0], "scheme": "https", "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
                                           "accept-encoding": "gzip, deflate, br", "accept-language": "en-US,en;q=0.9", "cache-control": "max-age=0", "upgrade-insecure-requests": "1",
                                           "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"})

            data = r.json()
            response = []

            if data["statusCode"] != 0:
                if verbose == 1:
                    print("Invalid Signature Retrying")
            else:
                for tiktok in data["body"]["itemListData"]:
                    response.append(tiktok)
                while True:
                    if count > len(response) and str(data['body']['hasMore']) == "True":
                        url = "https://m.tiktok.com/share/item/list?id=" + str(id) + "&type=1&count=" + \
                            str(count - len(response)) + "&minCursor=0&maxCursor=" + data['body']['maxCursor'] + "&_signature=" + \
                            self.signature
                        var = True
                        while var:

                            r = requests.get(url, headers={"authority": "m.tiktok.com", "method": "GET", "path": url.split("https://m.tiktok.com")[0], "scheme": "https", "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
                                                           "accept-encoding": "gzip, deflate, br", "accept-language": "en-US,en;q=0.9", "cache-control": "max-age=0", "upgrade-insecure-requests": "1",
                                                           "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"})

                            data = r.json()

                            if data["statusCode"] == 0:
                                for tiktok in data["body"]["itemListData"]:
                                    response.append(tiktok)
                                var = False

                            else:
                                if verbose == 1:
                                    print("Invalid Signature Retrying")

                    else:
                        return response
