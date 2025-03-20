import logging
from logging.handlers import TimedRotatingFileHandler
import os

# 创建logger
logger = logging.getLogger("autogbf")
logger.setLevel(logging.DEBUG)

# 创建格式化器
formatter_file = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s", datefmt="%y/%m/%d_%H:%M:%S"
)
formatter_console = logging.Formatter(
    "%(asctime)s - %(message)s", datefmt="%y/%m/%d_%H:%M:%S"
)

# 创建控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter_console)

# 创建文件处理器
log_dir = ".\log"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
file_handler = TimedRotatingFileHandler(
    filename=os.path.join(log_dir, "autogbf.log"),
    when="midnight",
    interval=1,
    backupCount=7,
    encoding="utf-8",
    delay=True,
)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter_file)

# 将处理器添加到logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# 使用示例
if __name__ == "__main__":
    logger.debug("这是一条调试信息")
    logger.info("这是一条信息")
    logger.warning("这是一条警告")
    logger.error("这是一条错误信息")
    logger.critical("这是一条严重错误信息")
