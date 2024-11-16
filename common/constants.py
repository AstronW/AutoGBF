from enum import Enum


class Loc:
    SUM_INFO = "c:div.selected > div > div > div.prt-summon-image"
    BTN_OK = ".:btn-usual-ok"
    LIST_TREASURE = ".lis-treasure"
    LIST_RAID = ".:btn-multi-raid lis-raid search"
    LIST_RAID_EVENT = ".:btn-multi-raid lis-raid"
    RAID_REFRESH = ".btn-search-refresh"
    RAID_REFRESH_EVENT = ".:btn-switch-list event"
    BTN_REWARD_RAID = ".:btn-multi-raid"

    # 战斗
    BTN_AUTO = "@@class=btn-auto@@style=display: block;"
    BTN_BACK = ".:btn-command-back"
    BTN_LIST_CHARAC = ".prt-member"
    BTN_CHARACTER = ".:btn-command-character"
    BTN_LIST_ABILITY = ".prt-ability-list"
    BTN_ABILITY = ".:lis-ability btn-ability"
    BTN_BOX = ".:btn-box"
    BTN_LIST_TARGET = ".:prt-character"
    BTN_COMMAND_SUMMON = ".:btn-command-summon"
    BTN_SUMMON = ".:lis-summon"
    BTN_SUMMON_OK = ".btn-usual-ok btn-summon-use"
    BTN_ATT = ".btn-attack-start display-on"
    BTN_GURAD = ".:btn-guard"
    BTN_CHAT = ".btn-chat comment display-on"
    BTN_CHAT_TEXT = ".lis-text"
    BTN_HEAL = ".btn-temporary"
    BTN_BLUE = ".:lis-item item-large btn-temporary-large"
    BTN_GREEN = ".:lis-item item-small btn-temporary-small"
    BTN_CHANGE_CA = ".:btn-lock"
    BTN_FC = ".:btn-cb-gauge"


class Url:
    MULTI_RAID = "https://game.granbluefantasy.jp/#quest/assist"
    MULTI_EVENT = "https://game.granbluefantasy.jp/#quest/assist/event"
    RAID_DETAIL_URL = "https://game.granbluefantasy.jp/#quest/supporter_raid/{multi_raid_id}/{quest_id}/1/{used_battle_point}/0/7"
    PENDING_BATTLE = "https://game.granbluefantasy.jp/#quest/assist/unclaimed/0/0"

class Pat(Enum):
    ATT = r"(multi)?raid/((normal_attack|ability|summon)_result)"
    RAID_INIT = r"quest/init_quest"
    RAID_START = r"(multi)?raid/start"
    RESULT = r"result(multi)?/content/index"
    SUPPORT = r"quest/content/supporter"
    SUM = r"quest/decks_info"
    CODE = r"/c/a\?_="
    RAID_CREATE = r"(?<!(model/))quest/(raid_deck_data_)?create"
    ASSIST_LIST = r"quest/(assist/search/)?assist_list"
    RAID_CHECK = r"quest/check_multi_start"
    MYPAGE = r"css/user/mypage.css"
    PLAYER_STATUS = r"quest/content/newassist"


ABILITY_LIST = ['Koenig Dekret', 'ケーニヒ・ベシュテレン', 'ツープラトン', 'Tag Team']