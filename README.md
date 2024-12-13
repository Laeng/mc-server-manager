# Minecraft Server Manager
## for Minecraft Forge Servers

A Python-based management tool for Minecraft Forge servers that provides automated scheduling, monitoring, and control features.

## Features
- **Automated Server Management**
  - Flexible scheduling system
    - Set specific days for 24/7 operation
    - Configure custom operating hours for other days
  - Configurable shutdown warnings
  - Automatic server recovery
  - Health monitoring

- **Real-time Monitoring**
  - Server status (online/offline)
  - TPS (Ticks Per Second)
  - Memory usage
  - CPU usage
  - Active players list
  - Color-coded performance indicators

## Requirements
- Python 3.8+
- Minecraft Forge Server
- RCON enabled on Minecraft server

## Installation
1. Clone the repository
2. Run `run.bat` to automatically:
   - Create a virtual environment
   - Install required packages
   - Set up logging directory

## Server Setup
1. Create `server.bat` in the root directory to launch your Minecraft Forge server
2. Configure your server settings in `config.py`

## Configuration
### Scheduling
In config.py, you can set:
- Operating hours (START_TIME, END_TIME)
- 24/7 operation days using TWENTYFOUR_HOUR_DAYS list
  - Monday = 0, Tuesday = 1, Wednesday = 2, Thursday = 3
  - Friday = 4, Saturday = 5, Sunday = 6

Examples:
- Weekend only: [5, 6]
- All week 24/7: [0, 1, 2, 3, 4, 5, 6]
- Mon/Wed/Fri/Weekend: [0, 2, 4, 5, 6]
- Weekdays only: [0, 1, 2, 3, 4]

### Discord Notifications
In config.py, configure Discord webhook for server status 
notifications:
- Set DISCORD_ENABLED = True
- Add your webhook details:
  ```python
  WEBHOOK_ID = 'your_webhook_id'
  WEBHOOK_TOKEN = 'your_webhook_token'
  THREAD_ID = ''  # Optional for channel threads
  ```

Notification Events:
- 🟢 Server Start
- 🔴 Server Stop
- ⚠️ Server Crash Detection & Auto-restart

#### Message Templates
You can customize notification messages in config.py:
- In-game notifications
- Discord webhook messages

## Usage
Execute `run.bat` to start the server manager
- This will launch the management interface
- Monitor your server status
- Control server operations

### Monitor Display
The monitoring interface shows:
- Server online status
- Current TPS
- Memory usage (MB)
- CPU usage (%)
- Active players list

Performance metrics are color-coded:
- 🟢 Green: Good
- 🟡 Yellow: Warning
- 🔴 Red: Critical
