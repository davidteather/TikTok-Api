from TikTokApi import TikTokapi

def test_trending():
    api = TikTokapi("browsermob-proxy/bin/browsermob-proxy", headless=False)
    assert len(api.trending(5)) == 5
    assert len(api.trending(10)) == 10
    api.quit_browser()