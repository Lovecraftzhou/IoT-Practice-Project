# ! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2024/4/9 20:34
# @Author : Lovecraftzhou
# @Site :
import yaml
import time
from loguru import logger
import os

# Get the directory where the current script is located
current_path = os.path.dirname(os.path.abspath(__file__))
# Get the root directory of the project where the current script is located
# root_path = os.path.dirname(current_path)
logs_path = os.path.join(current_path, "logs")
t = time.strftime("%Y_%m_%d")


def setup_logger():
    # logger.remove()
    # logger.add(sys.stdout, format="{time} {level} {message}")
    # Set up logs files to rotate once a day
    logger.add(f"{logs_path}/{t}.log", rotation="1 day", retention="30 days", encoding="utf-8", compression="zip")
    # logger.info("Test")


# print(logs_path)
setup_logger()


def init_config_file(config_path):
    """
    This function is designed to facilitate the loading of YAML file.
    @Args: config_path: file path of the YAML file
    @Returns: config data
    """
    try:
        with open(config_path, 'r') as stream:
            config_data = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        stream.close()
        logger.error(f"Error loading config file {config_path}: {exc}")
        # self.error_logger.log_error(f"Error loading config file {config_path}: {exc}")
    finally:
        stream.close()

    return config_data


mqtt_config = init_config_file("../service/config/mqtt_config.yml")
current_path = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(current_path, "config")
config_path = os.path.join(config_file_path, "config.yaml")
# Redis and db config
con_config = init_config_file(config_path)
