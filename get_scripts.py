import sources
import json
import time
import multiprocessing
import os

DIR = os.path.join("scripts", "temp")

if not os.path.exists(DIR):
    os.makedirs(DIR)

def main():
    f = open('sources.json', 'r')
    data = json.load(f)
    processes = []
    starttime = time.time()

    for source in data:
        included = data[source]
        if included == "true":
            p = multiprocessing.Process(target=sources.get_scripts, args=(source,))
            processes.append(p)
            p.start()

    for process in processes:
        process.join()

    print()    
    print('Time taken = {} seconds'.format(time.time() - starttime))

if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
