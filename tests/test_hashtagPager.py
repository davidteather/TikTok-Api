from TikTokApi import TikTokApi


class TestHashtagPager:
    """Test the pager returned by getHashtagPager"""
    def test_page_size(self):
        """Pages should be pretty close to the specified size"""
        api = TikTokApi()

        pager = api.getHashtagPager('regal', page_size=5)

        page = pager.__next__()
        assert abs(len(page)-5) <= 2

        page = pager.__next__()
        assert abs(len(page)-5) <= 2

    def test_max_pages(self):
        """Should have x pages only"""
        api = TikTokApi()

        pager = api.getHashtagPager('regal', max_pages=4)

        pages = 0
        for page in pager:
            pages += 1

        assert pages == 4
