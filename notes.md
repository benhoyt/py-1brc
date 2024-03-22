Tentative plan:

- r1: process char by char
- r2: re.match(r'([^;]+);([-.0-9])', line)
- r4: csv
- r3: line.partition(';')
- r5: thread pool / threading
- r6: multiprocessing

Notes:
- putting things in a function helped big-time! at least on Python 3.10 (try on 3.12)
- Brian's DuckDB + ChatGPT tool
- microoptimizations don't help much (anymore?), like assigning globals to local vars
- map, ThreadPool.map, Pool.map
- some way to show what GIL is doing?
- show Python 3.10 to Python 3.12 speed differences -- significant!
- reading large chunks as bytes/bytearray and then using .find(b';') and .find(b'\n') didn't help
  -> too many operations
- "if" statement much faster than min/max! (do a dis() to show: fewer opcodes doesn't necessarily mean faster)
- floats[temp_str] dict lookup a bit faster than float(temp_str)
- try/except KeyError is a bit faster than stats.get and "if v is None"
- note that r5 and r6 are Map Reduce

```
# TODO: show timeit of float(temp_str) vs floats[temp_str]
```

```
0 ~/h/py-1brc$ python3 -m timeit -s 's = "Auckland;34.0"' 'x, y = s.split(";")'
5000000 loops, best of 5: 55.6 nsec per loop
0 ~/h/py-1brc$ python3 -m timeit -s 's = "Auckland;34.0"' 'x, _, y = s.partition(";")'
10000000 loops, best of 5: 40.6 nsec per loop
```

```
# Useful use of dis.dis() -- BINARY_SUBSCR a bit faster than CALL
>>> import dis
>>> def f1(s):
...  return float(s)
... 
>>> floats = {str(i/10)+'\n': i/10 for i in range(-999, 1000)}
>>> def f2(s):
...  return floats[s]
... 
>>> dis.dis(f1)
  1           0 RESUME                   0

  2           2 LOAD_GLOBAL              1 (NULL + float)
             12 LOAD_FAST                0 (s)
             14 CALL                     1
             22 RETURN_VALUE
>>> dis.dis(f2)
  1           0 RESUME                   0

  2           2 LOAD_GLOBAL              0 (floats)
             12 LOAD_FAST                0 (s)
             14 BINARY_SUBSCR
             18 RETURN_VALUE
```

DuckDB query:

```
select station, min(temp), max(temp), round(avg(temp), 1)
from read_csv('/home/ben/h/1brc/data/measurements.txt', columns={'station': 'VARCHAR', 'temp': 'DOUBLE'})
group by station
order by station;
```

```
# cProfile is kinda useless for this:
0 ~/h/py-1brc$ python3 -m cProfile -s cumulative r1.py measurements-1M.txt 
         16745085 function calls (16744920 primitive calls) in 3.076 seconds

   Ordered by: cumulative time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
     20/1    0.000    0.000    3.076    3.076 {built-in method builtins.exec}
        1    0.000    0.000    3.076    3.076 r1.py:1(<module>)
        1    2.217    2.217    3.070    3.070 r1.py:12(main)
 13733780    0.594    0.000    0.600    0.000 {method 'read' of '_io.TextIOWrapper' objects}
   999592    0.086    0.000    0.086    0.000 {built-in method builtins.min}
  1000072    0.084    0.000    0.084    0.000 {method 'get' of 'dict' objects}
   999619    0.083    0.000    0.083    0.000 {built-in method builtins.max}
     30/1    0.000    0.000    0.006    0.006 <frozen importlib._bootstrap>:1022(_find_and_load)
     30/1    0.000    0.000    0.006    0.006 <frozen importlib._bootstrap>:987(_find_and_load_unlocked)
     27/1    0.000    0.000    0.006    0.006 <frozen importlib._bootstrap>:664(_load_unlocked)
     1685    0.001    0.000    0.006    0.000 codecs.py:319(decode)
     16/1    0.000    0.000    0.006    0.006 <frozen importlib._bootstrap_external>:877(exec_module)
     40/1    0.000    0.000    0.006    0.006 <frozen importlib._bootstrap>:233(_call_with_frames_removed)
        1    0.000    0.000    0.006    0.006 __init__.py:1(<module>)
        1    0.000    0.000    0.005    0.005 line_profiler.py:1(<module>)
     1685    0.005    0.000    0.005    0.000 {built-in method _codecs.utf_8_decode}
        1    0.000    0.000    0.002    0.002 tempfile.py:1(<module>)
       16    0.000    0.000    0.002    0.000 <frozen importlib._bootstrap_external>:950(get_code)
        1    0.000    0.000    0.001    0.001 shutil.py:1(<module>)
```

```
# line_profiler is much better:
0 ~/h/py-1brc$ time kernprof -l r1.py measurements-1M.txt 
Wrote profile results to r1.py.lprof
Inspect results with:
python3 -m line_profiler -rmt "r1.py.lprof"

real	0m12.033s
user	0m12.011s
sys	0m0.020s
$ python3 -m line_profiler -rmt "r1.py.lprof"
Timer unit: 1e-06 s

Total time: 6.16388 s
File: r1.py
Function: main at line 12

Line #      Hits         Time  Per Hit   % Time  Line Contents
==============================================================
    12                                           @profile
    13                                           def main():
    14         1          0.4      0.4      0.0      stats = {}
    15         2         23.9     11.9      0.0      with open(sys.argv[1]) as f:
    16   1000001     114156.3      0.1      1.9          while True:
    17   1000001     144546.6      0.1      2.3              c = f.read(1)
    18   1000001      82214.9      0.1      1.3              if not c:
    19         1          0.4      0.4      0.0                  break
    20                                           
    21   1000000      90592.5      0.1      1.5              station = ''
    22   8892283     962580.1      0.1     15.6              while c and c != ';':
    23   7892283     839291.8      0.1     13.6                  station += c
    24   7892283    1006976.7      0.1     16.3                  c = f.read(1)
    25   1000000     126703.9      0.1      2.1              c = f.read(1)  # skip ';'
    26                                           
    27   1000000      85661.3      0.1      1.4              temp_str = ''
    28   4841496     574751.2      0.1      9.3              while c and c != '\n':
    29   3841496     423729.6      0.1      6.9                  temp_str += c
    30   3841496     529228.7      0.1      8.6                  c = f.read(1)
    31   1000000     174346.0      0.2      2.8              temp = float(temp_str)
    32                                           
    33   1000000     178354.6      0.2      2.9              s = stats.get(station)
    34   1000000      93937.8      0.1      1.5              if s is None:
    35       413        240.9      0.6      0.0                  stats[station] = Stat(min=temp, max=temp, sum=temp, count=1)
    36       413         42.9      0.1      0.0                  continue
    37    999587     223229.8      0.2      3.6              s.min = min(s.min, temp)
    38    999587     217573.4      0.2      3.5              s.max = max(s.max, temp)
    39    999587     150858.6      0.2      2.4              s.sum += temp
    40    999587     144242.5      0.1      2.3              s.count += 1
    41                                           
    42       414        155.0      0.4      0.0      for station, s in sorted(stats.items()):
    43       413        442.3      1.1      0.0         print(f'{station}={s.min:.1f}/{s.sum/s.count:.1f}/{s.max:.1f}')

  6.16 seconds - r1.py:12 - main
```
