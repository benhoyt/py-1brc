# Read line at a time and parse with str.partition

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
    stats = {}
    with open(sys.argv[1]) as f:
        for line in f:
            station, _, temp_str = line.partition(';')
            temp = float(temp_str)

            s = stats.get(station)
            if s is None:
                stats[station] = Stat(min=temp, max=temp, sum=temp, count=1)
                continue

            s.min = min(s.min, temp)
            s.max = max(s.max, temp)
            s.sum += temp
            s.count += 1

    for station, s in sorted(stats.items()):
        print(f'{station}={s.min:.1f}/{s.sum/s.count:.1f}/{s.max:.1f}')

main()
