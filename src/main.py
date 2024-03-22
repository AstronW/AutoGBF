from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QComboBox,
    QDialog,
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QPushButton,
    QRadioButton,
    QSpacerItem,
    QSizePolicy,
    QSpinBox,
    QStackedWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtGui import QPixmap, QIcon, QTextCursor
from PySide6.QtCore import QObject, Qt, QFile, QTextStream, QSize, Signal, QEventLoop, QTimer, QThread
import sys
import threading
from config import DEFAULT_CONFIG
import yaml
import os
import aiohttp
import asyncio
# from logger import logger


LIST_METHOD = ["单人", "多人", "沙盒", "星本", "战货", "连战",]
LIST_ZONE = ["沙盒1.0-火光", "沙盒1.0-水暗", "沙盒1.0-土暗", "沙盒1.0-风光", "沙盒2.0-火光", "沙盒2.0-水暗", "沙盒2.0-土暗", "沙盒2.0-风光", "沙盒3.0"]  # noqa E501
LIST_SUMMON = ["2040034000_02", "2040028000_02", "2040027000_02", "2040020000_02", "2040047000_02", "2040046000_02", "2040094000_02", "2040100000_02", "2040084000_02", "2040098000_02", "2040080000_02", "2040090000_02", "2040056000_04", "2040003000_04", "2040157000", "2040158000", "2040114000",]  # noqa E501
PATH_SUMMON = r"./assets/summon/%s.jpg"
PATH_TREASURE = r"./assets/treasure/%s.jpg"
PATH_CONFIG = r"./config.yaml"
URL_TREASURE = r"https://prd-game-a-granbluefantasy.akamaized.net/assets_en/img/sp/assets/item/article/m/%s.jpg"


def thread_ui(func, *args):
    """
    开启一个新线程任务\n
    :param func: 要执行的线程函数;
    :param args: 函数中需要传入的参数 Any
    :return:
    """
    t = threading.Thread(target=func, args=args)  # 定义新线程
    t.daemon = True  # 开启线程守护
    t.start()  # 执行线程


class EmittingStr(QThread, QObject):
    textWritten = Signal(str)

    def write(self, text):
        self.textWritten.emit(str(text))
        loop = QEventLoop()
        QTimer.singleShot(100, loop.quit)
        loop.exec()
        QApplication.processEvents()

    def flush(self):
        pass


class MainUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_data()
        self.update_ui()
        self.redirect_output()
        self.button_start.clicked.connect(self.start)
        self.button_stop.clicked.connect(self.stop)
        self.method_list_widget.currentRowChanged.connect(
            lambda: self.stacked_widget.setCurrentIndex(self.method_list_widget.currentRow())
        )
        self.solo_summon_push_button.clicked.connect(self.check_summon)
        self.multi_summon_push_button.clicked.connect(self.check_summon)
        self.halo_summon_push_button.clicked.connect(self.check_summon)
        self.token_summon_push_button.clicked.connect(self.check_summon)
        self.pg_summon_push_button.clicked.connect(self.check_summon)

        self.solo_treasure_push_button.clicked.connect(self.check_treasure)
        self.multi_treasure_push_button.clicked.connect(self.check_treasure)
        self.sandbox_treasure_push_button.clicked.connect(self.check_treasure)
        self.pg_treasure_push_button.clicked.connect(self.check_treasure)

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("AutoGBF")
        self.setGeometry(500, 100, 800, 600)

        self.hori_spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.vert_spacer = QSpacerItem(40, 20, QSizePolicy.Preferred, QSizePolicy.Expanding)

        self.main_widget = QWidget()
        self.main_layout = QHBoxLayout(self.main_widget)

        self.method_list_widget = QListWidget()
        self.method_list_widget.addItems(LIST_METHOD)
        self.method_list_widget.setCurrentRow(0)

        self.central_layout = QVBoxLayout()

        self.stacked_widget = QStackedWidget()

        self.page1 = QWidget()
        self.page2 = QWidget()
        self.page3 = QWidget()
        self.page4 = QWidget()
        self.page5 = QWidget()
        self.page6 = QWidget()

        self.add_page_content_1(self.page1)
        self.add_page_content_2(self.page2)
        self.add_page_content_3(self.page3)
        self.add_page_content_4(self.page4)
        self.add_page_content_5(self.page5)
        self.add_page_content_6(self.page6)

        self.stacked_widget.addWidget(self.page1)
        self.stacked_widget.addWidget(self.page2)
        self.stacked_widget.addWidget(self.page3)
        self.stacked_widget.addWidget(self.page4)
        self.stacked_widget.addWidget(self.page5)
        self.stacked_widget.addWidget(self.page6)

        self.button_box = QHBoxLayout()
        self.button_start = QPushButton("开始")
        self.button_stop = QPushButton("停止")
        self.button_stop.setEnabled(False)
        self.button_box.addWidget(self.button_start)
        self.button_box.addWidget(self.button_stop)

        self.central_layout.addWidget(self.stacked_widget)
        self.central_layout.addLayout(self.button_box)

        self.text_browser = QTextBrowser()

        self.main_layout.addWidget(self.method_list_widget)
        self.main_layout.addLayout(self.central_layout)
        self.main_layout.addWidget(self.text_browser)

        self.setCentralWidget(self.main_widget)

    def open_chrome(self):
        from driver import Driver
        self.driver = Driver()
        self.driver.start_chrome()

    def add_page_content_1(self, page):
        layout = QFormLayout()
        self.solo_url_label = QLabel("副本网址")
        self.solo_url_line_edit = QLineEdit()
        self.solo_summon_label = QLabel("选择召唤石")
        self.solo_summon_layout = QHBoxLayout()
        self.solo_summon_push_button = QPushButton()
        self.solo_summon_push_button.setProperty("class", "summon")
        self.solo_summon_push_button.setIconSize(QSize(140, 80))
        self.solo_summon_layout.addWidget(self.solo_summon_push_button)
        self.solo_summon_layout.addSpacerItem(self.hori_spacer)
        self.solo_method_label = QLabel("选择战斗模式")
        self.solo_method_layout = QHBoxLayout()
        self.solo_method_button_group = QButtonGroup()
        self.solo_method_radio_button_1 = QRadioButton("单面")
        self.solo_method_radio_button_2 = QRadioButton("多面")
        self.solo_method_radio_button_3 = QRadioButton("古战场")
        self.solo_method_button_group.addButton(self.solo_method_radio_button_1, 1)
        self.solo_method_button_group.addButton(self.solo_method_radio_button_2, 2)
        self.solo_method_button_group.addButton(self.solo_method_radio_button_3, 3)
        self.solo_method_layout.addWidget(self.solo_method_radio_button_1)
        self.solo_method_layout.addWidget(self.solo_method_radio_button_2)
        self.solo_method_layout.addWidget(self.solo_method_radio_button_3)
        self.solo_method_layout.addSpacerItem(self.hori_spacer)
        self.solo_repeat_label = QLabel("重复次数")
        self.solo_repeat_spinbox = QSpinBox()
        self.solo_repeat_spinbox.setMaximum(999999)
        self.solo_treasure_label = QLabel("选择素材")
        self.solo_treasure_layout = QHBoxLayout()
        self.solo_treasure_push_button = QPushButton()
        self.solo_treasure_push_button.setProperty("class", "treasure")
        self.solo_treasure_push_button.setIconSize(QSize(140, 80))
        self.solo_treasure_layout.addWidget(self.solo_treasure_push_button)
        self.solo_treasure_layout.addSpacerItem(self.hori_spacer)
        self.solo_treasure_count_label = QLabel("素材数量")
        self.solo_treasure_count_spinbox = QSpinBox()
        self.solo_treasure_count_spinbox.setMaximum(999999)
        layout.addRow(self.solo_url_label, self.solo_url_line_edit)
        layout.addRow(self.solo_summon_label, self.solo_summon_layout)
        layout.addRow(self.solo_method_label, self.solo_method_layout)
        layout.addRow(self.solo_repeat_label, self.solo_repeat_spinbox)
        layout.addRow(self.solo_treasure_label, self.solo_treasure_layout)
        layout.addRow(self.solo_treasure_count_label, self.solo_treasure_count_spinbox)
        page.setLayout(layout)

    def add_page_content_2(self, page):
        layout = QFormLayout()
        self.multi_summon_label = QLabel("选择召唤石")
        self.multi_summon_layout = QHBoxLayout()
        self.multi_summon_push_button = QPushButton()
        self.multi_summon_push_button.setProperty("class", "summon")
        self.multi_summon_push_button.setIconSize(QSize(140, 80))
        self.multi_summon_layout.addWidget(self.multi_summon_push_button)
        self.multi_summon_layout.addSpacerItem(self.hori_spacer)
        self.multi_method_label = QLabel("选择战斗模式")
        self.multi_method_layout = QHBoxLayout()
        self.multi_method_button_group = QButtonGroup()
        self.multi_method_radio_button_1 = QRadioButton("连续战斗")
        self.multi_method_radio_button_2 = QRadioButton("等待回复")
        self.multi_method_button_group.addButton(self.multi_method_radio_button_1, 1)
        self.multi_method_button_group.addButton(self.multi_method_radio_button_2, 2)
        self.multi_method_layout.addWidget(self.multi_method_radio_button_1)
        self.multi_method_layout.addWidget(self.multi_method_radio_button_2)
        self.multi_method_layout.addSpacerItem(self.hori_spacer)
        self.multi_hp_cap_label = QLabel("BOSS血量限制")
        self.multi_hp_cap_layout = QHBoxLayout()
        self.multi_hp_cap_con_label = QLabel("—")
        self.multi_hp_upper_spinbox = QSpinBox()
        self.multi_hp_upper_spinbox.setProperty("class", "cap")
        self.multi_hp_upper_spinbox.setMaximum(100)
        self.multi_hp_lower_spinbox = QSpinBox()
        self.multi_hp_lower_spinbox.setProperty("class", "cap")
        self.multi_hp_lower_spinbox.setMaximum(100)
        self.multi_hp_cap_layout.addWidget(self.multi_hp_lower_spinbox)
        self.multi_hp_cap_layout.addWidget(self.multi_hp_cap_con_label)
        self.multi_hp_cap_layout.addWidget(self.multi_hp_upper_spinbox)
        self.multi_hp_cap_layout.addSpacerItem(self.hori_spacer)
        self.multi_joined_cap_label = QLabel("参加人数限制")
        self.multi_joined_cap_layout = QHBoxLayout()
        self.multi_joined_cap_con_label = QLabel("—")
        self.multi_joined_upper_spinbox = QSpinBox()
        self.multi_joined_upper_spinbox.setProperty("class", "cap")
        self.multi_joined_upper_spinbox.setMaximum(30)
        self.multi_joined_lower_spinbox = QSpinBox()
        self.multi_joined_lower_spinbox.setProperty("class", "cap")
        self.multi_joined_lower_spinbox.setMaximum(30)
        self.multi_joined_cap_layout.addWidget(self.multi_joined_lower_spinbox)
        self.multi_joined_cap_layout.addWidget(self.multi_joined_cap_con_label)
        self.multi_joined_cap_layout.addWidget(self.multi_joined_upper_spinbox)
        self.multi_joined_cap_layout.addSpacerItem(self.hori_spacer)
        self.multi_goal_label = QLabel("目标回合")
        self.multi_goal_spinbox = QSpinBox()
        self.multi_goal_spinbox.setMaximum(999999)
        self.multi_repeat_label = QLabel("重复次数")
        self.multi_repeat_spinbox = QSpinBox()
        self.multi_repeat_spinbox.setMaximum(999999)
        self.multi_treasure_label = QLabel("选择素材")
        self.multi_treasure_layout = QHBoxLayout()
        self.multi_treasure_push_button = QPushButton()
        self.multi_treasure_push_button.setProperty("class", "treasure")
        self.multi_treasure_push_button.setIconSize(QSize(140, 80))
        self.multi_treasure_layout.addWidget(self.multi_treasure_push_button)
        self.multi_treasure_layout.addSpacerItem(self.hori_spacer)
        self.multi_treasure_count_label = QLabel("素材数量")
        self.multi_treasure_count_spinbox = QSpinBox()
        self.multi_treasure_count_spinbox.setMaximum(999999)
        layout.addRow(self.multi_summon_label, self.multi_summon_layout)
        layout.addRow(self.multi_method_label, self.multi_method_layout)
        layout.addRow(self.multi_hp_cap_label, self.multi_hp_cap_layout)
        layout.addRow(self.multi_joined_cap_label, self.multi_joined_cap_layout)
        layout.addRow(self.multi_goal_label, self.multi_goal_spinbox)
        layout.addRow(self.multi_repeat_label, self.multi_repeat_spinbox)
        layout.addRow(self.multi_treasure_label, self.multi_treasure_layout)
        layout.addRow(self.multi_treasure_count_label, self.multi_treasure_count_spinbox)
        page.setLayout(layout)

    def add_page_content_3(self, page):
        layout = QFormLayout()
        self.sandbox_url_label = QLabel("副本网址")
        self.sandbox_url_line_edit = QLineEdit()
        self.sandbox_zone_label = QLabel("区域选择")
        self.sandbox_zone_combobox = QComboBox()
        self.sandbox_zone_combobox.addItems(LIST_ZONE)
        self.sandbox_buff_label = QLabel("buff怪数量")
        self.sandbox_buff_spinbox = QSpinBox()
        self.sandbox_buff_spinbox.setMaximum(999999)
        self.sandbox_repeat_label = QLabel("重复次数")
        self.sandbox_repeat_spinbox = QSpinBox()
        self.sandbox_repeat_spinbox.setMaximum(999999)
        self.sandbox_treasure_label = QLabel("选择素材")
        self.sandbox_treasure_layout = QHBoxLayout()
        self.sandbox_treasure_push_button = QPushButton()
        self.sandbox_treasure_push_button.setProperty("class", "treasure")
        self.sandbox_treasure_push_button.setIconSize(QSize(140, 80))
        self.sandbox_treasure_layout.addWidget(self.sandbox_treasure_push_button)
        self.sandbox_treasure_layout.addSpacerItem(self.hori_spacer)
        self.sandbox_treasure_count_label = QLabel("素材数量")
        self.sandbox_treasure_count_spinbox = QSpinBox()
        self.sandbox_treasure_count_spinbox.setMaximum(999999)
        layout.addRow(self.sandbox_url_label, self.sandbox_url_line_edit)
        layout.addRow(self.sandbox_zone_label, self.sandbox_zone_combobox)
        layout.addRow(self.sandbox_buff_label, self.sandbox_buff_spinbox)
        layout.addRow(self.sandbox_repeat_label, self.sandbox_repeat_spinbox)
        layout.addRow(self.sandbox_treasure_label, self.sandbox_treasure_layout)
        layout.addRow(self.sandbox_treasure_count_label, self.sandbox_treasure_count_spinbox)
        page.setLayout(layout)

    def add_page_content_4(self, page):
        layout = QFormLayout()
        self.halo_summon_label = QLabel("选择召唤石")
        self.halo_summon_layout = QHBoxLayout()
        self.halo_summon_push_button = QPushButton()
        self.halo_summon_push_button.setProperty("class", "summon")
        self.halo_summon_push_button.setIconSize(QSize(140, 80))
        self.halo_summon_layout.addWidget(self.halo_summon_push_button)
        self.halo_summon_layout.addSpacerItem(self.hori_spacer)
        self.halo_repeat_label = QLabel("重复次数")
        self.halo_repeat_spinbox = QSpinBox()
        self.halo_repeat_spinbox.setMaximum(999999)
        self.halo_treasure_label = QLabel("选择素材")
        self.halo_treasure_layout = QHBoxLayout()
        self.halo_treasure_push_button = QPushButton()
        self.halo_treasure_push_button.setProperty("class", "treasure")
        self.halo_treasure_push_button.setIconSize(QSize(140, 80))
        self.halo_treasure_layout.addWidget(self.halo_treasure_push_button)
        self.halo_treasure_layout.addSpacerItem(self.hori_spacer)
        self.halo_treasure_count_label = QLabel("素材数量")
        self.halo_treasure_count_spinbox = QSpinBox()
        self.halo_treasure_count_spinbox.setMaximum(999999)
        layout.addRow(self.halo_summon_label, self.halo_summon_layout)
        layout.addRow(self.halo_repeat_label, self.halo_repeat_spinbox)
        layout.addRow(self.halo_treasure_label, self.halo_treasure_layout)
        layout.addRow(self.halo_treasure_count_label, self.halo_treasure_count_spinbox)
        page.setLayout(layout)

    def add_page_content_5(self, page):
        layout = QFormLayout()
        self.token_url_label = QLabel("副本网址")
        self.token_url_line_edit = QLineEdit()
        self.token_summon_label = QLabel("选择召唤石")
        self.token_summon_layout = QHBoxLayout()
        self.token_summon_push_button = QPushButton()
        self.token_summon_push_button.setProperty("class", "summon")
        self.token_summon_push_button.setIconSize(QSize(140, 80))
        self.token_summon_layout.addWidget(self.token_summon_push_button)
        self.token_summon_layout.addSpacerItem(self.hori_spacer)
        self.token_method_label = QLabel("选择战斗模式")
        self.token_method_layout = QHBoxLayout()
        self.token_method_button_group = QButtonGroup()
        self.token_method_radio_button_1 = QRadioButton("单面")
        self.token_method_radio_button_2 = QRadioButton("多面")
        self.token_method_radio_button_3 = QRadioButton("古战场")
        self.token_method_button_group.addButton(self.token_method_radio_button_1, 1)
        self.token_method_button_group.addButton(self.token_method_radio_button_2, 2)
        self.token_method_button_group.addButton(self.token_method_radio_button_3, 3)
        self.token_method_layout.addWidget(self.token_method_radio_button_1)
        self.token_method_layout.addWidget(self.token_method_radio_button_2)
        self.token_method_layout.addWidget(self.token_method_radio_button_3)
        self.token_method_layout.addSpacerItem(self.hori_spacer)
        self.token_repeat_label = QLabel("重复次数")
        self.token_repeat_spinbox = QSpinBox()
        self.token_repeat_spinbox.setMaximum(999999)
        self.token_treasure_label = QLabel("素材ID")
        self.token_treasure_spinbox = QSpinBox()
        self.token_treasure_spinbox.setMaximum(999999)
        self.token_treasure_count_label = QLabel("素材数量")
        self.token_treasure_count_spinbox = QSpinBox()
        self.token_treasure_count_spinbox.setMaximum(999999)
        layout.addRow(self.token_url_label, self.token_url_line_edit)
        layout.addRow(self.token_summon_label, self.token_summon_layout)
        layout.addRow(self.token_method_label, self.token_method_layout)
        layout.addRow(self.token_repeat_label, self.token_repeat_spinbox)
        layout.addRow(self.token_treasure_label, self.token_treasure_spinbox)
        layout.addRow(self.token_treasure_count_label, self.token_treasure_count_spinbox)
        page.setLayout(layout)

    def add_page_content_6(self, page):
        layout = QFormLayout()
        self.pg_url_label = QLabel("副本网址")
        self.pg_url_line_edit = QLineEdit()
        self.pg_summon_label = QLabel("选择召唤石")
        self.pg_summon_layout = QHBoxLayout()
        self.pg_summon_push_button = QPushButton()
        self.pg_summon_push_button.setProperty("class", "summon")
        self.pg_summon_push_button.setIconSize(QSize(140, 80))
        self.pg_summon_layout.addWidget(self.pg_summon_push_button)
        self.pg_summon_layout.addSpacerItem(self.hori_spacer)
        self.pg_repeat_label = QLabel("重复次数")
        self.pg_repeat_spinbox = QSpinBox()
        self.pg_repeat_spinbox.setMaximum(999999)
        self.pg_treasure_label = QLabel("选择素材")
        self.pg_treasure_layout = QHBoxLayout()
        self.pg_treasure_push_button = QPushButton()
        self.pg_treasure_push_button.setProperty("class", "treasure")
        self.pg_treasure_push_button.setIconSize(QSize(140, 80))
        self.pg_treasure_layout.addWidget(self.pg_treasure_push_button)
        self.pg_treasure_layout.addSpacerItem(self.hori_spacer)
        self.pg_treasure_count_label = QLabel("素材数量")
        self.pg_treasure_count_spinbox = QSpinBox()
        self.pg_treasure_count_spinbox.setMaximum(999999)
        layout.addRow(self.pg_url_label, self.pg_url_line_edit)
        layout.addRow(self.pg_summon_label, self.pg_summon_layout)
        layout.addRow(self.pg_repeat_label, self.pg_repeat_spinbox)
        layout.addRow(self.pg_treasure_label, self.pg_treasure_layout)
        layout.addRow(self.pg_treasure_count_label, self.pg_treasure_count_spinbox)
        page.setLayout(layout)

    def output_written(self, str):
        cursor = self.text_browser.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(str)
        self.text_browser.setTextCursor(cursor)
        self.text_browser.ensureCursorVisible()

    def check_summon(self):
        self.sender_button = self.sender()
        self.summon_check = SummonCheck(self)
        self.summon_check.setModal(True)
        self.summon_check.show()
        self.setEnabled(False)
        self.summon_check.exec()
        self.setEnabled(True)

    def check_treasure(self):
        self.sender_button = self.sender()
        self.list_treasure_id = self.driver.get_treasure_id()
        count = 0
        lack_treasure_id = []
        for treasure_id in self.list_treasure_id:
            if not os.path.exists(PATH_TREASURE % treasure_id):
                count += 1
                lack_treasure_id.append(treasure_id)
        if count > 0:
            self.load_page = LoadWidget(self)
            self.load_page.setModal(True)
            self.load_page.show()
            self.setEnabled(False)
            self.load_thread = LoadPixThread(lack_treasure_id, self)
            self.load_thread.start()
            self.load_thread.finished.connect(self.show_treasure)
            self.load_thread.finished.connect(lambda: self.load_thread.deleteLater())
        else:
            self.treasure_check = TreasureCheck(self.list_treasure_id, self)
            self.treasure_check.setModal(True)
            self.treasure_check.show()
            self.setEnabled(False)
            self.treasure_check.exec()
            self.setEnabled(True)

    def show_treasure(self):
        self.load_page.close()
        self.treasure_check = TreasureCheck(self.list_treasure_id, self)
        self.treasure_check.setModal(True)
        self.treasure_check.show()
        self.treasure_check.exec()
        self.setEnabled(True)

    def update_summon(self, id):
        self.sender_button.setIcon(QIcon(PATH_SUMMON % id))
        if self.sender_button == self.solo_summon_push_button:
            self.solo_summon_id = id
        elif self.sender_button == self.multi_summon_push_button:
            self.multi_summon_id = id
        elif self.sender_button == self.halo_summon_push_button:
            self.halo_summon_id = id
        elif self.sender_button == self.token_summon_push_button:
            self.token_summon_id = id
        elif self.sender_button == self.pg_summon_push_button:
            self.pg_summon_id = id

    def update_treasure(self, id):
        treasure_id = self.list_treasure_id[id]
        self.sender_button.setIcon(QIcon(PATH_TREASURE % treasure_id))
        if self.sender_button == self.solo_treasure_push_button:
            self.solo_treasure_id = treasure_id
        elif self.sender_button == self.multi_treasure_push_button:
            self.multi_treasure_id = treasure_id
        elif self.sender_button == self.sandbox_treasure_push_button:
            self.sandbox_treasure_id = treasure_id
        elif self.sender_button == self.halo_treasure_push_button:
            self.halo_treasure_id = treasure_id
        # elif self.sender_button == self.token_treasure_push_button:
        #     self.token_treasure_id = treasure_id
        elif self.sender_button == self.pg_treasure_push_button:
            self.pg_treasure_id = treasure_id

    def update_data(self):
        self.data["solo"]["url"] = self.solo_url_line_edit.text()
        self.data["solo"]["summon_id"] = self.solo_summon_id
        self.data["solo"]["method"] = self.solo_method_button_group.checkedId()
        self.data["solo"]["repeat_times"] = self.solo_repeat_spinbox.value()
        self.data["solo"]["treasure_id"] = self.solo_treasure_id
        self.data["solo"]["treasure_count"] = self.solo_treasure_count_spinbox.value()
        self.data["multi"]["summon_id"] = self.multi_summon_id
        self.data["multi"]["method"] = self.multi_method_button_group.checkedId()
        self.data["multi"]["hp_upper"] = self.multi_hp_upper_spinbox.value()
        self.data["multi"]["hp_lower"] = self.multi_hp_lower_spinbox.value()
        self.data["multi"]["joined_upper"] = self.multi_joined_upper_spinbox.value()
        self.data["multi"]["joined_lower"] = self.multi_joined_lower_spinbox.value()
        self.data["multi"]["goal_turn"] = self.multi_goal_spinbox.value()
        self.data["multi"]["repeat_times"] = self.multi_repeat_spinbox.value()
        self.data["multi"]["treasure_id"] = self.multi_treasure_id
        self.data["multi"]["treasure_count"] = self.multi_treasure_count_spinbox.value()
        self.data["sandbox"]["url"] = self.sandbox_url_line_edit.text()
        self.data["sandbox"]["zone"] = self.sandbox_zone_combobox.currentIndex()
        self.data["sandbox"]["buff"] = self.sandbox_buff_spinbox.value()
        self.data["sandbox"]["repeat_times"] = self.sandbox_repeat_spinbox.value()
        self.data["sandbox"]["treasure_id"] = self.sandbox_treasure_id
        self.data["sandbox"]["treasure_count"] = self.sandbox_treasure_count_spinbox.value()
        self.data["halo"]["summon_id"] = self.halo_summon_id
        self.data["halo"]["repeat_times"] = self.halo_repeat_spinbox.value()
        self.data["halo"]["treasure_id"] = self.halo_treasure_id
        self.data["halo"]["treasure_count"] = self.halo_treasure_count_spinbox.value()
        self.data["pg"]["url"] = self.pg_url_line_edit.text()
        self.data["pg"]["summon_id"] = self.pg_summon_id
        self.data["pg"]["repeat_times"] = self.pg_repeat_spinbox.value()
        self.data["pg"]["treasure_id"] = self.pg_treasure_id
        self.data["pg"]["treasure_count"] = self.pg_treasure_count_spinbox.value()
        # self.data["token"]["url"] = self.token_url_line_edit.text()
        # self.data["token"]["summon_id"] = self.token_summon_id
        # self.data["token"]["method"] = self.token_method_button_group.checkedId()
        # self.data["token"]["repeat_times"] = self.token_repeat_spinbox.value()
        # self.data["token"]["treasure_id"] = self.token_treasure_id
        # self.data["token"]["treasure_count"] = self.token_treasure_count_spinbox.value()

        with open(PATH_CONFIG, "w", encoding="utf-8") as f:
            yaml.dump(self.data, f)

    def load_data(self):
        """加载数据"""
        self.data = DEFAULT_CONFIG
        if not os.path.exists(PATH_CONFIG):
            with open(PATH_CONFIG, "w", encoding="utf-8") as f:
                yaml.dump(data=self.data, stream=f, allow_unicode=True)
        else:
            with open(PATH_CONFIG) as f:
                self.config = yaml.load(f, Loader=yaml.FullLoader)
                dir_list = list(self.config.keys())
                for i in dir_list:
                    self.data[i].update(self.config[i])
        self.solo_url = self.data["solo"]["url"]
        self.solo_summon_id = self.data["solo"]["summon_id"]
        self.solo_method = self.data["solo"]["method"]
        self.solo_repeat_times = self.data["solo"]["repeat_times"]
        self.solo_treasure_id = self.data["solo"]["treasure_id"]
        self.solo_treasure_count = self.data["solo"]["treasure_count"]
        self.multi_summon_id = self.data["multi"]["summon_id"]
        self.multi_method = self.data["multi"]["method"]
        self.multi_hp_upper = self.data["multi"]["hp_upper"]
        self.multi_hp_lower = self.data["multi"]["hp_lower"]
        self.multi_joined_upper = self.data["multi"]["joined_upper"]
        self.multi_joined_lower = self.data["multi"]["joined_lower"]
        self.multi_goal = self.data["multi"]["goal_turn"]
        self.multi_repeat_times = self.data["multi"]["repeat_times"]
        self.multi_treasure_id = self.data["multi"]["treasure_id"]
        self.multi_treasure_count = self.data["multi"]["treasure_count"]
        self.sandbox_url = self.data["sandbox"]["url"]
        self.sandbox_zone = self.data["sandbox"]["zone"]
        self.sandbox_buff = self.data["sandbox"]["buff"]
        self.sandbox_repeat_times = self.data["sandbox"]["repeat_times"]
        self.sandbox_treasure_id = self.data["sandbox"]["treasure_id"]
        self.sandbox_treasure_count = self.data["sandbox"]["treasure_count"]
        self.halo_summon_id = self.data["halo"]["summon_id"]
        self.halo_repeat_times = self.data["halo"]["repeat_times"]
        self.halo_treasure_id = self.data["halo"]["treasure_id"]
        self.halo_treasure_count = self.data["halo"]["treasure_count"]
        self.pg_url = self.data["pg"]["url"]
        self.pg_summon_id = self.data["pg"]["summon_id"]
        self.pg_repeat_times = self.data["pg"]["repeat_times"]
        self.pg_treasure_id = self.data["pg"]["treasure_id"]
        self.pg_treasure_count = self.data["pg"]["treasure_count"]

    def update_ui(self):
        self.solo_url_line_edit.setText(self.solo_url)
        self.solo_summon_push_button.setIcon(QIcon(PATH_SUMMON % self.solo_summon_id))
        self.solo_method_radio_button_1.setChecked(True)
        self.solo_repeat_spinbox.setValue(self.solo_repeat_times)
        self.solo_treasure_push_button.setIcon(QIcon(PATH_TREASURE % self.solo_treasure_id))
        self.solo_treasure_count_spinbox.setValue(self.solo_treasure_count)
        self.multi_summon_push_button.setIcon(QIcon(PATH_SUMMON % self.multi_summon_id))
        self.multi_method_radio_button_1.setChecked(True)
        self.multi_hp_upper_spinbox.setValue(self.multi_hp_upper)
        self.multi_hp_lower_spinbox.setValue(self.multi_hp_lower)
        self.multi_joined_upper_spinbox.setValue(self.multi_joined_upper)
        self.multi_joined_lower_spinbox.setValue(self.multi_joined_lower)
        self.multi_goal_spinbox.setValue(self.multi_goal)
        self.multi_repeat_spinbox.setValue(self.multi_repeat_times)
        self.multi_treasure_push_button.setIcon(QIcon(PATH_TREASURE % self.multi_treasure_id))
        self.multi_treasure_count_spinbox.setValue(self.multi_treasure_count)
        self.sandbox_url_line_edit.setText(self.sandbox_url)
        self.sandbox_zone_combobox.setCurrentIndex(self.sandbox_zone)
        self.sandbox_buff_spinbox.setValue(self.sandbox_buff)
        self.sandbox_repeat_spinbox.setValue(self.sandbox_repeat_times)
        self.sandbox_treasure_push_button.setIcon(QIcon(PATH_TREASURE % self.sandbox_treasure_id))
        self.sandbox_treasure_count_spinbox.setValue(self.sandbox_treasure_count)
        self.halo_summon_push_button.setIcon(QIcon(PATH_SUMMON % self.halo_summon_id))
        self.halo_repeat_spinbox.setValue(self.halo_repeat_times)
        self.halo_treasure_push_button.setIcon(QIcon(PATH_TREASURE % self.halo_treasure_id))
        self.halo_treasure_count_spinbox.setValue(self.halo_treasure_count)
        self.pg_url_line_edit.setText(self.pg_url)
        self.pg_summon_push_button.setIcon(QIcon(PATH_SUMMON % self.pg_summon_id))
        self.pg_repeat_spinbox.setValue(self.pg_repeat_times)
        self.pg_treasure_push_button.setIcon(QIcon(PATH_TREASURE % self.pg_treasure_id))
        self.pg_treasure_count_spinbox.setValue(self.pg_treasure_count)

    def redirect_output(self):
        sys.stdout = EmittingStr()
        sys.stdout.textWritten.connect(self.output_written)

    def start(self):
        self.update_data()
        self.quit = False
        mission = None
        if not self.driver.chrome_is_exist():
            self.open_chrome()
        self.button_start.setEnabled(False)
        self.button_stop.setEnabled(True)
        mission = MissionQThread(self)
        mission.finished.connect(lambda: mission.deleteLater())
        mission.finished.connect(lambda: self.button_start.setEnabled(True))
        mission.finished.connect(lambda: self.button_stop.setEnabled(False))
        mission.start()

    def stop(self):
        self.quit = True


class SummonCheck(QDialog):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("请选择召唤石")

        layout = QGridLayout()

        self.button_group = QButtonGroup()
        self.button_group.setExclusive(True)

        row, col = 0, 0
        for index, summon_id in enumerate(LIST_SUMMON):
            image_path = PATH_SUMMON % summon_id
            pixmap = QPixmap(image_path)
            pixmap = pixmap.scaled(140, 80, Qt.KeepAspectRatio)
            icon = QIcon(pixmap)
            button = QPushButton()
            button.setIcon(icon)
            button.setIconSize(pixmap.size())
            button.setCheckable(True)
            button.setStyleSheet("padding: 3px;")
            button.setProperty("class", "summon")
            button.clicked.connect(self.customAccept)
            layout.addWidget(button, row, col)
            self.button_group.addButton(button, index)

            col += 1
            if col >= 6:
                col = 0
                row += 1

        button = QPushButton("取消")
        button.setProperty("class", "summon_cancel")
        button.clicked.connect(self.reject)
        layout.addWidget(button, 2, 5)

        self.setLayout(layout)

    def customAccept(self):
        selected_index = self.button_group.checkedId()
        summon_id = LIST_SUMMON[selected_index]
        self.parent.update_summon(summon_id)
        self.accept()


class TreasureCheck(QDialog):
    def __init__(self, list_treasure_id, parent=None):
        super().__init__()
        self.parent = parent
        self.driver = self.parent.driver
        self.list_treasure_id = list_treasure_id
        self.setWindowTitle("请选择素材")

        self.main_layout = QGridLayout()

        self.button_group = QButtonGroup()
        self.button_group.setExclusive(True)

        row, col = 0, 0
        for index, treasure_id in enumerate(list_treasure_id):
            image_path = PATH_TREASURE % treasure_id
            pixmap = QPixmap(image_path)
            pixmap = pixmap.scaled(140, 80, Qt.KeepAspectRatio)
            icon = QIcon(pixmap)
            button = QPushButton()
            button.setIcon(icon)
            button.setIconSize(pixmap.size())
            button.setCheckable(True)
            button.setStyleSheet("padding: 3px;")
            button.setProperty("class", "summon")
            button.clicked.connect(self.customAccept)
            self.main_layout.addWidget(button, row, col)
            self.button_group.addButton(button, index)

            col += 1
            if col >= 6:
                col = 0
                row += 1

        button = QPushButton("取消")
        button.setProperty("class", "summon_cancel")
        button.clicked.connect(self.reject)
        self.main_layout.addWidget(button, 3, 0)

        self.setLayout(self.main_layout)

    def customAccept(self):
        selected_index = self.button_group.checkedId()
        self.parent.update_treasure(selected_index)
        self.accept()


class LoadWidget(QDialog):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.mainLayout = QVBoxLayout()
        self.label = QLabel("正在加载中")
        self.mainLayout.addWidget(self.label)
        self.setLayout(self.mainLayout)


class LoadPixThread(QThread):
    def __init__(self, list_treasure_id, parent=None):
        super().__init__()
        self.parent = parent
        self.list_treasure_id = list_treasure_id

    def run(self):
        asyncio.run(self.download_many())

    async def download_many(self):
        tasks = []  # 保存所有任务的列表
        async with aiohttp.ClientSession() as session:  # aiohttp建议整个应用只创建一个session，不能为每个请求创建一个seesion
            for treasure_id in self.list_treasure_id:
                task = asyncio.create_task(self.download_one(session, treasure_id))
                tasks.append(task)
            await asyncio.gather(*tasks)

    async def download_one(self, session, treasure_id):
        async with session.get(URL_TREASURE % treasure_id) as response:
            image_content = await response.read()
        with open(PATH_TREASURE % treasure_id, 'wb') as f:
            f.write(image_content)


class MissionQThread(QThread):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.module = self.parent.method_list_widget.currentRow()
        self.driver = self.parent.driver.driver

    def run(self):
        if self.module == 0:
            from module.solo import Solo
            soloraid = Solo(self.parent)
            soloraid.start_mission()
        elif self.module == 1:
            from module.multi import Multi
            multiraid = Multi(self.parent)
            multiraid.start_mission()
        elif self.module == 2:
            from module.sandbox import Sandbox
            multiraid = Sandbox(self.parent)
            multiraid.start_mission()
        elif self.module == 3:
            from module.halo import Halo
            multiraid = Halo(self.parent)
            multiraid.start_mission()
        elif self.module == 5:
            from module.proving import Proving
            multiraid = Proving(self.parent)
            multiraid.start_mission()
        return


def start():
    app = QApplication(sys.argv)
    window = MainUI()
    style_file = QFile(r".\src\style.qss")
    if style_file.open(QFile.ReadOnly | QFile.Text):
        stream = QTextStream(style_file)
        app.setStyleSheet(stream.readAll())
    window.show()
    window.open_chrome()
    sys.exit(app.exec())


if __name__ == "__main__":
    start()
