# test performance of system

import client.sPinClient as sPinClient
import os, time # saving/timing

# concurrently run
import concurrent.futures

# run a full timing sequence
def test_performance():

    # set up client
    client = sPinClient.sPinClient(verbose=False)

    # get list of all files in files directory
    all_files = [f'files/{file}' for file in os.listdir('files/')]

    # test adds
    add_start = time.perf_counter_ns()
    all_ids = []
    for file in all_files:
        all_ids.append(client.sPinADD(file))
    add_duration = time.perf_counter_ns() - add_start

    # test gets
    # sPinGET verifies integrity internally
    get_start = time.perf_counter_ns()
    for id in all_ids:
        client.sPinGET(id, f'results/{id}')
    get_duration = time.perf_counter_ns() - get_start

    # test dels
    del_start = time.perf_counter_ns()
    for id in all_ids:
        client.sPinDEL(id)
    del_duration = time.perf_counter_ns() - del_start

    return {
        'ops': len(all_files),
        'add_ns': add_duration,
        'get_ns': get_duration,
        'del_ns': del_duration
    }

if __name__ == '__main__':

    # run with 1 and 3 clients
    for n in [1, 3]:

        # use concurrent executor, one thread per client
        with concurrent.futures.ThreadPoolExecutor(max_workers=n) as executor:
            futures = [executor.submit(test_performance) for _ in range(n)]

            # track totals for stats
            ops, add_ns, get_ns, del_ns = 0, 0, 0, 0

            # as things complete, read their results out
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                except Exception as err:
                    print(f'exception: {err}')

                ops += result['ops']
                add_ns += result['add_ns']
                get_ns += result['get_ns']
                del_ns += result['del_ns']

        print(f'Results for {n} Client(s):')
        # througput = ops / (ns * (1 / 10**9))
        add_thru = ops / (add_ns * (1 / 10 ** 9))
        get_thru = ops / (get_ns * (1 / 10 ** 9))
        del_thru = ops / (del_ns * (1 / 10 ** 9))
        # latency = 1 / throughput
        add_ltcy = 1 / add_thru
        get_ltcy = 1 / get_thru
        del_ltcy = 1 / del_thru

        print(f'ADD Throughput: {add_thru} ops/s')
        print(f'GET Throughput: {get_thru} ops/s')
        print(f'DEL Throughput: {del_thru} ops/s')

        print()

        print(f'ADD Latency: {add_ltcy} s/op')
        print(f'GET Latency: {get_ltcy} s/op')
        print(f'DEL Latency: {del_ltcy} s/op')

        print()
