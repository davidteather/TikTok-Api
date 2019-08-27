class TikTokapi:

    def __init__(self):
        val = 0

    def trending(self, count=10, verbose=0, sig="W5cHbxAVBvNS2316KIvp21uXB3"):
        import requests
        loop = True
        while loop is True:
            url = "https://m.tiktok.com/share/item/list?id=&type=5&count=" + \
                str(count) + "&minCursor=0&maxCursor=0&_signature=" + \
                sig
            r = requests.get(url, headers={"authority": "m.tiktok.com", "method": "GET", "path": url.split("https://m.tiktok.com")[0], "scheme": "https", "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
                                           "accept-encoding": "gzip, deflate, br", "accept-language": "en-US,en;q=0.9", "cache-control": "max-age=0", "upgrade-insecure-requests": "1",
                                           "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"})

            data = r.json()
            if data["statusCode"] != 0:
                if verbose == 1:
                    print("Invalid Signature Retrying")
            else:
                loop = False
                return data["body"]["itemListData"]

    def userPosts(self, id, count=10, verbose=0, sig="W5cHbxAVBvNS2316KIvp21uXB3"):
        import requests
        loop = True
        while loop is True:
            url = "https://m.tiktok.com/share/item/list?id=" + str(id) +"&type=1&count=" + \
                str(count) + "&minCursor=0&maxCursor=0&_signature=" + \
                sig
            r = requests.get(url, headers={"authority": "m.tiktok.com", "method": "GET", "path": url.split("https://m.tiktok.com")[0], "scheme": "https", "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
                                           "accept-encoding": "gzip, deflate, br", "accept-language": "en-US,en;q=0.9", "cache-control": "max-age=0", "upgrade-insecure-requests": "1",
                                           "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"})

            data = r.json()
            if data["statusCode"] != 0:
                if verbose == 1:
                    print("Invalid Signature Retrying")
            else:
                loop = False
                return data["body"]["itemListData"]
