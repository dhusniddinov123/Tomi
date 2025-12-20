"""System tray icon for Tomi AI Assistant.

Provides a system tray icon for easy access and control.
Requires: pystray, pillow
"""

try:
    import pystray
    from PIL import Image, ImageDraw
    import threading
    from core.logger import get_logger
    
    logger = get_logger("TrayIcon")
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False
    logger = None


class TrayIcon:
    """System tray icon manager."""
    
    def __init__(self, on_quit_callback=None):
        if not TRAY_AVAILABLE:
            raise ImportError("pystray and pillow are required for tray icon")
        
        self.on_quit_callback = on_quit_callback
        self.icon = None
        self.running = False
    
    def create_image(self):
        """Create a simple icon image."""
        # Create a simple colored circle as icon
        width = 64
        height = 64
        color1 = (0, 120, 215)  # Blue
        color2 = (255, 255, 255)  # White
        
        image = Image.new('RGB', (width, height), color1)
        dc = ImageDraw.Draw(image)
        dc.ellipse([16, 16, 48, 48], fill=color2)
        
        return image
    
    def on_quit(self, icon, item):
        """Handle quit action."""
        logger.info("Quit requested from tray icon")
        self.running = False
        icon.stop()
        
        if self.on_quit_callback:
            self.on_quit_callback()
    
    def setup_menu(self):
        """Setup tray icon menu."""
        return pystray.Menu(
            pystray.MenuItem("Tomi AI Assistant", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Status: Running", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self.on_quit)
        )
    
    def run(self):
        """Run the tray icon."""
        if not TRAY_AVAILABLE:
            logger.error("Tray icon not available - missing dependencies")
            return
        
        self.running = True
        image = self.create_image()
        
        self.icon = pystray.Icon(
            "Tomi",
            image,
            "Tomi AI Assistant",
            menu=self.setup_menu()
        )
        
        logger.info("Starting tray icon")
        self.icon.run()
    
    def start_background(self):
        """Start tray icon in background thread."""
        if not TRAY_AVAILABLE:
            return None
        
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()
        return thread
    
    def stop(self):
        """Stop the tray icon."""
        if self.icon:
            self.icon.stop()
        self.running = False


# Example usage
if __name__ == "__main__":
    import time
    
    def on_quit():
        print("Quitting application...")
    
    tray = TrayIcon(on_quit_callback=on_quit)
    tray.start_background()
    
    # Keep running
    try:
        while tray.running:
            time.sleep(1)
    except KeyboardInterrupt:
        tray.stop()
