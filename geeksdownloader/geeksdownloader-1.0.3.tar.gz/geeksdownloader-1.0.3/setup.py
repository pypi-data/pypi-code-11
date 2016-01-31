
from setuptools import setup

setup(name="geeksdownloader",
	version="1.0.3",
	description="Download all GeeksforGeeks articles/posts of a particular topic/company within a minute",
	url="https://github.com/madhuradlakha/GeeksforGeeks_Downloader",
	author="Madhur Adlakha",
	author_email="madhuradlakha@yahoo.co.in",
	license='MIT',
	packages=["geeksdownloader"],
	scripts=["bin/geeksdownloader"],
    install_requires=['future','pdfcrowd3','beautifulsoup4'],
	zip_safe=False)
