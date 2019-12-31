from TikTokApi import TikTokapi

def test_user():
    api = TikTokapi("browsermob-proxy/bin/browsermob-proxy", headless=True)

    assert len(api.userPosts(id="5058536", secUid="MS4wLjABAAAAoRsCq3Yj6BtSKBCQ4rf3WQYxIaxe5VetwJfYzW_U5K8", count=5)) == 5
    assert len(api.userPosts(id="5058536", secUid="MS4wLjABAAAAoRsCq3Yj6BtSKBCQ4rf3WQYxIaxe5VetwJfYzW_U5K8", count=10)) == 10
    assert len(api.userPosts(id="5058536", secUid="MS4wLjABAAAAoRsCq3Yj6BtSKBCQ4rf3WQYxIaxe5VetwJfYzW_U5K8", count=30)) == 30

    api.quit_browser()

def test_username():
    api = TikTokapi("browsermob-proxy/bin/browsermob-proxy", headless=True)

    assert len(api.userPosts(username="thecardguy", count=5)) == 5
    assert len(api.userPosts(username="thecardguy", count=10)) == 10
    assert len(api.userPosts(username="thecardguy", count=27)) == 27

    api.quit_browser()