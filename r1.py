# Read and process 1 byte at a time

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
        while True:
            c = f.read(1)
            if not c:
                break

            station = ''
            while c and c != ';':
                station += c
                c = f.read(1)
            c = f.read(1)  # skip ';'

            temp_str = ''
            while c and c != '\n':
                temp_str += c
                c = f.read(1)
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
