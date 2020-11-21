import requests


class TikTokUser:
    def __init__(self, user_cookie, debug=False, proxy=None):
        """A TikTok User Class. Represents a single user that is logged in.

        :param user_cookie: The cookies from a signed in session of TikTok.
         Sign into TikTok.com and run document.cookie in the javascript console
        and then copy the string and place it into this parameter.
        """
        self.cookies = user_cookie
        self.debug = debug
        self.proxy = proxy

    def get_insights(self, videoID, username=None, proxy=None) -> dict:
        """Get insights/analytics for a video.

        :param videoID: The TikTok ID to look up the insights for.
        """
        api_url = "https://api.tiktok.com/aweme/v1/data/insighs/?tz_offset=-25200&aid=1233&carrier_region=US"
        if username is not None:
            referrer = "https://www.tiktok.com/@" + username + "/video/" + videoID
        else:
            referrer = "https://www.tiktok.com/"
        insights = [
            "video_info",
            "video_page_percent",
            "video_region_percent",
            "video_total_duration",
            "video_per_duration",
        ]
        # Note: this list of parameters has to be in exactly this order with exactly this format
        # or else you will get "Invalid parameters"

        def build_insight(insight, videoID):
            return '{"insigh_type":"' + insight + '","aweme_id":"' + videoID + '"}'

        insight_string = ",".join([build_insight(i, videoID) for i in insights])
        insight_string = (
            insight_string
            + ',{"insigh_type": "user_info"}'
            + ',{"insigh_type":"video_uv","aweme_id":"'
            + videoID
            + '"}'
            + ',{"insigh_type":"vv_history","days":8}'
            + ',{"insigh_type":"follower_num_history","days":9}'
            + ',{"insigh_type":"follower_num"}'
            + ',{"insigh_type":"user_info"}'
        )
        r = requests.post(
            api_url,
            headers={
                "accept": "*/*",
                "accept-language": "en-US,en;q=0.9",
                "content-type": "application/x-www-form-urlencoded",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site",
                "referrer": referrer,
                "referrerPolicy": "no-referrer-when-downgrade",
                "method": "POST",
                "mode": "cors",
                "credentials": "include",
            },
            data="type_requests=[" + insight_string + "]",
            proxies=self.__format_proxy(proxy),
            cookies=self.__cookies_to_json(self.cookies),
        )
        try:
            return r.json()
        except Exception:
            if debug:
                print(f"Failed converting following to JSON\n{r.text}")
            raise Exception("Invalid Response (from TikTok)")

    #
    # PRIVATE METHODS
    #
    def __format_proxy(self, proxy) -> dict:
        """
        Formats the proxy object
        """
        if proxy is not None:
            return {"http": proxy, "https": proxy}
        else:
            return None

    def __cookies_to_json(self, cookie_string) -> dict:
        """
        Turns a cookie string into a dict for
        use in the requests module
        """
        if isinstance(cookie_string, dict):
            return cookie_string

        cookie_dict = {}
        for cookie in cookie_string.split("; "):
            cookie_dict[cookie.split("=")[0]] = cookie.split("=")[1]

        return cookie_dict
