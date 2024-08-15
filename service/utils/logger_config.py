# ! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2024/4/2 21:28
# @Author : Lovecraftzhou

""" Loguru Log file settings"""

import time
from loguru import logger
import os

# Get the directory where the current script is located
current_path = os.path.dirname(os.path.abspath(__file__))
# Get the root directory of the project where the current script is located
root_path = os.path.dirname(current_path)
logs_path = os.path.join(root_path, "logs")
t = time.strftime("%Y_%m_%d")


def setup_logger():
    """
    logger settings
    """
    # logger.remove()
    # logger.add(sys.stdout, format="{time} {level} {message}")
    # Set up logs files to rotate once a day
    logger.add(f"{logs_path}/{t}.log", rotation="1 day", retention="30 days", encoding="utf-8", compression="zip")
    # logger.info("Test")


# print(logs_path)
setup_logger()
