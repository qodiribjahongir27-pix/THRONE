from typing import Dict, List, Optional


# ==========================================
# THRONE — NIGHT ENGINE
# ==========================================

PHASE_NIGHT = "night"


# Tungi harakatlarning bajarilish tartibi
ACTION_PRIORITY = {
    "observer": 10,
    "protector": 20,
    "blocker": 30,
    "poison": 40,
    "weaken": 50,
    "attacker": 60,
    "special": 70,
}


def create_night_state() -> Dict:
    """
    Yangi tun uchun vaqtinchalik holat yaratadi.
    """
    return {
        "phase": PHASE_NIGHT,
        "actions": [],
        "protected": [],
        "blocked": [],
        "poisoned": [],
        "weakened": [],
        "attacked": [],
        "observations": [],
        "special_results": [],
        "dead_players": [],
    }


def add_night_action(
    state: Dict,
    player_id: int,
    role_key: str,
    action_type: str,
    target_id: Optional[int] = None,
    value: Optional[int] = None,
) -> bool:
    """
    O‘yinchining tungi harakatini navbatga qo‘shadi.
    """

    if not state:
        return False

    if state.get("phase") != PHASE_NIGHT:
        return False

    action = {
        "player_id": player_id,
        "role_key": role_key,
        "action_type": action_type,
        "target_id": target_id,
        "value": value,
    }

    state["actions"].append(action)
    return True


def sort_night_actions(state: Dict) -> List[Dict]:
    """
    Tungi harakatlarni belgilangan ustuvorlik bo‘yicha saralaydi.
    """

    actions = state.get("actions", [])

    return sorted(
        actions,
        key=lambda action: ACTION_PRIORITY.get(
            action.get("action_type"),
            999,
        ),
    )


def apply_protection(
    state: Dict,
    target_id: int,
    protector_id: Optional[int] = None,
) -> None:
    """
    O‘yinchini tungi hujumdan himoya qiladi.
    """

    if target_id not in state["protected"]:
        state["protected"].append(target_id)

    state["special_results"].append(
        {
            "type": "protection",
            "target_id": target_id,
            "protector_id": protector_id,
        }
    )


def apply_block(
    state: Dict,
    target_id: int,
    blocker_id: Optional[int] = None,
) -> None:
    """
    O‘yinchining tungi harakatini bloklaydi.
    """

    if target_id not in state["blocked"]:
        state["blocked"].append(target_id)

    state["special_results"].append(
        {
            "type": "block",
            "target_id": target_id,
            "blocker_id": blocker_id,
        }
    )


def apply_poison(
    state: Dict,
    target_id: int,
    attacker_id: Optional[int] = None,
) -> None:
    """
    Nishonga zahar ta’sirini beradi.
    """

    if target_id not in state["poisoned"]:
        state["poisoned"].append(target_id)

    state["special_results"].append(
        {
            "type": "poison",
            "target_id": target_id,
            "attacker_id": attacker_id,
        }
    )


def apply_weaken(
    state: Dict,
    target_id: int,
    attacker_id: Optional[int] = None,
) -> None:
    """
    Nishonni zaiflashtiradi.
    """

    if target_id not in state["weakened"]:
        state["weakened"].append(target_id)

    state["special_results"].append(
        {
            "type": "weaken",
            "target_id": target_id,
            "attacker_id": attacker_id,
        }
    )


def apply_attack(
    state: Dict,
    attacker_id: int,
    target_id: int,
) -> Dict:
    """
    Oddiy tungi hujumni hisoblaydi.
    """

    result = {
        "attacker_id": attacker_id,
        "target_id": target_id,
        "success": False,
        "reason": None,
    }

    if target_id in state["protected"]:
        result["reason"] = "protected"
        state["special_results"].append(
            {
                "type": "attack_blocked_by_protection",
                "attacker_id": attacker_id,
                "target_id": target_id,
            }
        )
        return result

    if target_id not in state["attacked"]:
        state["attacked"].append(target_id)

    result["success"] = True

    return result


def execute_night_actions(state: Dict) -> Dict:
    """
    Barcha tungi harakatlarni to‘g‘ri tartibda bajaradi.

    Muhim:
    Bu funksiya hali real DB o‘yinchilarini o‘ldirmaydi.
    U faqat tun natijasini tayyorlaydi.
    Yakuniy o‘lim/victory logikasi victory.py orqali ulanadi.
    """

    results = {
        "protected": [],
        "blocked": [],
        "poisoned": [],
        "weakened": [],
        "attacks": [],
        "observations": [],
        "special_results": [],
        "dead_players": [],
    }

    actions = sort_night_actions(state)

    # --------------------------------------
    # 1. Kuzatuvchilar
    # --------------------------------------

    for action in actions:
        if action["action_type"] != "observer":
            continue

        target_id = action.get("target_id")

        if target_id is not None:
            observation = {
                "observer_id": action["player_id"],
                "target_id": target_id,
            }

            state["observations"].append(observation)

    # --------------------------------------
    # 2. Himoyachilar
    # --------------------------------------

    for action in actions:
        if action["action_type"] != "protector":
            continue

        target_id = action.get("target_id")

        if target_id is not None:
            apply_protection(
                state,
                target_id,
                action["player_id"],
            )

    # --------------------------------------
    # 3. Bloklovchilar
    # --------------------------------------

    for action in actions:
        if action["action_type"] != "blocker":
            continue

        target_id = action.get("target_id")

        if target_id is not None:
            apply_block(
                state,
                target_id,
                action["player_id"],
            )

    # --------------------------------------
    # 4. Zahar
    # --------------------------------------

    for action in actions:
        if action["action_type"] != "poison":
            continue

        if action["player_id"] in state["blocked"]:
            continue

        target_id = action.get("target_id")

        if target_id is not None:
            apply_poison(
                state,
                target_id,
                action["player_id"],
            )

    # --------------------------------------
    # 5. Zaiflashtirish
    # --------------------------------------

    for action in actions:
        if action["action_type"] != "weaken":
            continue

        if action["player_id"] in state["blocked"]:
            continue

        target_id = action.get("target_id")

        if target_id is not None:
            apply_weaken(
                state,
                target_id,
                action["player_id"],
            )

    # --------------------------------------
    # 6. Hujumchilar
    # --------------------------------------

    for action in actions:
        if action["action_type"] != "attacker":
            continue

        if action["player_id"] in state["blocked"]:
            continue

        target_id = action.get("target_id")

        if target_id is None:
            continue

        attack_result = apply_attack(
            state,
            action["player_id"],
            target_id,
        )

        results["attacks"].append(attack_result)

        if attack_result["success"]:
            state["dead_players"].append(target_id)

    # --------------------------------------
    # 7. Maxsus qobiliyatlar
    # --------------------------------------

    for action in actions:
        if action["action_type"] != "special":
            continue

        if action["player_id"] in state["blocked"]:
            continue

        state["special_results"].append(
            {
                "type": "special",
                "player_id": action["player_id"],
                "target_id": action.get("target_id"),
                "value": action.get("value"),
            }
        )

    # --------------------------------------
    # Natijani qaytarish
    # --------------------------------------

    results["protected"] = list(state["protected"])
    results["blocked"] = list(state["blocked"])
    results["poisoned"] = list(state["poisoned"])
    results["weakened"] = list(state["weakened"])
    results["observations"] = list(state["observations"])
    results["special_results"] = list(state["special_results"])
    results["dead_players"] = list(
        dict.fromkeys(state["dead_players"])
    )

    return results


def build_night_summary(results: Dict) -> str:
    """
    Guruhga chiqadigan umumiy tun xabarini tayyorlaydi.
    Maxfiy rollar yoki yashirin harakatlarni oshkor qilmaydi.
    """

    deaths = len(results.get("dead_players", []))

    if deaths == 0:
        return (
            "🌙 <b>THRONE — TUN YAKUNLANDI</b>\n\n"
            "🏰 Saroy ustida tun sukunati hukm surdi.\n"
            "☀️ Tong otdi.\n\n"
            "⚔️ Hech kim bu tun taxtdan ayrilmadi."
        )

    if deaths == 1:
        return (
            "🌙 <b>THRONE — TUN YAKUNLANDI</b>\n\n"
            "🏰 Qorong‘ulik ortida keskin voqea yuz berdi.\n"
            "☀️ Tong otdi.\n\n"
            "⚔️ Bu tun qirollikdan <b>1 o‘yinchi</b> ayrildi."
        )

    return (
        "🌙 <b>THRONE — TUN YAKUNLANDI</b>\n\n"
        "🏰 Qorong‘ulik ortida bir nechta voqea yuz berdi.\n"
        "☀️ Tong otdi.\n\n"
        f"⚔️ Bu tun <b>{deaths} o‘yinchi</b> qirollikdan ayrildi."
          )
