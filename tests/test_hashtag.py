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
    api = TikTokapi("browsermob-proxy/bin/browsermob-proxy", headless=False)

    res = api.search_by_hashtag("funny")
    api.quit_browser()
    assert len(res) == 10
    assert checkDupes(res) == 0 
    