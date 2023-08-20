navigator_platform = """
if (opts.navigator_platform) {
    Object.defineProperty(Object.getPrototypeOf(navigator), 'platform', {
        get: () => opts.navigator_plaftorm,
    })
}
"""
