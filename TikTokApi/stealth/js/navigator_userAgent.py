navigator_userAgent = """
// replace Headless references in default useragent
const current_ua = navigator.userAgent;
Object.defineProperty(Object.getPrototypeOf(navigator), 'userAgent', {
    get: () => {
        try {
            if (typeof opts !== 'undefined' && opts.navigator_user_agent) {
                return opts.navigator_user_agent;
            }
        } catch (error) {
            console.warn('Error accessing opts:', error);
        }
        return current_ua.replace('HeadlessChrome/', 'Chrome/');
    }
});
"""
