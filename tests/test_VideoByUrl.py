from TikTokApi import TikTokapi

def test_get_video_by_url():
    api = TikTokapi("browsermob-proxy/bin/browsermob-proxy", headless=True)
    bytesV = api.get_Video_By_Url("https://www.tiktok.com/@bts_official_bighit/video/6741282343362759938?langCountry=en", return_bytes=1)
    assert type(bytesV) == type(bytes())