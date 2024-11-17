from module.solo import Solo
from module.multi import Multi
from config import ConfigManager
import os


NEEDED_PATH = ["UserData", "log", "assets/img", "config", "custom"] 


if __name__ == "__main__":
    for path in NEEDED_PATH:
        if not os.path.exists(path):
            os.makedirs(path)
    # solo = Solo()
    # data = ConfigManager("solo")
    # solo.start_mission(data.config)
    multi = Multi()
    data = ConfigManager("multi")
    multi.start_mission(data.config)

