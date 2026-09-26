import random
from collections import Counter

from roles import get_all_roles


# =========================
# ROLE DISTRIBUTION
# =========================

def build_role_pool(player_count: int):
    """
    O'yinchilar soniga qarab rol havzasini yaratadi.
    Maksimal 35 ta rol ishlatiladi.
    """

    if player_count < 7:
        raise ValueError("Kamida 7 o'yinchi kerak.")

    if player_count > 35:
        raise ValueError("Maksimal 35 o'yinchi mumkin.")

    roles = get_all_roles()

    throne_roles = [
        "king",
        "queen",
        "vizier",
        "prince",
        "commander",
        "royal_guard",
        "judge",
        "treasurer",
        "doctor",
        "spy",
        "astrologer",
        "palace_guard",
        "bird_keeper",
        "scribe",
        "hunter",
        "traveler",
        "herald",
    ]

    dark_roles = [
        "dark_ruler",
        "assassin",
        "poisoner",
        "shadow",
        "burner",
        "trapper",
        "poison_master",
        "dark_hunter",
    ]

    rebel_roles = [
        "rebel_leader",
        "executioner",
        "rebel",
        "schemer",
        "false_advisor",
        "avenger",
    ]

    independent_roles = [
        "madman",
        "revenge_spirit",
        "lone_hunter",
        "shadow_king",
    ]

    available = []

    for role_key in (
        throne_roles
        + dark_roles
        + rebel_roles
        + independent_roles
    ):
        if role_key in roles:
            available.append(role_key)

    if len(available) < player_count:
        raise ValueError(
            f"Yetarli rol mavjud emas: {len(available)} / {player_count}"
        )

    # Har bir o'yinda asosiy tomonlardan vakillar bo'lishi uchun
    # dastlabki xavfsiz tarkib.
    guaranteed = []

    if "king" in roles:
        guaranteed.append("king")

    if "dark_ruler" in roles:
        guaranteed.append("dark_ruler")

    if "rebel_leader" in roles and player_count >= 10:
        guaranteed.append("rebel_leader")

    # Mustaqil rollar kam sonli o'yinda majburiy emas.
    # Ular keyinchalik qolgan joylardan tanlanadi.
    remaining = [
        role
        for role in available
        if role not in guaranteed
    ]

    random.shuffle(remaining)

    needed = player_count - len(guaranteed)

    pool = guaranteed + remaining[:needed]

    random.shuffle(pool)

    return pool


# =========================
# ASSIGN ROLES
# =========================

def assign_roles(player_ids, player_count=None):
    """
    O'yinchilar ID lariga tasodifiy rollarni biriktiradi.

    Natija:
    {
        user_id: role_key
    }
    """

    player_ids = list(player_ids)

    if player_count is None:
        player_count = len(player_ids)

    if len(player_ids) != player_count:
        raise ValueError(
            "O'yinchilar soni player_count bilan mos emas."
        )

    role_pool = build_role_pool(player_count)

    random.shuffle(player_ids)

    assignments = {}

    for user_id, role_key in zip(player_ids, role_pool):
        assignments[user_id] = role_key

    return assignments


# =========================
# ROLE INFORMATION
# =========================

def get_assignment_summary(assignments):
    """
    Test va admin nazorati uchun rol taqsimoti statistikasi.
    O'yinchilarga maxfiy rolni ko'rsatish uchun ishlatilmaydi.
    """

    counter = Counter(assignments.values())

    return dict(counter)


# =========================
# SIDE HELPERS
# =========================

def get_role_side(role_key: str):
    roles = get_all_roles()

    role = roles.get(role_key)

    if not role:
        return None

    return role.get("side")


def get_assignments_by_side(assignments):
    """
    Taqsimlangan rollarni tomonlar bo'yicha ajratadi.
    """

    result = {
        "throne": [],
        "dark": [],
        "rebel": [],
        "independent": [],
    }

    for user_id, role_key in assignments.items():
        side = get_role_side(role_key)

        if side in result:
            result[side].append({
                "user_id": user_id,
                "role_key": role_key,
            })

    return result


# =========================
# VALIDATION
# =========================

def validate_assignments(assignments, expected_count: int):
    """
    Rol taqsimoti to'g'ri yoki noto'g'riligini tekshiradi.
    """

    if not assignments:
        return False

    if len(assignments) != expected_count:
        return False

    role_keys = list(assignments.values())

    if len(set(role_keys)) != len(role_keys):
        return False

    roles = get_all_roles()

    for role_key in role_keys:
        if role_key not in roles:
            return False

    return True
