from TikTokApi import TikTokapi

def test_trending():
    api = TikTokapi("browsermob-proxy/bin/browsermob-proxy", headless=True)
    assert len(api.trending(5)) == 5
    assert len(api.trending(10)) == 10
    assert len(api.trending(20)) == 20


def test_extended_trending():
    api = TikTokapi("browsermob-proxy/bin/browsermob-proxy", headless=True)
    assert len(api.trending(50)) == 50
    assert len(api.trending(100)) == 100