"""
Proxy Provider Example

This example demonstrates how to use the ProxyProviders package with TikTok-Api
for smart proxy rotation and management.

ProxyProviders Documentation: https://davidteather.github.io/proxyproviders

Requirements:
    pip install TikTokApi proxyproviders
    python -m playwright install
"""

import asyncio
import os
from TikTokApi import TikTokApi
from proxyproviders import Webshare, BrightData
from proxyproviders.algorithms import RoundRobin, Random, First, Algorithm
from typing import List
from proxyproviders.models.proxy import Proxy


# Get your ms_token from browser cookies after visiting TikTok
ms_token = os.environ.get("ms_token", None)


async def basic_proxy_provider_example():
    """Basic example using Webshare with default RoundRobin algorithm"""
    provider = Webshare(api_key=os.environ.get("WEBSHARE_API_KEY"))

    async with TikTokApi() as api:
        await api.create_sessions(
            num_sessions=5,
            proxy_provider=provider,
            ms_tokens=[ms_token] if ms_token else None,
            headless=True,
        )

        async for video in api.trending.videos(count=10):
            print(f"Video ID: {video.id}")


async def custom_algorithm_example():
    """Example using a custom proxy selection algorithm"""

    class USPreferredAlgorithm(Algorithm):
        def select(self, proxies: List[Proxy]) -> Proxy:
            us_proxies = [p for p in proxies if p.country_code == "US"]
            if us_proxies:
                return us_proxies[0]
            return proxies[0] if proxies else None

    provider = Webshare(api_key=os.environ.get("WEBSHARE_API_KEY"))

    async with TikTokApi() as api:
        await api.create_sessions(
            num_sessions=3,
            proxy_provider=provider,
            proxy_algorithm=USPreferredAlgorithm(),
            ms_tokens=[ms_token] if ms_token else None,
            headless=True,
        )

        async for video in api.search.videos("python", count=5):
            print(f"Found: {video.id}")


async def random_algorithm_example():
    """Example using Random algorithm for proxy selection"""
    provider = Webshare(api_key=os.environ.get("WEBSHARE_API_KEY"))

    async with TikTokApi() as api:
        await api.create_sessions(
            num_sessions=5,
            proxy_provider=provider,
            proxy_algorithm=Random(),
            ms_tokens=[ms_token] if ms_token else None,
            headless=True,
        )

        user = api.user(username="tiktok")
        user_data = await user.info()
        print(
            f"User: {user_data['uniqueId']}, Followers: {user_data['stats']['followerCount']}"
        )


async def brightdata_example():
    """Example using BrightData proxy provider"""
    provider = BrightData(
        api_key=os.environ.get("BRIGHTDATA_API_KEY"),
        zone=os.environ.get("BRIGHTDATA_ZONE"),
    )

    async with TikTokApi() as api:
        await api.create_sessions(
            num_sessions=10,
            proxy_provider=provider,
            proxy_algorithm=RoundRobin(),
            ms_tokens=[ms_token] if ms_token else None,
            headless=True,
        )

        async for video in api.trending.videos(count=5):
            print(f"Trending: {video.id}")


async def partial_sessions_with_provider():
    """Example using proxy provider with partial session creation"""
    provider = Webshare(api_key=os.environ.get("WEBSHARE_API_KEY"))

    async with TikTokApi() as api:
        await api.create_sessions(
            num_sessions=10,
            proxy_provider=provider,
            allow_partial_sessions=True,
            min_sessions=3,
            ms_tokens=[ms_token] if ms_token else None,
            headless=True,
        )

        print(f"Created {len(api.sessions)} sessions successfully")

        async for video in api.trending.videos(count=5):
            print(f"Video: {video.id}")


async def legacy_vs_new_comparison():
    """Comparison of legacy proxy approach vs new proxy provider approach"""

    async with TikTokApi() as api:
        proxies = [
            {
                "server": "http://proxy1.example.com:8080",
                "username": "user",
                "password": "pass",
            },
            {
                "server": "http://proxy2.example.com:8080",
                "username": "user",
                "password": "pass",
            },
        ]

        await api.create_sessions(
            num_sessions=2,
            proxies=proxies,
            ms_tokens=[ms_token] if ms_token else None,
            headless=True,
        )

    provider = Webshare(api_key=os.environ.get("WEBSHARE_API_KEY"))

    async with TikTokApi() as api:
        await api.create_sessions(
            num_sessions=5,
            proxy_provider=provider,
            proxy_algorithm=RoundRobin(),
            ms_tokens=[ms_token] if ms_token else None,
            headless=True,
        )


async def main():
    """Run all examples"""
    if not os.environ.get("WEBSHARE_API_KEY"):
        print("Warning: WEBSHARE_API_KEY not set. Some examples will be skipped.")
        print("Get your API key from: https://www.webshare.io")

    if not ms_token:
        print("Warning: ms_token not set. Sessions may fail.")
        print("Get ms_token from browser cookies after visiting TikTok.com")

    if os.environ.get("WEBSHARE_API_KEY"):
        await basic_proxy_provider_example()
        await custom_algorithm_example()
        await random_algorithm_example()
        await partial_sessions_with_provider()

    if os.environ.get("BRIGHTDATA_API_KEY") and os.environ.get("BRIGHTDATA_ZONE"):
        await brightdata_example()


if __name__ == "__main__":
    asyncio.run(main())
