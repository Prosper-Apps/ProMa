from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in proma/__init__.py
from proma import __version__ as version

setup(
	name="proma",
	version=version,
	description="Protocol Management App communicating cia API to a firebase database to send protocols in form of a checklist to a service worker app",
	author="phamos GmbH",
	author_email="post@phamos.eu",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
