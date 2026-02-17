from .exceptions import *

import requests
import random


def random_choice(choices: list):
    """Return a random choice from a list, or None if the list is empty"""
    if choices is None or len(choices) == 0:
        return None
    return random.choice(choices)


def requests_cookie_to_playwright_cookie(req_c):
    c = {
        "name": req_c.name,
        "value": req_c.value,
        "domain": req_c.domain,
        "path": req_c.path,
        "secure": req_c.secure,
    }
    if req_c.expires:
        c["expires"] = req_c.expires
    return c
