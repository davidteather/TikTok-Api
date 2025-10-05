import pytest
import os
import requests
from TikTokApi import TikTokApi
from proxyproviders import ProxyProvider
from proxyproviders.algorithms import RoundRobin, Random, Algorithm
from proxyproviders.models.proxy import Proxy, ProxyFormat
from typing import List


def test_proxy_format_playwright_with_auth():
    """Test proxy format conversion with authentication"""
    proxy = Proxy(
        id="test-1",
        username="user",
        password="pass",
        proxy_address="192.168.1.1",
        port=8080,
    )

    result = proxy.format(ProxyFormat.PLAYWRIGHT)
    assert result["server"] == "http://192.168.1.1:8080"
    assert result["username"] == "user"
    assert result["password"] == "pass"


def test_proxy_format_playwright_without_auth():
    """Test proxy format conversion without authentication"""
    proxy = Proxy(
        id="test-2", username="", password="", proxy_address="10.0.0.1", port=3128
    )

    result = proxy.format(ProxyFormat.PLAYWRIGHT)
    assert result["server"] == "http://10.0.0.1:3128"
    assert "username" not in result or result.get("username") == ""
    assert "password" not in result or result.get("password") == ""


def test_proxy_provider_storage():
    """Test that proxy provider and algorithm are stored in API instance"""
    from proxyproviders import ProxyProvider

    class MockProvider(ProxyProvider):
        def _fetch_proxies(self):
            return [Proxy(id="1", proxy_address="127.0.0.1", port=8080)]

    provider = MockProvider()
    algo = RoundRobin()

    api = TikTokApi()
    api._proxy_provider = provider
    api._proxy_algorithm = algo

    assert api._proxy_provider is provider
    assert api._proxy_algorithm is algo


@pytest.mark.asyncio
async def test_cannot_use_both_proxies_and_provider():
    """Test that using both proxies and proxy_provider raises an error"""

    class MockProvider(ProxyProvider):
        def _fetch_proxies(self):
            return [Proxy(id="1", proxy_address="127.0.0.1", port=8080)]

    provider = MockProvider()
    proxies = [{"server": "http://proxy.example.com:8080"}]
    ms_token = os.environ.get("ms_token")

    with pytest.raises(ValueError, match="Cannot use both"):
        async with TikTokApi() as api:
            await api.create_sessions(
                num_sessions=1,
                proxies=proxies,
                proxy_provider=provider,
                ms_tokens=[ms_token] if ms_token else None,
                headless=True,
            )


@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.environ.get("WEBSHARE_API_KEY"),
    reason="Requires WEBSHARE_API_KEY environment variable",
)
async def test_proxy_actually_used():
    """Test that proxy is actually being used by checking IP differs from local IP"""
    from proxyproviders import Webshare

    our_ip = requests.get("https://httpbin.org/ip").json()["origin"]

    provider = Webshare(api_key=os.environ.get("WEBSHARE_API_KEY"))
    ms_token = os.environ.get("ms_token")

    async with TikTokApi() as api:
        await api.create_sessions(
            num_sessions=1,
            proxy_provider=provider,
            ms_tokens=[ms_token] if ms_token else None,
            headless=True,
        )

        session = api.sessions[0]

        await session.page.goto("https://httpbin.org/ip")
        page_content = await session.page.content()

        assert (
            "httpbin.org" in page_content.lower() or "origin" in page_content.lower()
        ), "Page didn't load httpbin.org"
        assert (
            our_ip not in page_content
        ), f"Proxy not being used - detected our own IP: {our_ip}"
