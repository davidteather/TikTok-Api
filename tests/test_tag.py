import asyncio

from TikTokApi import TikTokApi


def test_tag():
    api = TikTokApi()
    result = api.get_videos_by_tag_id('1666161996609542')
    # result = api.trending()
    print(result)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(test_tag())
    test_tag()
