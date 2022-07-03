from TikTokApi import TikTokApi
import os

video_id = 7107272719166901550

def test_comment_page():
    with TikTokApi(custom_verify_fp=os.environ.get("verifyFp", None)) as api:
        video = api.video(id=video_id)

        count = 0
        for comment in video.comments():
            count += 1

        assert count >= 0

def test_comment_paging():
    with TikTokApi(custom_verify_fp=os.environ.get("verifyFp", None)) as api:
        video = api.video(id=video_id)

        count = 0
        for comment in video.comments(count=50):
            count += 1

        assert count >= 50