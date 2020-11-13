from TikTokApi import TikTokApi
import os
api = TikTokApi.get_instance()


def test_getHashtagDetails():
    result = api.getHashtagDetails("programming")
    assert result["challengeInfo"]["stats"]["viewCount"] > 1000
    assert result["challengeInfo"]["challenge"]["id"] == "5878100"


def test_non_latin1():
    result = api.getHashtagDetails("селфи")
    assert result["challengeInfo"]["stats"]["viewCount"] > 1000
