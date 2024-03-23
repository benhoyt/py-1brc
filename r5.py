# Micro-optimized r4 (read line at a time and parse with str.partition)

from dataclasses import dataclass
from line_profiler import profile
import sys

@dataclass
class Stat:
    min: float
    max: float
    sum: float
    count: float

@profile
def main():
    floats = {str(i/10)+'\n': i/10 for i in range(-999, 1000)}
    stats = {}
    with open(sys.argv[1]) as f:
        for line in f:
            station, _, temp_str = line.partition(';')
            temp = floats[temp_str]

            try:
                s = stats[station]
                if temp < s.min:
                    s.min = temp
                if temp > s.max:
                    s.max = temp
                s.sum += temp
                s.count += 1
            except KeyError:
                stats[station] = Stat(min=temp, max=temp, sum=temp, count=1)

    for station, s in sorted(stats.items()):
        print(f'{station}={s.min:.1f}/{s.sum/s.count:.1f}/{s.max:.1f}')

main()
