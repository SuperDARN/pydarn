import os
import sys
import logging.config
import yaml

real_path = os.path.realpath(__file__)
dirname = os.path.dirname(real_path)
log_path = dirname + "/logging_config.yaml"
with open(log_path,'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)


