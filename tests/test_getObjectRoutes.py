from TikTokApi import TikTokApi

api = TikTokApi.get_instance()


def test_tiktok_object():
    assert len(api.getTikTokById("6829267836783971589")) > 0
    assert (
        len(
            api.getTikTokByUrl(
                "https://www.tiktok.com/@therock/video/6829267836783971589"
            )
        )
        > 0
    )


def test_user_object():
    assert len(api.getUserObject("therock")) > 0


def test_music_object():
    assert len(api.getMusicObject("6820695018429253633")) > 0


def test_hashtag_object():
    assert len(api.getHashtagObject("funny")) > 0
