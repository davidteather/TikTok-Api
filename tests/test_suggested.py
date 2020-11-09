from TikTokApi import TikTokApi

api = TikTokApi.get_instance()


def test_suggested():
    assert len(api.getSuggestedHashtagsbyID()) > 0
    assert len(api.getSuggestedMusicbyID()) > 0
    assert len(api.getSuggestedUsersbyID()) > 0


def test_suggested_crawlers():
    assert len(api.getSuggestedUsersbyIDCrawler(count=50)) == 50
    assert len(api.getSuggestedHashtagsbyIDCrawler(count=10)) > 0
    assert len(api.getSuggestedMusicIDCrawler(count=10)) > 0
