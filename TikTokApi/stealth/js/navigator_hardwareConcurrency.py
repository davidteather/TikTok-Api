navigator_hardwareConcurrency = """
const patchNavigator = (name, value) =>
    utils.replaceProperty(Object.getPrototypeOf(navigator), name, {
        get() {
            return value
        }
    })

patchNavigator('hardwareConcurrency', opts.navigator_hardware_concurrency || 4);
"""
