import multiprocessing
import time

def worker(num):
    """Thread worker function"""
    print(f'Worker: {num}')
    time.sleep(2)
    print(f'Worker {num} done')

if __name__ == '__main__':
    processes = []
    for i in range(5):
        p = multiprocessing.Process(target=worker, args=(i,))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()
