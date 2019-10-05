from setuptools import setup

setup(
    name="noma",
    version="0.5.1",
    # Added fork of ConfigObj to repo for ini support
    # To be removed once PR is merged upstream
    packages=["noma", "configobj"],
    install_requires=["psutil", "docopt", "requests>=2.22.0", "docker-compose", "toml"],
    entry_points={"console_scripts": ["noma = noma.noma:main"]},
    # metadata to display on PyPI
    zip_safe=True,
    author="LNCM Contributors",
    author_email="lncm@protonmail.com",
    description="bitcoin lightning node management tool",
    license="Apache 2.0",
    keywords="bitcoin lightning node",
    url="http://github.com/lncm/noma",
)
