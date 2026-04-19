from itertools import combinations
from typing import List, Dict, Any, Optional

from utils.disc import INCOMPATIBLE_PAIRS


def check_disk_conflicts(selected_disks: List[str]) -> bool:
    """
    Проверяет наличие несовместимых пар DISK-типов.
    Возвращает True, если конфликтов нет, иначе False.
    """
    for a, b in combinations(selected_disks, 2):
        if (a, b) in INCOMPATIBLE_PAIRS:
            return False
    return True


def select_team(task: Dict[str, List[str]], roles: Dict[str, List[Dict[str, Any]]]) -> Optional[List[tuple]]:
    """
    Выбирает по одному участнику из каждой роли.

    :param task: требования задачи {'disk_allowed': [...], 'gerchikov_allowed': [...]}
    :param roles: словарь {роль: [список пользователей]}
    :return: список кортежей (роль, пользователь) или None, если подходящей комбинации нет
    """
    disk_allowed = set(task.get("disk_allowed", []))
    gerchikov_allowed = set(task.get("gerchikov_allowed", []))

    # Предварительная фильтрация пользователей по задаче
    filtered_roles = {}
    for role, users in roles.items():
        valid_users = []
        for user in users:
            if user.get("disk") in disk_allowed and user.get("gerchikov") in gerchikov_allowed:
                valid_users.append(user)
        if not valid_users:
            return None
        filtered_roles[role] = valid_users

    role_names = list(filtered_roles.keys())
    n = len(role_names)

    # Рекурсивный перебор
    def backtrack(idx: int, selected: List[tuple]) -> Optional[List[tuple]]:
        if idx == n:
            # Все роли заполнены, проверяем конфликты DISK
            disks = [user["disk"] for _, user in selected]
            if check_disk_conflicts(disks):
                return selected[:]  # копия результата
            else:
                return None

        role = role_names[idx]
        for user in filtered_roles[role]:
            selected.append((role, user))
            result = backtrack(idx + 1, selected)
            if result is not None:
                return result
            selected.pop()
        return None

    return backtrack(0, [])


if __name__ == "__main__":
    task_example = {
        "disk_allowed": ["D", "I", "S"],  # добавлен S
        "gerchikov_allowed": ["инструментальный", "профессиональный"],
    }

    # Роли и пользователи – в каждой роли есть хотя бы один S
    roles_example = {
        "менеджер": [
            {"name": "Анна", "disk": "D", "gerchikov": "инструментальный"},
            {"name": "Борис", "disk": "S", "gerchikov": "инструментальный"},  # безопасный S
            {"name": "Виктор", "disk": "I", "gerchikov": "хозяйский"},  # не подходит по Герчикову
        ],
        "разработчик": [
            {"name": "Глеб", "disk": "D", "gerchikov": "профессиональный"},
            {"name": "Дарья", "disk": "S", "gerchikov": "инструментальный"},  # безопасный S
            {"name": "Елена", "disk": "C", "gerchikov": "профессиональный"},  # не подходит по DISK
        ],
        "тестировщик": [
            {"name": "Иван", "disk": "S", "gerchikov": "профессиональный"},  # безопасный S
            {"name": "Кирилл", "disk": "D", "gerchikov": "инструментальный"},
        ],
    }

    result2 = select_team(task_example, roles_example)
    if result2:
        print("Найдена команда (с проверкой конфликтов DISK):")
        for role, user in result2:
            print(f"  {role}: {user['name']} (DISK={user['disk']}, Герчиков={user['gerchikov']})")
    else:
        print("Команду подобрать не удалось (с учётом конфликтов DISK).")
