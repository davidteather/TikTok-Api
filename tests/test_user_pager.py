from TikTokApi import TikTokApi
import os

api = TikTokApi.get_instance(
    custom_verifyFp=os.environ.get("verifyFp", None), use_test_endpoints=True
)


class TestUserPager:
    """Test the pager returned by getUserPager"""

    def test_page_size(self):
        """Pages should be pretty close to the specified size"""

        pager = api.get_user_pager("therock", page_size=5)

        page = pager.__next__()
        assert abs(len(page) - 5) <= 2

        page = pager.__next__()
        assert abs(len(page) - 5) <= 2

    def test_user_pager_before(self):
        """Should always request therock's first 19 tiktoks across 2 pages"""
        APR_24 = 1587757436000  # 2020-04-24 15:43:56 to be precise. Must be ms-precision timestamp

        pager = api.get_user_pager("therock", page_size=10, cursor=APR_24)

        total_tts = 0
        pages = 0
        for page in pager:
            pages += 1
            total_tts += len(page)

        assert pages == 2
        assert total_tts == 19

    # TikTokApi No Longer Supports
    '''def test_user_pager_before_after(self):
        """Should always request the 7 tiktoks between those times"""
        APR_24 = 1587757437000  # 2020-04-24 15:43:57
        AUG_10 = 1597076218000  # 2020-08-10 12:16:58

        pager = api.getUserPager(
            "therock", page_size=3, cursor=APR_24, maxCursor=AUG_10
        )

        total_tts = 0
        pages = 0
        for page in pager:
            pages += 1
            total_tts += len(page)

        assert pages == 3
        assert total_tts == 7'''
