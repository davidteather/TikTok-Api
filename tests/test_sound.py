from TikTokApi import TikTokApi
import os

song_id = "7016547803243022337"


def test_sound_videos():
    with TikTokApi(custom_verify_fp=os.environ.get("verifyFp", None)) as api:
        sound = api.sound(id=song_id)
        video_count = 0
        for video in sound.videos(count=100):
            video_count += 1

        assert video_count >= 100


def test_sound_info():
    with TikTokApi(custom_verify_fp=os.environ.get("verifyFp", None)) as api:
        sound = api.sound(id=song_id)
        data = sound.info()
        assert data["id"] == song_id
