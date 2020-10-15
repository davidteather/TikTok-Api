from TikTokApi import TikTokApi


def test_tiktok_object():
    api = TikTokApi()
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
    api = TikTokApi()
    assert len(api.getUserObject("therock")) > 0


def test_music_object():
    api = TikTokApi()
    assert len(api.getMusicObject("6820695018429253633")) > 0


def test_hashtag_object():
    api = TikTokApi()
    assert len(api.getHashtagObject("funny")) > 0
