import logging

def create_logger(log_filename, module_name, level):
    format='%(levelname)s<%(name)s> [%(asctime)s]: %(message)s'
    formatter = logging.Formatter(format)
    logging.basicConfig(format=format, datefmt='%Y-%m-%d %H:%M:%S.%F', level=level)
    logger = logging.getLogger(module_name)
    console = logging.StreamHandler()
    console.setLevel(level)
    logger.addHandler(console)
    if log_filename:
        file_handler = logging.FileHandler(log_filename)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        logger.addHandler(file_handler)
    return logger
