# import tkinter as tk
# from gui import GUI

# def main():
#     root = tk.Tk()
#     gui = GUI(root)
#     root.mainloop()

# if __name__ == '__main__':
#     main()
from module.solo import Solo
from module.multi import Multi
from config import ConfigManager


if __name__ == "__main__":
    # solo = Solo()
    # data = ConfigManager("solo")
    # solo.start_mission(data.config)
    multi = Multi()
    data = ConfigManager("multi")
    multi.start_mission(data.config)

