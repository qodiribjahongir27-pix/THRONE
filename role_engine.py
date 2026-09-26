
import random
from typing import Dict, List

from .roles import get_all_roles


# ============================================================
# THRONE ROLE ENGINE
# ============================================================

SIDE_TAXT = "Taxt"
SIDE_QORA = "Qora"
SIDE_ISYON = "Isyon"
SIDE_MUSTAQIL = "Mustaqil"


# O‘yinchilar soniga qarab asosiy tarkib.
# Muhim lider rollar doim saqlanadi.
COMPOSITIONS = {
    7: {
        "Taxt": 4,
        "Qora": 2,
        "Isyon": 0,
        "Mustaqil": 1,
    },
    8: {
        "Taxt": 4,
        "Qora": 2,
        "Isyon": 1,
        "Mustaqil": 1,
    },
    9: {
        "Taxt": 5,
        "Qora": 2,
        "Isyon": 1,
        "Mustaqil": 1,
    },
    10: {
        "Taxt": 5,
        "Qora": 3,
        "Isyon": 1,
        "Mustaqil": 1,
    },
    11: {
        "Taxt": 6,
        "Qora": 3,
        "Isyon": 1,
        "Mustaqil": 1,
    },
    12: {
        "Taxt": 6,
        "Qora": 3,
        "Isyon": 2,
        "Mustaqil": 1,
    },
    13: {
        "Taxt": 7,
        "Qora": 3,
        "Isyon": 2,
        "Mustaqil": 1,
    },
    14: {
        "Taxt": 7,
        "Qora": 4,
        "Isyon": 2,
        "Mustaqil": 1,
    },
    15: {
        "Taxt": 8,
        "Qora": 4,
        "Isyon": 2,
        "Mustaqil": 1,
    },
    16: {
        "Taxt": 8,
        "Qora": 4,
        "Isyon": 3,
        "Mustaqil": 1,
    },
    17: {
        "Taxt": 9,
        "Qora": 4,
        "Isyon": 3,
        "Mustaqil": 1,
    },
    18: {
        "Taxt": 9,
        "Qora": 5,
        "Isyon": 3,
        "Mustaqil": 1,
    },
    19: {
        "Taxt": 10,
        "Qora": 5,
        "Isyon": 3,
        "Mustaqil": 1,
    },
    20: {
        "Taxt": 10,
        "Qora": 5,
        "Isyon": 4,
        "Mustaqil": 1,
    },
    21: {
        "Taxt": 11,
        "Qora": 5,
        "Isyon": 4,
        "Mustaqil": 1,
    },
    22: {
        "Taxt": 11,
        "Qora": 6,
        "Isyon": 4,
        "Mustaqil": 1,
    },
    23: {
        "Taxt": 12,
        "Qora": 6,
        "Isyon": 4,
        "Mustaqil": 1,
    },
    24: {
        "Taxt": 12,
        "Qora": 6,
        "Isyon": 5,
        "Mustaqil": 1,
    },
    25: {
        "Taxt": 13,
        "Qora": 6,
        "Isyon": 5,
        "Mustaqil": 1,
    },
    26: {
        "Taxt": 13,
        "Qora": 7,
        "Isyon": 5,
        "Mustaqil": 1,
    },
    27: {
        "Taxt": 14,
        "Qora": 7,
        "Isyon": 5,
        "Mustaqil": 1,
    },
    28: {
        "Taxt": 14,
        "Qora": 7,
        "Isyon": 6,
        "Mustaqil": 1,
    },
    29: {
        "Taxt": 15,
        "Qora": 7,
        "Isyon": 6,
        "Mustaqil": 1,
    },
    30: {
        "Taxt": 15,
        "Qora": 8,
        "Isyon": 6,
        "Mustaqil": 1,
    },
    31: {
        "Taxt": 16,
        "Qora": 8,
        "Isyon": 6,
        "Mustaqil": 1,
    },
    32: {
        "Taxt": 16,
        "Qora": 8,
        "Isyon": 7,
        "Mustaqil": 1,
    },
    33: {
        "Taxt": 17,
        "Qora": 8,
        "Isyon": 7,
        "Mustaqil": 1,
    },
    34: {
        "Taxt": 17,
        "Qora": 9,
        "Isyon": 7,
        "Mustaqil": 1,
    },
    35: {
        "Taxt": 18,
        "Qora": 9,
        "Isyon": 7,
        "Mustaqil": 1,
    },
}


# ============================================================
# ROLE POOLS
# ============================================================

SIDE_ROLE_KEYS = {
    SIDE_TAXT: [
        "king",
        "queen",
        "minister",
        "prince",
        "commander",
        "royal_guard",
        "judge",
        "treasurer",
        "doctor",
        "spy",
        "astrologer",
        "palace_guard",
        "falconer",
        "scribe",
        "hunter",
        "guide",
        "herald",
    ],
    SIDE_QORA: [
        "dark_lord",
        "assassin",
        "poisoner",
        "shadow",
        "burner",
        "trapper",
        "master_poisoner",
        "dark_hunter",
    ],
    SIDE_ISYON: [
        "rebel_leader",
        "executioner",
        "rebel",
        "schemer",
        "false_advisor",
        "avenger",
    ],
    SIDE_MUSTAQIL: [
        "madman",
        "revenant",
        "lone_hunter",
        "shadow_king",
    ],
}


# ============================================================
# SIDE NORMALIZATION
# ============================================================

def normalize_side(side: str) -> str:
    if not side:
        return ""

    value = str(side).strip().lower()

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

    return aliases.get(value, side)


# ============================================================
# COMPOSITION
# ============================================================

def get_composition(player_count: int) -> Dict[str, int]:
    if player_count < 7:
        raise ValueError("O‘yin kamida 7 o‘yinchi bilan boshlanadi.")

    if player_count > 35:
        raise ValueError("O‘yinda ko‘pi bilan 35 o‘yinchi bo‘lishi mumkin.")

    if player_count in COMPOSITIONS:
        return COMPOSITIONS[player_count].copy()

    raise ValueError(
        f"{player_count} o‘yinchi uchun tarkib mavjud emas."
    )


# ============================================================
# ROLE SELECTION
# ============================================================

def _get_available_roles(side: str):
    roles = get_all_roles()

    available = []

    for role_key in SIDE_ROLE_KEYS[side]:
        if role_key in roles:
            available.append(role_key)

    return available


def _choose_roles_for_side(
    side: str,
    count: int
) -> List[str]:
    if count <= 0:
        return []

    available = _get_available_roles(side)

    if not available:
        raise ValueError(
            f"{side} tomoni uchun rollar topilmadi."
        )

    selected = []

    # Asosiy lider rollari.
    leader_roles = {
        SIDE_TAXT: "king",
        SIDE_QORA: "dark_lord",
        SIDE_ISYON: "rebel_leader",
        SIDE_MUSTAQIL: None,
    }

    leader = leader_roles.get(side)

    if leader and leader in available:
        selected.append(leader)

    remaining = [
        role
        for role in available
        if role not in selected
    ]

    random.shuffle(remaining)

    needed = count - len(selected)

    if needed > 0:
        selected.extend(
            remaining[:needed]
        )

    # Agar son katta bo‘lsa, mavjud rollarni qayta ishlatish
    # emas, avval barcha noyob rollar tugashi kerak.
    while len(selected) < count:
        selected.append(
            random.choice(available)
        )

    return selected


# ============================================================
# BUILD ROLE POOL
# ============================================================

def build_role_pool(player_count: int) -> List[str]:
    composition = get_composition(player_count)

    pool = []

    for side, count in composition.items():
        roles = _choose_roles_for_side(
            side,
            count
        )

        pool.extend(roles)

    if len(pool) != player_count:
        raise ValueError(
            "Rol tarkibi o‘yinchilar soniga teng emas."
        )

    random.shuffle(pool)

    return pool


# ============================================================
# ASSIGN ROLES
# ============================================================

def assign_roles(
    player_ids: List[int],
    player_count: int = None
) -> Dict[int, str]:

    if not player_ids:
        raise ValueError(
            "O‘yinchilar ro‘yxati bo‘sh."
        )

    if player_count is None:
        player_count = len(player_ids)

    if player_count != len(player_ids):
        raise ValueError(
            "player_count va player_ids soni mos emas."
        )

    if len(set(player_ids)) != len(player_ids):
        raise ValueError(
            "Bir xil user_id takrorlangan."
        )

    role_pool = build_role_pool(
        player_count
    )

    assignments = {}

    shuffled_players = list(player_ids)
    random.shuffle(shuffled_players)

    for user_id, role_key in zip(
        shuffled_players,
        role_pool
    ):
        assignments[user_id] = role_key

    return assignments


# ============================================================
# ROLE SIDE
# ============================================================

def get_role_side(role_key: str) -> str:
    roles = get_all_roles()

    role = roles.get(role_key)

    if not role:
        return ""

    return normalize_side(
        role.get("side", "")
    )


# ============================================================
# ASSIGNMENT DETAILS
# ============================================================

def get_assignment_details(
    assignments: Dict[int, str]
):
    result = {}

    roles = get_all_roles()

    for user_id, role_key in assignments.items():
        role = roles.get(role_key)

        if not role:
            continue

        result[user_id] = {
            "role_key": role_key,
            "role_name": role.get(
                "name",
                role_key
            ),
            "side": normalize_side(
                role.get("side", "")
            ),
            "description": role.get(
                "description",
                ""
            ),
            "ability": role.get(
                "ability",
                ""
            ),
            "limitation": role.get(
                "limitation",
                ""
            ),
            "win": role.get(
                "win",
                ""
            ),
        }

    return result


# ============================================================
# SIDE GROUPING
# ============================================================

def get_assignments_by_side(
    assignments: Dict[int, str]
):
    result = {
        SIDE_TAXT: [],
        SIDE_QORA: [],
        SIDE_ISYON: [],
        SIDE_MUSTAQIL: [],
    }

    roles = get_all_roles()

    for user_id, role_key in assignments.items():
        role = roles.get(role_key)

        if not role:
            continue

        side = normalize_side(
            role.get("side", "")
        )

        if side not in result:
            result[side] = []

        result[side].append(user_id)

    return result


# ============================================================
# SUMMARY
# ============================================================

def get_assignment_summary(
    assignments: Dict[int, str]
):
    details = get_assignment_details(
        assignments
    )

    summary = {
        SIDE_TAXT: 0,
        SIDE_QORA: 0,
        SIDE_ISYON: 0,
        SIDE_MUSTAQIL: 0,
    }

    for data in details.values():
        side = data["side"]

        if side in summary:
            summary[side] += 1

    return summary


# ============================================================
# VALIDATION
# ============================================================

def validate_assignments(
    assignments: Dict[int, str]
) -> bool:

    if not assignments:
        return False

    roles = get_all_roles()

    for user_id, role_key in assignments.items():

        if not isinstance(
            user_id,
            int
        ):
            return False

        if role_key not in roles:
            return False

        role = roles[role_key]

        side = normalize_side(
            role.get("side", "")
        )

        if side not in {
            SIDE_TAXT,
            SIDE_QORA,
            SIDE_ISYON,
            SIDE_MUSTAQIL,
        }:
            return False

    return True


# ============================================================
# REQUIRED LEADER CHECK
# ============================================================

def validate_required_leaders(
    assignments: Dict[int, str]
) -> bool:

    roles = list(
        assignments.values()
    )

    composition = get_assignment_summary(
        assignments
    )

    if composition.get(SIDE_TAXT, 0) > 0:
        if "king" not in roles:
            return False

    if composition.get(SIDE_QORA, 0) > 0:
        if "dark_lord" not in roles:
            return False

    if composition.get(SIDE_ISYON, 0) > 0:
        if "rebel_leader" not in roles:
            return False

    return True


# ============================================================
# FULL VALIDATION
# ============================================================

def validate_game_roles(
    player_ids: List[int],
    assignments: Dict[int, str]
) -> bool:

    if len(player_ids) != len(assignments):
        return False

    if set(player_ids) != set(
        assignments.keys()
    ):
        return False

    if not validate_assignments(
        assignments
    ):
        return False

    if not validate_required_leaders(
        assignments
    ):
        return False

    try:
        expected = get_composition(
            len(player_ids)
        )
    except ValueError:
        return False

    actual = get_assignment_summary(
        assignments
    )

    return actual == expected
