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

// app in window.chrome means we're running headful and don't need to mock anything
if (!('app' in window.chrome)) {
    const makeError = {
        ErrorInInvocation: fn => {
            const err = new TypeError(`Error in invocation of app.${fn}()`)
            return utils.stripErrorWithAnchor(
                err,
                `at ${fn} (eval at <anonymous>`
            )
        }
    }

// There's a some static data in that property which doesn't seem to change,
// we should periodically check for updates: `JSON.stringify(window.app, null, 2)`
    const APP_STATIC_DATA = JSON.parse(
        `
{
  "isInstalled": false,
  "InstallState": {
    "DISABLED": "disabled",
    "INSTALLED": "installed",
    "NOT_INSTALLED": "not_installed"
  },
  "RunningState": {
    "CANNOT_RUN": "cannot_run",
    "READY_TO_RUN": "ready_to_run",
    "RUNNING": "running"
  }
}
        `.trim()
    )

    window.chrome.app = {
        ...APP_STATIC_DATA,

        get isInstalled() {
            return false
        },

        getDetails: function getDetails() {
            if (arguments.length) {
                throw makeError.ErrorInInvocation(`getDetails`)
            }
            return null
        },
        getIsInstalled: function getDetails() {
            if (arguments.length) {
                throw makeError.ErrorInInvocation(`getIsInstalled`)
            }
            return false
        },
        runningState: function getDetails() {
            if (arguments.length) {
                throw makeError.ErrorInInvocation(`runningState`)
            }
            return 'cannot_run'
        }
    }
    utils.patchToStringNested(window.chrome.app)
}