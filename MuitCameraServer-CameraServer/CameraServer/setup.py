from setuptools import setup, find_packages

setup(
    name="camera_server",
    version="1.0",
    packages=find_packages(),
    install_requires=[
        'PyQt5',
        'SQLAlchemy',
        'pyodbc',
        'opencv-python',
        'ultralytics',
    ],
    entry_points={
        'console_scripts': [
            'camera_server = main_python:main',
        ],
    },
)