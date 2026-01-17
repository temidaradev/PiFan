from setuptools import setup, find_packages

setup(
    name="pifan",
    version="3.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "customtkinter",
        "packaging",
        "Pillow",
        "rpi-lgpio"
    ],
    entry_points={
        "console_scripts": [
            "pifan=pifan.__main__:main",
        ],
    },
)
