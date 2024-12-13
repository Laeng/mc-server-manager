import os
from server_monitor import MinecraftServerMonitor

def main():
    os.system('title Minecraft Server Monitor')
    os.system('mode con: cols=40 lines=30')

    monitor = MinecraftServerMonitor()
    monitor.display_status()

if __name__ == "__main__":
    main()
