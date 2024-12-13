from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import os
import time
import psutil
from colorama import init, Fore, Style

from config import ServerConfig
from utils import LoggerSetup, RconManager

@dataclass
class ServerStatus:
    timestamp: str = ''
    is_online: bool = False
    players: List[str] = None
    memory_used: float = 0.0
    cpu_usage: float = 0.0
    tps: float = 0.0
    
    def __post_init__(self):
        if self.players is None:
            self.players = []
        if not self.timestamp:
            self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

class MinecraftServerMonitor:
    def __init__(self):
        self.config = ServerConfig()
        self.logger = LoggerSetup.setup('monitor')
        self.rcon = RconManager.get_instance(
            self.config.HOST,
            self.config.RCON_PASSWORD,
            self.config.PORT
        )
        init()  # colorama initialization
        
    def _get_java_process(self) -> Optional[psutil.Process]:
        """마인크래프트 자바 프로세스 찾기"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if (proc.name() == 'java.exe' and 
                    'forge' in ' '.join(proc.cmdline()).lower()):
                    return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None

    def _get_rcon_data(self) -> tuple[List[str], float]:
        """RCON 을 통해 서버 정보 수집"""
        players = []
        tps = 0.0
    
        player_response = self.rcon.send_command("list")
        if player_response:
            self.logger.debug(f"List command response:\n{player_response}")
            for line in player_response.splitlines():
                if "players online:" in line:
                    if "There are 0" in line:
                        players = []
                else:
                    player_list = line.split('online:')[1].strip()
                    if player_list:
                        players = [p.strip() for p in player_list.split(',')]
    
        tps_response = self.rcon.send_command("forge tps")
        if tps_response:
            self.logger.debug(f"TPS command response:\n{tps_response}")
            for line in tps_response.splitlines():
                if 'Overall:' in line:
                    tps_part = line.split('Mean TPS:')[1].strip()
                    tps = float(tps_part)
                    break
                
        return players, tps

    def get_server_status(self) -> ServerStatus:
        """서버 상태 정보를 수집"""
        status = ServerStatus()
        
        proc = self._get_java_process()
        if not proc:
            return status
            
        try:
            memory = proc.memory_info()
            status.memory_used = memory.rss / (1024 * 1024)  # Convert to MB
            status.cpu_usage = proc.cpu_percent()
            status.is_online = True
            
            status.players, status.tps = self._get_rcon_data()
            
        except Exception as e:
            self.logger.error(f"Status collection failed: {e}")
            
        return status

    def display_status(self):
        """서버 상태 정보를 화면에 출력"""
        next_check = time.time()
        last_status = self.get_server_status()
        
        while True:
            try:
                current_time = time.time()
                
                if current_time >= next_check:
                    last_status = self.get_server_status()
                    next_check = current_time + self.config.MONITOR_REFRESH
                
                os.system('cls' if os.name == 'nt' else 'clear')
                self._print_status(last_status, next_check - current_time)
                
                time.sleep(self.config.DISPLAY_REFRESH)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.logger.error(f"Display error: {e}")
                time.sleep(self.config.MONITOR_REFRESH)

    def _print_status(self, status: ServerStatus, time_left: float):
        """출력 포맷 설정"""
        print(f"======= Minecraft Server Monitor=======")
        print(f"Last check: {status.timestamp}")
        print("-" * 40)
        
        # Server status
        status_color = Fore.GREEN if status.is_online else Fore.RED
        print(f"Status: {status_color}"
              f"{'Online' if status.is_online else 'Offline'}"
              f"{Style.RESET_ALL}")
        
        if status.is_online:
            # TPS
            tps_color = (Fore.GREEN if status.tps >= 19 else 
                        Fore.YELLOW if status.tps >= 15 else Fore.RED)
            print(f"TPS: {tps_color}{status.tps:.1f}{Style.RESET_ALL}")
            
            # Memory
            mem_color = (Fore.GREEN if status.memory_used < 4096 else
                        Fore.YELLOW if status.memory_used < 6144 else Fore.RED)
            print(f"Memory: {mem_color}{status.memory_used:.0f}MB{Style.RESET_ALL}")
            
            # CPU
            cpu_color = (Fore.GREEN if status.cpu_usage < 70 else
                        Fore.YELLOW if status.cpu_usage < 85 else Fore.RED)
            print(f"CPU Usage: {cpu_color}{status.cpu_usage:.1f}%{Style.RESET_ALL}")
            
            # Player list
            print(f"\n{Fore.CYAN}Players Online: {len(status.players)}{Style.RESET_ALL}")
            if status.players:
                print("┌" + "─" * 30 + "┐")
                for player in status.players:
                    print(f"│ {Fore.YELLOW} {player}{Style.RESET_ALL}" + " " * (28 - len(player)) + "│")
                print("└" + "─" * 30 + "┘")
            else:
                print(f"{Fore.YELLOW}No players online{Style.RESET_ALL}")
        
        print("\nPress Ctrl+C to stop monitoring")
