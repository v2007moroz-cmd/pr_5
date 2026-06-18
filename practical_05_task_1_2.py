"""Скрипт перевірки середовища розробки."""

import importlib
import sys
from importlib import metadata


def check_python_version() -> bool:
    """Перевіряє версію Python: потрібна версія 3.10 або новіша."""
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")

    if version >= (3, 10):
        print("  Версія Python підходить ✓")
        return True

    print("  Увага: потрібна версія Python 3.10 або новіша ✗")
    return False


def get_package_version(package_name: str) -> str:
    """Повертає версію пакета через importlib.metadata."""
    distribution_names = {
        "django": "Django",
        "flask": "Flask",
    }
    dist_name = distribution_names.get(package_name.lower(), package_name)

    try:
        return metadata.version(dist_name)
    except metadata.PackageNotFoundError:
        return "невідома"


def check_package(package_name: str) -> bool:
    """Перевіряє, чи встановлено пакет, і виводить його версію.

    Args:
        package_name: назва пакета для перевірки.

    Returns:
        True, якщо пакет встановлено.
    """
    try:
        importlib.import_module(package_name)
        version = get_package_version(package_name)
        print(f"  {package_name}: {version} ✓")
        return True
    except ImportError:
        print(f"  {package_name}: НЕ ВСТАНОВЛЕНО ✗")
        return False


def main() -> None:
    """Основна функція програми."""
    check_python_version()

    print("\nВстановлені пакети:")
    packages = ["django", "flask"]
    results = {pkg: check_package(pkg) for pkg in packages}

    installed_count = sum(results.values())
    missing_packages = [pkg for pkg, installed in results.items() if not installed]

    print("\nПідсумок:")
    print(f"  Встановлено: {installed_count}")
    print(f"  Відсутні: {len(missing_packages)}")

    if missing_packages:
        command = "pip install " + " ".join(missing_packages)
        print("\nДля встановлення відсутніх пакетів виконайте:")
        print(f"  {command}")
    else:
        print("\nУсі необхідні пакети встановлено ✓")


if __name__ == "__main__":
    main()
