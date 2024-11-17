# -*- coding: UTF-8 -*-
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QComboBox,
    QDialog,
    QDialogButtonBox,
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
    QToolButton,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtGui import QPixmap, QIcon
# , QTextCursor
from PySide6.QtCore import (
    Qt,
    QFile,
    QMutex,
    QMutexLocker,
    QSize,
    QThread,
    QTimer,
    QTextStream,
)
import sys
from autogbf import AutoGBF
from config import ConfigManager
import os
import logging
import logging.handlers
import queue
# from logger import logger


LIST_METHOD = ["单人", "多人", "沙盒", "星本", "战货", "录制"]
LIST_CONFIG = ["solo", "multi", "sandbox", "halo", "token"]
LIST_ZONE = ["沙盒1.0-火光", "沙盒1.0-水暗", "沙盒1.0-土暗", "沙盒1.0-风光", "沙盒2.0-火光", "沙盒2.0-水暗", "沙盒2.0-土暗", "沙盒2.0-风光", "沙盒3.0"]  # noqa E501
LIST_SUMMON = ["2040034000", "2040028000", "2040027000", "2040020000", "2040047000", "2040046000", "2040094000", "2040100000", "2040084000", "2040098000", "2040080000", "2040090000", "2040056000", "2040003000", "2040157000", "2040158000", "2040114000",]  # noqa E501
PATH_SUMMON = r"./assets/summon/%s.jpg"
PATH_TREASURE = r"./assets/treasure/%s.jpg"
PATH_CONFIG = r"./config.yaml"
PATH_CUSTOM = r"./AutoGBF.side"
URL_TREASURE = r"https://prd-game-a-granbluefantasy.akamaized.net/assets_en/img/sp/assets/item/article/m/%s.jpg"


class QTextEditHandler(logging.Handler):
    def __init__(self, text_edit):
        super().__init__()
        self.text_edit = text_edit
        self.mutex = QMutex()

    def emit(self, record):
        msg = self.format(record)
        with QMutexLocker(self.mutex):
            self.text_edit.append(msg)


class MainUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_data()
        self.update_ui()
        self.page = AutoGBF()
        self.set_queue()
        self.setup_logger()
        # logger.setup_logging(self.text_browser)
        self.button_start.clicked.connect(self.start)
        self.button_stop.clicked.connect(self.stop)
        self.method_list_widget.currentRowChanged.connect(
            lambda: self.stacked_widget.setCurrentIndex(self.method_list_widget.currentRow())
        )
        self.method_list_widget.itemClicked.connect(self.update_custom)
        self.solo_summon_push_button.clicked.connect(self.check_summon)
        self.multi_summon_push_button.clicked.connect(self.check_summon)
        self.halo_summon_push_button.clicked.connect(self.check_summon)
        self.token_summon_push_button.clicked.connect(self.check_summon)

        self.solo_treasure_push_button.clicked.connect(self.check_treasure)
        self.multi_treasure_push_button.clicked.connect(self.check_treasure)
        self.sandbox_treasure_push_button.clicked.connect(self.check_treasure)
        self.halo_treasure_push_button.clicked.connect(self.check_treasure)

        self.token_draw_toolbutton.clicked.connect(self.draw)
        self.token_pick_toolbutton.clicked.connect(self.pick)
        # self.text_browser.textChanged.connect(self.cursor_to_end)

    def set_queue(self):
        self.log_queue = queue.Queue()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_text_browser)
        self.timer.start(1000)  # 每秒刷新一次

    def setup_logger(self):
        # 创建logger
        logger = logging.getLogger('autogbf')
        logger.setLevel(logging.DEBUG)

        # 创建控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # 创建文件处理器
        log_file = './logs/autogbf'
        file_handler = logging.handlers.TimedRotatingFileHandler(
            filename=log_file, when='MIDNIGHT', interval=1, backupCount=7, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # 创建自定义处理器，用于将日志信息发送到QTextBrowser
        class QueueHandler(logging.Handler):
            def __init__(self, log_queue):
                super().__init__()
                self.log_queue = log_queue

            def emit(self, record):
                message = self.format(record)
                self.log_queue.put(message)

        queue_handler = QueueHandler(self.log_queue)
        queue_handler.setLevel(logging.DEBUG)
        text_browser_formatter = logging.Formatter(fmt='%(asctime)s │ %(message)s', datefmt='%m-%d %H:%M:%S')
        queue_handler.setFormatter(text_browser_formatter)
        logger.addHandler(queue_handler)

        max_chars = self.text_browser.width() // 15 - 17

        def hr(level=3, title=None):
            title = str(title).upper()
            title = " " * (max_chars - len(title)) + title + " " * (max_chars - len(title))
            if level == 1:
                logger.info('═' * max_chars)
            if level == 2:
                logger.info('─' * max_chars)
            if level == 0:
                logger.info('═' * max_chars)
                logger.info(title)
                logger.info('═' * max_chars)

        def attr(name, text):
            logger.info('[%s] %s' % (str(name), str(text)))
        logger.hr = hr
        logger.attr = attr

    def update_text_browser(self):
        while not self.log_queue.empty():
            message = self.log_queue.get()
            self.text_browser.append(message)
            # 自动滚动到最下面一行
            self.text_browser.verticalScrollBar().setValue(self.text_browser.verticalScrollBar().maximum())
        # cursor = self.text_browser.textCursor()
        # cursor.movePosition(QTextCursor.End)
        # self.text_browser.setTextCursor(cursor)

    # def update_logger(self):
    #     logger.updata_max_chars(self.text_browser)

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
        self.text_browser.setReadOnly(True)
        self.text_browser.setAcceptRichText(True)

        self.main_layout.addWidget(self.method_list_widget)
        self.main_layout.addLayout(self.central_layout)
        self.main_layout.addWidget(self.text_browser)

        self.setCentralWidget(self.main_widget)

    def open_chrome(self):
        driver = PageQThread(self)
        driver.finished.connect(lambda: driver.deleteLater())
        driver.start()

    def add_page_content_1(self, page : QWidget):
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
        self.solo_custom_label = QLabel("自定义战斗")
        self.solo_custom_combobox = QComboBox()
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
        layout.addRow(self.solo_custom_label, self.solo_custom_combobox)
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
        self.multi_method_radio_button_1 = QRadioButton("通常")
        self.multi_method_radio_button_2 = QRadioButton("活动")
        self.multi_method_radio_button_3 = QRadioButton("快速")
        self.multi_method_button_group.addButton(self.multi_method_radio_button_1, 1)
        self.multi_method_button_group.addButton(self.multi_method_radio_button_2, 2)
        self.multi_method_button_group.addButton(self.multi_method_radio_button_3, 3)
        self.multi_method_layout.addWidget(self.multi_method_radio_button_1)
        self.multi_method_layout.addWidget(self.multi_method_radio_button_2)
        self.multi_method_layout.addWidget(self.multi_method_radio_button_3)
        self.multi_method_layout.addSpacerItem(self.hori_spacer)
        self.multi_custom_label = QLabel("自定义战斗")
        self.multi_custom_combobox = QComboBox()
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
        layout.addRow(self.multi_custom_label, self.multi_custom_combobox)
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
        self.sandbox_custom_label = QLabel("自定义战斗")
        self.sandbox_custom_combobox = QComboBox()
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
        layout.addRow(self.sandbox_custom_label, self.sandbox_custom_combobox)
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
        self.token_url_label = QLabel("活动网址")
        self.token_url_line_edit = QLineEdit()
        self.token_summon_label = QLabel("选择召唤石")
        self.token_summon_layout = QHBoxLayout()
        self.token_summon_push_button = QPushButton()
        self.token_summon_push_button.setProperty("class", "summon")
        self.token_summon_push_button.setIconSize(QSize(140, 80))
        self.token_summon_layout.addWidget(self.token_summon_push_button)
        self.token_summon_layout.addSpacerItem(self.hori_spacer)
        self.token_method_label = QLabel("副本选择")
        self.token_method_layout = QHBoxLayout()
        self.token_method_button_group = QButtonGroup()
        self.token_method_radio_button_1 = QRadioButton("3肉")
        self.token_method_radio_button_2 = QRadioButton("5肉")
        self.token_method_button_group.addButton(self.token_method_radio_button_1, 1)
        self.token_method_button_group.addButton(self.token_method_radio_button_2, 2)
        self.token_method_layout.addWidget(self.token_method_radio_button_1)
        self.token_method_layout.addWidget(self.token_method_radio_button_2)
        self.token_method_layout.addSpacerItem(self.hori_spacer)
        self.token_custom_label = QLabel("自定义战斗")
        self.token_custom_combobox = QComboBox()
        self.token_draw_toolbutton = QToolButton()
        self.token_draw_toolbutton.setText("一键抽战货")
        self.token_draw_toolbutton.setIconSize(QSize(140, 80))
        self.token_pick_toolbutton = QToolButton()
        self.token_pick_toolbutton.setText("一键领取邮箱奖励")
        self.token_pick_toolbutton.setIconSize(QSize(140, 80))
        self.token_draw_count_label = QLabel("古战场抽取箱数")
        self.token_draw_count_spinbox = QSpinBox()
        self.token_draw_count_spinbox.setMaximum(999999)
        layout.addRow(self.token_url_label, self.token_url_line_edit)
        layout.addRow(self.token_summon_label, self.token_summon_layout)
        layout.addRow(self.token_method_label, self.token_method_layout)
        layout.addRow(self.token_custom_label, self.token_custom_combobox)
        layout.addRow(self.token_draw_count_label, self.token_draw_count_spinbox)
        layout.addRow(None, self.token_draw_toolbutton)
        layout.addRow(None, self.token_pick_toolbutton)
        page.setLayout(layout)

    def add_page_content_6(self, page):
        layout = QFormLayout()
        self.record_start_toolbutton = QToolButton()
        self.record_start_toolbutton.setText("开始录制")
        self.record_start_toolbutton.setIconSize(QSize(140, 80))
        self.record_start_toolbutton.clicked.connect(self.start_record)

        self.record_stop_toolbutton = QToolButton()
        self.record_stop_toolbutton.setText("停止录制")
        self.record_stop_toolbutton.setIconSize(QSize(140, 80))
        self.record_stop_toolbutton.clicked.connect(self.stop_record)
        self.record_stop_toolbutton.setEnabled(True)

        layout.addRow(None, self.record_start_toolbutton)
        layout.addRow(None, self.record_stop_toolbutton)
        page.setLayout(layout)

    def start_record(self):
        self.record_stop = False
        record = None
        self.record_start_toolbutton.setEnabled(False)
        self.record_stop_toolbutton.setEnabled(True)
        self.button_start.setEnabled(False)
        self.button_stop.setEnabled(False)
        record = RecordQThread(self)
        record.finished.connect(lambda: record.deleteLater())
        record.finished.connect(lambda: self.record_start_toolbutton.setEnabled(True))
        record.finished.connect(lambda: self.record_stop_toolbutton.setEnabled(False))
        record.finished.connect(lambda: self.button_start.setEnabled(True))
        record.finished.connect(lambda: self.button_stop.setEnabled(False))
        record.start()

    def on_text_entered(self, text):
        # 当对话框被接受时，将sd设置为输入框的内容
        self.record_name = text

    def stop_record(self):
        input_dialog = InputDialog(self)
        input_dialog.exec()
        self.record_stop = True

    def check_summon(self):
        self.sender_button = self.sender()
        self.summon_check = SummonCheck(self)
        self.summon_check.exec()

    def check_treasure(self):
        self.sender_button = self.sender()
        # self.list_treasure_id = []
        if self.page is None:
            self.page = AutoGBF()
        self.list_treasure_id = self.page.update_treasure()
        self.treasure_check = TreasureCheck(self.list_treasure_id, self)
        self.treasure_check.exec()

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

    def update_data(self):
        method = self.method_list_widget.currentRow()
        if method == 0:
            data = ConfigManager("solo")
            data.set_config("url", self.solo_url_line_edit.text())
            data.set_config("summon_id", self.solo_summon_id)
            data.set_config("custom", self.solo_custom_combobox.currentText())
            data.set_config("repeat_times", self.solo_repeat_spinbox.value())
            data.set_config("treasure_id", self.solo_treasure_id)
            data.set_config("treasure_count", self.solo_treasure_count_spinbox.value())
        elif method == 1:
            data = ConfigManager("multi")
            data.set_config("summon_id", self.multi_summon_id)
            data.set_config("method", self.multi_method_button_group.checkedId())
            data.set_config("custom", self.multi_custom_combobox.currentText())
            data.set_config("hp_upper", self.multi_hp_upper_spinbox.value())
            data.set_config("hp_lower", self.multi_hp_lower_spinbox.value())
            data.set_config("joined_upper", self.multi_joined_upper_spinbox.value())
            data.set_config("joined_lower", self.multi_joined_lower_spinbox.value())
            data.set_config("goal_turn", self.multi_goal_spinbox.value())
            data.set_config("repeat_times", self.multi_repeat_spinbox.value())
            data.set_config("treasure_id", self.multi_treasure_id)
            data.set_config("treasure_count", self.multi_treasure_count_spinbox.value())
        elif method == 2:
            data = ConfigManager("sandbox")
            data.set_config("url", self.sandbox_url_line_edit.text())
            data.set_config("custom", self.sandbox_custom_combobox.currentText())
            data.set_config("buff", self.sandbox_buff_spinbox.value())
            data.set_config("repeat_times", self.sandbox_repeat_spinbox.value())
            data.set_config("treasure_id", self.sandbox_treasure_id)
            data.set_config("treasure_count", self.sandbox_treasure_count_spinbox.value())
        elif method == 3:
            data = ConfigManager("halo")
            data.set_config("summon_id", self.halo_summon_id)
            data.set_config("repeat_times", self.halo_repeat_spinbox.value())
            data.set_config("treasure_id", self.halo_treasure_id)
            data.set_config("treasure_count", self.halo_treasure_count_spinbox.value())
        elif method == 4:
            data = ConfigManager("token")
            data.set_config("url", self.token_url_line_edit.text())
            data.set_config("summon_id", self.token_summon_id)
            data.set_config("method", self.token_method_button_group.checkedId())
            data.set_config("custom", self.token_custom_combobox.currentText())
            data.set_config("count_goal", self.token_draw_count_spinbox.value())
        data.save_config()

    def load_data(self):
        """加载数据"""
        solo_data = ConfigManager("solo")
        self.solo_url = solo_data.get_config(["url"])
        self.solo_summon_id = solo_data.get_config(["summon_id"])
        self.solo_repeat_times = solo_data.get_config(["repeat_times"])
        self.solo_treasure_id = solo_data.get_config(["treasure_id"])
        self.solo_treasure_count = solo_data.get_config(["treasure_count"])
        multi_data = ConfigManager("multi")
        self.multi_summon_id = multi_data.get_config(["summon_id"])
        self.multi_method = multi_data.get_config(["method"])
        self.multi_hp_upper = multi_data.get_config(["hp_upper"])
        self.multi_hp_lower = multi_data.get_config(["hp_lower"])
        self.multi_joined_upper = multi_data.get_config(["joined_upper"])
        self.multi_joined_lower = multi_data.get_config(["joined_lower"])
        self.multi_goal = multi_data.get_config(["goal_turn"])
        self.multi_repeat_times = multi_data.get_config(["repeat_times"])
        self.multi_treasure_id = multi_data.get_config(["treasure_id"])
        self.multi_treasure_count = multi_data.get_config(["treasure_count"])
        sandbox_data = ConfigManager("sandbox")
        self.sandbox_url = sandbox_data.get_config(["url"])
        self.sandbox_buff = sandbox_data.get_config(["buff"])
        self.sandbox_repeat_times = sandbox_data.get_config(["repeat_times"])
        self.sandbox_treasure_id = sandbox_data.get_config(["treasure_id"])
        self.sandbox_treasure_count = sandbox_data.get_config(["treasure_count"])
        halo_data = ConfigManager("halo")
        self.halo_summon_id = halo_data.get_config(["summon_id"])
        self.halo_repeat_times = halo_data.get_config(["repeat_times"])
        self.halo_treasure_id = halo_data.get_config(["treasure_id"])
        self.halo_treasure_count = halo_data.get_config(["treasure_count"])
        token_data = ConfigManager("token")
        self.token_url = token_data.get_config(["url"])
        self.token_summon_id = token_data.get_config(["summon_id"])
        self.token_method = token_data.get_config(["method"])
        self.token_draw_count = token_data.get_config(["count_goal"])
        self.update_custom()

    def update_custom(self):
        self.custom_battle = ["无"]
        list_custom = os.listdir("./custom/")
        for custom in list_custom:
            if custom.endswith(".json"):
                self.custom_battle.append(custom.replace(".json", ""))
        self.solo_custom_combobox.clear()
        self.solo_custom_combobox.addItems(self.custom_battle)
        self.multi_custom_combobox.clear()
        self.multi_custom_combobox.addItems(self.custom_battle)
        self.sandbox_custom_combobox.clear()
        self.sandbox_custom_combobox.addItems(self.custom_battle)
        self.token_custom_combobox.clear()
        self.token_custom_combobox.addItems(self.custom_battle)

    def update_ui(self):
        self.solo_url_line_edit.setText(self.solo_url)
        self.solo_summon_push_button.setIcon(QIcon(PATH_SUMMON % self.solo_summon_id))
        self.solo_repeat_spinbox.setValue(self.solo_repeat_times if self.solo_repeat_times else 0)
        self.solo_treasure_push_button.setIcon(QIcon(PATH_TREASURE % self.solo_treasure_id))
        self.solo_treasure_count_spinbox.setValue(self.solo_treasure_count if self.solo_treasure_count else 0)
        self.multi_summon_push_button.setIcon(QIcon(PATH_SUMMON % self.multi_summon_id))
        self.multi_method_radio_button_1.setChecked(True)
        self.multi_hp_upper_spinbox.setValue(self.multi_hp_upper if self.multi_hp_upper else 100)
        self.multi_hp_lower_spinbox.setValue(self.multi_hp_lower if self.multi_hp_lower else 0)
        self.multi_joined_upper_spinbox.setValue(self.multi_joined_upper if self.multi_joined_upper else 30)
        self.multi_joined_lower_spinbox.setValue(self.multi_joined_lower if self.multi_joined_lower else 0)
        self.multi_goal_spinbox.setValue(self.multi_goal if self.multi_goal else 0)
        self.multi_repeat_spinbox.setValue(self.multi_repeat_times if self.multi_repeat_times else 0)
        self.multi_treasure_push_button.setIcon(QIcon(PATH_TREASURE % self.multi_treasure_id))
        self.multi_treasure_count_spinbox.setValue(self.multi_treasure_count if self.multi_treasure_count else 0)
        self.sandbox_url_line_edit.setText(self.sandbox_url)
        self.sandbox_buff_spinbox.setValue(self.sandbox_buff if self.sandbox_buff else 0)
        self.sandbox_repeat_spinbox.setValue(self.sandbox_repeat_times if self.sandbox_repeat_times else 0)
        self.sandbox_treasure_push_button.setIcon(QIcon(PATH_TREASURE % self.sandbox_treasure_id))
        self.sandbox_treasure_count_spinbox.setValue(self.sandbox_treasure_count if self.sandbox_treasure_count else 0)
        self.halo_summon_push_button.setIcon(QIcon(PATH_SUMMON % self.halo_summon_id))
        self.halo_repeat_spinbox.setValue(self.halo_repeat_times if self.halo_repeat_times else 0)
        self.halo_treasure_push_button.setIcon(QIcon(PATH_TREASURE % self.halo_treasure_id))
        self.halo_treasure_count_spinbox.setValue(self.halo_treasure_count if self.halo_treasure_count else 0)
        self.token_url_line_edit.setText(self.token_url)
        self.token_summon_push_button.setIcon(QIcon(PATH_SUMMON % self.token_summon_id))
        self.token_method_radio_button_1.setChecked(True)
        self.token_draw_count_spinbox.setValue(self.token_draw_count if self.token_draw_count else 0)

    def start(self):
        self.update_data()
        self.quit = False
        mission = None
        self.button_start.setEnabled(False)
        self.button_stop.setEnabled(True)
        mission = MissionQThread(self)
        mission.finished.connect(lambda: mission.deleteLater())
        mission.finished.connect(lambda: self.button_start.setEnabled(True))
        mission.finished.connect(lambda: self.button_stop.setEnabled(False))
        mission.start()

    # def draw(self):
    #     self.update_data()
    #     self.quit = False
    #     mission = None
    #     self.button_start.setEnabled(False)
    #     self.token_draw_toolbutton.setEnabled(False)
    #     self.token_pick_toolbutton.setEnabled(False)
    #     mission = DrawQThread(self)
    #     mission.finished.connect(lambda: mission.deleteLater())
    #     mission.finished.connect(lambda: self.button_start.setEnabled(True))
    #     mission.finished.connect(lambda: self.token_draw_toolbutton.setEnabled(True))
    #     mission.finished.connect(lambda: self.token_pick_toolbutton.setEnabled(True))
    #     mission.start()

    # def pick(self):
    #     self.update_data()
    #     self.quit = False
    #     mission = None
    #     self.button_start.setEnabled(False)
    #     self.token_draw_toolbutton.setEnabled(False)
    #     self.token_pick_toolbutton.setEnabled(False)
    #     mission = PickQThread(self)
    #     mission.finished.connect(lambda: mission.deleteLater())
    #     mission.finished.connect(lambda: self.button_start.setEnabled(True))
    #     mission.finished.connect(lambda: self.token_draw_toolbutton.setEnabled(True))
    #     mission.finished.connect(lambda: self.token_pick_toolbutton.setEnabled(True))
    #     mission.start()

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


class InputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("是否保存")

        # 创建布局
        layout = QVBoxLayout(self)

        # 创建输入框
        self.line_edit = QLineEdit(self)
        layout.addWidget(self.line_edit)

        # 创建按钮框
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def accept(self):
        # 获取输入框的内容并打印
        text = self.line_edit.text()
        self.parent.on_text_entered(text)
        super().accept()

    def reject(self):
        self.parent.on_text_entered(None)
        super().reject()


class PageQThread(QThread):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent

    def run(self):
        self.driver = self.parent.page
        self.driver.start_gbf()
        self.finished.emit()
        return


class MissionQThread(QThread):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.module = self.parent.method_list_widget.currentRow()

    def run(self):
        if self.module == 0:
            from module.solo import Solo
            raid = Solo(self.parent)
            raid.start()
        elif self.module == 1:
            from module.multi import Multi
            raid = Multi(self.parent)
            raid.start()
        elif self.module == 2:
            from module.sandbox import Sandbox
            raid = Sandbox(self.parent)
            raid.start()
        # elif self.module == 3:
        #     from module.halo import Halo
        #     raid = Halo(self.parent)
        #     raid.start()
        # elif self.module == 4:
        #     from module.token import Token
        #     raid = Token(self.parent)
        #     raid.start()
        # self.finished.emit()
        # return


class RecordQThread(QThread):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent

    def run(self):
        from autogbf import AutoGBF
        self.driver = AutoGBF(self.parent)
        self.driver.record_raid()
        self.finished.emit()
        return


# class DrawQThread(QThread):
#     def __init__(self, parent=None):
#         super().__init__()
#         self.parent = parent

#     def run(self):
#         from module.token import Token
#         raid = Token(self.parent)
#         raid.draw()
#         self.finished.emit()
#         return


# class PickQThread(QThread):
#     def __init__(self, parent=None):
#         super().__init__()
#         self.parent = parent

#     def run(self):
#         from module.token import Token
#         raid = Token(self.parent)
#         raid.pick()
#         self.finished.emit()
#         return


def start():
    app = QApplication(sys.argv)
    window = MainUI()
    style_file = QFile(r".\src\style.qss")
    if style_file.open(QFile.ReadOnly | QFile.Text):
        stream = QTextStream(style_file)
        app.setStyleSheet(stream.readAll())
    window.show()
    # logger.start()
    # window.open_chrome()
    sys.exit(app.exec())


if __name__ == "__main__":
    start()
