from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in connect_mqtt/__init__.py
from connect_mqtt import __version__ as version

setup(
	name="connect_mqtt",
	version=version,
	description="Connect MQTT",
	author="Revant",
	author_email="support@castlecraft.in",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
