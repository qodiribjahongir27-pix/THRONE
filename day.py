from typing import Dict, List, Optional


# ==========================================
# THRONE — DAY ENGINE
# ==========================================

PHASE_DAY = "day"
PHASE_DISCUSSION = "discussion"
PHASE_VOTING = "voting"


def create_day_state(day_number: int = 1) -> Dict:
    """Yangi kun uchun vaqtinchalik holat yaratadi."""

    return {
        "phase": PHASE_DAY,
        "day_number": day_number,
        "discussion_started": False,
        "voting_started": False,
        "votes": {},
        "eliminated_player": None,
        "last_words_player": None,
        "last_words_text": None,
        "events": [],
    }


def start_day(state: Dict, day_number: Optional[int] = None) -> Dict:
    """Tun tugagach yangi kunni boshlaydi."""

    if day_number is not None:
        state["day_number"] = day_number

    state["phase"] = PHASE_DAY
    state["discussion_started"] = False
    state["voting_started"] = False
    state["votes"] = {}
    state["eliminated_player"] = None
    state["last_words_player"] = None
    state["last_words_text"] = None

    state["events"].append(
        {
            "type": "day_started",
            "day": state["day_number"],
        }
    )

    return state


def start_discussion(state: Dict) -> bool:
    """Kunlik muhokamani boshlaydi."""

    if state.get("phase") != PHASE_DAY:
        return False

    state["phase"] = PHASE_DISCUSSION
    state["discussion_started"] = True

    state["events"].append(
        {
            "type": "discussion_started",
            "day": state["day_number"],
        }
    )

    return True


def start_voting(state: Dict) -> bool:
    """Muhokama tugagach ovoz berishni boshlaydi."""

    if state.get("phase") not in (
        PHASE_DAY,
        PHASE_DISCUSSION,
    ):
        return False

    state["phase"] = PHASE_VOTING
    state["voting_started"] = True
    state["votes"] = {}

    state["events"].append(
        {
            "type": "voting_started",
            "day": state["day_number"],
        }
    )

    return True


def add_vote(
    state: Dict,
    voter_id: int,
    target_id: int,
) -> bool:
    """O‘yinchining ovozini saqlaydi."""

    if state.get("phase") != PHASE_VOTING:
        return False

    state["votes"][voter_id] = target_id

    return True


def remove_vote(
    state: Dict,
    voter_id: int,
) -> bool:
    """Ovozini o‘chiradi."""

    if voter_id not in state.get("votes", {}):
        return False

    del state["votes"][voter_id]

    return True


def get_vote_counts(state: Dict) -> Dict[int, int]:
    """Har bir nomzod nechta ovoz olganini hisoblaydi."""

    counts: Dict[int, int] = {}

    for target_id in state.get("votes", {}).values():
        counts[target_id] = counts.get(target_id, 0) + 1

    return counts


def get_vote_result(state: Dict) -> Dict:
    """
    Ovoz berish natijasini chiqaradi.

    Qoidalar:
    - eng ko‘p ovoz olgan o‘yinchi chiqariladi;
    - durang bo‘lsa qayta ovoz berish kerak;
    - qayta ovozda ham durang bo‘lsa hech kim chiqmaydi.
    """

    counts = get_vote_counts(state)

    if not counts:
        return {
            "status": "no_votes",
            "winner": None,
            "top_count": 0,
            "counts": {},
        }

    top_count = max(counts.values())

    leaders = [
        player_id
        for player_id, count in counts.items()
        if count == top_count
    ]

    if len(leaders) == 1:
        return {
            "status": "elimination",
            "winner": leaders[0],
            "top_count": top_count,
            "counts": counts,
        }

    return {
        "status": "tie",
        "winner": None,
        "leaders": leaders,
        "top_count": top_count,
        "counts": counts,
    }


def eliminate_player(
    state: Dict,
    player_id: int,
) -> bool:
    """Ovoz orqali chiqarilgan o‘yinchini belgilaydi."""

    if state.get("phase") != PHASE_VOTING:
        return False

    state["eliminated_player"] = player_id

    state["events"].append(
        {
            "type": "player_eliminated",
            "player_id": player_id,
            "day": state["day_number"],
        }
    )

    return True


def set_last_words(
    state: Dict,
    player_id: int,
    text: str,
) -> bool:
    """Chiqarilgan o‘yinchining so‘nggi so‘zini saqlaydi."""

    if state.get("eliminated_player") != player_id:
        return False

    clean_text = (text or "").strip()

    if not clean_text:
        return False

    state["last_words_player"] = player_id
    state["last_words_text"] = clean_text

    state["events"].append(
        {
            "type": "last_words",
            "player_id": player_id,
        }
    )

    return True


def auto_last_words(
    state: Dict,
    player_id: int,
) -> str:
    """
    O‘yinchi so‘nggi so‘z yozmasa ishlatiladigan
    avtomatik THRONE uslubidagi jumla.
    """

    text = (
        "👑 Taxt jim qolmaydi. "
        "Haqiqat bir kun baribir yuzaga chiqadi."
    )

    state["last_words_player"] = player_id
    state["last_words_text"] = text

    state["events"].append(
        {
            "type": "auto_last_words",
            "player_id": player_id,
        }
    )

    return text


def finish_voting(state: Dict) -> Dict:
    """
    Ovoz berishni yakunlaydi.

    Birinchi ovozda durang bo‘lsa:
    status = revote

    Qayta ovoz berishda ham durang bo‘lsa:
    status = no_elimination
    """

    result = get_vote_result(state)

    if result["status"] == "no_votes":
        return {
            "status": "no_elimination",
            "player_id": None,
            "message": (
                "⚖️ Hech qanday ovoz berilmadi. "
                "Bugun hech kim chiqarilmadi."
            ),
        }

    if result["status"] == "tie":
        return {
            "status": "revote",
            "player_id": None,
            "leaders": result["leaders"],
            "message": (
                "⚖️ Ovozlar teng keldi.\n"
                "🔄 Qayta ovoz berish boshlanadi."
            ),
        }

    player_id = result["winner"]

    eliminate_player(
        state,
        player_id,
    )

    return {
        "status": "elimination",
        "player_id": player_id,
        "votes": result["top_count"],
        "message": (
            "⚔️ Ovoz berish yakunlandi.\n"
            "👑 Eng ko‘p ovoz olgan o‘yinchi "
            "taxtdan chetlatildi."
        ),
    }


def finish_revote(state: Dict) -> Dict:
    """
    Qayta ovoz berish natijasini yakunlaydi.

    Bu bosqichda yana durang bo‘lsa,
    hech kim chiqarilmaydi.
    """

    result = get_vote_result(state)

    if result["status"] == "no_votes":
        state["eliminated_player"] = None

        return {
            "status": "no_elimination",
            "player_id": None,
        }

    if result["status"] == "tie":
        state["eliminated_player"] = None

        state["events"].append(
            {
                "type": "revote_tie",
                "day": state["day_number"],
            }
        )

        return {
            "status": "no_elimination",
            "player_id": None,
            "leaders": result["leaders"],
            "message": (
                "⚖️ Qayta ovoz berishda ham "
                "tenglik yuz berdi.\n"
                "🏰 Bugun hech kim chiqarilmadi."
            ),
        }

    player_id = result["winner"]

    eliminate_player(
        state,
        player_id,
    )

    return {
        "status": "elimination",
        "player_id": player_id,
        "votes": result["top_count"],
    }


def build_day_message(
    day_number: int,
    eliminated_count: int = 0,
) -> str:
    """Guruhga yuboriladigan kun xabarini tayyorlaydi."""

    if eliminated_count == 0:
        return (
            f"☀️ <b>THRONE — {day_number}-KUN</b>\n\n"
            "🏰 Tong otdi.\n"
            "Qirollik yana uyg‘ondi.\n\n"
            "🗣️ Muhokama boshlanadi.\n"
            "Har bir so‘z va har bir qaror muhim."
        )

    return (
        f"☀️ <b>THRONE — {day_number}-KUN</b>\n\n"
        "🏰 Tong otdi.\n"
        f"⚔️ Kecha <b>{eliminated_count}</b> o‘yinchi "
        "qirollikdan ayrildi.\n\n"
        "🗣️ Endi muhokama boshlanadi."
    )


def build_voting_message() -> str:
    """Ovoz berish boshlanganda chiqadigan xabar."""

    return (
        "⚖️ <b>THRONE — OVOZ BERISH</b>\n\n"
        "👑 Endi qaror sizning qo‘lingizda.\n"
        "Shubhali deb hisoblagan o‘yinchingizga ovoz bering.\n\n"
        "⏳ Ovoz berish yakunlangach natija e’lon qilinadi."
    )


def build_elimination_message(
    player_name: str,
    votes: int,
) -> str:
    """Chiqarilgan o‘yinchi uchun umumiy guruh xabari."""

    return (
        "⚖️ <b>HUKM CHIQARILDI</b>\n\n"
        f"👤 <b>{player_name}</b>\n"
        f"🗳️ Ovozlar: <b>{votes}</b>\n\n"
        "🗣️ Unga so‘nggi so‘z uchun imkon beriladi."
    )


def build_last_words_message(
    player_name: str,
    last_words: str,
) -> str:
    """So‘nggi so‘z xabari."""

    return (
        "🗣️ <b>SO‘NGGI SO‘Z</b>\n\n"
        f"👤 <b>{player_name}</b>:\n"
        f"«{last_words}»"
    )


def build_revote_message() -> str:
    """Durangdan keyingi qayta ovoz berish xabari."""

    return (
        "🔄 <b>QAYTA OVOZ BERISH</b>\n\n"
        "⚖️ Ovozlar teng keldi.\n"
        "Endi yakuniy qaror uchun qayta ovoz bering."
    )


def build_no_elimination_message() -> str:
    """Qayta ovozda ham durang bo‘lganda."""

    return (
        "⚖️ <b>YAKUNIY HUKM</b>\n\n"
        "Ovozlar yana teng keldi.\n"
        "🏰 Bugun hech kim chiqarilmadi.\n\n"
        "🌙 Qirollik yana tun bag‘riga kiradi."
    )
