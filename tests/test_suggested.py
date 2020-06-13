from TikTokApi import TikTokApi

def test_suggested():
    api = TikTokApi()
    assert len(api.getSuggestedHashtagsbyID()) == 30
    assert len(api.getSuggestedMusicbyID()) == 30
    assert len(api.getSuggestedUsersbyID()) == 30

def test_suggested_crawlers():
    api = TikTokApi()
    assert len(api.getSuggestedUsersbyIDCrawler(count=50)) == 50
    assert len(api.getSuggestedHashtagsbyIDCrawler(count=50)) > 0
    assert len(api.getSuggestedMusicIDCrawler(count=50)) > 0