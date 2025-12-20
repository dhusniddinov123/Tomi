"""Local command execution module.

Handles system commands like opening applications, searching, etc.
These are executed locally without requiring Ollama.
"""

import subprocess
import webbrowser
import os
from core.logger import get_logger

logger = get_logger("Commands")


class CommandHandler:
    """Handler for local system commands."""
    
    def __init__(self):
        self.commands = {
            # Application launching
            "notepad": self.open_notepad,
            "calculator": self.open_calculator,
            "browser": self.open_browser,
            "chrome": self.open_chrome,
            "edge": self.open_edge,
            
            # System commands
            "shutdown": self.shutdown_computer,
            "restart": self.restart_computer,
            "lock": self.lock_computer,
            
            # Searches
            "search": self.web_search,
            "youtube": self.youtube_search,
        }
    
    def execute(self, command_text):
        """
        Execute a local command if recognized.
        
        Args:
            command_text (str): User command
            
        Returns:
            tuple: (success: bool, response: str or None)
                  - If command is handled, returns (True, response_message)
                  - If command is not local, returns (False, None) to pass to AI
        """
        command_lower = command_text.lower()
        
        # Check for application launches
        if "open notepad" in command_lower or "launch notepad" in command_lower:
            return self.open_notepad()
        
        if "open calculator" in command_lower or "launch calculator" in command_lower:
            return self.open_calculator()
        
        if "open browser" in command_lower or "open chrome" in command_lower:
            return self.open_chrome()
        
        if "open edge" in command_lower:
            return self.open_edge()
        
        # Web searches
        if "search for" in command_lower or "google" in command_lower:
            query = self._extract_search_query(command_text, ["search for", "google"])
            if query:
                return self.web_search(query)
        
        if "youtube" in command_lower:
            query = self._extract_search_query(command_text, ["youtube", "on youtube"])
            if query:
                return self.youtube_search(query)
        
        # System commands (require confirmation in production)
        if "shutdown" in command_lower or "shut down" in command_lower:
            # Disabled for safety - uncomment to enable
            # return self.shutdown_computer()
            return (True, "Shutdown command disabled for safety.")
        
        if "lock computer" in command_lower or "lock screen" in command_lower:
            return self.lock_computer()
        
        # Time/date
        if "what time" in command_lower or "current time" in command_lower:
            return self.get_time()
        
        if "what date" in command_lower or "today's date" in command_lower:
            return self.get_date()
        
        # Not a local command - pass to AI
        return (False, None)
    
    def _extract_search_query(self, text, keywords):
        """Extract search query from command text."""
        text_lower = text.lower()
        for keyword in keywords:
            if keyword in text_lower:
                parts = text_lower.split(keyword, 1)
                if len(parts) > 1:
                    return parts[1].strip()
        return None
    
    # Application launchers
    def open_notepad(self):
        """Open Notepad."""
        try:
            subprocess.Popen(["notepad.exe"])
            logger.info("Opened Notepad")
            return (True, "Opening Notepad.")
        except Exception as e:
            logger.error(f"Failed to open Notepad: {e}")
            return (True, "Sorry, I couldn't open Notepad.")
    
    def open_calculator(self):
        """Open Calculator."""
        try:
            subprocess.Popen(["calc.exe"])
            logger.info("Opened Calculator")
            return (True, "Opening Calculator.")
        except Exception as e:
            logger.error(f"Failed to open Calculator: {e}")
            return (True, "Sorry, I couldn't open Calculator.")
    
    def open_browser(self):
        """Open default browser."""
        try:
            webbrowser.open("https://www.google.com")
            logger.info("Opened browser")
            return (True, "Opening browser.")
        except Exception as e:
            logger.error(f"Failed to open browser: {e}")
            return (True, "Sorry, I couldn't open the browser.")
    
    def open_chrome(self):
        """Open Chrome."""
        try:
            chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"
            if os.path.exists(chrome_path):
                subprocess.Popen([chrome_path])
                logger.info("Opened Chrome")
                return (True, "Opening Chrome.")
            else:
                webbrowser.open("https://www.google.com")
                return (True, "Opening default browser.")
        except Exception as e:
            logger.error(f"Failed to open Chrome: {e}")
            return (True, "Sorry, I couldn't open Chrome.")
    
    def open_edge(self):
        """Open Microsoft Edge."""
        try:
            subprocess.Popen(["msedge.exe"])
            logger.info("Opened Edge")
            return (True, "Opening Edge.")
        except Exception as e:
            logger.error(f"Failed to open Edge: {e}")
            return (True, "Sorry, I couldn't open Edge.")
    
    # System commands
    def shutdown_computer(self):
        """Shutdown computer (disabled for safety)."""
        try:
            # Uncomment to enable: subprocess.run(["shutdown", "/s", "/t", "30"])
            logger.warning("Shutdown command called (disabled)")
            return (True, "Shutdown is disabled for safety.")
        except Exception as e:
            logger.error(f"Shutdown failed: {e}")
            return (True, "Sorry, I couldn't shutdown the computer.")
    
    def restart_computer(self):
        """Restart computer (disabled for safety)."""
        try:
            # Uncomment to enable: subprocess.run(["shutdown", "/r", "/t", "30"])
            logger.warning("Restart command called (disabled)")
            return (True, "Restart is disabled for safety.")
        except Exception as e:
            logger.error(f"Restart failed: {e}")
            return (True, "Sorry, I couldn't restart the computer.")
    
    def lock_computer(self):
        """Lock computer."""
        try:
            subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
            logger.info("Locked computer")
            return (True, "Locking computer.")
        except Exception as e:
            logger.error(f"Lock failed: {e}")
            return (True, "Sorry, I couldn't lock the computer.")
    
    # Searches
    def web_search(self, query):
        """Perform web search."""
        try:
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(url)
            logger.info(f"Web search: {query}")
            return (True, f"Searching for {query}.")
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return (True, "Sorry, I couldn't perform the search.")
    
    def youtube_search(self, query):
        """Search YouTube."""
        try:
            url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
            webbrowser.open(url)
            logger.info(f"YouTube search: {query}")
            return (True, f"Searching YouTube for {query}.")
        except Exception as e:
            logger.error(f"YouTube search failed: {e}")
            return (True, "Sorry, I couldn't search YouTube.")
    
    # Information
    def get_time(self):
        """Get current time."""
        from datetime import datetime
        current_time = datetime.now().strftime("%I:%M %p")
        return (True, f"It's {current_time}.")
    
    def get_date(self):
        """Get current date."""
        from datetime import datetime
        current_date = datetime.now().strftime("%A, %B %d, %Y")
        return (True, f"Today is {current_date}.")


# Global command handler instance
command_handler = CommandHandler()
