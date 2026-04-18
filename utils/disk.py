from typing import Tuple, Any

# https://chat.deepseek.com/share/nytk7hoy1gilom0ok5

# Таблица несовместимых пар (критические конфликты)
INCOMPATIBLE_PAIRS: dict[Tuple[str, str], str] = {
    ("D", "D"): "Два доминантных лидера",
    ("I", "I"): "Два «души компании»",
    ("C", "C"): "Два педанта / аналитика",
    ("D", "I"): "Напор vs эмоции",
    ("I", "D"): "Напор vs эмоции",
}

# Рискованные пары (предупреждения)
RISKY_PAIRS: dict[Tuple[str, str], str] = {
    ("D", "C"): "Скорость vs точность",
    ("C", "D"): "Скорость vs точность",
    ("I", "S"): "Активность vs пассивность",
    ("S", "I"): "Активность vs пассивность",
    ("S", "C"): "Оба медленные, но по разным причинам",
    ("C", "S"): "Оба медленные, но по разным причинам",
}

DISK_LIST = ["D", "I", "S", "C"]


def check_disk_compatibility(participants: list[dict[str, int]]) -> dict[str, Any]:
    """
    Проверяет совместимость команды по DISK.
    """

    # Шаг 1: нормализовать участников и определить доминантные типы
    normalized_participants = []
    dominant_types = []

    for idx, p in enumerate(participants):
        # Нормализуем профиль участника
        normalized_profile = {"user": p.get("user")}
        profile_values = {}

        for t in DISK_LIST:
            num_val = p.get(t, 0)
            profile_values[t] = num_val
            normalized_profile[t] = num_val

        normalized_profile["_values"] = profile_values
        normalized_participants.append(normalized_profile)

        # Находим доминантный тип (с максимальным значением)
        max_type = max(profile_values, key=profile_values.get)
        dominant_types.append((normalized_profile["user"], max_type))

    # Шаг 2: проверить все пары на конфликты
    conflicts = []
    warnings = []

    for i in range(len(dominant_types)):
        user1, type1 = dominant_types[i]
        for j in range(i + 1, len(dominant_types)):
            user2, type2 = dominant_types[j]
            pair = (type1, type2)

            if pair in INCOMPATIBLE_PAIRS:
                conflicts.append({"user1": user1, "user2": user2, "reason": INCOMPATIBLE_PAIRS[pair]})
            elif pair in RISKY_PAIRS:
                warnings.append({"user1": user1, "user2": user2, "reason": RISKY_PAIRS[pair]})

    return {"conflicts": conflicts, "warnings": warnings}
