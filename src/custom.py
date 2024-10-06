import sys
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QSizePolicy,
    QGroupBox,
    QSpacerItem,
    QGridLayout,
    QLineEdit,
    QScrollArea,
    QDialog,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget
)
from PySide6.QtCore import Qt
import json


class CustomCreate(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):

        # 设置窗口标题和大小
        self.setWindowTitle('创建自定义战斗流程')
        self.setGeometry(50, 50, 1200, 600)
        self.setMaximumHeight(800)

        # 创建一个水平布局
        main_layout = QHBoxLayout()

        # 创建一个垂直布局用于添加按钮
        left_layout = QVBoxLayout()

        self.hori_spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.vert_spacer = QSpacerItem(40, 20, QSizePolicy.Preferred, QSizePolicy.Fixed)

        # %% 创建连线用角色按钮布局

        role_layout = QGridLayout()

        self.role_button_1 = QPushButton('角色1')
        self.role_button_2 = QPushButton('角色2')
        self.role_button_3 = QPushButton('角色3')
        self.role_button_4 = QPushButton('角色4')
        self.role_button_5 = QPushButton('角色5')
        self.role_button_6 = QPushButton('角色6')

        role_layout.addWidget(self.role_button_1, 0, 0)
        role_layout.addWidget(self.role_button_2, 0, 1)
        role_layout.addWidget(self.role_button_3, 0, 2)
        role_layout.addWidget(self.role_button_4, 1, 0)
        role_layout.addWidget(self.role_button_5, 1, 1)
        role_layout.addWidget(self.role_button_6, 1, 2)

        role_groupbox = QGroupBox("技能连线")
        role_groupbox.setStyleSheet("QGroupBox { border: 2px solid black; margin: 4px; padding: 10px 1px 5px 1px; }")
        role_groupbox.setLayout(role_layout)

        left_layout.addWidget(role_groupbox)

        char12_layout = QHBoxLayout()
        char34_layout = QHBoxLayout()

        # %%

        box_layout = QHBoxLayout()

        self.box_button_1 = QPushButton('技能1')
        self.box_button_2 = QPushButton('技能2')
        self.box_button_3 = QPushButton('技能3')
        self.box_button_4 = QPushButton('技能4')

        box_layout.addWidget(self.box_button_1)
        box_layout.addWidget(self.box_button_2)
        box_layout.addWidget(self.box_button_3)
        box_layout.addWidget(self.box_button_4)

        box_groupbox = QGroupBox("技能分支")
        box_groupbox.setStyleSheet("QGroupBox { border: 2px solid black; margin: 5px; padding: 10px 1px 5px 1px; }")
        box_groupbox.setLayout(box_layout)

        left_layout.addWidget(box_groupbox)

        # %% 创建角色1技能布局

        skill_layout_1 = QGridLayout()

        self.skill_button_1_1 = QPushButton('技能1')
        self.skill_button_1_2 = QPushButton('技能2')
        self.skill_button_1_3 = QPushButton('技能3')
        self.skill_button_1_4 = QPushButton('技能4')
        self.guard_1 = QPushButton('Guard')

        skill_layout_1.addWidget(self.skill_button_1_1, 0, 0)
        skill_layout_1.addWidget(self.skill_button_1_2, 0, 1)
        skill_layout_1.addWidget(self.skill_button_1_3, 1, 0)
        skill_layout_1.addWidget(self.skill_button_1_4, 1, 1)
        skill_layout_1.addWidget(self.guard_1, 2, 0, 1, 2)

        skill_groupbox_1 = QGroupBox("角色1")
        skill_groupbox_1.setStyleSheet("QGroupBox { border: 2px solid black; margin: 5px; padding: 10px 1px 5px 1px; }")
        skill_groupbox_1.setLayout(skill_layout_1)

        char12_layout.addWidget(skill_groupbox_1)

        # left_layout.addWidget(skill_groupbox_1)

        # %% 创建角色2技能布局

        skill_layout_2 = QGridLayout()

        self.skill_button_2_1 = QPushButton('技能1')
        self.skill_button_2_2 = QPushButton('技能2')
        self.skill_button_2_3 = QPushButton('技能3')
        self.skill_button_2_4 = QPushButton('技能4')
        self.guard_2 = QPushButton('Guard')

        skill_layout_2.addWidget(self.skill_button_2_1, 0, 0)
        skill_layout_2.addWidget(self.skill_button_2_2, 0, 1)
        skill_layout_2.addWidget(self.skill_button_2_3, 1, 0)
        skill_layout_2.addWidget(self.skill_button_2_4, 1, 1)
        skill_layout_2.addWidget(self.guard_2, 2, 0, 1, 2)

        skill_groupbox_2 = QGroupBox("角色2")
        skill_groupbox_2.setStyleSheet("QGroupBox { border: 2px solid black; margin: 5px; padding: 10px 1px 5px 1px; }")
        skill_groupbox_2.setLayout(skill_layout_2)

        char12_layout.addWidget(skill_groupbox_2)

        # left_layout.addWidget(skill_groupbox_2)

        # %% 创建角色3技能布局

        skill_layout_3 = QGridLayout()

        self.skill_button_3_1 = QPushButton('技能1')
        self.skill_button_3_2 = QPushButton('技能2')
        self.skill_button_3_3 = QPushButton('技能3')
        self.skill_button_3_4 = QPushButton('技能4')
        self.guard_3 = QPushButton('Guard')

        skill_layout_3.addWidget(self.skill_button_3_1, 0, 0)
        skill_layout_3.addWidget(self.skill_button_3_2, 0, 1)
        skill_layout_3.addWidget(self.skill_button_3_3, 1, 0)
        skill_layout_3.addWidget(self.skill_button_3_4, 1, 1)
        skill_layout_3.addWidget(self.guard_3, 2, 0, 1, 2)

        skill_groupbox_3 = QGroupBox("角色3")
        skill_groupbox_3.setStyleSheet("QGroupBox { border: 2px solid black; margin: 5px; padding: 10px 1px 5px 1px; }")
        skill_groupbox_3.setLayout(skill_layout_3)

        char34_layout.addWidget(skill_groupbox_3)

        # left_layout.addWidget(skill_groupbox_3)

        # %% 创建角色4技能布局

        skill_layout_4 = QGridLayout()

        self.skill_button_4_1 = QPushButton('技能1')
        self.skill_button_4_2 = QPushButton('技能2')
        self.skill_button_4_3 = QPushButton('技能3')
        self.skill_button_4_4 = QPushButton('技能4')
        self.guard_4 = QPushButton('Guard')

        skill_layout_4.addWidget(self.skill_button_4_1, 0, 0)
        skill_layout_4.addWidget(self.skill_button_4_2, 0, 1)
        skill_layout_4.addWidget(self.skill_button_4_3, 1, 0)
        skill_layout_4.addWidget(self.skill_button_4_4, 1, 1)
        skill_layout_4.addWidget(self.guard_4, 2, 0, 1, 2)

        skill_groupbox_4 = QGroupBox("角色4")
        skill_groupbox_4.setStyleSheet("QGroupBox { border: 2px solid black; margin: 5px; padding: 10px 1px 5px 1px; }")
        skill_groupbox_4.setLayout(skill_layout_4)

        char34_layout.addWidget(skill_groupbox_4)

        # left_layout.addWidget(skill_groupbox_4)

        left_layout.addLayout(char12_layout)
        left_layout.addLayout(char34_layout)

        # %% 添加奥义布局

        ca_layout = QHBoxLayout()

        self.ca_button_open = QPushButton("开启奥义")
        self.ca_button_close = QPushButton("关闭奥义")

        ca_layout.addWidget(self.ca_button_open)
        ca_layout.addWidget(self.ca_button_close)

        ca_groupbox = QGroupBox("奥义")
        ca_groupbox.setStyleSheet("QGroupBox { border: 2px solid black; margin: 5px; padding: 10px 1px 5px 1px; }")
        ca_groupbox.setLayout(ca_layout)

        left_layout.addWidget(ca_groupbox)

        # %% 创建召唤石布局

        summon_layout = QGridLayout()

        self.summon_button_1 = QPushButton('召唤石1')
        self.summon_button_2 = QPushButton('召唤石2')
        self.summon_button_3 = QPushButton('召唤石3')
        self.summon_button_4 = QPushButton('召唤石4')
        self.summon_button_5 = QPushButton('召唤石5')
        self.summon_button_6 = QPushButton('召唤石6')

        summon_layout.addWidget(self.summon_button_1, 0, 0)
        summon_layout.addWidget(self.summon_button_2, 0, 1)
        summon_layout.addWidget(self.summon_button_3, 0, 2)
        summon_layout.addWidget(self.summon_button_4, 1, 0)
        summon_layout.addWidget(self.summon_button_5, 1, 1)
        summon_layout.addWidget(self.summon_button_6, 1, 2)

        summon_groupbox = QGroupBox("召唤石")
        summon_groupbox.setStyleSheet("QGroupBox { border: 2px solid black; margin: 5px; padding: 10px 1px 5px 1px; }")
        summon_groupbox.setLayout(summon_layout)

        left_layout.addWidget(summon_groupbox)

        # %% 创建回复布局

        recovery_layout = QHBoxLayout()

        self.chat_button = QPushButton('发送消息')
        self.green_button = QPushButton('绿药')
        self.blue_button = QPushButton('蓝药')

        recovery_layout.addWidget(self.chat_button)
        recovery_layout.addWidget(self.green_button)
        recovery_layout.addWidget(self.blue_button)

        recovery_groupbox = QGroupBox("回复")
        recovery_groupbox.setStyleSheet("QGroupBox{ border: 2px solid black; margin: 5px; padding: 10px 1px 5px 1px; }")
        recovery_groupbox.setLayout(recovery_layout)

        left_layout.addWidget(recovery_groupbox)

        # %% 创建FA以及攻击布局

        battle_layout = QHBoxLayout()

        self.fa_button = QPushButton('FA')
        self.fc_button = QPushButton('FC')
        self.attack_button = QPushButton('攻击')
        self.refresh_button = QPushButton('刷新')
        self.home_button = QPushButton('返回主页')

        battle_layout.addWidget(self.fa_button)
        battle_layout.addWidget(self.fc_button)
        battle_layout.addWidget(self.attack_button)
        battle_layout.addWidget(self.refresh_button)
        battle_layout.addWidget(self.home_button)

        battle_groupbox = QGroupBox("FA/FC/攻击/刷新/返回主页")
        battle_groupbox.setStyleSheet("QGroupBox { border: 2px solid black; margin: 5px; padding: 10px 1px 5px 1px; }")
        battle_groupbox.setLayout(battle_layout)

        left_layout.addWidget(battle_groupbox)

        # %% 添加管理布局

        config_layout = QHBoxLayout()

        self.save_button = QPushButton('保存')
        self.clear_button = QPushButton('清空')

        config_layout.addWidget(self.save_button)
        config_layout.addWidget(self.clear_button)

        config_group = QGroupBox('')
        config_group.setStyleSheet("QGroupBox { border: 2px solid black; margin: 5px; padding: 10px 1px 5px 1px; }")
        config_group.setLayout(config_layout)

        left_layout.addWidget(config_group)

        # %% 设置按钮大小

        self.role_button_1.setFixedHeight(30)
        self.role_button_2.setFixedHeight(30)
        self.role_button_3.setFixedHeight(30)
        self.role_button_4.setFixedHeight(30)
        self.role_button_5.setFixedHeight(30)
        self.role_button_6.setFixedHeight(30)

        self.box_button_1.setFixedHeight(30)
        self.box_button_2.setFixedHeight(30)
        self.box_button_3.setFixedHeight(30)
        self.box_button_4.setFixedHeight(30)

        self.skill_button_1_1.setFixedHeight(30)
        self.skill_button_1_2.setFixedHeight(30)
        self.skill_button_1_3.setFixedHeight(30)
        self.skill_button_1_4.setFixedHeight(30)
        self.guard_1.setFixedHeight(30)

        self.skill_button_2_1.setFixedHeight(30)
        self.skill_button_2_2.setFixedHeight(30)
        self.skill_button_2_3.setFixedHeight(30)
        self.skill_button_2_4.setFixedHeight(30)
        self.guard_2.setFixedHeight(30)

        self.skill_button_3_1.setFixedHeight(30)
        self.skill_button_3_2.setFixedHeight(30)
        self.skill_button_3_3.setFixedHeight(30)
        self.skill_button_3_4.setFixedHeight(30)
        self.guard_3.setFixedHeight(30)

        self.skill_button_4_1.setFixedHeight(30)
        self.skill_button_4_2.setFixedHeight(30)
        self.skill_button_4_3.setFixedHeight(30)
        self.skill_button_4_4.setFixedHeight(30)
        self.guard_4.setFixedHeight(30)

        self.summon_button_1.setFixedHeight(30)
        self.summon_button_2.setFixedHeight(30)
        self.summon_button_3.setFixedHeight(30)
        self.summon_button_4.setFixedHeight(30)
        self.summon_button_5.setFixedHeight(30)
        self.summon_button_6.setFixedHeight(30)

        self.ca_button_open.setFixedHeight(30)
        self.ca_button_close.setFixedHeight(30)

        self.chat_button.setFixedHeight(30)
        self.green_button.setFixedHeight(30)
        self.blue_button.setFixedHeight(30)

        self.fa_button.setFixedHeight(30)
        self.fc_button.setFixedHeight(30)
        self.attack_button.setFixedHeight(30)
        self.refresh_button.setFixedHeight(30)
        self.home_button.setFixedHeight(30)

        self.save_button.setFixedHeight(30)
        self.clear_button.setFixedHeight(30)

        # %%

        self.turn_count = 1

        self.scroll_area_left = QScrollArea()
        self.scroll_area_left.setWidgetResizable(True)

        # 设置水平方向不显示滚动条，垂直方向显示滚动条
        self.scroll_area_left.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area_left.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        left_widget.setContentsMargins(-1, -1, 15, -1)
        self.scroll_area_left.setWidget(left_widget)

        self.scroll_area_left.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        # 创建一个垂直布局用于右侧显示点击的按钮
        self.right_layout = QVBoxLayout()
        self.right_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        # 创建一个水平布局用于右侧的单行按钮
        self.right_row_layout = QHBoxLayout()
        self.right_row_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        right_row_label = QLabel(f"第\n{self.turn_count}\n回\n合")
        right_row_label.setStyleSheet("QLabel { border: 2px solid black;}")

        self.right_button_layout = QGridLayout()

        self.right_row_layout.addWidget(right_row_label)
        self.right_row_layout.addLayout(self.right_button_layout)

        # 将水平布局添加到垂直布局中
        self.right_layout.addLayout(self.right_row_layout)

        # 创建一个QScrollArea
        self.scroll_area_right = QScrollArea()
        self.scroll_area_right.setWidgetResizable(True)

        # 设置水平方向不显示滚动条，垂直方向显示滚动条
        self.scroll_area_right.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area_right.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # 创建一个QWidget作为滚动区域的内容
        self.scroll_widget = QWidget()
        self.scroll_widget.setLayout(self.right_layout)

        # 将内容设置到QScrollArea
        self.scroll_area_right.setWidget(self.scroll_widget)

        self.scroll_area_right.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 将左侧和右侧布局添加到主布局中
        main_layout.addWidget(self.scroll_area_left)
        main_layout.addWidget(self.scroll_area_right)

        self.list_right_button = []
        self.list_list_spacer = []
        self.list_right_label = [right_row_label]
        self.list_right_layout = [self.right_row_layout]
        self.row_count = 0
        self.col_count = 0

        self.data = {}
        self.data_count = 0

        self.role_button_1.clicked.connect(lambda: self.on_button_clicked("role", 1))
        self.role_button_2.clicked.connect(lambda: self.on_button_clicked("role", 2))
        self.role_button_3.clicked.connect(lambda: self.on_button_clicked("role", 3))
        self.role_button_4.clicked.connect(lambda: self.on_button_clicked("role", 4))
        self.role_button_5.clicked.connect(lambda: self.on_button_clicked("role", 5))
        self.role_button_6.clicked.connect(lambda: self.on_button_clicked("role", 6))

        self.box_button_1.clicked.connect(lambda: self.on_button_clicked("box", 1))
        self.box_button_2.clicked.connect(lambda: self.on_button_clicked("box", 2))
        self.box_button_3.clicked.connect(lambda: self.on_button_clicked("box", 3))
        self.box_button_4.clicked.connect(lambda: self.on_button_clicked("box", 4))

        self.skill_button_1_1.clicked.connect(lambda: self.on_button_clicked("skill", 1, 1))
        self.skill_button_1_2.clicked.connect(lambda: self.on_button_clicked("skill", 1, 2))
        self.skill_button_1_3.clicked.connect(lambda: self.on_button_clicked("skill", 1, 3))
        self.skill_button_1_4.clicked.connect(lambda: self.on_button_clicked("skill", 1, 4))

        self.skill_button_2_1.clicked.connect(lambda: self.on_button_clicked("skill", 2, 1))
        self.skill_button_2_2.clicked.connect(lambda: self.on_button_clicked("skill", 2, 2))
        self.skill_button_2_3.clicked.connect(lambda: self.on_button_clicked("skill", 2, 3))
        self.skill_button_2_4.clicked.connect(lambda: self.on_button_clicked("skill", 2, 4))

        self.skill_button_3_1.clicked.connect(lambda: self.on_button_clicked("skill", 3, 1))
        self.skill_button_3_2.clicked.connect(lambda: self.on_button_clicked("skill", 3, 2))
        self.skill_button_3_3.clicked.connect(lambda: self.on_button_clicked("skill", 3, 3))
        self.skill_button_3_4.clicked.connect(lambda: self.on_button_clicked("skill", 3, 4))

        self.skill_button_4_1.clicked.connect(lambda: self.on_button_clicked("skill", 4, 1))
        self.skill_button_4_2.clicked.connect(lambda: self.on_button_clicked("skill", 4, 2))
        self.skill_button_4_3.clicked.connect(lambda: self.on_button_clicked("skill", 4, 3))
        self.skill_button_4_4.clicked.connect(lambda: self.on_button_clicked("skill", 4, 4))

        self.guard_1.clicked.connect(lambda: self.on_button_clicked("guard", 1))
        self.guard_2.clicked.connect(lambda: self.on_button_clicked("guard", 2))
        self.guard_3.clicked.connect(lambda: self.on_button_clicked("guard", 3))
        self.guard_4.clicked.connect(lambda: self.on_button_clicked("guard", 4))

        self.summon_button_1.clicked.connect(lambda: self.on_button_clicked("summon", 1))
        self.summon_button_2.clicked.connect(lambda: self.on_button_clicked("summon", 2))
        self.summon_button_3.clicked.connect(lambda: self.on_button_clicked("summon", 3))
        self.summon_button_4.clicked.connect(lambda: self.on_button_clicked("summon", 4))
        self.summon_button_5.clicked.connect(lambda: self.on_button_clicked("summon", 5))
        self.summon_button_6.clicked.connect(lambda: self.on_button_clicked("summon", 6))

        self.chat_button.clicked.connect(lambda: self.on_button_clicked("chat"))
        self.green_button.clicked.connect(lambda: self.on_button_clicked("green"))
        self.blue_button.clicked.connect(lambda: self.on_button_clicked("blue"))

        self.ca_button_open.clicked.connect(lambda: self.on_button_clicked("ca", True))
        self.ca_button_close.clicked.connect(lambda: self.on_button_clicked("ca", False))

        self.fa_button.clicked.connect(lambda: self.on_button_clicked("fa"))
        self.fc_button.clicked.connect(lambda: self.on_button_clicked("fc"))
        self.attack_button.clicked.connect(lambda: self.on_button_clicked("attack"))
        self.refresh_button.clicked.connect(lambda: self.on_button_clicked("refresh"))
        self.home_button.clicked.connect(lambda: self.on_button_clicked("home"))

        self.clear_button.clicked.connect(self.clear_right_layout)
        self.save_button.clicked.connect(self.save_data)

        # 创建一个中心窗口并设置布局
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def on_button_clicked(self, *message):
        # 在右侧添加相对应的按钮

        if message[0] == "skill":
            button_text = f"角色{message[1]}\n技能{message[2]}"
            self.data[self.data_count] = {
                "type": "skill",
                "user": message[1],
                "ability": message[2],
            }
        elif message[0] == "role":
            button_text = f"-->角色{message[1]}"
            self.data[self.data_count] = {
                "type": "role",
                "target": message[1],
            }
        elif message[0] == "box":
            button_text = f"-->技能{message[1]}"
            self.data[self.data_count] = {
                "type": "box",
                "target": message[1],
            }
        elif message[0] == "guard":
            button_text = f"角色{message[1]}\nGuard"
            self.data[self.data_count] = {
                "type": "guard",
                "target": message[1],
            }
        elif message[0] == "ca":
            button_text = "开启奥义" if message[1] else "关闭奥义"
            self.data[self.data_count] = {
                "type": "ca",
                "target": message[1],
            }
        elif message[0] == "summon":
            button_text = f"召唤石{message[1]}"
            self.data[self.data_count] = {
                "type": "summon",
                "target": message[1],
            }
        elif message[0] == "chat":
            button_text = "发送消息"
            self.data[self.data_count] = {
                "type": "chat",
            }
        elif message[0] == "green":
            button_text = "绿药"
            self.data[self.data_count] = {
                "type": "green",
            }
        elif message[0] == "blue":
            button_text = "蓝药"
            self.data[self.data_count] = {
                "type": "blue",
            }
        elif message[0] == "fa":
            button_text = "FA"
            self.data[self.data_count] = {
                "type": "fa",
            }
        elif message[0] == "fc":
            button_text = "FC"
            self.data[self.data_count] = {
                "type": "fc",
            }
        elif message[0] == "attack":
            button_text = "攻击"
            self.data[self.data_count] = {
                "type": "attack",
            }
        elif message[0] == "refresh":
            button_text = "刷新"
            self.data[self.data_count] = {
                "type": "refresh",
            }
        elif message[0] == "home":
            button_text = "返回首页"
            self.data[self.data_count] = {
                "type": "home",
            }
        self.data_count += 1
        new_button = QPushButton(button_text)
        self.list_right_button.append(new_button)
        new_button.setFixedSize(80, 60)  # 设置新按钮的大小

        self.right_button_layout.addWidget(new_button, self.col_count, self.row_count)

        self.row_count += 1
        if self.row_count >= 6:
            self.col_count += 1
            self.row_count = 0

        if message[0] in ["attack", "fa"]:
            # 如果需要新的一行，创建一个新的水平布局
            self.col_count = 0
            self.row_count = 0
            self.turn_count += 1

            self.right_row_layout = QHBoxLayout()
            self.right_row_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

            right_row_label = QLabel(f"第\n{self.turn_count}\n回\n合")
            right_row_label.setStyleSheet("QLabel { border: 2px solid black;}")

            self.right_button_layout = QGridLayout()

            self.right_row_layout.addWidget(right_row_label)
            self.right_row_layout.addLayout(self.right_button_layout)

            self.list_right_label.append(right_row_label)
            self.list_right_layout.append(self.right_row_layout)

            self.right_layout.addLayout(self.right_row_layout)

    def save_data(self):
        self.name = ''
        name_check = NameCheck(self)
        name_check.exec()

        with open(f"./custom/{self.name}.json", "w", encoding='utf-8') as f:
            json.dump(self.data, f, sort_keys=True, indent=4, separators=(',', ': '))

    def clear_right_layout(self):
        for button in self.list_right_button:
            button.setParent(None)
            button.deleteLater()
        for label in self.list_right_label:
            label.setParent(None)
            label.deleteLater()
        for layout in self.list_right_layout:
            layout.setParent(None)
            layout.deleteLater()

        self.turn_count = 1
        self.row_count = 0
        self.col_count = 0

        self.data = {}
        self.data_count = 0

        # 创建一个水平布局用于右侧的单行按钮
        self.right_row_layout = QHBoxLayout()
        self.right_row_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        right_row_label = QLabel(f"第\n{self.turn_count}\n回\n合")
        right_row_label.setStyleSheet("QLabel { border: 2px solid black;}")

        self.right_button_layout = QGridLayout()

        self.right_row_layout.addWidget(right_row_label)
        self.right_row_layout.addLayout(self.right_button_layout)

        # 将水平布局添加到垂直布局中
        self.right_layout.addLayout(self.right_row_layout)
        self.list_right_button = []
        self.list_right_label = [right_row_label]
        self.list_right_layout = [self.right_row_layout]


class NameCheck(QDialog):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        layout = QVBoxLayout()

        self.label = QLabel("请输入配置名称")

        self.lineedit = QLineEdit()

        button_layout = QHBoxLayout()

        self.button = QPushButton("确定")
        self.button.clicked.connect(self.customAccept)
        self.cancel = QPushButton("取消")
        self.cancel.clicked.connect(self.reject)

        button_layout.addWidget(self.button)
        button_layout.addWidget(self.cancel)

        layout.addWidget(self.label)
        layout.addWidget(self.lineedit)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def customAccept(self):
        name = self.lineedit.text()
        self.parent.name = name
        self.accept()


if __name__ == "__main__":
    # 创建应用程序和窗口
    app = QApplication(sys.argv)
    window = CustomCreate()
    window.show()

    # 运行应用程序
    sys.exit(app.exec())
