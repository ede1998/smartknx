import logging
import oyaml as yaml
import logging.config

with open('../config/logging.yaml', 'r') as f:
    config = yaml.safe_load(f)
logging.config.dictConfig(config)
