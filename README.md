# py-1brc

This repo contains the source code for a talk I gave on Python performance at the Christchurch Python User Group. My talk looked at increasingly faster solutions to the [One Billion Row Challenge](https://www.morling.dev/blog/one-billion-row-challenge/), showing how to profile and optimise Python as we went.

Some of the solutions import [line_profiler](https://pypi.org/project/line-profiler/), so to run them, first set up a virtual environment and install that package:

```
$ python3 -m venv venv             # create the virtual environment
$ source venv/bin/activate         # active it
$ pip install -r requirements.txt  # install modules (line_profiler)
```

Then run a solution as follows (r1 through r7):

```
$ time python3 r7.py measurements.txt >results.txt
```
