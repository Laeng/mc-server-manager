import os
from server_monitor import MinecraftServerMonitor

def main():
    os.system('title Minecraft Server Monitor')

    monitor = MinecraftServerMonitor()
    monitor.display_status()

if __name__ == "__main__":
    main()
