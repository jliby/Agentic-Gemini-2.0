import sys
from Cocoa import (
    NSApplication,
    NSWindow,
    NSBackingStoreBuffered,
    NSWindowStyleMaskBorderless,
    NSColor,
    NSView,
    NSMakeRect,
    NSScreen,
    NSFloatingWindowLevel,
    NSWindowCollectionBehaviorCanJoinAllSpaces,
    NSWindowCollectionBehaviorTransient,
)
from Foundation import NSObject

class AppDelegate(NSObject):
    def applicationDidFinishLaunching_(self, notification):
        print("Application did finish launching.")
        
        screen = NSScreen.mainScreen()
        if not screen:
            print("No main screen found.")
            sys.exit(1)
        screen_size = screen.frame().size
        window_width = 300
        window_height = 200
        window_rect = NSMakeRect(
            (screen_size.width - window_width) / 2,
            (screen_size.height - window_height) / 2,
            window_width,
            window_height
        )
        print(f"Window rect: {window_rect}")

        window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            window_rect,
            NSWindowStyleMaskBorderless,
            NSBackingStoreBuffered,
            False
        )
        window.setTitle_("Test Overlay")
        window.setLevel_(NSFloatingWindowLevel)
        window.setOpaque_(False)
        window.setBackgroundColor_(NSColor.clearColor())

        window.setCollectionBehavior_(
            NSWindowCollectionBehaviorCanJoinAllSpaces |
            NSWindowCollectionBehaviorTransient
        )

        content_view = NSView.alloc().initWithFrame_(window.contentView().frame())
        content_view.setWantsLayer_(True)
        content_view.layer().setBackgroundColor_(
            NSColor.systemRedColor().colorWithAlphaComponent_(0.5).CGColor()
        )
        window.setContentView_(content_view)

        window.makeKeyAndOrderFront_(None)
        window.orderFrontRegardless()
        print("Window should now be visible.")

if __name__ == "__main__":
    print("Starting application.")
    app = NSApplication.sharedApplication()
    delegate = AppDelegate.alloc().init()
    app.setDelegate_(delegate)
    app.run()
    print("Application has exited.")