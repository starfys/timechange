"""Copyright 2017
Steven Sheffey <stevensheffey4@gmail.com>,
John Ford,
Eyasu Asrat,
Jordan Flowers,
Joseph Volmer,
Luke Stanley,
Serenah Smith, and
Chandu Budati

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

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

