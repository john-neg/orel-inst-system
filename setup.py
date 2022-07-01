from distutils.core import setup

from setuptools import find_packages

setup(
    name="apeks-vuz-extension",
    version="0.1",
    packages=find_packages(),
    package_data={p: ["*"] for p in find_packages()},
    url="",
    license="",
    install_requires=[
        "flask",
    ],
    python_requires=">=3.8.0",
    author="Evgeny.Semenov",
    description="Расширения базовых функций Апекс-ВУЗ",
)