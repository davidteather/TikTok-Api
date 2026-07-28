import pytest

from TikTokApi.api.user import User


class DummyVideo:
    def __init__(self, data):
        self.data = data


class DummyParent:
    def __init__(self):
        self.calls = []

    async def make_request(self, **kwargs):
        self.calls.append(kwargs["params"])
        return {
            "itemList": [{"id": f"video-{i}"} for i in range(30)],
            "hasMore": True,
            "cursor": 1,
        }

    def video(self, data):
        return DummyVideo(data)


@pytest.mark.asyncio
async def test_user_videos_respects_requested_count():
    parent = DummyParent()
    user = User(username="test")
    user.sec_uid = "sec_uid"
    user.parent = parent

    videos = []
    async for video in user.videos(count=1):
        videos.append(video)

    assert len(videos) == 1
    assert parent.calls[0]["count"] == 1
