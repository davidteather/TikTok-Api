from TikTokApi import TikTokapi


def checkDupes(res):
    thing = []
    dupes = []
    for result in res:
        if result in thing:
            dupes.append(result)
        else:
            thing.append(result)
        
    return len(dupes)


def test_hashtag():
    api = TikTokapi("browsermob-proxy/bin/browsermob-proxy", headless=True)

    res = api.search_by_hashtag("funny", count=10)
    assert len(res) == 10
    assert checkDupes(res) == 0

    res = api.search_by_hashtag("funny", count=20)
    assert len(res) == 20
    assert checkDupes(res) == 0

    res = api.search_by_hashtag("funny", count=30)
    assert len(res) == 30
    assert checkDupes(res) == 0

    api.quit_browser()