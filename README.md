# Minecraft Server Manager
## for Minecraft Forge Servers

A Python-based management tool for Minecraft Forge servers that provides automated scheduling, monitoring, and control features.

## Features

- **Automated Server Management**
  - Scheduled server start/stop times
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
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage
Start the server manager:
```bash
python -m manager.manager
```

Start the monitoring interface:
```bash
python -m manager.monitor
```

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
