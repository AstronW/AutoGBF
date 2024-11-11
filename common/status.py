from enum import Enum, auto
from DrissionPage._units.listener import DataPacket
import re
from common.constants import ABILITY_LIST, Pat
from logger import logger


class Status(Enum):
    CODE_TRUE = auto()
    CODE_FALSE = auto()
    CODE_POP = auto()
    SUPPORT = auto()
    ASSIST_NONE = auto()
    ASSIST_ENABLE = auto()
    PLAYER_STATUS = auto()
    RAID_UNABLE = auto()
    RAID_ENABLE = auto()
    PARTY_CLICK = auto()
    RAID_CREATE = auto()
    RAID_CREATE_FALSE = auto()
    RAID_INIT = auto()
    RAID_START = auto()
    RAID_ERROR = auto()
    RAID_TRIGGER = auto()
    RAID_LOSE = auto()
    RAID_FINISH = auto()
    RAID_EMPTY = auto()
    RAID_RESULT = auto()
    RAID_RESULT_EMPTY = auto()
    TURN_ENOUGH = auto()
    TURN_END = auto()
    SUMMON_RESULT_DIE = auto()
    ABILITY_RESULT_DIE = auto()
    NEED_BACK = auto()
    LONG_ABILITY = auto()
    ABILITY_RESULT = auto()
    NORMAL_ATTACK_RESULT = auto()
    SUMMON_RESULT = auto()
    ATTACK_RESULT = ABILITY_RESULT | SUMMON_RESULT | NORMAL_ATTACK_RESULT
    NEED_REFRESH = RAID_ERROR | RAID_FINISH | NORMAL_ATTACK_RESULT | LONG_ABILITY | SUMMON_RESULT_DIE | ABILITY_RESULT_DIE
    NET_ERROR = auto()
    NOTHING = auto()


def get_status(packet: DataPacket):
    logger.info(packet.url)
    if packet.is_failed:
        return Status.NET_ERROR
    # 验证码
    elif re.search(Pat.CODE.value, packet.url):
        if packet.response.body.get("is_correct"):
            return Status.CODE_TRUE
        else:
            return Status.CODE_FALSE
    # 召唤石
    elif re.search(Pat.SUPPORT.value, packet.url):
        return Status.SUPPORT
    elif re.search(Pat.SUM.value, packet.url):
        if "popup" in packet.response.body:
            return Status.CODE_POP
        else:
            return Status.PARTY_CLICK
    elif re.search(Pat.RAID_CREATE.value, packet.url):
        if "error" in packet.response.body or "popup" in packet.response.body:
            return Status.RAID_CREATE_FALSE
        else:
            return Status.RAID_CREATE
    # 战斗
    elif re.search(Pat.RAID_INIT.value, packet.url):
        return Status.RAID_INIT
    elif re.search(Pat.RAID_START.value, packet.url):
        if packet.response.body == "":
            return Status.RAID_ERROR
        elif packet.response.body.get("scenario"):
            return Status.RAID_TRIGGER
        else:
            return Status.RAID_START
    elif re.search(Pat.ATT.value, packet.url):
        status = None
        die = False
        long_ability = False
        scenarios = packet.response.body.get("scenario")
        if scenarios is None or scenarios == []:
            return Status.NET_ERROR
        for scenario in scenarios:
            if scenario == []:
                continue
            cmd = scenario.get("cmd")
            match cmd:
                case "lose":
                    return Status.RAID_LOSE
                case "finished":
                    return Status.TURN_END
                case "win":
                    if scenario.get("is_last_raid"):
                        return Status.TURN_END
                    else:
                        return Status.NEED_BACK
                case "ability":
                    if scenario.get("name") in ABILITY_LIST:
                        long_ability = True
                case "die":
                    if scenario.get("to") == "player":
                        die = True
        if long_ability:
            return Status.LONG_ABILITY
        elif 'attack' in packet.url:
            return Status.TURN_END
        elif 'ability' in packet.url:
            if die:
                return Status.ABILITY_RESULT_DIE
            else:
                return Status.ABILITY_RESULT
        elif 'summon' in packet.url:
            if die:
                return Status.SUMMON_RESULT_DIE
            else:
                return Status.SUMMON_RESULT
        else:
            return Status.NOTHING
    # 战斗结果
    elif re.search(Pat.RESULT.value, packet.url):
        if 'redirect' in packet.response.body:
            return Status.RAID_RESULT_EMPTY
        else:
            return Status.RAID_RESULT
    # 副本选择
    elif re.search(Pat.PLAYER_STATUS.value, packet.url):
        return Status.PLAYER_STATUS
    elif "assist_list" in packet.url:
        data = packet.response.body.get("assist_raids_data")
        if data is None or data == []:
            return Status.ASSIST_NONE
        else:
            return Status.ASSIST_ENABLE
    elif re.search(Pat.RAID_CHECK.value, packet.url):
        pop = packet.response.body.get("popup")
        if pop:
            return Status.RAID_UNABLE
        else:
            return Status.RAID_ENABLE
    else:
        return Status.NOTHING

