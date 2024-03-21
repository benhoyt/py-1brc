# Split into chunks and process in parallel with process pool (to get around the GIL)

from dataclasses import dataclass
import multiprocessing.pool, os, sys, time

@dataclass
class Stat:
    min: float
    max: float
    sum: float
    count: float

def process_chunk(path_offset_size):
    path, offset, size = path_offset_size
    with open(path, 'rb') as f:
        f.seek(offset)
        bytes_read = 0
        stats = {}

        for line in f:
            station, _, temp_str = line.partition(b';')
            temp = float(temp_str)
            s = stats.get(station)
            if s is None:
                stats[station] = Stat(min=temp, max=temp, sum=temp, count=1)
            else:
                s.min = min(s.min, temp)
                s.max = max(s.max, temp)
                s.sum += temp
                s.count += 1

            bytes_read += len(line)
            if bytes_read >= size:
                break

    return stats

def get_parts(path, num_parts):
    total_size = os.path.getsize(path)
    split_size = total_size // num_parts
    parts = []
    offset, size = 0, 0
    with open(path, 'rb') as f:
        while offset + size < total_size:
            offset = f.tell()
            f.seek(min(offset + split_size, total_size))
            f.readline()  # sync to after next '\n'
            size = f.tell() - offset
            parts.append((offset, size))
    assert sum(size for _, size in parts) == total_size
    return parts

def merge_results(results):
    totals = {}
    for result in results:
        for station, s in result.items():
            ts = totals.get(station)
            if ts is None:
                totals[station] = Stat(min=s.min, max=s.max, sum=s.sum, count=s.count)
                continue
            ts.min = min(ts.min, s.min)
            ts.max = max(ts.max, s.max)
            ts.sum += s.sum
            ts.count += s.count
    return totals

def main(path):
    start = time.time()

    num_cpus = os.cpu_count()
    args = [(path, offset, size) for offset, size in get_parts(path, num_cpus)]

    with multiprocessing.pool.Pool(num_cpus) as p:
        results = p.map(process_chunk, args)

    totals = merge_results(results)
    for station, s in sorted(totals.items()):
        print(f'{station.decode()}={s.min:.1f}/{s.sum/s.count:.1f}/{s.max:.1f}')

    elapsed = time.time() - start
    total_size = os.path.getsize(path)
    print(f'Processed {total_size/(1024*1024):.1f}MB in {elapsed*1000:.3f}ms on {num_cpus} cores', file=sys.stderr)

main(sys.argv[1])
