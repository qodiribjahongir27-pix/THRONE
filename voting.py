from typing import Dict, List, Optional


# ==========================================
# THRONE — VOTING ENGINE
# ==========================================

VOTING_ACTIVE = "active"
VOTING_REVOTE = "revote"
VOTING_FINISHED = "finished"


def create_voting_state(
    players: Optional[List[int]] = None,
    revote: bool = False,
) -> Dict:
    """
    Yangi ovoz berish holatini yaratadi.
    """

    return {
        "status": VOTING_REVOTE if revote else VOTING_ACTIVE,
        "players": list(players or []),
        "votes": {},
        "revote": revote,
        "result": None,
    }


def is_voting_active(state: Dict) -> bool:
    return state.get("status") in (
        VOTING_ACTIVE,
        VOTING_REVOTE,
    )


def can_vote(
    state: Dict,
    voter_id: int,
    alive_players: Optional[List[int]] = None,
) -> bool:
    """
    O‘yinchi ovoz bera oladimi?
    """

    if not is_voting_active(state):
        return False

    players = alive_players if alive_players is not None else state["players"]

    return voter_id in players


def can_target(
    state: Dict,
    target_id: int,
    alive_players: Optional[List[int]] = None,
) -> bool:
    """
    Nishon ovoz berishdagi tirik o‘yinchi ekanini tekshiradi.
    """

    if not is_voting_active(state):
        return False

    players = alive_players if alive_players is not None else state["players"]

    return target_id in players


def cast_vote(
    state: Dict,
    voter_id: int,
    target_id: int,
    alive_players: Optional[List[int]] = None,
) -> Dict:
    """
    Ovoz beradi yoki mavjud ovozni almashtiradi.
    """

    if not is_voting_active(state):
        return {
            "success": False,
            "reason": "voting_not_active",
        }

    if not can_vote(
        state,
        voter_id,
        alive_players,
    ):
        return {
            "success": False,
            "reason": "voter_not_allowed",
        }

    if not can_target(
        state,
        target_id,
        alive_players,
    ):
        return {
            "success": False,
            "reason": "target_not_allowed",
        }

    previous_target = state["votes"].get(voter_id)

    state["votes"][voter_id] = target_id

    return {
        "success": True,
        "voter_id": voter_id,
        "target_id": target_id,
        "changed": previous_target is not None,
        "previous_target": previous_target,
    }


def remove_vote(
    state: Dict,
    voter_id: int,
) -> bool:
    """
    O‘yinchining ovozini olib tashlaydi.
    """

    if voter_id not in state["votes"]:
        return False

    del state["votes"][voter_id]

    return True


def get_voter_count(state: Dict) -> int:
    return len(state.get("votes", {}))


def get_vote_counts(state: Dict) -> Dict[int, int]:
    """
    Har bir nishonning ovoz sonini hisoblaydi.
    """

    counts: Dict[int, int] = {}

    for target_id in state.get("votes", {}).values():
        counts[target_id] = counts.get(target_id, 0) + 1

    return counts


def get_votes_for_player(
    state: Dict,
    player_id: int,
) -> int:
    return get_vote_counts(state).get(player_id, 0)


def get_vote_leaders(state: Dict) -> List[int]:
    """
    Eng ko‘p ovoz olgan o‘yinchilar.
    """

    counts = get_vote_counts(state)

    if not counts:
        return []

    highest = max(counts.values())

    return [
        player_id
        for player_id, count in counts.items()
        if count == highest
    ]


def calculate_result(state: Dict) -> Dict:
    """
    Ovoz berish natijasini hisoblaydi.
    """

    counts = get_vote_counts(state)

    if not counts:
        return {
            "status": "no_votes",
            "eliminated_player": None,
            "leaders": [],
            "votes": 0,
            "counts": {},
        }

    leaders = get_vote_leaders(state)

    highest = max(counts.values())

    if len(leaders) > 1:
        return {
            "status": "tie",
            "eliminated_player": None,
            "leaders": leaders,
            "votes": highest,
            "counts": counts,
        }

    return {
        "status": "elimination",
        "eliminated_player": leaders[0],
        "leaders": leaders,
        "votes": highest,
        "counts": counts,
    }


def finish_first_vote(state: Dict) -> Dict:
    """
    Birinchi ovoz berishni yakunlaydi.

    Durang bo‘lsa qayta ovozga o‘tadi.
    """

    result = calculate_result(state)

    if result["status"] == "no_votes":
        state["status"] = VOTING_FINISHED
        state["result"] = result

        return result

    if result["status"] == "tie":
        state["status"] = VOTING_REVOTE
        state["revote"] = True
        state["votes"] = {}

        return {
            "status": "revote",
            "leaders": result["leaders"],
            "votes": result["votes"],
            "counts": result["counts"],
        }

    state["status"] = VOTING_FINISHED
    state["result"] = result

    return result


def finish_revote(state: Dict) -> Dict:
    """
    Qayta ovoz berishni yakunlaydi.

    Agar yana durang bo‘lsa, hech kim chiqarilmaydi.
    """

    result = calculate_result(state)

    if result["status"] == "no_votes":
        final_result = {
            "status": "no_elimination",
            "eliminated_player": None,
            "leaders": [],
            "votes": 0,
        }

        state["status"] = VOTING_FINISHED
        state["result"] = final_result

        return final_result

    if result["status"] == "tie":
        final_result = {
            "status": "no_elimination",
            "eliminated_player": None,
            "leaders": result["leaders"],
            "votes": result["votes"],
            "reason": "second_tie",
        }

        state["status"] = VOTING_FINISHED
        state["result"] = final_result

        return final_result

    state["status"] = VOTING_FINISHED
    state["result"] = result

    return result


def reset_for_revote(state: Dict) -> None:
    """
    Qayta ovoz berishga tayyorlaydi.
    """

    state["status"] = VOTING_REVOTE
    state["revote"] = True
    state["votes"] = {}
    state["result"] = None


def remove_dead_players(
    state: Dict,
    dead_players: List[int],
) -> None:
    """
    Tirik o‘yinchilar ro‘yxatidan chiqarilganlarni olib tashlaydi.
    """

    dead = set(dead_players)

    state["players"] = [
        player_id
        for player_id in state["players"]
        if player_id not in dead
    ]

    state["votes"] = {
        voter_id: target_id
        for voter_id, target_id in state["votes"].items()
        if voter_id not in dead
        and target_id not in dead
    }


def build_vote_keyboard_data(
    players: List[Dict],
    voter_id: int,
) -> List[Dict]:
    """
    Telegram inline tugmalari uchun xavfsiz
    ovoz nishonlari ro‘yxatini tayyorlaydi.

    Bu yerda Telegram keyboard yaratilmaydi;
    keyboards.py keyin shu ma'lumotdan foydalanadi.
    """

    result = []

    for player in players:
        player_id = player.get("user_id")

        if player_id is None:
            continue

        if player_id == voter_id:
            continue

        result.append(
            {
                "user_id": player_id,
                "name": player.get(
                    "full_name",
                    f"Player {player_id}",
                ),
                "callback": f"vote:{player_id}",
            }
        )

    return result


def build_vote_status(
    state: Dict,
    player_names: Optional[Dict[int, str]] = None,
) -> str:
    """
    Ovoz berish holatini guruh uchun umumiy ko‘rinishda tayyorlaydi.
    """

    counts = get_vote_counts(state)

    if not counts:
        return (
            "⚖️ <b>OVOZ BERISH</b>\n\n"
            "Hozircha ovozlar yo‘q."
        )

    names = player_names or {}

    lines = [
        "⚖️ <b>OVOZ BERISH NATIJASI</b>",
        "",
    ]

    sorted_counts = sorted(
        counts.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    for player_id, count in sorted_counts:
        name = names.get(
            player_id,
            f"Player {player_id}",
        )

        lines.append(
            f"👤 {name} — <b>{count}</b>"
        )

    lines.extend(
        [
            "",
            f"🗳️ Ovoz berganlar: <b>{get_voter_count(state)}</b>",
        ]
    )

    return "\n".join(lines)


def build_vote_result_message(
    result: Dict,
    player_names: Optional[Dict[int, str]] = None,
) -> str:
    """
    Yakuniy ovoz natijasi uchun guruh xabari.
    """

    names = player_names or {}

    status = result.get("status")

    if status == "no_votes":
        return (
            "⚖️ <b>HUKM</b>\n\n"
            "Ovoz berilmadi.\n"
            "🏰 Hech kim chiqarilmadi."
        )

    if status == "revote":
        leaders = result.get("leaders", [])

        names_text = ", ".join(
            names.get(
                player_id,
                f"Player {player_id}",
            )
            for player_id in leaders
        )

        return (
            "⚖️ <b>OVOZLAR TENGLASHDI</b>\n\n"
            f"👤 {names_text}\n\n"
            "🔄 Qayta ovoz berish boshlanadi."
        )

    if status == "no_elimination":
        return (
            "⚖️ <b>YAKUNIY HUKM</b>\n\n"
            "Ovozlar yana teng keldi.\n"
            "🏰 Bugun hech kim chiqarilmadi."
        )

    if status == "elimination":
        player_id = result.get("eliminated_player")

        name = names.get(
            player_id,
            f"Player {player_id}",
        )

        votes = result.get("votes", 0)

        return (
            "⚔️ <b>HUKM CHIQARILDI</b>\n\n"
            f"👤 <b>{name}</b>\n"
            f"🗳️ Ovozlar: <b>{votes}</b>\n\n"
            "🗣️ Endi so‘nggi so‘z vaqti."
        )

    return "⚖️ Ovoz berish yakunlandi."


def voting_finished(state: Dict) -> bool:
    return state.get("status") == VOTING_FINISHED


def get_final_eliminated_player(
    state: Dict,
) -> Optional[int]:
    result = state.get("result") or {}

    if result.get("status") != "elimination":
        return None

    return result.get("eliminated_player")
