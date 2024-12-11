import asyncio
import threading
import schedule
import subprocess
import os
import psutil
from datetime import datetime, timedelta
from typing import Optional

from config import ServerConfig
from utils import LoggerSetup, RconManager
from server_monitor import MinecraftServerMonitor

class MinecraftServerScheduler:
    def __init__(self):
        self.config = ServerConfig()
        self.logger = LoggerSetup.setup('scheduler')
        self.monitor = MinecraftServerMonitor()
        self.shutdown_flag = False
        self.loop = asyncio.new_event_loop()
        self.warning_times = self._calculate_warning_times()
        max_warning = max(self.warning_times) if self.warning_times else 1
        self.shutdown_sequence_start = datetime.combine(datetime.now().date(), self.config.END_TIME) - timedelta(minutes=max_warning)
        self.rcon = RconManager.get_instance(
            self.config.HOST,
            self.config.RCON_PASSWORD,
            self.config.PORT
        )
        self.starting_pid = None
        self.starting_time = None

    def _calculate_warning_times(self) -> list:
        """운영 시간에 따른 종료 경고 시간 계산"""
        today = datetime.now().date()
        start_dt = datetime.combine(today, self.config.START_TIME)
        end_dt = datetime.combine(today, self.config.END_TIME)
    
        if self.config.END_TIME < self.config.START_TIME:
            end_dt = datetime.combine(today + timedelta(days=1), self.config.END_TIME)
    
        operation_minutes = (end_dt - start_dt).total_seconds() / 60
    
        max_config_warning = max(self.config.SHUTDOWN_WARNINGS)
        max_warning_time = max(min(operation_minutes / 3, max_config_warning), 1)
    
        valid_warnings = sorted([t for t in self.config.SHUTDOWN_WARNINGS if t <= max_warning_time], reverse=True)
    
        if not valid_warnings:
            return [max(round(operation_minutes / 3), 1)]
    
        return valid_warnings

    def _is_operating_hours(self) -> bool:
        """현재 서버 운영 시간인지 확인"""
        now = datetime.now()
        today = now.date()
        current_time = now.time()
    
        start_dt = datetime.combine(today, self.config.START_TIME)
        end_dt = datetime.combine(today, self.config.END_TIME)
    
        if self.config.END_TIME < self.config.START_TIME:
            if current_time >= self.config.START_TIME:
                end_dt = datetime.combine(today + timedelta(days=1), self.config.END_TIME)
            else:
                start_dt = datetime.combine(today - timedelta(days=1), self.config.START_TIME)
    
        return start_dt <= now <= end_dt

    def _get_java_process(self) -> Optional[psutil.Process]:
        """Minecraft 서버 Java 프로세스 찾기"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if (proc.name() == 'java.exe' and 
                    'forge' in ' '.join(proc.cmdline()).lower()):
                    return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None

    async def start_server(self):
        """서버 시작 프로세스"""
        self.logger.info("Starting Minecraft server...")
        try:
            os.system('taskkill /f /im java.exe 2>nul')
            await asyncio.sleep(5)
            
            current_dir = os.path.dirname(os.path.abspath(__file__))
            bat_path = os.path.join(current_dir, "..", "server.bat")
            
            process = subprocess.Popen(
                [bat_path], 
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            self.starting_pid = process.pid
            self.starting_time = datetime.now()
            
            for _ in range(30):
                await asyncio.sleep(10)
                if self._get_java_process() is not None:
                    await self.send_message(self.config.SERVER_START_MSG)
                    self.logger.info("Server started successfully")
                    return True
            
            self.logger.error("Server failed to start within timeout")
            return False
            
        except Exception as e:
            self.logger.error(f"Error starting server: {e}")
            return False
        finally:
            self.starting_pid = None
            self.starting_time = None

    async def stop_server(self):
        """서버 종료 프로세스"""
        if self.shutdown_flag:
            return
            
        self.shutdown_flag = True
        self.logger.info("Initiating server shutdown sequence")

        try:
            previous_minutes = 0
            for minutes in self.warning_times:
                await self.send_message(self.config.SHUTDOWN_WARNING_MSG.format(minutes=minutes))
                wait_time = (minutes - previous_minutes) * 60
                await asyncio.sleep(wait_time)
                previous_minutes = minutes

            for seconds in range(10, 0, -1):
                await self.send_message(self.config.SHUTDOWN_COUNTDOWN_MSG.format(seconds=seconds))
                await asyncio.sleep(1)

            await self._send_rcon_command("stop")
            self.logger.info("Shutdown command sent")
            
            await asyncio.sleep(30)
            os.system('taskkill /f /im java.exe 2>nul')
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
        finally:
            self.shutdown_flag = False

    async def send_message(self, message: str):
        """서버 내 메시지 전송"""
        try:
            await self._send_rcon_command(f"say {message}")
            self.logger.debug(f"Sent message: {message}")
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")

    async def _send_rcon_command(self, command: str) -> Optional[str]:
        """RCON 명령어 전송"""
        return self.rcon.send_command(command)

    async def _check_server_running(self) -> bool:
        """서버 실행 상태 확인"""
        return self._get_java_process() is not None

    async def health_check(self):
        """서버 상태 점검 및 자동 복구"""
        if self.shutdown_flag:
            return

        if self.starting_pid:
            if (datetime.now() - self.starting_time).total_seconds() > 300:
                self.starting_pid = None
                self.starting_time = None
            else:
                self.logger.info("Health Check - Server is currently starting")
                return
            
        process_running = await self._check_server_running()
        server_running = process_running
        should_be_running = self._is_operating_hours()
        
        self.logger.info(
            f"Health Check - Operating Hours: {'Yes' if should_be_running else 'No'}, "
            f"Process: {'Running' if process_running else 'Offline'} "
        )
        
        if should_be_running and not server_running:
            self.logger.warning("Server offline during operating hours, attempting restart")
            await self.start_server()
        elif not should_be_running and server_running:
            self.logger.warning("Server running outside operating hours")
            await self.stop_server()

    async def run(self):
        """서버 매니저 메인 루프"""
        self.logger.info("Starting server scheduler...")
        self.logger.info(f"Operating hours: {self.config.START_TIME} - {self.config.END_TIME}")
        self.logger.info(f"Shutdown sequence will start at: {self.shutdown_sequence_start.time()}")
        self.logger.info(f"Warning times: {', '.join(map(str, self.warning_times))} minutes")
        
        if self._is_operating_hours():
            self.logger.info("Within operating hours. Starting server...")
            await self.start_server()
        else:
            self.logger.info("Outside operating hours. Waiting for start time...")
        
        schedule.every().day.at(self.config.START_TIME.strftime("%H:%M")).do(
            lambda: asyncio.create_task(self.start_server())
        )
        schedule.every().day.at(self.shutdown_sequence_start.time().strftime("%H:%M")).do(
            lambda: asyncio.create_task(self.stop_server())
        )
        schedule.every(self.config.HEALTH_CHECK_INTERVAL).seconds.do(
            lambda: asyncio.create_task(self.health_check())
        )
        
        try:
            while True:
                schedule.run_pending()
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Shutdown requested")
            await self.stop_server()
