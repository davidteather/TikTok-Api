import tempfile
import asyncio
from playwright.async_api import BrowserContext, Page, Playwright
from TikTokApi import TikTokApi
import os
import pytest

from TikTokApi.stealth.stealth import stealth_async


@pytest.mark.asyncio
async def test_browser_context_factory():

    context_created_in_factory = [False]

    async def browser_context_factory(p: Playwright) -> BrowserContext:
        user_data_dir_tempdir = tempfile.TemporaryDirectory()
        user_data_dir = user_data_dir_tempdir.name
        ctx = await p.chromium.launch_persistent_context(user_data_dir, headless=False)
        context_created_in_factory[0] = True
        return ctx

    async with TikTokApi() as api:
        await api.create_sessions(
            num_sessions=1,
            sleep_after=3,
            browser=os.getenv("TIKTOK_BROWSER", "chromium"),
            headless=False,
            browser_context_factory=browser_context_factory,
        )
        assert context_created_in_factory[0] == True


@pytest.mark.asyncio
async def test_page_factory():

    page_created_in_factory = [False]

    async def page_factory(ctx: BrowserContext) -> Page:
        page = await ctx.new_page()
        _ = await page.goto("https://tiktok.com")
        page_created_in_factory[0] = True
        return page

    async with TikTokApi() as api:
        await api.create_sessions(
            num_sessions=1,
            sleep_after=3,
            browser=os.getenv("TIKTOK_BROWSER", "chromium"),
            headless=False,
            page_factory=page_factory,
        )
        assert page_created_in_factory[0] == True


@pytest.mark.asyncio
@pytest.mark.skip(reason="not enabled for TikTokAPI CI/CD")
async def test_custom_login_flow_with_captcha_solve():
    # NOTE: This example test uses tiktok_captcha_solver library from SadCaptcha.
    # The test is skipped in CI/CD to avoid import errors since the library is not included in requirements.
    # This serves as an example of how to implement custom captcha solving functionality, you are not required to use this library.
    # And you can create your own login page factories and logic for your situation.
    from tiktok_captcha_solver import make_async_playwright_solver_context

    async def captcha_solver_context_factory(p: Playwright) -> BrowserContext:
        ctx = await make_async_playwright_solver_context(
            p, os.environ["API_KEY"], headless=False  # SadCaptcha key
        )
        return ctx

    async def login_page_factory(ctx: BrowserContext) -> Page:
        page = await ctx.new_page()
        await stealth_async(page)
        _ = await page.goto("https://www.tiktok.com/login/phone-or-email/email")
        await asyncio.sleep(5)
        await page.locator('xpath=//input[contains(@name,"username")]').type(
            os.environ["TIKTOK_USERNAME"]
        )
        await asyncio.sleep(2)
        await page.get_by_placeholder("Password").type(os.environ["TIKTOK_PASSWORD"])
        await asyncio.sleep(2)
        await page.locator('//button[contains(@data-e2e,"login-button")]').click()
        await asyncio.sleep(5)  # wait for captcha to be solved
        return page

    async with TikTokApi() as api:
        await api.create_sessions(
            num_sessions=1,
            sleep_after=3,
            browser=os.getenv("TIKTOK_BROWSER", "chromium"),
            headless=False,
            page_factory=login_page_factory,
            browser_context_factory=captcha_solver_context_factory,
        )
