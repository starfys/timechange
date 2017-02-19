from distutils.core import setup

setup(
    name="TimeChange",
    version="0.1dev",
    description="Timechange is a library for analysis of timeseries data using convolutional neural nets",
    author=", ".join(["Steven Sheffey",
                      "John Ford"]),
    author_email=", ".join(["stevensheffey4@gmail.com"]),
    packages=["timechange",],
    license="MIT",
    long_description=open("README.rst","r").read(),
)

