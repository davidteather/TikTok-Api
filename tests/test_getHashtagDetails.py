from TikTokApi import TikTokApi


def test_getHashtagDetails():
    api = TikTokApi()
    result = api.getHashtagDetails("programming")
    assert result["body"]["challengeData"]["posts"] > 1000
    assert result["body"]["challengeData"]["challengeId"] == "5878100"


def test_non_latin1():
    api = TikTokApi()
    result = api.getHashtagDetails("селфи")
    assert result["body"]["challengeData"]["posts"] > 1000
