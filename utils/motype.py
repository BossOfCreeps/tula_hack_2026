import math
from pprint import pprint
from typing import Dict, List, Tuple

# Константы: названия типов
MOTYPES = ["IN", "PR", "PA", "HO", "LU"]


# Пороги для критических фильтров
THRESHOLDS = {
    "creative": {"required": ["HO", "PR"], "forbidden": ["LU"], "forbidden_threshold": 0.3},
    "routine": {"required": ["IN", "LU"], "forbidden": ["HO", "PR"], "forbidden_threshold": 0.3},
    "team": {"required": ["PA"], "forbidden": ["IN"], "forbidden_threshold": 0.4},
    "risk": {"required": ["HO"], "forbidden": ["LU"], "forbidden_threshold": 0.2},
}


def cosine_similarity(vec_a: Dict[str, float], vec_b: Dict[str, float]) -> float:
    """
    Вычисляет косинусное сходство между двумя векторами (5 типов).
    Возвращает значение от -1 до 1, где 1 = идеальное совпадение.
    """
    dot_product = 0.0
    norm_a = 0.0
    norm_b = 0.0

    for key in MOTYPES:
        dot_product += vec_a.get(key, 0) * vec_b.get(key, 0)
        norm_a += vec_a.get(key, 0) ** 2
        norm_b += vec_b.get(key, 0) ** 2

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (math.sqrt(norm_a) * math.sqrt(norm_b))


def determine_task_type(profile: Dict[str, float]) -> str:
    """
    Определяет тип задачи по доминирующим мотиваторам.
    Используется для применения критических фильтров.
    """
    # Находим максимальное значение
    max_value = max(profile.values())
    # Собираем типы с максимальным значением
    dominant = [k for k, v in profile.items() if v == max_value]

    # Логика определения типа
    if "HO" in dominant or "PR" in dominant and profile.get("HO", 0) + profile.get("PR", 0) > 0.4:
        return "creative"
    elif "LU" in dominant or "IN" in dominant and profile.get("LU", 0) + profile.get("IN", 0) > 0.4:
        return "routine"
    elif "PA" in dominant and profile.get("PA", 0) > 0.25:
        return "team"
    elif "HO" in dominant and profile.get("HO", 0) > 0.3:
        return "risk"
    else:
        return "creative"  # по умолчанию


def apply_hard_filters(employee_profile: Dict[str, float], task_profile: Dict[str, float]) -> Tuple[bool, str]:
    """
    Применяет критические фильтры.
    Возвращает (passed, reason) — прошёл ли сотрудник фильтр и причина отклонения.
    """
    task_type = determine_task_type(task_profile)
    rules = THRESHOLDS.get(task_type, {})

    # Проверка запрещённых типов
    for forbidden_type in rules.get("forbidden", []):
        threshold = rules.get("forbidden_threshold", 0.3)
        if employee_profile.get(forbidden_type, 0) > threshold:
            return False, f"Критический запрет: высокий {forbidden_type} при типе задачи '{task_type}'"

    # Особые случаи (можно расширять)
    # Люмпен + Хозяин в ответственной задаче
    if task_profile.get("HO", 0) > 0.3 and employee_profile.get("LU", 0) > 0.2:
        return False, "Люмпен не подходит для ответственной задачи"

    # Хозяин в строго регламентированной задаче
    if task_profile.get("LU", 0) > 0.25 and employee_profile.get("HO", 0) > 0.3:
        return False, "Хозяин не подходит для строго регламентированной работы"

    return True, ""


def select_motype_employees(task_profile: Dict[str, float], employees: List[Dict]) -> List[Dict]:
    """
    Главная функция: выбирает лучших сотрудников для задачи.

    Args:
        task_profile: словарь с 5 ключами (IN, PR, PA, HO, LU) сумма = 1.0
        employees: список словарей, каждый содержит:
            - id: идентификатор
            - name: имя
            - profile: словарь профиля (аналогичный task_profile)

    Returns:
        Отсортированный список сотрудников с добавленными полями:
        - score: итоговая оценка
        - similarity: косинусное сходство
        - passed_filters: прошёл ли фильтры
        - filter_reason: причина отклонения (если не прошёл)
    """
    results = []

    for emp in employees:
        employee_profile = emp.get("profile", {})

        # 1. Применяем критические фильтры
        passed, reason = apply_hard_filters(employee_profile, task_profile)

        if not passed:
            results.append(
                {
                    **emp,
                    "passed_filters": False,
                    "filter_reason": reason,
                    "score": 0,
                }
            )
            continue

        # 2. Вычисляем сходство
        final_score = cosine_similarity(employee_profile, task_profile)

        results.append(
            {
                **emp,
                "passed_filters": True,
                "filter_reason": "",
                "score": round(final_score, 4),
            }
        )

    # 4. Сортируем по убыванию score
    results.sort(key=lambda x: x["score"], reverse=True)

    # 5. Возвращаем топ-N (включая непрошедших фильтры в конце списка)
    return results


# ========== ПРИМЕР ИСПОЛЬЗОВАНИЯ ==========
if __name__ == "__main__":
    # Профиль задачи
    task = {"IN": 0.10, "PR": 0.30, "PA": 0.10, "HO": 0.45, "LU": 0.05}

    # Сотрудники
    employees = [
        {"id": 1, "name": "Петров А.А.", "profile": {"IN": 0.10, "PR": 0.05, "PA": 0.10, "HO": 0.35, "LU": 0.40}},
        {"id": 2, "name": "Сидоров Б.Б.", "profile": {"IN": 0.40, "PR": 0.20, "PA": 0.10, "HO": 0.10, "LU": 0.20}},
        {"id": 3, "name": "Иванова В.В.", "profile": {"IN": 0.05, "PR": 0.15, "PA": 0.60, "HO": 0.10, "LU": 0.10}},
    ]

    # Выбираем лучших
    best = select_motype_employees(task, employees)
    pprint(best)
