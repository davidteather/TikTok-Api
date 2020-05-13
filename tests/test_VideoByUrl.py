from TikTokApi import TikTokApi

def test_get_video_by_url():
    api = TikTokApi()
    bytesV = api.get_Video_By_TikTok(api.trending(count=30)[0])
    assert type(bytesV) == type(bytes())