"""
Скрипт для запуска Streamlit приложения
"""
import subprocess
import sys
import os
import logging
from pathlib import Path
import argparse
import signal
import time

# Настройка путей
PROJECT_ROOT = Path(__file__).parent.parent
STREAMLIT_APP = PROJECT_ROOT / "src" / "streamlit_app" / "main.py"
LOGS_DIR = PROJECT_ROOT / "logs"

# Создаем директорию для логов
LOGS_DIR.mkdir(exist_ok=True)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / "app_runner.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class StreamlitRunner:
    """Класс для управления запуском Streamlit приложения"""
    
    def __init__(self):
        self.process = None
        self.project_root = PROJECT_ROOT
        self.app_path = STREAMLIT_APP
        
    def check_dependencies(self):
        """Проверка зависимостей"""
        try:
            logger.info("Проверка зависимостей...")
            
            # Проверяем наличие streamlit
            result = subprocess.run([sys.executable, "-c", "import streamlit"], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                logger.error("Streamlit не установлен")
                return False
            
            # Проверяем наличие основного файла приложения
            if not self.app_path.exists():
                logger.error(f"Файл приложения не найден: {self.app_path}")
                return False
            
            # Проверяем структуру проекта
            required_dirs = [
                self.project_root / "src",
                self.project_root / "config",
                self.project_root / "data",
                self.project_root / "logs"
            ]
            
            for dir_path in required_dirs:
                if not dir_path.exists():
                    logger.warning(f"Директория не найдена: {dir_path}")
                    dir_path.mkdir(parents=True, exist_ok=True)
                    logger.info(f"Создана директория: {dir_path}")
            
            logger.info("Проверка зависимостей завершена успешно")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при проверке зависимостей: {e}")
            return False
    
    def setup_environment(self):
        """Настройка окружения"""
        try:
            logger.info("Настройка окружения...")
            
            # Добавляем корневую директорию проекта в PYTHONPATH
            current_pythonpath = os.environ.get('PYTHONPATH', '')
            project_path = str(self.project_root)
            
            if project_path not in current_pythonpath:
                if current_pythonpath:
                    os.environ['PYTHONPATH'] = f"{project_path}:{current_pythonpath}"
                else:
                    os.environ['PYTHONPATH'] = project_path
                
                logger.info(f"Добавлен путь в PYTHONPATH: {project_path}")
            
            # Устанавливаем рабочую директорию
            os.chdir(self.project_root)
            logger.info(f"Рабочая директория: {self.project_root}")
            
            logger.info("Настройка окружения завершена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при настройке окружения: {e}")
            return False
    
    def start_app(self, host="0.0.0.0", port=8501, debug=False):
        """Запуск Streamlit приложения"""
        try:
            logger.info(f"Запуск Streamlit приложения на {host}:{port}")
            
            # Формируем команду запуска
            cmd = [
                sys.executable, "-m", "streamlit", "run",
                str(self.app_path),
                "--server.address", host,
                "--server.port", str(port),
                "--server.headless", "true",
                "--browser.gatherUsageStats", "false"
            ]
            
            if debug:
                cmd.extend(["--logger.level", "debug"])
            
            logger.info(f"Команда запуска: {' '.join(cmd)}")
            
            # Запускаем процесс
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            logger.info(f"Приложение запущено с PID: {self.process.pid}")
            logger.info(f"Доступ к приложению: http://{host}:{port}")
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при запуске приложения: {e}")
            return False
    
    def monitor_app(self):
        """Мониторинг работы приложения"""
        try:
            if not self.process:
                logger.error("Процесс приложения не запущен")
                return
            
            logger.info("Начат мониторинг приложения. Для остановки нажмите Ctrl+C")
            
            # Читаем вывод процесса
            while True:
                if self.process.poll() is not None:
                    logger.error("Процесс приложения завершился неожиданно")
                    break
                
                # Читаем строку из stdout
                line = self.process.stdout.readline()
                if line:
                    # Логируем вывод Streamlit
                    line = line.strip()
                    if line:
                        if "error" in line.lower() or "exception" in line.lower():
                            logger.error(f"Streamlit: {line}")
                        elif "warning" in line.lower():
                            logger.warning(f"Streamlit: {line}")
                        else:
                            logger.info(f"Streamlit: {line}")
                
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            logger.info("Получен сигнал остановки")
            self.stop_app()
        except Exception as e:
            logger.error(f"Ошибка при мониторинге: {e}")
            self.stop_app()
    
    def stop_app(self):
        """Остановка приложения"""
        try:
            if self.process:
                logger.info("Остановка приложения...")
                
                # Отправляем сигнал завершения
                self.process.terminate()
                
                # Ждем завершения процесса
                try:
                    self.process.wait(timeout=10)
                    logger.info("Приложение остановлено корректно")
                except subprocess.TimeoutExpired:
                    logger.warning("Принудительная остановка приложения")
                    self.process.kill()
                    self.process.wait()
                
                self.process = None
            else:
                logger.info("Приложение не было запущено")
                
        except Exception as e:
            logger.error(f"Ошибка при остановке приложения: {e}")
    
    def restart_app(self, host="0.0.0.0", port=8501, debug=False):
        """Перезапуск приложения"""
        try:
            logger.info("Перезапуск приложения...")
            
            # Останавливаем текущий процесс
            self.stop_app()
            
            # Ждем немного
            time.sleep(2)
            
            # Запускаем снова
            if self.start_app(host, port, debug):
                logger.info("Приложение перезапущено успешно")
                return True
            else:
                logger.error("Ошибка при перезапуске приложения")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка при перезапуске: {e}")
            return False
    
    def get_status(self):
        """Получение статуса приложения"""
        try:
            if self.process:
                if self.process.poll() is None:
                    return {
                        "status": "running",
                        "pid": self.process.pid,
                        "message": "Приложение работает"
                    }
                else:
                    return {
                        "status": "stopped",
                        "pid": None,
                        "message": "Приложение остановлено"
                    }
            else:
                return {
                    "status": "not_started",
                    "pid": None,
                    "message": "Приложение не запускалось"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "pid": None,
                "message": f"Ошибка получения статуса: {str(e)}"
            }

def signal_handler(signum, frame):
    """Обработчик сигналов"""
    logger.info(f"Получен сигнал {signum}")
    if 'runner' in globals():
        runner.stop_app()
    sys.exit(0)

def main():
    """Основная функция"""
    parser = argparse.ArgumentParser(description="Запуск Streamlit приложения")
    parser.add_argument("--host", default="0.0.0.0", help="Хост для привязки")
    parser.add_argument("--port", type=int, default=8501, help="Порт для привязки")
    parser.add_argument("--debug", action="store_true", help="Режим отладки")
    parser.add_argument("--no-monitor", action="store_true", help="Запуск без мониторинга")
    parser.add_argument("--check-only", action="store_true", help="Только проверка зависимостей")
    
    args = parser.parse_args()
    
    # Создаем экземпляр runner
    global runner
    runner = StreamlitRunner()
    
    # Устанавливаем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Проверяем зависимости
        if not runner.check_dependencies():
            logger.error("Проверка зависимостей не пройдена")
            sys.exit(1)
        
        if args.check_only:
            logger.info("Проверка зависимостей завершена успешно")
            return
        
        # Настраиваем окружение
        if not runner.setup_environment():
            logger.error("Ошибка настройки окружения")
            sys.exit(1)
        
        # Запускаем приложение
        if not runner.start_app(args.host, args.port, args.debug):
            logger.error("Ошибка запуска приложения")
            sys.exit(1)
        
        # Мониторинг (если не отключен)
        if not args.no_monitor:
            runner.monitor_app()
        else:
            logger.info("Приложение запущено в фоновом режиме")
            
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)
    finally:
        if runner.process:
            runner.stop_app()

if __name__ == "__main__":
    main()
