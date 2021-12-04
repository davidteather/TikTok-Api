from TikTokApi import TikTokApi
import os

api = TikTokApi.get_instance(
    custom_verifyFp=os.environ.get("verifyFp", None), use_test_endpoints=True
)


def test_get_music_object_full_by_api():
    music_id = "6819262113299565318"
    res = api.get_music_object_full_by_api(music_id)
    assert res["music"]["id"] == music_id
