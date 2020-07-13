import asyncio
import pyppeteer
import random
import time
import json
import string
import atexit
import requests

from .signer import signer

# Import Detection From Stealth
from .stealth import stealth

class browser:
    def __init__(self, url=None, language='en', proxy=None, debug=False, signerObject=None):
        
        loop = asyncio.new_event_loop()
        if signerObject != None:
            signerObject.loop.create_task(signerObject.sign_url(url))
        else:
            s = signer(proxy=proxy, debug=debug, language=language)
            loop.run_until_complete( self.await_sign(url, proxy, debug, language, s) )
            

    async def await_sign(self, url, proxy, debug, language, s):
        await s.start()
        self.verifyFp, self.signature = await s.sign_url(url)
        self.referrer = s.referrer
        self.userAgent = s.userAgent
        await s.close_browser()

    async def await_multi_sign(self, url, signerObject):
        self.verifyFp, self.signature = await signerObject.sign_url(url) 