#!/usr/bin/env python3
"""
Планировщик для автоматических уведомлений
"""

import schedule
import time
import asyncio
import threading
from datetime import datetime
from notifications import run_notifications
from config import config

class NotificationScheduler:
    def __init__(self):
        self.running = False
        self.thread = None
    
    def start(self):
        """Запуск планировщика"""
        if self.running:
            print("⚠️ Планировщик уже запущен")
            return
        
        print("🚀 Запуск планировщика уведомлений...")
        print(f"⏰ Уведомления будут отправляться в {config.NOTIFICATION_HOUR}:00")
        
        # Настраиваем расписание
        schedule.every().day.at(f"{config.NOTIFICATION_HOUR:02d}:00").do(self._run_notifications)
        
        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        
        print("✅ Планировщик уведомлений запущен")
    
    def stop(self):
        """Остановка планировщика"""
        if not self.running:
            print("⚠️ Планировщик не запущен")
            return
        
        print("🛑 Остановка планировщика уведомлений...")
        self.running = False
        schedule.clear()
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
        
        print("✅ Планировщик уведомлений остановлен")
    
    def _run_scheduler(self):
        """Запуск планировщика в отдельном потоке"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Проверяем каждую минуту
            except Exception as e:
                print(f"❌ Ошибка в планировщике: {e}")
                time.sleep(60)
    
    def _run_notifications(self):
        """Запуск уведомлений"""
        print(f"🔔 Запуск уведомлений в {datetime.now().strftime('%H:%M:%S')}")
        
        try:
            # Запускаем уведомления в новом event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(run_notifications())
            loop.close()
            
            print("✅ Уведомления отправлены")
        except Exception as e:
            print(f"❌ Ошибка при отправке уведомлений: {e}")
    
    def run_now(self):
        """Запуск уведомлений немедленно (для тестирования)"""
        print("🔔 Запуск уведомлений немедленно...")
        self._run_notifications()
    
    def get_next_run_time(self):
        """Получение времени следующего запуска"""
        jobs = schedule.get_jobs()
        if jobs:
            return jobs[0].next_run
        return None

def main():
    """Основная функция для запуска планировщика"""
    scheduler = NotificationScheduler()
    
    try:
        scheduler.start()
        
        print("📅 Планировщик работает...")
        print("Нажмите Ctrl+C для остановки")
        
        # Показываем время следующего запуска
        next_run = scheduler.get_next_run_time()
        if next_run:
            print(f"⏰ Следующая проверка: {next_run}")
        
        # Ждем сигнала остановки
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Получен сигнал остановки...")
        scheduler.stop()
        print("✅ Планировщик остановлен")

if __name__ == "__main__":
    main()
