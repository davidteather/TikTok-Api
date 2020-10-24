from TikTokApi import TikTokApi


def test_getHashtagDetails():
    api = TikTokApi()
    result = api.getHashtagDetails("programming")
    assert result["challengeInfo"]["stats"]["viewCount"] > 1000
    assert result["challengeInfo"]["challenge"]["id"] == "5878100"


def test_non_latin1():
    api = TikTokApi()
    result = api.getHashtagDetails("селфи")
    assert result["challengeInfo"]["stats"]["viewCount"] > 1000
