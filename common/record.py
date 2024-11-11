from logger import logger
import json
from common.status import Status, get_status


class Record:
    def __init__(self, page) -> None:
        self.page = page

    def record_battle(self):
        data = []
        init_flag = True
        while True:
            for packet in self.page.listen.steps(timeout=1):
                status = get_status(packet)
                status_type = None
                additional_data = {}

                match status:
                    case Status.MYPAGE:
                        status_type = "mypage"
                    case Status.RAID_START:
                        status_type = "start" if init_flag else "refresh"
                        init_flag = False
                    case Status.CHANGE_CA:
                        status_type = "change_ca"
                    case Status.FC:
                        status_type = "fc"
                    case Status.HEAL:
                        status_type = "heal"
                        list_heal = packet.response.body.get("scenario")[0].get("list")
                        if len(list_heal) == 1:
                            pos = list_heal[0].get("pos")
                            type_heal = "green"
                        else:
                            pos = -1
                            type_heal = "blue"
                        additional_data = {"pos": pos, "type_heal": type_heal}
                    case Status.CHAT:
                        status_type = "chat"
                    case Status.TURN_END:
                        status_type = "attack"
                        guard = []
                        for s in packet.response.body.get("status").get("is_guard_status"):
                            guard.append(s.get("is_guard_status"))
                        is_fa = self.page.run_js("stage.gGameStatus.auto_attack", as_expr=True)
                        additional_data = {"is_fa": is_fa, "guard": guard[:]}
                    case Status.SUMMON_RESULT | Status.SUMMON_RESULT_DIE:
                        status_type = "summon"
                        name = packet.response.body.get("scenario")[0].get("name")
                        param = self.page.run_js("stage.gGameStatus.attackQueue.queue[0].param", as_expr=True)
                        summon_id = int(param.get("summon_id")) + 1 if param.get("summon_id") != "supporter" else 6
                        is_fa = param.get("is_quick_summon")
                        additional_data = {"target": summon_id, "is_fa": is_fa, "name": name}
                    case Status.ABILITY_RESULT | Status.ABILITY_RESULT_DIE:
                        status_type = "ability"
                        name = packet.response.body.get("scenario")[0].get("name")
                        param = self.page.run_js("stage.gGameStatus.attackQueue.queue[0].param", as_expr=True)
                        is_fa = param.get("is_by_auto")
                        if is_fa:
                            ability_number = param.get("abilityNumber")
                            user = int(param.get("ability_character_num")) + 1
                            target = 0
                            ability_sub_param = 0
                        else:
                            ele_ablity_class = self.page.run_js("stage.gGameStatus.$use_ability.context.firstElementChild", as_expr=True).attr("class")
                            user, ability_number = ele_ablity_class[-3:].split("-")
                            target = int(param.get("ability_aim_num")) + 1 if param.get("ability_aim_num") is not None else 0
                            ability_sub_param = param.get("ability_sub_param")
                        additional_data = {
                            "user": int(user),
                            "ability_number": int(ability_number),
                            "target": int(target),
                            "is_fa": is_fa,
                            "ability_sub_param": ability_sub_param,
                            "name": name,
                        }

                if status_type:
                    logger.attr("type", status_type)
                    for key, value in additional_data.items():
                        logger.info(f"{key} = {value}")
                    data.append({"type": status_type, **additional_data})

                if self.parent.record_stop:
                    break
                logger.hr(2)

            if self.parent.record_stop:
                self.page.listen.stop()
                if self.parent.record_name:
                    with open(f"./custom/{self.parent.record_name}.json", 'w', encoding="utf-8") as file:
                        json.dump(data, file, indent=4)
                return True