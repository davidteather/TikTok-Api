navigator_vendor = """
Object.defineProperty(Object.getPrototypeOf(navigator), 'vendor', {
    get: () => opts.navigator_vendor || 'Google Inc.',
})

"""
