"""Генератор requirements.txt з перевіркою залежностей."""

import json
import subprocess
import sys
from importlib import metadata
from pathlib import Path


SYSTEM_PACKAGES = {"pip", "setuptools", "wheel"}


def get_installed_packages() -> list[dict]:
    """Повертає список встановлених пакетів з версіями.

    Returns:
        Список словників {'name': ..., 'version': ...}.
    """
    result = subprocess.run(
        [sys.executable, "-m", "pip", "list", "--format=json"],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        print("Помилка отримання списку пакетів:")
        print(result.stderr)
        return []

    try:
        packages = json.loads(result.stdout)
    except json.JSONDecodeError:
        print("Не вдалося розпарсити JSON-вивід pip list")
        return []

    return sorted(packages, key=lambda item: item["name"].lower())


def generate_requirements(packages: list[dict], filename: str = "requirements.txt") -> None:
    """Записує пакети у файл requirements.txt.

    Args:
        packages: список словників з ключами 'name' та 'version'.
        filename: ім'я файлу для запису.
    """
    filtered_packages = [
        pkg for pkg in packages
        if pkg["name"].lower() not in SYSTEM_PACKAGES
    ]

    with open(filename, "w", encoding="utf-8") as file:
        for pkg in filtered_packages:
            file.write(f"{pkg['name']}=={pkg['version']}\n")


def normalize_package_name(name: str) -> str:
    """Нормалізує назву пакета для коректного порівняння."""
    return name.strip().lower().replace("_", "-")


def verify_requirements(filename: str = "requirements.txt") -> bool:
    """Перевіряє, чи всі пакети з requirements.txt встановлені.

    Args:
        filename: шлях до файлу requirements.txt.

    Returns:
        True, якщо всі залежності задоволені.
    """
    path = Path(filename)
    if not path.exists():
        print(f"Файл {filename} не знайдено")
        return False

    ok = True

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if "==" not in line:
            print(f"  ⚠ Непідтримуваний формат рядка: {line}")
            ok = False
            continue

        required_name, required_version = line.split("==", 1)
        required_name = required_name.strip()
        required_version = required_version.strip()

        try:
            installed_version = metadata.version(required_name)
        except metadata.PackageNotFoundError:
            print(f"  ✗ {required_name}: пакет не встановлено")
            ok = False
            continue

        if installed_version == required_version:
            print(f"  ✓ {required_name}=={required_version}")
        else:
            print(
                f"  ✗ {required_name}: потрібно {required_version}, "
                f"встановлено {installed_version}"
            )
            ok = False

    return ok


def main() -> None:
    """Основна функція програми."""
    packages = get_installed_packages()
    print(f"Знайдено {len(packages)} встановлених пакетів\n")

    for pkg in packages[:10]:
        print(f"  {pkg['name']}=={pkg['version']}")
    if len(packages) > 10:
        print(f"  ... та ще {len(packages) - 10}")

    generate_requirements(packages)
    print("\nФайл requirements.txt створено")

    print("\nПеревірка залежностей:")
    ok = verify_requirements()
    print(f"\nРезультат: {'✓ Усе OK' if ok else '✗ Є розбіжності'}")


if __name__ == "__main__":
    main()
