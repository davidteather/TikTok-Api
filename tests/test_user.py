from TikTokApi import TikTokApi


def test_user():
    api = TikTokApi()

    assert api.getUser("charlidamelio")["user"]["uniqueId"] == "charlidamelio"
    assert api.getUserObject("charlidamelio")["uniqueId"] == "charlidamelio"
    assert (
        abs(
            len(
                api.userPosts(
                    userID="5058536",
                    secUID="MS4wLjABAAAAoRsCq3Yj6BtSKBCQ4rf3WQYxIaxe5VetwJfYzW_U5K8",
                    count=5,
                )
            )
            - 5
        )
        <= 1
    )
    assert (
        abs(
            len(
                api.userPosts(
                    userID="5058536",
                    secUID="MS4wLjABAAAAoRsCq3Yj6BtSKBCQ4rf3WQYxIaxe5VetwJfYzW_U5K8",
                    count=10,
                )
            )
            - 10
        )
        <= 1
    )
    assert (
        abs(
            len(
                api.userPosts(
                    userID="5058536",
                    secUID="MS4wLjABAAAAoRsCq3Yj6BtSKBCQ4rf3WQYxIaxe5VetwJfYzW_U5K8",
                    count=30,
                )
            )
            - 30
        )
        <= 1
    )
