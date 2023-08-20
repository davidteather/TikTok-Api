generate_magic_arrays = """
generateFunctionMocks = (
    proto,
    itemMainProp,
    dataArray
) => ({
    item: utils.createProxy(proto.item, {
        apply(target, ctx, args) {
            if (!args.length) {
                throw new TypeError(
                    `Failed to execute 'item' on '${
                        proto[Symbol.toStringTag]
                    }': 1 argument required, but only 0 present.`
                )
            }
            // Special behavior alert:
            // - Vanilla tries to cast strings to Numbers (only integers!) and use them as property index lookup
            // - If anything else than an integer (including as string) is provided it will return the first entry
            const isInteger = args[0] && Number.isInteger(Number(args[0])) // Cast potential string to number first, then check for integer
            // Note: Vanilla never returns `undefined`
            return (isInteger ? dataArray[Number(args[0])] : dataArray[0]) || null
        }
    }),
    /** Returns the MimeType object with the specified name. */
    namedItem: utils.createProxy(proto.namedItem, {
        apply(target, ctx, args) {
            if (!args.length) {
                throw new TypeError(
                    `Failed to execute 'namedItem' on '${
                        proto[Symbol.toStringTag]
                    }': 1 argument required, but only 0 present.`
                )
            }
            return dataArray.find(mt => mt[itemMainProp] === args[0]) || null // Not `undefined`!
        }
    }),
    /** Does nothing and shall return nothing */
    refresh: proto.refresh
        ? utils.createProxy(proto.refresh, {
            apply(target, ctx, args) {
                return undefined
            }
        })
        : undefined
})

function generateMagicArray(
    dataArray = [],
    proto = MimeTypeArray.prototype,
    itemProto = MimeType.prototype,
    itemMainProp = 'type'
) {
    // Quick helper to set props with the same descriptors vanilla is using
    const defineProp = (obj, prop, value) =>
        Object.defineProperty(obj, prop, {
            value,
            writable: false,
            enumerable: false, // Important for mimeTypes & plugins: `JSON.stringify(navigator.mimeTypes)`
            configurable: false
        })

    // Loop over our fake data and construct items
    const makeItem = data => {
        const item = {}
        for (const prop of Object.keys(data)) {
            if (prop.startsWith('__')) {
                continue
            }
            defineProp(item, prop, data[prop])
        }
        // navigator.plugins[i].length should always be 1
        if (itemProto === Plugin.prototype) {
            defineProp(item, 'length', 1)
        }
        // We need to spoof a specific `MimeType` or `Plugin` object
        return Object.create(itemProto, Object.getOwnPropertyDescriptors(item))
    }

    const magicArray = []

    // Loop through our fake data and use that to create convincing entities
    dataArray.forEach(data => {
        magicArray.push(makeItem(data))
    })

    // Add direct property access  based on types (e.g. `obj['application/pdf']`) afterwards
    magicArray.forEach(entry => {
        defineProp(magicArray, entry[itemMainProp], entry)
    })

    // This is the best way to fake the type to make sure this is false: `Array.isArray(navigator.mimeTypes)`
    const magicArrayObj = Object.create(proto, {
        ...Object.getOwnPropertyDescriptors(magicArray),

        // There's one ugly quirk we unfortunately need to take care of:
        // The `MimeTypeArray` prototype has an enumerable `length` property,
        // but headful Chrome will still skip it when running `Object.getOwnPropertyNames(navigator.mimeTypes)`.
        // To strip it we need to make it first `configurable` and can then overlay a Proxy with an `ownKeys` trap.
        length: {
            value: magicArray.length,
            writable: false,
            enumerable: false,
            configurable: true // Important to be able to use the ownKeys trap in a Proxy to strip `length`
        }
    })

    // Generate our functional function mocks :-)
    const functionMocks = generateFunctionMocks(
        proto,
        itemMainProp,
        magicArray
    )

    // Override custom object with proxy
    return new Proxy(magicArrayObj, {
        get(target, key = '') {
            // Redirect function calls to our custom proxied versions mocking the vanilla behavior
            if (key === 'item') {
                return functionMocks.item
            }
            if (key === 'namedItem') {
                return functionMocks.namedItem
            }
            if (proto === PluginArray.prototype && key === 'refresh') {
                return functionMocks.refresh
            }
            // Everything else can pass through as normal
            return utils.cache.Reflect.get(...arguments)
        },
        ownKeys(target) {
            // There are a couple of quirks where the original property demonstrates "magical" behavior that makes no sense
            // This can be witnessed when calling `Object.getOwnPropertyNames(navigator.mimeTypes)` and the absense of `length`
            // My guess is that it has to do with the recent change of not allowing data enumeration and this being implemented weirdly
            // For that reason we just completely fake the available property names based on our data to match what regular Chrome is doing
            // Specific issues when not patching this: `length` property is available, direct `types` props (e.g. `obj['application/pdf']`) are missing
            const keys = []
            const typeProps = magicArray.map(mt => mt[itemMainProp])
            typeProps.forEach((_, i) => keys.push(`${i}`))
            typeProps.forEach(propName => keys.push(propName))
            return keys
        }
    })
}
"""
