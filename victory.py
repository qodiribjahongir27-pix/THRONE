from typing import Dict, List, Optional, Set


# ==========================================
# THRONE — VICTORY ENGINE
# ==========================================

SIDE_TAXT = "Taxt"
SIDE_QORA = "Qora"
SIDE_ISYON = "Isyon"
SIDE_MUSTAQIL = "Mustaqil"

GAME_RUNNING = "running"
GAME_FINISHED = "finished"

INDEPENDENT_ROLES = {
    "madman",
    "revenant",
    "lone_hunter",
    "shadow_king",
}


# ==========================================
# STATE
# ==========================================

def create_victory_state() -> Dict:
    return {
        "game_status": GAME_RUNNING,
        "winner_side": None,
        "winner_players": [],
        "reason": None,
        "independent_winners": [],
    }


# ==========================================
# HELPERS
# ==========================================

def normalize_side(side: Optional[str]) -> str:
    if not side:
        return ""

    value = side.strip().lower()

    aliases = {
        "taxt": SIDE_TAXT,
        "throne": SIDE_TAXT,
        "qora": SIDE_QORA,
        "dark": SIDE_QORA,
        "isyon": SIDE_ISYON,
        "rebel": SIDE_ISYON,
        "mustaqil": SIDE_MUSTAQIL,
        "independent": SIDE_MUSTAQIL,
    }

    return aliases.get(value, side.strip())


def is_alive(player: Dict) -> bool:
    return player.get("alive") is not False


def alive_players(players: List[Dict]) -> List[Dict]:
    return [
        player
        for player in players
        if is_alive(player)
    ]


def alive_players_by_side(
    players: List[Dict],
) -> Dict[str, List[Dict]]:

    result = {
        SIDE_TAXT: [],
        SIDE_QORA: [],
        SIDE_ISYON: [],
        SIDE_MUSTAQIL: [],
    }

    for player in players:
        if not is_alive(player):
            continue

        side = normalize_side(
            player.get("side")
        )

        if side in result:
            result[side].append(player)

    return result


def alive_role_keys(
    players: List[Dict],
) -> Set[str]:

    return {
        player.get("role_key")
        for player in players
        if is_alive(player)
        and player.get("role_key")
    }


def count_alive_side(
    players: List[Dict],
    side: str,
) -> int:

    normalized = normalize_side(side)

    return sum(
        1
        for player in players
        if is_alive(player)
        and normalize_side(
            player.get("side")
        ) == normalized
    )


def get_alive_player(
    players: List[Dict],
    user_id: int,
) -> Optional[Dict]:

    for player in players:
        if (
            player.get("user_id") == user_id
            and is_alive(player)
        ):
            return player

    return None


# ==========================================
# INDEPENDENT VICTORIES
# ==========================================

def check_madman_victory(
    players: List[Dict],
    eliminated_player_id: Optional[int] = None,
) -> Optional[Dict]:
    """
    🃏 Telba:
    Ovoz orqali chiqarilsa darhol maxsus g‘alaba oladi.
    """

    if eliminated_player_id is None:
        return None

    for player in players:

        if player.get("role_key") != "madman":
            continue

        if player.get("user_id") != eliminated_player_id:
            continue

        return {
            "side": SIDE_MUSTAQIL,
            "role_key": "madman",
            "user_id": eliminated_player_id,
            "reason": "madman_voted_out",
        }

    return None


def check_revenant_victory(
    players: List[Dict],
) -> Optional[Dict]:

    for player in players:

        if player.get("role_key") != "revenant":
            continue

        if player.get(
            "revenant_objective_complete"
        ) is True:

            return {
                "side": SIDE_MUSTAQIL,
                "role_key": "revenant",
                "user_id": player.get("user_id"),
                "reason": "revenant_objective_complete",
            }

    return None


def check_lone_hunter_victory(
    players: List[Dict],
) -> Optional[Dict]:

    for player in players:

        if player.get("role_key") != "lone_hunter":
            continue

        if player.get(
            "lone_hunter_objective_complete"
        ) is True:

            return {
                "side": SIDE_MUSTAQIL,
                "role_key": "lone_hunter",
                "user_id": player.get("user_id"),
                "reason": "lone_hunter_objective_complete",
            }

    return None


def check_shadow_king_victory(
    players: List[Dict],
) -> Optional[Dict]:

    for player in players:

        if player.get("role_key") != "shadow_king":
            continue

        if player.get(
            "shadow_king_objective_complete"
        ) is True:

            return {
                "side": SIDE_MUSTAQIL,
                "role_key": "shadow_king",
                "user_id": player.get("user_id"),
                "reason": "shadow_king_objective_complete",
            }

    return None


def check_independent_victories(
    players: List[Dict],
    eliminated_player_id: Optional[int] = None,
) -> List[Dict]:

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


# ==========================================
# MAIN SIDE VICTORY
# ==========================================

def check_main_side_victory(
    players: List[Dict],
) -> Optional[Dict]:
    """
    Asosiy tomonlarning g‘alaba shartlari.

    TAxt:
        Qora va Isyon yo‘q qilinsa.

    Qora:
        Qora kuchi qolgan dushman kuchlariga
        teng yoki ustun bo‘lsa.

    Isyon:
        Taxt va Qora tomonlari qolmasa.
    """

    sides = alive_players_by_side(players)

    taxt_count = len(sides[SIDE_TAXT])
    qora_count = len(sides[SIDE_QORA])
    isyon_count = len(sides[SIDE_ISYON])

    # ======================================
    # TAХT G‘ALABASI
    # ======================================

    if (
        taxt_count > 0
        and qora_count == 0
        and isyon_count == 0
    ):

        return {
            "side": SIDE_TAXT,
            "reason": "all_enemy_factions_eliminated",
        }

    # ======================================
    # QORA G‘ALABASI
    # ======================================

    if qora_count > 0:

        enemy_count = (
            taxt_count
            + isyon_count
        )

        # Qora butun raqiblarni yo‘q qilgan
        if enemy_count == 0:

            return {
                "side": SIDE_QORA,
                "reason": "dark_side_controls_kingdom",
            }

        # Qora son jihatdan teng yoki ustun
        if qora_count >= enemy_count:

            return {
                "side": SIDE_QORA,
                "reason": "dark_side_reaches_parity",
            }

    # ======================================
    # ISYON G‘ALABASI
    # ======================================

    if isyon_count > 0:

        enemy_count = (
            taxt_count
            + qora_count
        )

        if enemy_count == 0:

            return {
                "side": SIDE_ISYON,
                "reason": "rebels_control_kingdom",
            }

    return None


# ==========================================
# COMPLETE VICTORY CHECK
# ==========================================

def check_victory(
    players: List[Dict],
    eliminated_player_id: Optional[int] = None,
) -> Dict:

    if not players:

        return {
            "finished": False,
            "game_status": GAME_RUNNING,
            "winner_side": None,
            "winner_players": [],
            "independent_winners": [],
            "reason": None,
        }

    independent_winners = (
        check_independent_victories(
            players,
            eliminated_player_id,
        )
    )

    main_winner = check_main_side_victory(
        players
    )

    # ======================================
    # MAIN SIDE WIN
    # ======================================

    if main_winner:

        winner_side = main_winner["side"]

        winner_players = [
            player.get("user_id")
            for player in players
            if is_alive(player)
            and normalize_side(
                player.get("side")
            ) == winner_side
        ]

        return {
            "finished": True,
            "game_status": GAME_FINISHED,
            "winner_side": winner_side,
            "winner_players": winner_players,
            "independent_winners": independent_winners,
            "reason": main_winner["reason"],
        }

    # ======================================
    # INDEPENDENT WIN
    # ======================================

    if independent_winners:

        winner_players = [
            winner.get("user_id")
            for winner in independent_winners
            if winner.get("user_id") is not None
        ]

        return {
            "finished": True,
            "game_status": GAME_FINISHED,
            "winner_side": SIDE_MUSTAQIL,
            "winner_players": winner_players,
            "independent_winners": independent_winners,
            "reason": "independent_victory",
        }

    # ======================================
    # GAME CONTINUES
    # ======================================

    return {
        "finished": False,
        "game_status": GAME_RUNNING,
        "winner_side": None,
        "winner_players": [],
        "independent_winners": [],
        "reason": None,
    }


# ==========================================
# RESULT MESSAGE
# ==========================================

def build_victory_message(
    result: Dict,
    player_names: Optional[Dict[int, str]] = None,
) -> str:

    names = player_names or {}

    if not result.get("finished"):
        return (
            "⚔️ <b>THRONE</b>\n\n"
            "🏰 O‘yin hali davom etmoqda."
        )

    winner_side = result.get(
        "winner_side"
    )

    winner_players = result.get(
        "winner_players",
        [],
    )

    if winner_side == SIDE_TAXT:

        title = "👑 TAХT G‘ALABA QOZONDI"

    elif winner_side == SIDE_QORA:

        title = "🩸 QORA KUCHLAR G‘ALABA QOZONDI"

    elif winner_side == SIDE_ISYON:

        title = "⚔️ ISYON G‘ALABA QOZONDI"

    elif winner_side == SIDE_MUSTAQIL:

        title = "🃏 MUSTAQIL G‘ALABA"

    else:

        title = "👑 THRONE — O‘YIN YAKUNLANDI"

    lines = [
        "🏰 <b>THRONE — O‘YIN YAKUNLANDI</b>",
        "",
        title,
        "",
    ]

    if winner_players:

        lines.append(
            "🏆 G‘oliblar:"
        )

        for user_id in winner_players:

            name = names.get(
                user_id,
                f"Player {user_id}",
            )

            lines.append(
                f"👤 {name}"
            )

    independent_winners = result.get(
        "independent_winners",
        [],
    )

    if independent_winners:

        lines.extend(
            [
                "",
                "✨ <b>MAXSUS G‘ALABALAR</b>",
            ]
        )

        for winner in independent_winners:

            user_id = winner.get(
                "user_id"
            )

            role_key = winner.get(
                "role_key"
            )

            name = names.get(
                user_id,
                f"Player {user_id}",
            )

            lines.append(
                f"🎭 {name} — {role_key}"
            )

    lines.extend(
        [
            "",
            "👑 THRONE’da har bir qaror tarixga aylandi.",
        ]
    )

    return "\n".join(lines)


# ==========================================
# SIMPLE HELPERS
# ==========================================

def game_finished(
    result: Dict,
) -> bool:

    return result.get(
        "finished",
        False,
    )


def get_winner_side(
    result: Dict,
) -> Optional[str]:

    return result.get(
        "winner_side"
    )


def get_winner_players(
    result: Dict,
) -> List[int]:

    return result.get(
        "winner_players",
        [],
    )


def get_independent_winners(
    result: Dict,
) -> List[Dict]:

    return result.get(
        "independent_winners",
        [],
    )


def get_victory_reason(
    result: Dict,
) -> Optional[str]:

    return result.get(
        "reason"
        )
