class TikTokapi:
    #
    # The TikTokapi class initial function
    #
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
        chromeProfile.add_experimental_option(
            "excludeSwitches", ["enable-automation"])
        chromeProfile.add_argument("--proxy-server={0}".format(self.proxy.proxy))
        chromeProfile.add_experimental_option("mobileEmulation", {"deviceName": "Galaxy S5"})

        if headless == True:
            chromeProfile.add_argument('headless')
        self.driver = webdriver.Chrome(chrome_options=chromeProfile)

        # Records FF Har
        self.proxy.new_har("list")
        self.driver.get("https://www.tiktok.com/en/trending")
        data = self.proxy.har
        for element in data['log']['entries']:
            if "https://m.tiktok.com/share/item/list?" in element['request']['url'] or "https://www.tiktok.com/share/item/list?" in element['request']['url']:
                print("Found signature, continuing.")

                for queryS in element['request']['queryString']:
                    if queryS['name'] == "_signature":
                        self.signature = queryS['value']
                        break


        self.cookieString = ""
        for cookie in self.driver.get_cookies():
            self.cookieString = self.cookieString + cookie['name'] + "=" + cookie['value'] + "; "

        self.cookieString = self.cookieString[:-2]

        # Get Trending hashtags
        hashtags = self.driver.find_elements_by_xpath(
            '//h3[@class="_list_item_title"]/a')
        hashtagArray = []
        for hashtag in hashtags:
            hashtagArray.append(hashtag.get_attribute('title'))

        self.hashtag = hashtagArray
        self.headless = headless
        self.browsermobDirectory = browsermobDirectory


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
        # Browsermob-capture
        proxy.new_har("list")
        self.driver.get("https://www.tiktok.com/tag/" + hashtag + "?langCountry=en")
        data = proxy.har

        hashtagId = None

        # Assigns signature and hashtagID
        for element in data['log']['entries']:
            if "https://m.tiktok.com/share/item/list?" in element['request']['url'] or "https://www.tiktok.com/share/item/list?" in element['request']['url']:

                for queryS in element['request']['queryString']:
                    if queryS['name'] == "_signature":
                        self.signature = queryS['value']
                        break

        response = []

        if hashtagId != None:
            while True:
                cookie = ''.join(random.choice(
                    string.ascii_uppercase + string.digits) for _ in range(40))

                url = "https://m.tiktok.com/share/item/list?secUid=&id=" + hashtagId + "&type=3&count=" + \
                    str(count - len(response)) + "&minCursor=-1&maxCursor=0&_signature=" + \
                    self.signature + "&shareUid="

                self.driver.get(url)


                data = json.loads(self.driver.find_element_by_xpath("//pre").text)

                if data["statusCode"] == 0:
                    maxCursor = data['body']['maxCursor']
                    for tiktok in data["body"]["itemListData"]:
                        response.append(tiktok)

                    while True:
                        try:
                            if count > len(response):
                                data['body']['hasMore'] == True
                                cookie = ''.join(random.choice(
                                    string.ascii_uppercase + string.digits) for _ in range(40))

                                url = "https://m.tiktok.com/share/item/list?secUid=&id=" + str(hashtagId) + "&type=3&count=" + \
                                    str(count - len(response)) + "&minCursor=-1&maxCursor=" + str(maxCursor) + "&_signature=" + \
                                    self.signature + "&shareUid="

                                
                                self.driver.get(url)
                                data = json.loads(self.driver.find_element_by_xpath("//pre").text)

                                if data["statusCode"] == 0:
                                    maxCursor = data['body']['maxCursor']
                                    for tiktok in data["body"]["itemListData"]:
                                        response.append(tiktok)

                            else:
                                return response

                        except:
                            cookie = ''.join(random.choice(
                                string.ascii_uppercase + string.digits) for _ in range(40))

                            url = "https://m.tiktok.com/share/item/list?secUid=&id=" + str(hashtagId) + "&type=3&count=" + \
                                str(count - len(response)) + "&minCursor=-1&maxCursor=" + str(maxCursor) + "&_signature=" + \
                                self.signature + "&shareUid="

                            self.driver.get(url)
                            data = json.loads(self.driver.find_element_by_xpath("//pre").text)
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
        import string
        import time
        import json
        import random
        def cookie_generator(size=100, chars=string.ascii_uppercase + string.digits):
            return ''.join(random.choice(chars) for _ in range(size))

        while True:
            # TODO: Max Cursor Issue
            # https://m.tiktok.com/share/item/list?secUid=&id=&type=5&count=2&minCursor=0&maxCursor=1000005823613&shareUid=&_signature=0NDOfgAgEB-lIUUg-oc9StDQz2AAI10
            # https://m.tiktok.com/share/item/list?secUid=&id=&type=5&count=5&minCursor=0&maxCursor=0&shareUid=&_signature=Oo2r.AAgEBtPfCCiX9JspzqNquAAGc9
            url = "https://m.tiktok.com/share/item/list?secUid=&id=&type=5&count=" + str(count) + "&minCursor=0&maxCursor=0&shareUid=&_signature=" + self.signature

            # https://m.tiktok.com/share/item/list?secUid=&id=&type=5&count=5&minCursor=0&maxCursor=0&shareUid=&_signature=DGZaZAAgEB95l9E6AB.J8gxmW3AAFHi
                

            self.driver.get(url)
            data = json.loads(self.driver.find_element_by_xpath("//pre").text)
            print(data)

            response = []
            if data["statusCode"] == 0:
                maxCursor = data['body']['maxCursor']
                for tiktok in data["body"]["itemListData"]:
                    response.append(tiktok)
                print(response)
                while True:
                    try:
                        time.sleep(5)
                        print(count)
                        print(len(response))
                        if count > len(response):
                            var = data['body']['hasMore']
                            maxCursor = data['body']['maxCursor']
                            url = "https://m.tiktok.com/share/item/list?id=&type=5&count=" + \
                                str(count - len(response)) + "&minCursor=0&maxCursor=" + \
                                str(maxCursor) + \
                                "&_signature=" + self.signature

                            if count - len(response) > 5:
                                var = count - len(response)
                            else:
                                var = 5

                            url = "https://m.tiktok.com/share/item/list?secUid=&id=&type=5&count=" + str(var) + "&minCursor=0&maxCursor=" + str(maxCursor) + "&shareUid=&_signature=" + self.signature

                            self.driver.get(url)
                            data = json.loads(self.driver.find_element_by_xpath("//pre").text)
                            if data["statusCode"] == 0:
                                for tiktok in data["body"]["itemListData"]:
                                    response.append(tiktok)
                        else:
                            return response
                    except:

                        if count - len(response) > 5:
                                var = count - len(response)
                        else:
                            var = 5

                        url = "https://m.tiktok.com/share/item/list?id=&type=5&count=" + \
                            str(count - len(response)) + "&minCursor=0&maxCursor=" + \
                            str(maxCursor) + \
                            "&_signature=" + self.signature
                        
                        url = "https://m.tiktok.com/share/item/list?secUid=&id=&type=5&count=" + str(var) + "&minCursor=0&maxCursor=" + str(maxCursor) + "&shareUid=&_signature=" + self.signature

                        self.driver.get(url)
                        data = json.loads(self.driver.find_element_by_xpath("//pre").text)

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
            r = requests.get(url, headers={"authority": "m.tiktok.com", "method": "GET", "path": url.split("https://m.tiktok.com")[0], "scheme": "https", "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
                                           "accept-encoding": "gzip, deflate, br", "accept-language": "en-US,en;q=0.9", "cache-control": "max-age=0", "upgrade-insecure-requests": "1",
                                           "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"})

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

                            r = requests.get(url, headers={"authority": "m.tiktok.com", "method": "GET", "path": url.split("https://m.tiktok.com")[0], "scheme": "https", "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
                                                           "accept-encoding": "gzip, deflate, br", "accept-language": "en-US,en;q=0.9", "cache-control": "max-age=0", "upgrade-insecure-requests": "1",
                                                           "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"})

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

                        r = requests.get(url, headers={"authority": "m.tiktok.com", "method": "GET", "path": url.split("https://m.tiktok.com")[0], "scheme": "https", "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
                                                       "accept-encoding": "gzip, deflate, br", "accept-language": "en-US,en;q=0.9", "cache-control": "max-age=0", "upgrade-insecure-requests": "1",
                                                       "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"})

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
        from selenium import webdriver
        from selenium.webdriver.firefox.options import Options

        # Checks if they should determine the return_bytes
        if return_bytes == 0:
            self.proxy.new_har("vid")
            self.driver.get(video_url)
            data = self.proxy.har
            
            for entry in data['log']['entries']:
                try:
                    if "muscdn.com" in entry['response']['redirectURL']:
                        url = entry['response']['redirectURL']
                        break
                except:
                    continue

            return url
        else:
            self.proxy.new_har("vid")
            self.driver.get(video_url)
            data = self.proxy.har
            
            for entry in data['log']['entries']:
                try:
                    if "muscdn.com" in entry['response']['redirectURL']:
                        url = entry['response']['redirectURL']
                        break
                except:
                    continue

            r = requests.get(url)

            return r.content
