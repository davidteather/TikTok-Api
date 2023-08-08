// replace Headless references in default useragent
const current_ua = navigator.userAgent
Object.defineProperty(Object.getPrototypeOf(navigator), 'userAgent', {
    get: () => opts.navigator_user_agent || current_ua.replace('HeadlessChrome/', 'Chrome/')
})
