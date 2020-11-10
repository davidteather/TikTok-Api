from gevent import monkey
monkey.patch_all()
from flask import Flask, request, jsonify
from TikTokApi import TikTokApi
from TikTokApi import browser

import random

proxy = None

signing_browser = browser.browser(proxy=proxy)

app = Flask(__name__)

@app.route('/sign', methods=['GET'])
def sign_url():
    url = request.args.get("url")
    did = request.args.get("custom_did", None)
    if url == None:
        return jsonify({'success': False, 'error': 'You must provide a URL'})

    if did != None:
        did = str(random.randint(10000, 999999999))
    verifyFp, did, _signature = signing_browser.sign_url(url=url, custom_did=did)

    return jsonify({
        'verifyFp': verifyFp,
        'did': did,
        '_signature': _signature,
        'userAgent': signing_browser.userAgent,
        'referrer': signing_browser.referrer
    })

if __name__ == "__main__":
    app.run(debug=False, port=5000, host="0.0.0.0", threaded=True)
    print('Cleaning Up')
    try:
        signing_browser.clean_up()
    except:
        pass
    try:
        browser.get_playwright().stop()
    except:
        pass

# Example script below for production use

# from TikTokApi import TikTokApi
# api = TikTokApi(external_signer="http://localhost:5000/sign")
# print(api.trending())