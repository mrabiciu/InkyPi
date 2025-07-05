#!/usr/bin/env python3

# set up logging
import decimal
import os, logging.config
logging.config.fileConfig(os.path.join(os.path.dirname(__file__), 'config', 'logging.conf'))

# suppress warning from inky library https://github.com/pimoroni/inky/issues/205
import warnings
warnings.filterwarnings("ignore", message=".*Busy Wait: Held high.*")

import os
import random
import time
import sys
import json
import logging
import threading
from utils.app_utils import generate_startup_image
from flask import Flask, request
from werkzeug.serving import is_running_from_reloader
from config import Config
from display.display_manager import DisplayManager
from refresh_task import RefreshTask
from blueprints.main import main_bp
from blueprints.settings import settings_bp
from blueprints.plugin import plugin_bp
from blueprints.playlist import playlist_bp
from jinja2 import ChoiceLoader, FileSystemLoader
from plugins.plugin_registry import load_plugins
from plugins.weather.weather import Weather
import subprocess
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# logger.info("Starting web server")
# app = Flask(__name__)
# template_dirs = [
#    os.path.join(os.path.dirname(__file__), "templates"),    # Default template folder
#    os.path.join(os.path.dirname(__file__), "plugins"),      # Plugin templates
# ]
# app.jinja_loader = ChoiceLoader([FileSystemLoader(directory) for directory in template_dirs])

device_config = Config()
display_manager = DisplayManager(device_config)
refresh_task = RefreshTask(device_config, display_manager)

load_plugins(device_config.get_plugins())

# Store dependencies
# app.config['DEVICE_CONFIG'] = device_config
# app.config['DISPLAY_MANAGER'] = display_manager
# app.config['REFRESH_TASK'] = refresh_task

# Register Blueprints
# app.register_blueprint(main_bp)
# app.register_blueprint(settings_bp)
# app.register_blueprint(plugin_bp)
# app.register_blueprint(playlist_bp)

if __name__ == '__main__':
    from werkzeug.serving import is_running_from_reloader

    # start the background refresh task
    # if not is_running_from_reloader():
    #     refresh_task.start()

    # run bash command
    nc = subprocess.run(
        ['nc', '-q', '0', '127.0.0.1', '8423'],
        input="get battery",
        capture_output=True,
        text=True
    )
    battery_level = decimal.Decimal(nc.stdout.split(" ")[1])
    logger.info(f"[battery_level]: {battery_level}")


    # display default inkypi image on startup
    if device_config.get_config("startup") is True:
        logger.info("Startup flag is set, displaying startup image")
        img = generate_startup_image(device_config.get_resolution())
        display_manager.display_image(img)
        device_config.update_value("startup", False, write=True)

    weather = Weather({
        "display_name": "Weather",
        "id": "weather",
        "class": "Weather"
    })
    display_manager.display_image(weather.generate_image_on_start(device_config=device_config))

    # get current time
    current_time = datetime.now()
    logger.info(f"[current_time]: {current_time}")  
    formatted_time = current_time.strftime("%Y-%m-%dT%H:%M:%S.000-07:00")
    # get next hour
    next_hour = current_time + timedelta(hours=1)
    formatted_next_hour = next_hour.strftime("%Y-%m-%dT%H:00:00.000-07:00")

    nc = subprocess.run(
        ['nc', '-q', '0', '127.0.0.1', '8423'],
        input=f"rtc_alarm_set {formatted_time} 127",
        capture_output=True,
        text=True
    )
    logger.info(f"[nc]: {nc.stdout}")


    # echo "rtc_alarm_set 2001-01-01T10:47:33.000-07:00 127" | nc -q 0 127.0.0.1 8423

    


    # try:
    #     # Run the Flask app
    #     app.secret_key = str(random.randint(100000,999999))
    #     app.run(host="0.0.0.0", port=80)
    # finally:
    #     refresh_task.stop()