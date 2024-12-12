from datetime import time

class ServerConfig:
    # Server Settings
    HOST = '127.0.0.1'
    PORT = 25575
    RCON_PASSWORD = 'your_rcon_password'

    # Schedule Settings
    START_TIME = time(17, 0)  # Server start time
    END_TIME = time(2, 0)    # Server end time
    SHUTDOWN_WARNINGS = [30, 15, 10, 5, 3, 1]  # Warning intervals in minutes

    # Monitoring Settings
    MONITOR_REFRESH = 5    # Status check interval
    DISPLAY_REFRESH = 1    # Display update interval
    HEALTH_CHECK_INTERVAL = 30  # Health check interval

    # Autosave Settings
    AUTOSAVE_WARNINGS = [5, 3, 1]  # Warning intervals in minutes

    # Message Templates
    SERVER_START_MSG = "§a[Notice] §fServer is now running!"
    SHUTDOWN_WARNING_MSG = "§e[Notice] §fServer will shutdown in {minutes} minutes"
    SHUTDOWN_COUNTDOWN_MSG = "§e[Notice] §fShutdown in {seconds} seconds!"
    
    # Autosave Message Templates
    AUTOSAVE_WARNING_MSG = "§7[Notice] §fServer will save in {minutes} minutes"
    AUTOSAVE_COUNTDOWN_MSG = "§7[Notice] §fSaving in {seconds} seconds!"
    AUTOSAVE_START_MSG = "§7[Notice] §fSaving server..."
    AUTOSAVE_COMPLETE_MSG = "§7[Notice] §fServer save complete!"
