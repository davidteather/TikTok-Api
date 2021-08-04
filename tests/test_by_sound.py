from TikTokApi import TikTokApi
import os

api = TikTokApi.get_instance(
    custom_verifyFp=os.environ.get("verifyFp", None), use_test_endpoints=True
)


def test_trending():
    assert abs(len(api.by_sound("6819262113299565318", 5)) - 5) <= 1
    assert abs(len(api.by_sound("6819262113299565318", 10)) - 10) <= 1
    assert abs(len(api.by_sound("6819262113299565318", 20)) - 20) <= 1
