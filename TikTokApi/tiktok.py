from __future__ import annotations

import asyncio
import logging
import dataclasses
from typing import Any, Awaitable, Callable, Optional
import random
import time
import json

from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    ProxySettings,
    async_playwright,
    TimeoutError,
    Error as PlaywrightError,
)
from urllib.parse import urlencode, quote, urlparse
from proxyproviders import ProxyProvider
from proxyproviders.algorithms import Algorithm
from proxyproviders.models.proxy import ProxyFormat

from .stealth import stealth_async
from .helpers import random_choice

from .api.user import User
from .api.video import Video
from .api.sound import Sound
from .api.hashtag import Hashtag
from .api.comment import Comment
from .api.trending import Trending
from .api.search import Search
from .api.playlist import Playlist

from .exceptions import (
    InvalidJSONException,
    EmptyResponseException,
)


@dataclasses.dataclass
class TikTokPlaywrightSession:
    """A TikTok session using Playwright"""

    context: Any
    page: Any
    proxy: str = None
    params: dict = None
    headers: dict = None
    ms_token: str = None
    base_url: str = "https://www.tiktok.com"
    is_valid: bool = True


class TikTokApi:
    """The main TikTokApi class that contains all the endpoints.

    Import With:
        .. code-block:: python

            from TikTokApi import TikTokApi
            api = TikTokApi()
    """

    user = User
    video = Video
    sound = Sound
    hashtag = Hashtag
    comment = Comment
    trending = Trending
    search = Search
    playlist = Playlist

    def __init__(self, logging_level: int = logging.WARN, logger_name: str = None):
        """
        Create a TikTokApi object.

        Args:
            logging_level (int): The logging level you want to use.
            logger_name (str): The name of the logger you want to use.
        """
        self.sessions = []
        self._session_recovery_enabled = True
        self._session_creation_lock = asyncio.Lock()
        self._cleanup_called = False
        self._auto_cleanup_dead_sessions = True
        self._proxy_provider: Optional[ProxyProvider] = None
        self._proxy_algorithm: Optional[Algorithm] = None

        if logger_name is None:
            logger_name = __name__
        self.__create_logger(logger_name, logging_level)

        User.parent = self
        Video.parent = self
        Sound.parent = self
        Hashtag.parent = self
        Comment.parent = self
        Trending.parent = self
        Search.parent = self
        Playlist.parent = self

        self.browser: Browser = None
        self.playwright: Playwright = None

    def __create_logger(self, name: str, level: int = logging.DEBUG):
        """Create a logger for the class."""
        self.logger: logging.Logger = logging.getLogger(name)
        self.logger.setLevel(level)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def __del__(self):
        """
        Destructor to ensure cleanup happens even if user forgets.

        Warning: This is a safety net. Users should still call close_sessions() explicitly
        in async contexts. This will log a warning if cleanup wasn't called properly.
        """
        if not self._cleanup_called:
            if self.sessions or self.browser or self.playwright:
                self.logger.warning(
                    "TikTokApi object is being destroyed but cleanup was not called. "
                    "Please use 'async with TikTokApi()' or call 'await api.close_sessions()' and "
                    "'await api.stop_playwright()' explicitly to avoid resource leaks. "
                    f"Leaked resources: {len(self.sessions)} sessions, "
                    f"browser={'exists' if self.browser else 'none'}, "
                    f"playwright={'exists' if self.playwright else 'none'}"
                )

    async def __set_session_params(self, session: TikTokPlaywrightSession):
        """Set the session params for a TikTokPlaywrightSession"""
        user_agent = await session.page.evaluate("() => navigator.userAgent")
        language = await session.page.evaluate(
            "() => navigator.language || navigator.userLanguage"
        )
        platform = await session.page.evaluate("() => navigator.platform")
        device_id = str(random.randint(10**18, 10**19 - 1))  # Random device id
        history_len = str(random.randint(1, 10))  # Random history length
        screen_height = str(random.randint(600, 1080))  # Random screen height
        screen_width = str(random.randint(800, 1920))  # Random screen width
        timezone = await session.page.evaluate(
            "() => Intl.DateTimeFormat().resolvedOptions().timeZone"
        )

        session_params = {
            "aid": "1988",
            "app_language": language,
            "app_name": "tiktok_web",
            "browser_language": language,
            "browser_name": "Mozilla",
            "browser_online": "true",
            "browser_platform": platform,
            "browser_version": user_agent,
            "channel": "tiktok_web",
            "cookie_enabled": "true",
            "device_id": device_id,
            "device_platform": "web_pc",
            "focus_state": "true",
            "from_page": "user",
            "history_len": history_len,
            "is_fullscreen": "false",
            "is_page_visible": "true",
            "language": language,
            "os": platform,
            "priority_region": "",
            "referer": "",
            "region": "US",  # TODO: TikTokAPI option
            "screen_height": screen_height,
            "screen_width": screen_width,
            "tz_name": timezone,
            "webcast_language": language,
        }
        session.params = session_params

    async def _is_session_valid(self, session: TikTokPlaywrightSession) -> bool:
        """
        Check if a session is still valid/alive.

        Args:
            session: The session to check

        Returns:
            bool: True if session is valid, False otherwise
        """
        if not session.is_valid:
            return False

        try:
            # Quick validation - try to get page URL
            # This will fail immediately if the page/context/browser is closed
            _ = session.page.url
            return True
        except (PlaywrightError, AttributeError) as e:
            self.logger.warning(f"Session validation failed: {e}")
            session.is_valid = False
            return False

    async def _mark_session_invalid(self, session: TikTokPlaywrightSession):
        """
        Mark a session as invalid and attempt cleanup.

        Args:
            session: The session to mark as invalid
        """
        session.is_valid = False

        # Attempt graceful cleanup
        try:
            if session.page:
                await session.page.close()
        except Exception as e:
            self.logger.debug(f"Error closing page during invalidation: {e}")

        try:
            if session.context:
                await session.context.close()
        except Exception as e:
            self.logger.debug(f"Error closing context during invalidation: {e}")

        # Immediately remove from sessions list if auto-cleanup is enabled
        # This prevents memory leaks from accumulating dead sessions
        if self._auto_cleanup_dead_sessions and session in self.sessions:
            try:
                self.sessions.remove(session)
                self.logger.debug(
                    f"Automatically removed dead session from pool. Remaining: {len(self.sessions)}"
                )
            except ValueError:
                pass  # Session already removed

    async def _get_valid_session_index(
        self, **kwargs
    ) -> tuple[int, TikTokPlaywrightSession]:
        """
        Get a valid session, with automatic recovery if needed.

        Args:
            session_index (int, optional): Specific session index to use

        Returns:
            tuple: (index, session)

        Raises:
            Exception: If no valid sessions available and recovery fails
        """
        max_attempts = 3

        for attempt in range(max_attempts):
            # First, try to get a valid session
            if kwargs.get("session_index") is not None:
                i = kwargs["session_index"]
                if i < len(self.sessions):
                    session = self.sessions[i]
                    if await self._is_session_valid(session):
                        return i, session
                    else:
                        self.logger.warning(f"Requested session {i} is invalid")
            else:
                # Try to find any valid session
                valid_sessions = []
                for idx, session in enumerate(self.sessions):
                    if await self._is_session_valid(session):
                        valid_sessions.append((idx, session))

                if valid_sessions:
                    return random.choice(valid_sessions)

            # No valid sessions found - attempt recovery if enabled
            if self._session_recovery_enabled and attempt < max_attempts - 1:
                self.logger.warning(
                    f"No valid sessions found, attempting recovery (attempt {attempt + 1}/{max_attempts})"
                )
                await self._recover_sessions()
            else:
                break

        raise Exception(
            "No valid sessions available. All sessions appear to be dead. "
            "Please call create_sessions() again or restart the API."
        )

    async def _recover_sessions(self):
        """
        Attempt to recover from session failures by cleaning up dead sessions
        and potentially creating new ones if we have the necessary configuration.
        """
        async with self._session_creation_lock:
            self.logger.info("Starting session recovery...")

            # Remove invalid sessions
            initial_count = len(self.sessions)
            self.sessions = [
                s for s in self.sessions if await self._is_session_valid(s)
            ]
            removed_count = initial_count - len(self.sessions)

            if removed_count > 0:
                self.logger.info(f"Removed {removed_count} dead session(s)")

            # Note: We don't automatically create new sessions here because we'd need
            # all the original parameters (proxies, ms_tokens, etc.)
            # Users should call create_sessions() again if they need more sessions

    async def __create_session(
        self,
        url: str = "https://www.tiktok.com",
        ms_token: str | None = None,
        proxy: dict[str, Any] | ProxySettings | None = None,
        context_options: dict[str, Any] = {},
        sleep_after: int = 1,
        cookies: dict[str, Any] | None = None,
        suppress_resource_load_types: list[str] = None,
        timeout: int = 30000,
        page_factory: Callable[[BrowserContext], Awaitable[Page]] | None = None,
        browser_context_factory: (
            Callable[[Playwright], Awaitable[BrowserContext]] | None
        ) = None,
    ):
        try:
            """Create a TikTokPlaywrightSession"""
            if ms_token is not None:
                if cookies is None:
                    cookies = {}
                cookies["msToken"] = ms_token

            if self._proxy_provider is not None:
                proxy_obj = self._proxy_provider.get_proxy(self._proxy_algorithm)
                proxy = proxy_obj.format(ProxyFormat.PLAYWRIGHT)

            if browser_context_factory is not None:
                context = self.browser
            else:
                context = await self.browser.new_context(proxy=proxy, **context_options)
            if cookies is not None:
                formatted_cookies = [
                    {"name": k, "value": v, "domain": urlparse(url).netloc, "path": "/"}
                    for k, v in cookies.items()
                    if v is not None
                ]
                await context.add_cookies(formatted_cookies)

            if page_factory:
                page = await page_factory(context)
            else:
                page = await context.new_page()
                await stealth_async(page)
                _ = await page.goto(url)

            if "tiktok" not in page.url:
                _ = await page.goto("https://www.tiktok.com")

            # Get the request headers to the url
            request_headers = None

            def handle_request(request):
                nonlocal request_headers
                request_headers = request.headers

            page.once("request", handle_request)

            if suppress_resource_load_types is not None:
                await page.route(
                    "**/*",
                    lambda route, request: (
                        route.abort()
                        if request.resource_type in suppress_resource_load_types
                        else route.continue_()
                    ),
                )

            # Set the navigation timeout
            page.set_default_navigation_timeout(timeout)

            # by doing this, we are simulate scroll event using mouse to `avoid` bot detection
            x, y = random.randint(0, 50), random.randint(0, 50)
            a, b = random.randint(1, 50), random.randint(100, 200)

            await page.mouse.move(x, y)
            await page.wait_for_load_state("networkidle")
            await page.mouse.move(a, b)

            session = TikTokPlaywrightSession(
                context,
                page,
                ms_token=ms_token,
                proxy=proxy,
                headers=request_headers,
                base_url=url,
                is_valid=True,
            )

            if ms_token is None:
                await asyncio.sleep(
                    sleep_after
                )  # TODO: Find a better way to wait for msToken
                cookies = await self.get_session_cookies(session)
                ms_token = cookies.get("msToken")
                session.ms_token = ms_token
                if ms_token is None:
                    self.logger.info(
                        f"Failed to get msToken on session index {len(self.sessions)}, you should consider specifying ms_tokens"
                    )
            self.sessions.append(session)
            await self.__set_session_params(session)
        except Exception as e:
            # clean up
            self.logger.error(f"Failed to create session: {e}")
            # Cleanup resources if they were partially created
            if "page" in locals():
                try:
                    await page.close()
                except Exception:
                    pass
            if "context" in locals():
                try:
                    await context.close()
                except Exception:
                    pass
            raise  # Re-raise the exception after cleanup

    async def create_sessions(
        self,
        num_sessions: int = 5,
        headless: bool = True,
        ms_tokens: list[str] | None = None,
        proxies: list[dict[str, Any] | ProxySettings] | None = None,
        proxy_provider: Optional[ProxyProvider] = None,
        proxy_algorithm: Optional[Algorithm] = None,
        sleep_after: int = 1,
        starting_url: str = "https://www.tiktok.com",
        context_options: dict[str, Any] = {},
        override_browser_args: list[str] | None = None,
        cookies: list[dict[str, Any]] | None = None,
        suppress_resource_load_types: list[str] | None = None,
        browser: str = "chromium",
        executable_path: str | None = None,
        page_factory: Callable[[BrowserContext], Awaitable[Page]] | None = None,
        browser_context_factory: (
            Callable[[Playwright], Awaitable[BrowserContext]] | None
        ) = None,
        timeout: int = 30000,
        enable_session_recovery: bool = True,
        allow_partial_sessions: bool = False,
        min_sessions: int | None = None,
    ):
        """
        Create sessions for use within the TikTokApi class.

        These sessions are what will carry out requesting your data from TikTok.

        Args:
            num_sessions (int): The amount of sessions you want to create.
            headless (bool): Whether or not you want the browser to be headless.
            ms_tokens (list[str]): A list of msTokens to use for the sessions, you can get these from your cookies after visiting TikTok.
                                   If you don't provide any, the sessions will try to get them themselves, but this is not guaranteed to work.
            proxies (list): **DEPRECATED - Use proxy_provider instead.** A list of proxies to use for the sessions.
                           This parameter is maintained for backwards compatibility but will be removed in a future version.
            proxy_provider (ProxyProvider | None): A ProxyProvider instance for smart proxy rotation.
                                                   See examples/proxy_provider_example.py for usage examples. Full documentation: https://davidteather.github.io/proxyproviders/
            proxy_algorithm (Algorithm | None): Algorithm for proxy selection (RoundRobin, Random, First, or custom) per session.
                                               Only used with proxy_provider. Defaults to RoundRobin if not specified.
            sleep_after (int): The amount of time to sleep after creating a session, this is to allow the msToken to be generated.
            starting_url (str): The url to start the sessions on, this is usually https://www.tiktok.com.
            context_options (dict): Options to pass to the playwright context.
            override_browser_args (list[dict]): A list of dictionaries containing arguments to pass to the browser.
            cookies (list[dict]): A list of cookies to use for the sessions, you can get these from your cookies after visiting TikTok.
            suppress_resource_load_types (list[str]): Types of resources to suppress playwright from loading, excluding more types will make playwright faster.. Types: document, stylesheet, image, media, font, script, textrack, xhr, fetch, eventsource, websocket, manifest, other.
            browser (str): firefox, chromium, or webkit; default is chromium
            executable_path (str): Path to the browser executable
            page_factory (Callable[[BrowserContext], Awaitable[Page]]) | None: Optional async function for instantiating pages.
            browser_context_factory (Callable[[Playwright], Awaitable[BrowserContext]]) | None: Optional async function for creating browser contexts. When provided, you can choose any browser (chromium/firefox/webkit) inside the factory, and the 'browser' parameter is ignored.
            timeout (int): The timeout in milliseconds for page navigation
            enable_session_recovery (bool): Enable automatic session recovery on failures (default: True)
            allow_partial_sessions (bool): If True, succeed even if some sessions fail to create. If False (default), fail if any session fails
            min_sessions (int | None): Minimum number of sessions required. Only used if allow_partial_sessions=True. If None, defaults to 1.

        Example Usage:
            .. code-block:: python

                from TikTokApi import TikTokApi

                async with TikTokApi() as api:
                    await api.create_sessions(num_sessions=5, ms_tokens=['msToken1', 'msToken2'])

        Proxy Provider Usage:
            For proxy provider examples with different algorithms and configurations,
            see examples/proxy_provider_example.py

        Custom Launchers:
            To implement custom functionality, such as login or captcha solving, when the session is being created,
            you may use the keyword arguments `browser_context_factory` and `page_factory`.
            These arguments are callable functions that TikTok-Api will use to launch your browser and pages,
            and allow you to perform custom actions on the page before the session is created.
            You can find examples in the test file: tests/test_custom_launchers.py
        """
        self._session_recovery_enabled = enable_session_recovery
        self._proxy_provider = proxy_provider
        self._proxy_algorithm = proxy_algorithm

        if proxies is not None and proxy_provider is not None:
            raise ValueError(
                "Cannot use both 'proxies' and 'proxy_provider' parameters. "
                "Please use 'proxy_provider' (recommended) or 'proxies' (deprecated)."
            )

        self.playwright = await async_playwright().start()
        if browser_context_factory is not None:
            self.browser = await browser_context_factory(self.playwright)
        elif browser == "chromium":
            if headless and override_browser_args is None:
                override_browser_args = ["--headless=new"]
                headless = False  # managed by the arg
            self.browser = await self.playwright.chromium.launch(
                headless=headless,
                args=override_browser_args,
                proxy=random_choice(proxies),
                executable_path=executable_path,
            )
        elif browser == "firefox":
            self.browser = await self.playwright.firefox.launch(
                headless=headless,
                args=override_browser_args,
                proxy=random_choice(proxies),
                executable_path=executable_path,
            )
        elif browser == "webkit":
            self.browser = await self.playwright.webkit.launch(
                headless=headless,
                args=override_browser_args,
                proxy=random_choice(proxies),
                executable_path=executable_path,
            )
        else:
            raise ValueError("Invalid browser argument passed")

        # Create sessions concurrently
        # Use return_exceptions only if partial sessions are allowed
        if allow_partial_sessions:
            results = await asyncio.gather(
                *(
                    self.__create_session(
                        proxy=(
                            random_choice(proxies) if proxy_provider is None else None
                        ),
                        ms_token=random_choice(ms_tokens),
                        url=starting_url,
                        context_options=context_options,
                        sleep_after=sleep_after,
                        cookies=random_choice(cookies),
                        suppress_resource_load_types=suppress_resource_load_types,
                        timeout=timeout,
                        page_factory=page_factory,
                        browser_context_factory=browser_context_factory,
                    )
                    for _ in range(num_sessions)
                ),
                return_exceptions=True,
            )

            # Count failures and provide feedback
            failed_count = sum(1 for r in results if isinstance(r, Exception))
            success_count = len(self.sessions)
            minimum_required = min_sessions if min_sessions is not None else 1

            if success_count < minimum_required:
                # Didn't meet minimum requirements
                error_messages = [str(r) for r in results if isinstance(r, Exception)]
                raise Exception(
                    f"Failed to create minimum required sessions. "
                    f"Created {success_count}/{num_sessions}, needed at least {minimum_required}.\n"
                    f"Errors: {error_messages[:3]}"  # Show first 3 errors
                )
            elif failed_count > 0:
                # Some sessions failed but we have enough - log warning and continue
                self.logger.warning(
                    f"Created {success_count}/{num_sessions} sessions successfully. "
                    f"{failed_count} session(s) failed to create."
                )
                # Log individual errors at debug level
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        self.logger.debug(f"Session {i} creation failed: {result}")
        else:
            await asyncio.gather(
                *(
                    self.__create_session(
                        proxy=(
                            random_choice(proxies) if proxy_provider is None else None
                        ),
                        ms_token=random_choice(ms_tokens),
                        url=starting_url,
                        context_options=context_options,
                        sleep_after=sleep_after,
                        cookies=random_choice(cookies),
                        suppress_resource_load_types=suppress_resource_load_types,
                        timeout=timeout,
                        page_factory=page_factory,
                        browser_context_factory=browser_context_factory,
                    )
                    for _ in range(num_sessions)
                )
            )

    async def close_sessions(self):
        """
        Close all the sessions. Should be called when you're done with the TikTokApi object

        This is called automatically when using the TikTokApi with "with"
        """
        self.logger.debug(f"Closing {len(self.sessions)} sessions...")

        for session in self.sessions:
            try:
                if session.page:
                    await session.page.close()
            except Exception as e:
                self.logger.debug(f"Error closing page: {e}")

            try:
                if session.context:
                    await session.context.close()
            except Exception as e:
                self.logger.debug(f"Error closing context: {e}")

        self.sessions.clear()

        try:
            if self.browser:
                await self.browser.close()
                self.browser = None
        except Exception as e:
            self.logger.debug(f"Error closing browser: {e}")

        try:
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
        except Exception as e:
            self.logger.debug(f"Error stopping playwright: {e}")

        self._cleanup_called = True
        self.logger.debug("All sessions and browser resources closed successfully")

    def generate_js_fetch(self, method: str, url: str, headers: dict) -> str:
        """Generate a javascript fetch function for use in playwright"""
        headers_js = json.dumps(headers)
        return f"""
            () => {{
                return new Promise((resolve, reject) => {{
                    fetch('{url}', {{ method: '{method}', headers: {headers_js} }})
                        .then(response => response.text())
                        .then(data => resolve(data))
                        .catch(error => reject(error.message));
                }});
            }}
        """

    def _get_session(self, **kwargs):
        """Get a random session

        DEPRECATED: Use _get_valid_session_index() for better error handling

        Args:
            session_index (int): The index of the session you want to use, if not provided a random session will be used.

        Returns:
            int: The index of the session.
            TikTokPlaywrightSession: The session.
        """
        if len(self.sessions) == 0:
            raise Exception("No sessions created, please create sessions first")

        if kwargs.get("session_index") is not None:
            i = kwargs["session_index"]
        else:
            i = random.randint(0, len(self.sessions) - 1)
        return i, self.sessions[i]

    async def set_session_cookies(self, session, cookies):
        """
        Set the cookies for a session

        Args:
            session (TikTokPlaywrightSession): The session to set the cookies for.
            cookies (dict): The cookies to set for the session.
        """
        await session.context.add_cookies(cookies)

    async def get_session_cookies(self, session):
        """
        Get the cookies for a session

        Args:
            session (TikTokPlaywrightSession): The session to get the cookies for.

        Returns:
            dict: The cookies for the session.
        """
        cookies = await session.context.cookies()
        return {cookie["name"]: cookie["value"] for cookie in cookies}

    async def run_fetch_script(self, url: str, headers: dict, **kwargs):
        """
        Execute a javascript fetch function in a session

        Args:
            url (str): The url to fetch.
            headers (dict): The headers to use for the fetch.

        Returns:
            any: The result of the fetch. Seems to be a string or dict
        """
        js_script = self.generate_js_fetch("GET", url, headers)

        try:
            _, session = await self._get_valid_session_index(**kwargs)
        except Exception:
            # Fallback to old method for backwards compatibility
            _, session = self._get_session(**kwargs)

        try:
            result = await session.page.evaluate(js_script)
            return result
        except PlaywrightError as e:
            # Session died during operation
            self.logger.error(f"Session failed during fetch: {e}")
            await self._mark_session_invalid(session)
            raise

    async def generate_x_bogus(self, url: str, **kwargs):
        """Generate the X-Bogus header for a url"""
        try:
            _, session = await self._get_valid_session_index(**kwargs)
        except Exception:
            # Fallback to old method for backwards compatibility
            _, session = self._get_session(**kwargs)

        max_attempts = 5
        attempts = 0
        while attempts < max_attempts:
            attempts += 1
            try:
                timeout_time = random.randint(5000, 20000)
                await session.page.wait_for_function(
                    "window.byted_acrawler !== undefined", timeout=timeout_time
                )
                break
            except TimeoutError as e:
                if attempts == max_attempts:
                    raise TimeoutError(
                        f"Failed to load tiktok after {max_attempts} attempts, consider using a proxy"
                    )

                try_urls = [
                    "https://www.tiktok.com/foryou",
                    "https://www.tiktok.com",
                    "https://www.tiktok.com/@tiktok",
                    "https://www.tiktok.com/foryou",
                ]

                await session.page.goto(random.choice(try_urls))
            except PlaywrightError as e:
                # Session died
                self.logger.error(f"Session died during x-bogus generation: {e}")
                await self._mark_session_invalid(session)
                raise

        try:
            result = await session.page.evaluate(
                f'() => {{ return window.byted_acrawler.frontierSign("{url}") }}'
            )
            return result
        except PlaywrightError as e:
            # Session died during operation
            self.logger.error(f"Session died during x-bogus evaluation: {e}")
            await self._mark_session_invalid(session)
            raise

    async def sign_url(self, url: str, **kwargs):
        """Sign a url"""
        try:
            i, session = await self._get_valid_session_index(**kwargs)
        except Exception:
            # Fallback to old method for backwards compatibility
            i, session = self._get_session(**kwargs)

        # TODO: Would be nice to generate msToken here

        # Add X-Bogus to url
        x_bogus = (await self.generate_x_bogus(url, session_index=i)).get("X-Bogus")
        if x_bogus is None:
            raise Exception("Failed to generate X-Bogus")

        if "?" in url:
            url += "&"
        else:
            url += "?"
        url += f"X-Bogus={x_bogus}"

        return url

    async def make_request(
        self,
        url: str,
        headers: dict = None,
        params: dict = None,
        retries: int = 3,
        exponential_backoff: bool = True,
        **kwargs,
    ):
        """
        Makes a request to TikTok through a session.

        Args:
            url (str): The url to make the request to.
            headers (dict): The headers to use for the request.
            params (dict): The params to use for the request.
            retries (int): The amount of times to retry the request if it fails.
            exponential_backoff (bool): Whether or not to use exponential backoff when retrying the request.
            session_index (int): The index of the session you want to use, if not provided a random session will be used.

        Returns:
            dict: The json response from TikTok.

        Raises:
            Exception: If the request fails.
        """
        try:
            i, session = await self._get_valid_session_index(**kwargs)
        except Exception:
            # Fallback to old method for backwards compatibility
            i, session = self._get_session(**kwargs)

        if session.params is not None:
            params = {**session.params, **params}

        if headers is not None:
            headers = {**session.headers, **headers}
        else:
            headers = session.headers

        # get msToken
        if params.get("msToken") is None:
            # try to get msToken from session
            if session.ms_token is not None:
                params["msToken"] = session.ms_token
            else:
                # we'll try to read it from cookies
                cookies = await self.get_session_cookies(session)
                ms_token = cookies.get("msToken")
                if ms_token is None:
                    self.logger.warn(
                        "Failed to get msToken from cookies, trying to make the request anyway (probably will fail)"
                    )
                params["msToken"] = ms_token

        encoded_params = f"{url}?{urlencode(params, safe='=', quote_via=quote)}"
        signed_url = await self.sign_url(encoded_params, session_index=i)

        retry_count = 0
        while retry_count < retries:
            retry_count += 1
            try:
                result = await self.run_fetch_script(
                    signed_url, headers=headers, session_index=i
                )

                if result is None:
                    raise Exception("TikTokApi.run_fetch_script returned None")

                if result == "":
                    raise EmptyResponseException(
                        result,
                        "TikTok returned an empty response. They are detecting you're a bot, try some of these: headless=False, browser='webkit', consider using a proxy",
                    )

                try:
                    data = json.loads(result)
                    if data.get("status_code") != 0:
                        self.logger.error(f"Got an unexpected status code: {data}")
                    return data
                except json.decoder.JSONDecodeError:
                    if retry_count == retries:
                        self.logger.error(f"Failed to decode json response: {result}")
                        raise InvalidJSONException()

                    self.logger.info(
                        f"Failed a request, retrying ({retry_count}/{retries})"
                    )
                    if exponential_backoff:
                        await asyncio.sleep(2**retry_count)
                    else:
                        await asyncio.sleep(1)
            except PlaywrightError as e:
                # Session died during request
                self.logger.error(f"Playwright error during request: {e}")
                await self._mark_session_invalid(session)

                if retry_count < retries:
                    self.logger.info(
                        f"Retrying with a new session ({retry_count}/{retries})"
                    )
                    # Get a new valid session for the retry
                    try:
                        i, session = await self._get_valid_session_index(**kwargs)
                    except Exception as session_error:
                        self.logger.error(
                            f"Failed to get valid session: {session_error}"
                        )
                        raise
                else:
                    raise

    async def stop_playwright(self):
        """
        Stop the playwright browser.

        Note: It's better to use close_sessions() which calls this automatically.
        """
        try:
            if self.browser:
                await self.browser.close()
                self.browser = None
        except Exception as e:
            self.logger.debug(f"Error closing browser: {e}")

        try:
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
        except Exception as e:
            self.logger.debug(f"Error stopping playwright: {e}")

    async def get_session_content(self, url: str, **kwargs):
        """Get the content of a url"""
        try:
            _, session = await self._get_valid_session_index(**kwargs)
        except Exception:
            # Fallback to old method
            _, session = self._get_session(**kwargs)

        try:
            return await session.page.content()
        except PlaywrightError as e:
            self.logger.error(f"Session died during get_session_content: {e}")
            await self._mark_session_invalid(session)
            raise

    def get_resource_stats(self) -> dict:
        """
        Get statistics about current resource usage.

        Useful for monitoring and detecting potential memory leaks.

        Returns:
            dict: Statistics including session count, browser status, etc.
        """
        valid_sessions = sum(1 for s in self.sessions if s.is_valid)
        invalid_sessions = len(self.sessions) - valid_sessions

        return {
            "total_sessions": len(self.sessions),
            "valid_sessions": valid_sessions,
            "invalid_sessions": invalid_sessions,
            "has_browser": self.browser is not None,
            "has_playwright": self.playwright is not None,
            "cleanup_called": self._cleanup_called,
            "auto_cleanup_enabled": self._auto_cleanup_dead_sessions,
            "recovery_enabled": self._session_recovery_enabled,
        }

    async def health_check(self) -> dict:
        """
        Perform a health check on all resources.

        This actively validates all sessions and returns detailed health info.
        Useful for monitoring and debugging.

        Returns:
            dict: Health check results
        """
        health = self.get_resource_stats()

        # Actively validate all sessions
        session_health = []
        for i, session in enumerate(self.sessions):
            is_valid = await self._is_session_valid(session)
            session_health.append(
                {
                    "index": i,
                    "valid": is_valid,
                    "marked_valid": session.is_valid,
                }
            )

        health["session_details"] = session_health
        health["healthy_sessions"] = sum(1 for s in session_health if s["valid"])

        # Check for potential leaks
        if health["invalid_sessions"] > 0 and not self._auto_cleanup_dead_sessions:
            health["warning"] = (
                f"{health['invalid_sessions']} invalid sessions accumulating (auto-cleanup disabled)"
            )

        return health

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        """Ensure cleanup happens when exiting context manager"""
        await self.close_sessions()
        # stop_playwright is already called by close_sessions, but call it again for safety
        if not self._cleanup_called:
            await self.stop_playwright()
