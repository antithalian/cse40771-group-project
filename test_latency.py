# test latency of system
import client.sPinClient
import os
import time

client = client.sPinClient.sPinClient(False)

all_files = [f'files/{file}' for file in os.listdir('files/')]
print(len(all_files))
# test adds
add_start = time.perf_counter_ns()
all_ids = []
for file in all_files:
    all_ids.append(client.sPinADD(file))
add_duration = time.perf_counter_ns() - add_start
print(len(all_ids))

# test gets
get_start = time.perf_counter_ns()
for id in all_ids:
    client.sPinGET(id, f'results/{id}')
get_duration = time.perf_counter_ns() - get_start


# test dels
del_start = time.perf_counter_ns()
for id in all_ids:
    client.sPinDEL(id)
del_duration = time.perf_counter_ns() - del_start

print(add_duration * (1 / len(all_files)) * (1 / (10 ** 9)))
print(get_duration * (1 / len(all_files)) * (1 / (10 ** 9)))
print(del_duration * (1 / len(all_files)) * (1 / (10 ** 9)))