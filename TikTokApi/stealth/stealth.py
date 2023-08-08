# -*- coding: utf-8 -*-
import json
from dataclasses import dataclass
from typing import Tuple, Optional, Dict

from playwright.async_api import Page as AsyncPage

from .js.chrome_app import chrome_app
from .js.chrome_csi import chrome_csi
from .js.chrome_hairline import chrome_hairline
from .js.chrome_load_times import chrome_load_times
from .js.chrome_runtime import chrome_runtime
from .js.generate_magic_arrays import generate_magic_arrays
from .js.iframe_contentWindow import iframe_contentWindow
from .js.media_codecs import media_codecs
from .js.navigator_hardwareConcurrency import navigator_hardwareConcurrency
from .js.navigator_languages import navigator_languages
from .js.navigator_permissions import navigator_permissions
from .js.navigator_platform import navigator_platform
from .js.navigator_plugins import navigator_plugins
from .js.navigator_userAgent import navigator_userAgent
from .js.navigator_vendor import navigator_vendor
from .js.webgl_vendor import webgl_vendor
from .js.window_outerdimensions import window_outerdimensions
from .js.utils import utils

SCRIPTS: Dict[str, str] = {
    "chrome_csi": chrome_csi,
    "chrome_app": chrome_app,
    "chrome_runtime": chrome_runtime,
    "chrome_load_times": chrome_load_times,
    "chrome_hairline": chrome_hairline,
    "generate_magic_arrays": generate_magic_arrays,
    "iframe_content_window": iframe_contentWindow,
    "media_codecs": media_codecs,
    "navigator_vendor": navigator_vendor,
    "navigator_plugins": navigator_plugins,
    "navigator_permissions": navigator_permissions,
    "navigator_languages": navigator_languages,
    "navigator_platform": navigator_platform,
    "navigator_user_agent": navigator_userAgent,
    "navigator_hardware_concurrency": navigator_hardwareConcurrency,
    "outerdimensions": window_outerdimensions,
    "utils": utils,
    "webdriver": "delete Object.getPrototypeOf(navigator).webdriver",
    "webgl_vendor": webgl_vendor,
}


@dataclass
class StealthConfig:
    """
    Playwright stealth configuration that applies stealth strategies to playwright page objects.
    The stealth strategies are contained in ./js package and are basic javascript scripts that are executed
    on every page.goto() called.
    Note:
        All init scripts are combined by playwright into one script and then executed this means
        the scripts should not have conflicting constants/variables etc. !
        This also means scripts can be extended by overriding enabled_scripts generator:
        ```
        @property
        def enabled_scripts():
            yield 'console.log("first script")'
            yield from super().enabled_scripts()
            yield 'console.log("last script")'
        ```
    """

    # load script options
    webdriver: bool = True
    webgl_vendor: bool = True
    chrome_app: bool = True
    chrome_csi: bool = True
    chrome_load_times: bool = True
    chrome_runtime: bool = True
    iframe_content_window: bool = True
    media_codecs: bool = True
    navigator_hardware_concurrency: int = 4
    navigator_languages: bool = True
    navigator_permissions: bool = True
    navigator_platform: bool = True
    navigator_plugins: bool = True
    navigator_user_agent: bool = True
    navigator_vendor: bool = True
    outerdimensions: bool = True
    hairline: bool = True

    # options
    vendor: str = "Intel Inc."
    renderer: str = "Intel Iris OpenGL Engine"
    nav_vendor: str = "Google Inc."
    nav_user_agent: str = None
    nav_platform: str = None
    languages: Tuple[str] = ("en-US", "en")
    runOnInsecureOrigins: Optional[bool] = None

    @property
    def enabled_scripts(self):
        opts = json.dumps(
            {
                "webgl_vendor": self.vendor,
                "webgl_renderer": self.renderer,
                "navigator_vendor": self.nav_vendor,
                "navigator_platform": self.nav_platform,
                "navigator_user_agent": self.nav_user_agent,
                "languages": list(self.languages),
                "runOnInsecureOrigins": self.runOnInsecureOrigins,
            }
        )
        # defined options constant
        yield f"const opts = {opts}"
        # init utils and generate_magic_arrays helper
        yield SCRIPTS["utils"]
        yield SCRIPTS["generate_magic_arrays"]

        if self.chrome_app:
            yield SCRIPTS["chrome_app"]
        if self.chrome_csi:
            yield SCRIPTS["chrome_csi"]
        if self.hairline:
            yield SCRIPTS["chrome_hairline"]
        if self.chrome_load_times:
            yield SCRIPTS["chrome_load_times"]
        if self.chrome_runtime:
            yield SCRIPTS["chrome_runtime"]
        if self.iframe_content_window:
            yield SCRIPTS["iframe_content_window"]
        if self.media_codecs:
            yield SCRIPTS["media_codecs"]
        if self.navigator_languages:
            yield SCRIPTS["navigator_languages"]
        if self.navigator_permissions:
            yield SCRIPTS["navigator_permissions"]
        if self.navigator_platform:
            yield SCRIPTS["navigator_platform"]
        if self.navigator_plugins:
            yield SCRIPTS["navigator_plugins"]
        if self.navigator_user_agent:
            yield SCRIPTS["navigator_user_agent"]
        if self.navigator_vendor:
            yield SCRIPTS["navigator_vendor"]
        if self.webdriver:
            yield SCRIPTS["webdriver"]
        if self.outerdimensions:
            yield SCRIPTS["outerdimensions"]
        if self.webgl_vendor:
            yield SCRIPTS["webgl_vendor"]


async def stealth_async(page: AsyncPage, config: StealthConfig = None):
    """stealth the page"""
    for script in (config or StealthConfig()).enabled_scripts:
        await page.add_init_script(script)
