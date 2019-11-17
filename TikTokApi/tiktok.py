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
        chromeProfile.add_argument("--no-sandbox")
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
            self.cookieString = self.cookieString + \
                cookie['name'] + "=" + cookie['value'] + "; "

        self.cookieString = self.cookieString[:-2]
        self.headless = headless
        self.browsermobDirectory = browsermobDirectory

    def quit_browser(self):
        self.driver.quit()

    #
    # Show the user the trending hashtags
    #

    def get_trending_hashtags(self):
        # Returns the trending hashtags from /en/trending
        return "Deprecated"

    #
    # Allows the user to search by a specific hashtag
    #
    # hastag - the hashtag you want to search by
    # count - the amount of results you want
    #

    def search_by_hashtag(self, hashtag, count=10, verbose=0):
        import requests
        import string
        import time
        import json
        import random

        self.driver.get("https://www.tiktok.com/tag/" +
                        hashtag.replace("#", "") + "?lang=en")
        time.sleep(2)

        self.driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        TikToks = self.driver.find_elements_by_xpath(
            "//div[@class='jsx-1410658769 video-feed-item']")
        TikToksUrls = self.driver.find_elements_by_xpath(
            "//div[@class='jsx-1410658769 video-feed-item']/div/div/div/a")
        TikToksViews = self.driver.find_elements_by_xpath(
            "//div[@class='jsx-1410658769 video-feed-item']/div/div/div/a/div/div/div/div/div/span")

        returnArr = []
        if count > len(TikToks):
            lower = len(TikToks)
        else:
            lower = count
        for i in range(0, lower):
            if "k" in TikToksViews[i].text.strip():
                likes = float(
                    TikToksViews[i].text.strip().replace("k", "")) * 1000
            elif "m" in TikToksViews[i].text.strip():
                likes = float(
                    TikToksViews[i].text.strip().replace("m", "")) * 1000000
            else:
                likes = TikToksViews[i].text.strip()

            returnArr.append({
                "link": TikToksUrls[i].get_attribute("href"),
                "author": TikToksUrls[i].get_attribute("href").split("/")[3],
                "likes": likes
            })

        return returnArr

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

        self.driver.get("https://www.tiktok.com/en/trending")
        time.sleep(2)

        self.driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        TikToks = self.driver.find_elements_by_xpath(
            "//div[@class='jsx-1410658769 video-feed-item']")
        TikToksUrls = self.driver.find_elements_by_xpath(
            "//div[@class='jsx-1410658769 video-feed-item']/div/div/div/a")
        TikToksViews = self.driver.find_elements_by_xpath(
            "//div[@class='jsx-1410658769 video-feed-item']/div/div/div/a/div/div/div/div/div/span")

        returnArr = []
        if count > len(TikToks):
            lower = len(TikToks)
        else:
            lower = count
        for i in range(0, lower):
            if "k" in TikToksViews[i].text.strip():
                likes = float(
                    TikToksViews[i].text.strip().replace("k", "")) * 1000
            elif "m" in TikToksViews[i].text.strip():
                likes = float(
                    TikToksViews[i].text.strip().replace("m", "")) * 1000000
            else:
                likes = TikToksViews[i].text.strip()

            returnArr.append({
                "link": TikToksUrls[i].get_attribute("href"),
                "author": TikToksUrls[i].get_attribute("href").split("/")[3],
                "likes": likes
            })

        return returnArr

    #
    # Gets the song of a tiktok url
    #
    # url - url of the tiktok
    #

    def get_song(self, url):
        import requests
        import string
        import time
        import json
        import random

        self.driver.get(url)
        time.sleep(2)

        return {
            "song_name": self.driver.find_element_by_xpath("//a[@tag='a']").text.strip(),
            "song_link": self.driver.find_element_by_xpath("//a[@class='jsx-1861775669 jsx-537314381']").get_attribute("href"),
        }

    #
    # Gets a user's post
    #
    # count - the count of results
    # verbose - 1 is high logging
    #

    def userPosts(self, username, count=10, verbose=0):
        import requests
        import string
        import time
        import json
        import random

        self.driver.get("https://www.tiktok.com/@" +
                        username.replace("@", "") + "?")
        time.sleep(2)

        self.driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        TikToks = self.driver.find_elements_by_xpath(
            "//div[@class='jsx-1410658769 video-feed-item']")
        TikToksUrls = self.driver.find_elements_by_xpath(
            "//div[@class='jsx-1410658769 video-feed-item']/div/div/div/a")
        TikToksViews = self.driver.find_elements_by_xpath(
            "//div[@class='jsx-1410658769 video-feed-item']/div/div/div/a/div/div/div/div/div/span")

        returnArr = []
        if count > len(TikToks):
            lower = len(TikToks)
        else:
            lower = count
        for i in range(0, lower):
            if "k" in TikToksViews[i].text.strip():
                likes = float(
                    TikToksViews[i].text.strip().replace("k", "")) * 1000
            elif "m" in TikToksViews[i].text.strip():
                likes = float(
                    TikToksViews[i].text.strip().replace("m", "")) * 1000000
            else:
                likes = TikToksViews[i].text.strip()

            returnArr.append({
                "link": TikToksUrls[i].get_attribute("href"),
                "author": TikToksUrls[i].get_attribute("href").split("/")[3],
                "likes": likes
            })

        return returnArr

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
            return self.driver.find_element_by_xpath("//video[@class='jsx-3382097194 video-player']").get_attribute("src")
        
        else:
            self.proxy.new_har("vid")
            self.driver.get(video_url)
            r = requests.get( self.driver.find_element_by_xpath("//video[@class='jsx-3382097194 video-player']").get_attribute("src") )
            return r.content
