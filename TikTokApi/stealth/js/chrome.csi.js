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

// Check if we're running headful and don't need to mock anything
// Check that the Navigation Timing API v1 is available, we need that
if (!('csi' in window.chrome) && (window.performance || window.performance.timing)) {
    const {csi_timing} = window.performance

    log.info('loading chrome.csi.js')
    window.chrome.csi = function () {
        return {
            onloadT: csi_timing.domContentLoadedEventEnd,
            startE: csi_timing.navigationStart,
            pageT: Date.now() - csi_timing.navigationStart,
            tran: 15 // Transition type or something
        }
    }
    utils.patchToString(window.chrome.csi)
}