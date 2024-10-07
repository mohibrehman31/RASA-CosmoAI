import subprocess
import time
import os
import signal
import logging
import sys

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

RASA_MODEL = os.getenv('RASA_MODEL', 'models/your_model.tar.gz')
ENDPOINTS_FILE = os.getenv('ENDPOINTS_FILE', 'endpoints.yml')
CREDENTIALS_FILE = os.getenv('CREDENTIALS_FILE', 'credentials.yml')
FLASK_APP = os.getenv('FLASK_APP', 'flask_app.py')

def run_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    logger.debug(f"Started process: {command}")
    return process

def start_server(command, name):
    process = run_command(command)
    logger.info(f"{name} server started with PID {process.pid}")
    return process

def stop_server(process, name):
    if process:
        process.terminate()
        logger.info(f"{name} server stopped")

def check_server_health(process, name):
    if process.poll() is not None:
        logger.error(f"{name} server has stopped unexpectedly. Return code: {process.returncode}")
        stdout, stderr = process.communicate()
        logger.error(f"{name} stdout: {stdout}")
        logger.error(f"{name} stderr: {stderr}")
        return start_server(process.args, name)
    return process

def main():
    python_executable = sys.executable
    flask_command = f"gunicorn -w 4 -b 0.0.0.0:8000 {FLASK_APP.replace('.py', ':app')} --log-level debug"

    servers = {
        "Rasa": start_server(f"{python_executable} -m rasa run --model {RASA_MODEL} --endpoints {ENDPOINTS_FILE} --credentials {CREDENTIALS_FILE} --enable-api --cors '*' --port 5005", "Rasa"),
        "Action": start_server(f"{python_executable} -m rasa run actions --port 5055", "Action"),
        "Flask": start_server(flask_command, "Flask")
    }

    logger.info("All servers are running.")

    try:
        while True:
            for name, process in servers.items():
                servers[name] = check_server_health(process, name)
            time.sleep(10)
    except KeyboardInterrupt:
        logger.info("Stopping all servers...")
    finally:
        for name, process in servers.items():
            stop_server(process, name)

if __name__ == "__main__":
    main()