import sys
import os
import asyncio
from typing import Optional

from server_scheduler import MinecraftServerScheduler
from server_monitor import MinecraftServerMonitor
from utils import LoggerSetup

class Application:
    def __init__(self):
        self.logger = LoggerSetup.setup('main')
        self.server_scheduler: Optional[MinecraftServerScheduler] = None
        self.monitor: Optional[MinecraftServerMonitor] = None

    async def start(self):
        try:
            # Initialize components
            self.server_scheduler = MinecraftServerScheduler()
            self.monitor = MinecraftServerMonitor()
            
            # Start monitor display in separate window
            self._start_monitor_window()
            
            # Start server scheduler
            await self.server_scheduler.run()
            
        except Exception as e:
            self.logger.error(f"Application error: {e}")
            raise
        
    def _start_monitor_window(self):
        """Start monitor in a new console window"""
        try:
            base_dir = os.path.dirname(os.path.dirname(__file__))
            monitor_script = os.path.join(os.path.dirname(__file__), "monitor_window.py")
            python_exe = os.path.join(base_dir, "venv", "Scripts", "python.exe")
        
            command = f'start cmd /k {python_exe} {monitor_script}'
            os.system(command)
        
        except Exception as e:
            self.logger.error(f"Failed to start monitor window: {e}")

async def main():
    app = Application()
    try:
        await app.start()
    except KeyboardInterrupt:
        print("\nShutdown requested...")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
    finally:
        # Cleanup if needed
        pass

if __name__ == "__main__":
    asyncio.run(main())
