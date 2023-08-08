Object.defineProperty(Object.getPrototypeOf(navigator), 'languages', {
    get: () => opts.languages || ['en-US', 'en']
})
