window_outerdimensions = """
'use strict'

try {
    if (!!window.outerWidth && !!window.outerHeight) {
        const windowFrame = 85 // probably OS and WM dependent
        window.outerWidth = window.innerWidth
        console.log(`current window outer height ${window.outerHeight}`)
        window.outerHeight = window.innerHeight + windowFrame
        console.log(`new window outer height ${window.outerHeight}`)
    }
} catch (err) {
}

"""
