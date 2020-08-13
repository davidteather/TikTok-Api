from TikTokApi import TikTokApi
import pytest

def test_insights():
    api = TikTokApi()
    with pytest.raises(Exception):
        api.get_insights('charlidamelio', 6860178143399955717)