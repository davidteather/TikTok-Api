if (!window.chrome) {
    // Use the exact property descriptor found in headful Chrome
    // fetch it via `Object.getOwnPropertyDescriptor(window, 'chrome')`
    Object.defineProperty(window, 'chrome', {
        writable: true,
        enumerable: true,
        configurable: false, // note!
        value: {} // We'll extend that later
    })
}

// That means we're running headful and don't need to mock anything
if ('loadTimes' in window.chrome) {
    throw new Error('skipping chrome loadtimes update, running in headfull mode')
}

// Check that the Navigation Timing API v1 + v2 is available, we need that
if (
    window.performance ||
    window.performance.timing ||
    window.PerformancePaintTiming
) {

    const {performance} = window

    // Some stuff is not available on about:blank as it requires a navigation to occur,
    // let's harden the code to not fail then:
    const ntEntryFallback = {
        nextHopProtocol: 'h2',
        type: 'other'
    }

    // The API exposes some funky info regarding the connection
    const protocolInfo = {
        get connectionInfo() {
            const ntEntry =
                performance.getEntriesByType('navigation')[0] || ntEntryFallback
            return ntEntry.nextHopProtocol
        },
        get npnNegotiatedProtocol() {
            // NPN is deprecated in favor of ALPN, but this implementation returns the
            // HTTP/2 or HTTP2+QUIC/39 requests negotiated via ALPN.
            const ntEntry =
                performance.getEntriesByType('navigation')[0] || ntEntryFallback
            return ['h2', 'hq'].includes(ntEntry.nextHopProtocol)
                ? ntEntry.nextHopProtocol
                : 'unknown'
        },
        get navigationType() {
            const ntEntry =
                performance.getEntriesByType('navigation')[0] || ntEntryFallback
            return ntEntry.type
        },
        get wasAlternateProtocolAvailable() {
            // The Alternate-Protocol header is deprecated in favor of Alt-Svc
            // (https://www.mnot.net/blog/2016/03/09/alt-svc), so technically this
            // should always return false.
            return false
        },
        get wasFetchedViaSpdy() {
            // SPDY is deprecated in favor of HTTP/2, but this implementation returns
            // true for HTTP/2 or HTTP2+QUIC/39 as well.
            const ntEntry =
                performance.getEntriesByType('navigation')[0] || ntEntryFallback
            return ['h2', 'hq'].includes(ntEntry.nextHopProtocol)
        },
        get wasNpnNegotiated() {
            // NPN is deprecated in favor of ALPN, but this implementation returns true
            // for HTTP/2 or HTTP2+QUIC/39 requests negotiated via ALPN.
            const ntEntry =
                performance.getEntriesByType('navigation')[0] || ntEntryFallback
            return ['h2', 'hq'].includes(ntEntry.nextHopProtocol)
        }
    }

    const {timing} = window.performance

// Truncate number to specific number of decimals, most of the `loadTimes` stuff has 3
    function toFixed(num, fixed) {
        var re = new RegExp('^-?\\d+(?:.\\d{0,' + (fixed || -1) + '})?')
        return num.toString().match(re)[0]
    }

    const timingInfo = {
        get firstPaintAfterLoadTime() {
            // This was never actually implemented and always returns 0.
            return 0
        },
        get requestTime() {
            return timing.navigationStart / 1000
        },
        get startLoadTime() {
            return timing.navigationStart / 1000
        },
        get commitLoadTime() {
            return timing.responseStart / 1000
        },
        get finishDocumentLoadTime() {
            return timing.domContentLoadedEventEnd / 1000
        },
        get finishLoadTime() {
            return timing.loadEventEnd / 1000
        },
        get firstPaintTime() {
            const fpEntry = performance.getEntriesByType('paint')[0] || {
                startTime: timing.loadEventEnd / 1000 // Fallback if no navigation occured (`about:blank`)
            }
            return toFixed(
                (fpEntry.startTime + performance.timeOrigin) / 1000,
                3
            )
        }
    }

    window.chrome.loadTimes = function () {
        return {
            ...protocolInfo,
            ...timingInfo
        }
    }
    utils.patchToString(window.chrome.loadTimes)
}