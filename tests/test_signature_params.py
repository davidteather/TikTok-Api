import pytest

from TikTokApi.tiktok import TikTokApi


class DummySession:
    def __init__(self):
        self.params = {"aid": "1988"}
        self.headers = {}
        self.ms_token = None
        self.is_valid = True
        self.page = None
        self.context = None


class DummyApi(TikTokApi):
    async def _get_valid_session_index(self, **kwargs):
        return 0, DummySession()

    async def _get_session(self, **kwargs):
        return 0, DummySession()

    async def run_fetch_script(self, *args, **kwargs):
        return '{"status_code": 0, "item_list": []}'

    async def sign_url(self, url, **kwargs):
        return url

    async def get_session_cookies(self, session):
        return {}


@pytest.mark.asyncio
async def test_make_request_strips_manual_signature_params(monkeypatch):
    api = DummyApi()

    params = {
        "msToken": "abc",
        "X-Bogus": "bogus",
        "X-Dynosaur": "dyno",
        "X-Gnarly": "gnarly",
        "aid": "1988",
    }

    captured = {}

    async def fake_run_fetch_script(*args, **kwargs):
        captured["url"] = args[0]
        return '{"status_code": 0, "item_list": []}'

    monkeypatch.setattr(api, "run_fetch_script", fake_run_fetch_script)

    await api.make_request("https://example.com", params=params)

    assert "msToken=abc" in captured["url"]
    assert "X-Bogus" not in captured["url"]
    assert "X-Dynosaur" not in captured["url"]
    assert "X-Gnarly" not in captured["url"]
