from setuptools import setup

setup(
    name="noma",
    version="0.5.0",
    packages=["noma"],
    install_requires=["psutil", "docopt", "requests", "docker-compose"],
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
