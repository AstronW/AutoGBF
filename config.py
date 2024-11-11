# -*- coding: UTF-8 -*-
from typing import Any
import yaml


class ConfigManager:
    def __init__(self, config_file="config") -> None:
        self.config_file = "./config/" + config_file + ".yaml"
        self.config = {}
        self.load_config()

    def load_config(self) -> None:
        try:
            with open(self.config_file, 'r', encoding='utf-8') as file:
                self.config = yaml.safe_load(file)
                if self.config is None:
                    self.config = {}
        except FileNotFoundError:
            self.save_config()

    def save_config(self) -> None:
        with open(self.config_file, 'w', encoding='utf-8') as file:
            yaml.dump(self.config, file)

    def set_config(self, keys : list | str, value : Any) -> None:
        current_dict = self.config
        if isinstance(keys, str):
            current_dict[keys] = value
        elif isinstance(keys, list):
            for key in keys[:-1]:
                if key not in current_dict:
                    current_dict[key] = {}
                current_dict = current_dict[key]
            current_dict[keys[-1]] = value

    def get_config(self, keys : list | str) -> int | str | bool | None:
        current_dict = self.config
        if isinstance(keys, str):
            if keys not in current_dict:
                return None
            return current_dict[keys]
        elif isinstance(keys, list):
            for key in keys:
                if key not in current_dict:
                    return None
                current_dict = current_dict[key]
            return current_dict


# 使用示例
if __name__ == "__main__":
    data = ConfigManager("token")

    # 加载配置文件
    print
