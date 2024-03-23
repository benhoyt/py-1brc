# Read and process 1 byte at a time (unbuffered), stats list instead of dict

from dataclasses import dataclass
from line_profiler import profile
import sys

@dataclass
class Stat:
    station: str
    min: float
    max: float
    sum: float
    count: float

@profile
def main():
    stats = []
    with open(sys.argv[1], 'rb', buffering=0) as f:
        while True:
            b = f.read(1)
            if not b:
                break

            station = b''
            while b and b != b';':
                station += b
                b = f.read(1)
            b = f.read(1)  # skip ';'
            temp_str = b''
            while b and b != b'\n':
                temp_str += b
                b = f.read(1)
            temp = float(temp_str)

            s = next((s for s in stats if s.station == station), None)
            if s is None:
                stats.append(Stat(station=station, min=temp, max=temp, sum=temp, count=1))
                continue
            s.min = min(s.min, temp)
            s.max = max(s.max, temp)
            s.sum += temp
            s.count += 1

    for s in sorted(stats, key=lambda s: s.station):
        print(f'{s.station.decode()}={s.min:.1f}/{s.sum/s.count:.1f}/{s.max:.1f}')

main()
