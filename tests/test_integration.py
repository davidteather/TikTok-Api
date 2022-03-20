from TikTokApi import TikTokApi
import os


def test_video_attributes():
    with TikTokApi(custom_verify_fp=os.environ.get("verifyFp", None)) as api:
        tag_name = "funny"
        for video in api.hashtag(name=tag_name).videos():
            # Test hashtags on video.
            tag_included = False
            for tag in video.hashtags:
                if tag.name == tag_name:
                    tag_included = True

            assert tag_included

            # Test sound on video.
            assert video.sound is not None
            assert video.sound.id is not None

            # Test author.
            assert video.author is not None
            assert video.author.user_id is not None
            assert video.author.sec_uid is not None
