from TikTokApi import TikTokApi
import os

api = TikTokApi.get_instance(
    custom_verifyFp=os.environ.get(
        "verifyFp", None
    )  # , use_test_endpoints=True - test endpoint not working on this endpoint anymore
)


def test_suggested():
    assert len(api.get_suggested_users_by_id()) > 0
    assert len(api.get_suggested_hashtags_by_id()) > 0
    assert len(api.get_suggested_music_by_id()) > 0


def test_suggested_crawlers():
    assert len(api.get_suggested_users_by_id_crawler(count=50)) == 50
    assert len(api.get_suggested_hashtags_by_id_crawler(count=10)) > 0
    assert len(api.get_suggested_music_id_crawler(count=10)) > 0
