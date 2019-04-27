from setuptools import setup

setup(
    name="noma",
    version="0.3.6",
    packages=["noma"],
    install_requires=["psutil", "docopt", "requests"],
    entry_points={"console_scripts": ["noma = noma.noma:main"]},
    # metadata to display on PyPI
    zip_safe=True,
    author="AnotherDroog",
    author_email="another_droog@protonmail.com",
    description="bitcoin lightning node management tool",
    license="Apache 2.0",
    keywords="bitcoin lightning node",
    url="http://github.com/lncm/noma",
)
