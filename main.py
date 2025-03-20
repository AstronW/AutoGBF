import os
from src.gui.main_window import init_gui
from src.common.base_page import BasePage


if __name__ == "__main__":
    page = BasePage().get_page()
    init_gui(page)
