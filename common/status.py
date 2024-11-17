from enum import Enum, auto
from DrissionPage._units.listener import DataPacket
import re
from common.constants import ABILITY_LIST
from logger import logger


class Status(Enum):
    ## 副本选择
    ASSIST_INIT = auto()
    ASSIST_ENABLE = auto()
    ASSIST_DISABLE = auto()
    RAID_ENABLE = auto()
    RAID_DISABLE = auto()
    ## 召唤石选择
    SUMMON_INIT = auto()
    SUMMON_ENABLE = auto()
    SUMMON_DISABLE = auto()
    ## 验证码
    CODE_INIT = auto()
    CODE_TRUE = auto()
    CODE_FALSE = auto()
    CODE_NONE = auto()
    ## 战斗
    BATTLE_INIT = auto()
    BATTLE_START = auto()
    BATTLE_TRIGGER = auto()
    BATTLE_FINISH = auto()
    BATTLE_TURN_ENOUGH = auto()
    BATTLE_LOSE = auto()
    BATTLE_TURN_END = auto()
    BATTLE_BACK = auto()
    BATTLE_LONG_ABILITY = auto()
    BATTLE_DIE = auto()
    BATTLE_NORMAL_ATTACK = auto()
    BATTLE_ABILITY = auto()
    BATTLE_SUMMON = auto()
    ## 战斗结果
    # BATTLE_EMPTY = auto()
    BATTLE_RESULT = auto()
    BATTLE_RESULT_EMPTY = auto()
    ## 网络错误
    NET_ERROR = auto()
    ## 无状态
    NOTHING = auto()


def get_status(packet: DataPacket):
    # logger.info(packet.url)
    if packet.is_failed:
        return Status.NET_ERROR
    ## 副本选择
    if 'newassist' in packet.url:
        return Status.ASSIST_INIT
    elif 'assist_list' in packet.url:
        data = packet.response.body.get("assist_raids_data")
        if data is None or data == []:
            return Status.ASSIST_DISABLE
        else:
            return Status.ASSIST_ENABLE
    elif 'check_multi_start' in packet.url:
        pop = packet.response.body.get("popup")
        if pop:
            return Status.RAID_DISABLE
        else:
            return Status.RAID_ENABLE
    ## 召唤石选择
    elif 'content/supporter' in packet.url:
        return Status.SUMMON_INIT
    elif re.search('quest/(raid_deck_data_)?create', packet.url):
        if "error" in packet.response.body or "popup" in packet.response.body:
            return Status.SUMMON_DISABLE
        else:
            return Status.SUMMON_ENABLE
    ## 验证码
    elif 'decks_info' in packet.url:
        if "popup" in packet.response.body:
            return Status.CODE_INIT
        else:
            return Status.CODE_NONE
    elif '/c/a?_=' in packet.url:
        if packet.response.body.get("is_correct"):
            return Status.CODE_TRUE
        else:
            return Status.CODE_FALSE
    ## 战斗
    elif 'init_quest' in packet.url:
        return Status.BATTLE_INIT
    elif 'raid/start' in packet.url:
        if packet.response.body == "":
            return Status.NET_ERROR
        elif packet.response.body.get("scenario"):
            return Status.BATTLE_TRIGGER
        else:
            return Status.BATTLE_START
    elif 'normal_attack_result' in packet.url:
        scenarios = packet.response.body.get("scenario")
        if scenarios is None or scenarios == []:
            return Status.NET_ERROR
        for scenario in scenarios:
            if scenario == []:
                continue
            cmd = scenario.get("cmd")
            match cmd:
                case "lose":
                    return Status.BATTLE_LOSE
                case "finished":
                    return Status.BATTLE_FINISH
                case "win":
                    if scenario.get("is_last_raid"):
                        return Status.BATTLE_FINISH
                    else:
                        return Status.BATTLE_BACK
        return Status.BATTLE_NORMAL_ATTACK
    elif 'ability_result' in packet.url:
        long_ability, die = False, False
        scenarios = packet.response.body.get("scenario")
        if scenarios is None or scenarios == []:
            return Status.NET_ERROR
        for scenario in scenarios:
            if scenario == []:
                continue
            cmd = scenario.get("cmd")
            match cmd:
                case "lose":
                    return Status.BATTLE_LOSE
                case "finished":
                    return Status.BATTLE_FINISH
                case "win":
                    if scenario.get("is_last_raid"):
                        return Status.BATTLE_FINISH
                    else:
                        return Status.BATTLE_BACK
                case "ability":
                    if scenario.get("name") in ABILITY_LIST:
                        long_ability = True
                case "die":
                    if scenario.get("to") == "player":
                        die = True
        if long_ability:
            return Status.BATTLE_LONG_ABILITY
        elif die:
            return Status.BATTLE_DIE
        else:
            return Status.BATTLE_ABILITY
    elif 'summon_result' in packet.url:
        long_ability, die = False, False
        scenarios = packet.response.body.get("scenario")
        if scenarios is None or scenarios == []:
            return Status.NET_ERROR
        for scenario in scenarios:
            if scenario == []:
                continue
            cmd = scenario.get("cmd")
            match cmd:
                case "lose":
                    return Status.BATTLE_LOSE
                case "finished":
                    return Status.BATTLE_FINISH
                case "win":
                    if scenario.get("is_last_raid"):
                        return Status.BATTLE_FINISH
                    else:
                        return Status.BATTLE_BACK
                case "die":
                    if scenario.get("to") == "player":
                        die = True
        if die:
            return Status.BATTLE_DIE
        else:
            return Status.BATTLE_SUMMON
    ## 战斗结果
    elif re.search('result(multi)?/content/index', packet.url):
        if 'redirect' in packet.response.body:
            return Status.BATTLE_RESULT_EMPTY
        else:
            return Status.BATTLE_RESULT
    else:
        return Status.NOTHING
