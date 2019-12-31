from TikTokApi import TikTokapi

def test_sound():
    api = TikTokapi("browsermob-proxy/bin/browsermob-proxy", headless=True)
    assert len(api.search_by_sound("https://www.tiktok.com/music/original-sound-6742171751955843846", count=5)) == 5
    assert len(api.search_by_sound("https://www.tiktok.com/music/original-sound-6742171751955843846", count=10)) == 10
    assert len(api.search_by_sound("https://www.tiktok.com/music/original-sound-6742171751955843846", count=30)) == 30

    api.quit_browser()