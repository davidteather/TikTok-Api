from TikTokApi import TikTokApi
import os

api = TikTokApi(custom_verify_fp=os.environ.get("verifyFp", None))


def test_video_id_from_url():
    url = "https://www.tiktok.com/@therock/video/7041997751718137094?is_copy_url=1&is_from_webapp=v1"
    video = api.video(url=url)

    assert video.id == "7041997751718137094"

    mobile_url = "https://vm.tiktok.com/TTPdhJDvej"
    video = api.video(url=mobile_url)

    assert video.id == "7041997751718137094"

    pass


def test_video_info():
    video_id = "7041997751718137094"
    video = api.video(id=video_id)

    data = video.info()

    assert data["id"] == video_id


def test_video_bytes():
    video_id = "7041997751718137094"
    video = api.video(id=video_id)

    data = video.bytes()

    assert len(data) > 10000
