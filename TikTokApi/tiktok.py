class TikTokapi:

    def __init__(self, browsermobDirectory):
        print("New class reference, finding valid signature. This might take a minute.")
        from browsermobproxy import Server
        import psutil
        import json
        import time

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
        from selenium import webdriver
        profile = webdriver.FirefoxProfile()
        selenium_proxy = proxy.selenium_proxy()
        profile.set_proxy(selenium_proxy)
        driver = webdriver.Firefox(firefox_profile=profile)

        proxy.new_har("list")
        driver.get("https://www.tiktok.com/en/trending")
        data = proxy.har
        for element in data['log']['entries']:
            if "https://m.tiktok.com/share/item/list?" in element['request']['url'] or "https://www.tiktok.com/share/item/list?" in element['request']['url']:
                print("Found signature, continuing.")
                self.signature = element['request']['queryString'][6]['value']

        server.stop()
        driver.quit()

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
                        for tiktok in data["body"]["itemListData"]:
                            response.append(tiktok)
                    else:
                        return response

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
