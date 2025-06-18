import logging

def log_setup(logger_file, 
              log_level='DEBUG', 
              console_level='INFO', 
              format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'):

    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level))
    logger.handlers.clear()  # Очищаем старые хендлеры, чтобы не дублировались

    formatter = logging.Formatter(format, datefmt="%Y-%m-%d %H:%M:%S")

    # Файловый лог с кодировкой UTF-8
    file_handler = logging.FileHandler(logger_file, mode='w', encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(getattr(logging, log_level))
    logger.addHandler(file_handler)

    # Консольный вывод (если нужен)
    if console_level is not None:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(getattr(logging, console_level))
        logger.addHandler(console_handler)

    # Отключаем спам от других библиотек
    logging.getLogger('selenium').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

    return logger