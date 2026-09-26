from typing import Dict, List, Optional, Set


# ==========================================
# THRONE — VICTORY ENGINE
# ==========================================

SIDE_THRONE = "throne"
SIDE_DARK = "dark"
SIDE_REBEL = "rebel"
SIDE_INDEPENDENT = "independent"


GAME_RUNNING = "running"
GAME_FINISHED = "finished"


# Mustaqil rollarning maxsus g‘alaba shartlari
INDEPENDENT_ROLES = {
    "madman",
    "revenant",
    "lone_hunter",
    "shadow_king",
}


def create_victory_state() -> Dict:
    """
    O‘yin g‘alaba holatini yaratadi.
    """

    return {
        "game_status": GAME_RUNNING,
        "winner_side": None,
        "winner_players": [],
        "reason": None,
        "independent_winners": [],
    }


def normalize_side(side: Optional[str]) -> str:
    """
    Rollar uchun tomon nomlarini standartlashtiradi.
    """

    if not side:
        return ""

    return side.strip().lower()


def alive_players_by_side(
    players: List[Dict],
) -> Dict[str, List[Dict]]:
    """
    Tirik o‘yinchilarni tomonlarga ajratadi.
    """

    result = {
        SIDE_THRONE: [],
        SIDE_DARK: [],
        SIDE_REBEL: [],
        SIDE_INDEPENDENT: [],
    }

    for player in players:
        if player.get("alive") is False:
            continue

        side = normalize_side(
            player.get("side")
        )

        if side in result:
            result[side].append(player)

    return result


def alive_role_keys(players: List[Dict]) -> Set[str]:
    """
    Tirik mustaqil rollarni qaytaradi.
    """

    return {
        player.get("role_key")
        for player in players
        if player.get("alive") is not False
        and player.get("role_key")
    }


def count_alive_side(
    players: List[Dict],
    side: str,
) -> int:
    side = normalize_side(side)

    return sum(
        1
        for player in players
        if player.get("alive") is not False
        and normalize_side(player.get("side")) == side
    )


def get_alive_player(
    players: List[Dict],
    user_id: int,
) -> Optional[Dict]:
    """
    Tirik o‘yinchini ID bo‘yicha topadi.
    """

    for player in players:
        if (
            player.get("user_id") == user_id
            and player.get("alive") is not False
        ):
            return player

    return None


def check_madman_victory(
    players: List[Dict],
    eliminated_player_id: Optional[int] = None,
) -> Optional[Dict]:
    """
    🃏 Telba:
    Agar o‘zini ovoz bilan chiqarishga erishsa,
    maxsus g‘alaba oladi.
    """

    if eliminated_player_id is None:
        return None

    for player in players:
        if player.get("role_key") != "madman":
            continue

        if player.get("user_id") == eliminated_player_id:
            return {
                "side": SIDE_INDEPENDENT,
                "role_key": "madman",
                "user_id": eliminated_player_id,
                "reason": "madman_voted_out",
            }

    return None


def check_revenant_victory(
    players: List[Dict],
) -> Optional[Dict]:
    """
    💀 Qasoskor ruh uchun maxsus yakuniy shart.

    Asosiy maxsus effekt keyinchalik game state
    orqali boyitiladi.
    """

    for player in players:
        if player.get("role_key") != "revenant":
            continue

        if player.get("revenant_objective_complete") is True:
            return {
                "side": SIDE_INDEPENDENT,
                "role_key": "revenant",
                "user_id": player.get("user_id"),
                "reason": "revenant_objective_complete",
            }

    return None


def check_lone_hunter_victory(
    players: List[Dict],
) -> Optional[Dict]:
    """
    🐺 Yolg‘iz ovchi:
    Maxsus yakka maqsad bajarilganda g‘alaba.
    """

    for player in players:
        if player.get("role_key") != "lone_hunter":
            continue

        if player.get("lone_hunter_objective_complete") is True:
            return {
                "side": SIDE_INDEPENDENT,
                "role_key": "lone_hunter",
                "user_id": player.get("user_id"),
                "reason": "lone_hunter_objective_complete",
            }

    return None


def check_shadow_king_victory(
    players: List[Dict],
) -> Optional[Dict]:
    """
    👤 Soyadagi qirol:
    Maxsus yashirin maqsad bajarilganda g‘alaba.
    """

    for player in players:
        if player.get("role_key") != "shadow_king":
            continue

        if player.get("shadow_king_objective_complete") is True:
            return {
                "side": SIDE_INDEPENDENT,
                "role_key": "shadow_king",
                "user_id": player.get("user_id"),
                "reason": "shadow_king_objective_complete",
            }

    return None


def check_independent_victories(
    players: List[Dict],
    eliminated_player_id: Optional[int] = None,
) -> List[Dict]:
    """
    Barcha mustaqil rollarning g‘alaba shartlarini tekshiradi.
    """

    winners = []

    madman = check_madman_victory(
        players,
        eliminated_player_id,
    )

    if madman:
        winners.append(madman)

    revenant = check_revenant_victory(players)

    if revenant:
        winners.append(revenant)

    lone_hunter = check_lone_hunter_victory(players)

    if lone_hunter:
        winners.append(lone_hunter)

    shadow_king = check_shadow_king_victory(players)

    if shadow_king:
        winners.append(shadow_king)

    return winners


def check_main_side_victory(
    players: List[Dict],
) -> Optional[Dict]:
    """
    Asosiy tomonlarning g‘alaba shartlarini tekshiradi.

    THRONE:
    Qora va Isyon tomonlari qolmasa.

    QORA:
    Qora kuchi Taxt tomoniga teng yoki ustun
    bo‘lib, Isyon tomoni xavf tug‘dirmasa.

    ISYON:
    Taxt tomoni ustidan nazoratni qo‘lga olganida.
    """

    sides = alive_players_by_side(players)

    throne_count = len(sides[SIDE_THRONE])
    dark_count = len(sides[SIDE_DARK])
    rebel_count = len(sides[SIDE_REBEL])

    # Taxt tomonining g‘alabasi
    if dark_count == 0 and rebel_count == 0 and throne_count > 0:
        return {
            "side": SIDE_THRONE,
            "reason": "all_enemy_factions_eliminated",
        }

    # Qora tomonining g‘alabasi
    if dark_count > 0:
        enemy_count = throne_count + rebel_count

        if enemy_count == 0:
            return {
                "side": SIDE_DARK,
                "reason": "dark_side_controls_kingdom",
            }

        if dark_count >= enemy_count:
            return {
                "side": SIDE_DARK,
                "reason": "dark_side_reaches_parity",
            }

    # Isyon tomonining g‘alabasi
    if rebel_count > 0:
        enemy_count = throne_count + dark_count

        if enemy_count == 0:
            return {
                "side": SIDE_REBEL,
                "reason": "rebels_control_kingdom",
            }

    return None


def check_victory(
    players: List[Dict],
    eliminated_player_id: Optional[int] = None,
) -> Dict:
    """
    Butun o‘yin g‘alaba tizimini tekshiradi.

    Mustaqil rol g‘alabasi alohida qayd qilinadi.
    """

    if not players:
        return {
            "finished": False,
            "winner_side": None,
            "winner_players": [],
            "independent_winners": [],
            "reason": None,
        }

    independent_winners = check_independent_victories(
        players,
        eliminated_player_id,
    )

    main_winner = check_main_side_victory(players)

    if main_winner:
        winner_side = main_winner["side"]

        winner_players = [
            player.get("user_id")
            for player in players
            if player.get("alive") is not False
            and normalize_side(player.get("side
