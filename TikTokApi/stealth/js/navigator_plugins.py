navigator_plugins = """
data = {
    "mimeTypes": [
        {
            "type": "application/pdf",
            "suffixes": "pdf",
            "description": "",
            "__pluginName": "Chrome PDF Viewer"
        },
        {
            "type": "application/x-google-chrome-pdf",
            "suffixes": "pdf",
            "description": "Portable Document Format",
            "__pluginName": "Chrome PDF Plugin"
        },
        {
            "type": "application/x-nacl",
            "suffixes": "",
            "description": "Native Client Executable",
            "__pluginName": "Native Client"
        },
        {
            "type": "application/x-pnacl",
            "suffixes": "",
            "description": "Portable Native Client Executable",
            "__pluginName": "Native Client"
        }
    ],
    "plugins": [
        {
            "name": "Chrome PDF Plugin",
            "filename": "internal-pdf-viewer",
            "description": "Portable Document Format",
            "__mimeTypes": ["application/x-google-chrome-pdf"]
        },
        {
            "name": "Chrome PDF Viewer",
            "filename": "mhjfbmdgcfjbbpaeojofohoefgiehjai",
            "description": "",
            "__mimeTypes": ["application/pdf"]
        },
        {
            "name": "Native Client",
            "filename": "internal-nacl-plugin",
            "description": "",
            "__mimeTypes": ["application/x-nacl", "application/x-pnacl"]
        }
    ]
}


// That means we're running headful
const hasPlugins = 'plugins' in navigator && navigator.plugins.length
if (!(hasPlugins)) {

    const mimeTypes = generateMagicArray(
        data.mimeTypes,
        MimeTypeArray.prototype,
        MimeType.prototype,
        'type'
    )
    const plugins = generateMagicArray(
        data.plugins,
        PluginArray.prototype,
        Plugin.prototype,
        'name'
    )

    // Plugin and MimeType cross-reference each other, let's do that now
    // Note: We're looping through `data.plugins` here, not the generated `plugins`
    for (const pluginData of data.plugins) {
        pluginData.__mimeTypes.forEach((type, index) => {
            plugins[pluginData.name][index] = mimeTypes[type]
            plugins[type] = mimeTypes[type]
            Object.defineProperty(mimeTypes[type], 'enabledPlugin', {
                value: JSON.parse(JSON.stringify(plugins[pluginData.name])),
                writable: false,
                enumerable: false, // Important: `JSON.stringify(navigator.plugins)`
                configurable: false
            })
        })
    }

    const patchNavigator = (name, value) =>
        utils.replaceProperty(Object.getPrototypeOf(navigator), name, {
            get() {
                return value
            }
        })

    patchNavigator('mimeTypes', mimeTypes)
    patchNavigator('plugins', plugins)
}
"""
