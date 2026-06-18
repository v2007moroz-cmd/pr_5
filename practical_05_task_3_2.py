"""Аналізатор конфігурації Django-проекту."""

import ast
import os
import sys
from pathlib import Path
from typing import Any


def literal_value(node: ast.AST) -> Any:
    """Повертає значення вузла AST, якщо його можна безпечно обчислити."""
    try:
        return ast.literal_eval(node)
    except (ValueError, SyntaxError):
        return "динамічне значення"


def get_assignments(settings_path: str) -> dict[str, ast.AST]:
    """Зчитує прості присвоєння верхнього рівня з settings.py."""
    source = Path(settings_path).read_text(encoding="utf-8")
    tree = ast.parse(source)
    assignments: dict[str, ast.AST] = {}

    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assignments[target.id] = node.value

    return assignments


def analyze_settings(settings_path: str) -> dict:
    """Аналізує файл settings.py та повертає ключові параметри.

    Args:
        settings_path: шлях до файлу settings.py.

    Returns:
        Словник з аналізом конфігурації.
    """
    assignments = get_assignments(settings_path)

    debug = literal_value(assignments.get("DEBUG", ast.Constant(value="не знайдено")))
    installed_apps = literal_value(
        assignments.get("INSTALLED_APPS", ast.Constant(value=[]))
    )
    databases = literal_value(assignments.get("DATABASES", ast.Constant(value={})))
    language_code = literal_value(
        assignments.get("LANGUAGE_CODE", ast.Constant(value="не знайдено"))
    )
    time_zone = literal_value(
        assignments.get("TIME_ZONE", ast.Constant(value="не знайдено"))
    )

    db_engine = "не визначено"
    if isinstance(databases, dict):
        default_db = databases.get("default", {})
        if isinstance(default_db, dict):
            db_engine = default_db.get("ENGINE", "не визначено")

    return {
        "DEBUG": debug,
        "INSTALLED_APPS": installed_apps,
        "DATABASE_ENGINE": db_engine,
        "LANGUAGE_CODE": language_code,
        "TIME_ZONE": time_zone,
    }


def node_contains_os_environ(node: ast.AST) -> bool:
    """Перевіряє, чи використовується os.environ у значенні."""
    source = ast.unparse(node) if hasattr(ast, "unparse") else ""
    return "os.environ" in source or "environ" in source


def check_security(settings_path: str) -> list[str]:
    """Перевіряє базову безпеку конфігурації.

    Args:
        settings_path: шлях до файлу settings.py.

    Returns:
        Список попереджень безпеки.
    """
    warnings = []
    assignments = get_assignments(settings_path)

    debug_value = literal_value(assignments.get("DEBUG", ast.Constant(value=False)))
    if debug_value is True:
        warnings.append("DEBUG = True: для production це небезпечно")

    secret_node = assignments.get("SECRET_KEY")
    if secret_node is None:
        warnings.append("SECRET_KEY не знайдено")
    elif isinstance(secret_node, ast.Constant) and isinstance(secret_node.value, str):
        warnings.append("SECRET_KEY захардкоджений у settings.py")
    elif not node_contains_os_environ(secret_node):
        warnings.append("SECRET_KEY бажано отримувати зі змінної оточення")

    allowed_hosts = literal_value(assignments.get("ALLOWED_HOSTS", ast.Constant(value=[])))
    if allowed_hosts == []:
        warnings.append("ALLOWED_HOSTS порожній")

    return warnings


def main() -> None:
    """Основна функція програми."""
    settings_path = "mysite/mysite/settings.py"
    if not os.path.exists(settings_path):
        print(f"Файл {settings_path} не знайдено")
        sys.exit(1)

    config = analyze_settings(settings_path)
    print("=== Аналіз конфігурації Django ===\n")

    for key, value in config.items():
        print(f"  {key}: {value}")

    print("\n=== Перевірка безпеки ===\n")
    warnings = check_security(settings_path)
    if warnings:
        for warning in warnings:
            print(f"  ⚠ {warning}")
    else:
        print("  Попереджень не знайдено")


if __name__ == "__main__":
    main()
