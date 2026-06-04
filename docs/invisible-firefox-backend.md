# Stealth patched-Firefox session option (proposal)

> Status: Draft proposal / interest check
> Tracking discussion: TBD

## Goal

Let create_sessions run against a fingerprint-patched Firefox 150 binary for the
cases where TikTok throws CaptchaException / returns an empty response on the
default chromium session.

## Why this is basically zero-cost here

create_sessions already takes both knobs needed:

```python
async def create_sessions(
    ...
    browser: str = "chromium",          # firefox, chromium, or webkit
    executable_path: str | None = None,
    ...
):
    ...
    elif browser == "firefox":
        self.browser = await self.playwright.firefox.launch(
            ...
            executable_path=executable_path,
        )
```

So pointing the API at a patched firefox is already possible today:

```python
await api.create_sessions(
    num_sessions=5,
    browser="firefox",
    executable_path="/path/to/patched/firefox",
    # firefox_user_prefs would carry the spoof config (see caveat below)
)
```

The only gap is `firefox_user_prefs`: the patched binary is fully pref-driven, so
the spoof values are selected via Firefox prefs. Right now `firefox.launch(...)`
in tiktok.py doesn't forward a `firefox_user_prefs` argument. Passing it through
(one kwarg on the firefox branch) is the whole change.

## Why a patched binary vs default chromium/firefox

The empty-response path in tiktok.py already tells users "they are detecting
you're a bot, try headless=False, browser='webkit'..." which is the right
instinct: swap the engine. The patched firefox goes further than swapping to
stock firefox/webkit because the fingerprint patches are applied at the C++
source level (canvas readback, webgl getParameter, font metrics, audio,
navigator, system colors). no JS shim, no CDP attach signature, values come back
through the normal Gecko paths with nothing for the detector to enumerate.

The binary lives at https://github.com/feder-cr/invisible_firefox (MPL-2, same
license family as Firefox upstream) and auto-downloads on first run.

## Out of scope

No change to the default chromium session. Firefox-stealth stays opt-in via the
existing `browser=` / `executable_path=` args.

## Honest caveats

- helps the fingerprint/engine layer only. it does not solve IP reputation or a
  per-account ban once TikTok has flagged it.
- the only code change is forwarding `firefox_user_prefs` to the existing
  `firefox.launch(...)` call; everything else (sessions, ms_tokens, contexts) is
  unchanged.

If forwarding `firefox_user_prefs` + a docs example is in scope, i can wire it.
If not, happy to close without noise.
