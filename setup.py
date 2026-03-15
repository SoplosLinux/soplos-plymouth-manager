from setuptools import setup, find_packages

setup(
    name="soplos-plymouth-manager",
    version="2.0.0",
    author="Sergi Perich",
    author_email="info@soploslinux.com",
    description="Graphical Plymouth theme manager for Soplos Linux",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/SoplosLinux/soplos-plymouth-manager",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "PyGObject>=3.0.0",
        "psutil>=5.0.0",
        "Pillow>=6.0.0",
        "pyxdg>=0.26",
    ],
    entry_points={
        "console_scripts": [
            "soplos-plymouth-manager=main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: POSIX :: Linux",
        "Environment :: X11 Applications :: GTK",
    ],
    python_requires=">=3.6",
)
