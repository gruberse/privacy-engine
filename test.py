import json
import random
import requests
import time

N = 100
M = 500

weights = [[random.randint(0, 128) for _ in range(N)] for _ in range(N)]
mapping = {f"Airline {n}": [n] for n in range(M)}
configs = []
decoder = json.JSONDecoder()

for _ in range(M):
    config = list(range(N))
    random.shuffle(config)
    configs.append(config)

print("\tGet Status")
print(requests.get("http://127.0.0.1:80/status"))

# print("\tPut Session")
# r1 = requests.put("http://127.0.0.1:80/sessionClear", json={'weights': weights, 'mapping': {}})
# print(r1)

print("\tEncode Weights")
r0 = requests.put("http://127.0.0.1:88/", json=weights)
print(r0)
encoded = decoder.decode(r0.content.decode())

print("\tInstall Encoded Weights")
r1 = requests.put("http://127.0.0.1:80/sessionSecret", json={'mapping': mapping, 'weights': encoded})
print(r1)

print("\tCompute Fitness Clear")
t1 = time.time()
r2 = requests.put("http://127.0.0.1:80/computeFitnessClear", json=configs)
t2 = time.time()
print(r2)
print(f"time: {t2 - t1:.2f}s")
res2 = [sum([weights[i][j] for i, j in enumerate(c)]) for c in configs]
if res2 == r2.json():
    print("OK")
else:
    print(res2)
    print(r2.json())

print("\tCompute Population Order")
t1 = time.time()
r3 = requests.put("http://127.0.0.1:80/computePopulationOrder", json=configs)
t2 = time.time()
print(r3)
print(f"time: {t2 - t1:.2f}s")
res3 = list(enumerate(res2))
res3.sort(key=(lambda x: x[1]))
res3 = [x[0] for x in res3]
if r3.json() == {'maximum': max(res2), 'order': res3}:
    print("OK")
else:
    print(max(res2), res3)
    print(r3.json())

print("\tCompute Classification")
t1 = time.time()
r4 = requests.put("http://127.0.0.1:80/computeClassification", json=configs)
t2 = time.time()
print(r4)
print(f"time: {t2 - t1:.2f}s")
ma = max(res2)
mi = min(res2)
span = ma - mi
thresh = ma - (span // 4)
res4 = [i for i, x in enumerate(res2) if x >= thresh]
if r4.json() == {'highest': -1, 'best': False, 'indices': res4}:
    print("OK")
else:
    print(res4)
    print(r4.json())

print("\tCompute Exact Solution")
t1 = time.time()
r5 = requests.put("http://127.0.0.1:80/computeExact", json=configs)
t2 = time.time()
print(r5)
print(f"time: {t2 - t1:.2f}s")

print("\tCompute 5 Buckets")
t1 = time.time()
r6 = requests.put("http://127.0.0.1:80/computeBuckets/5", json=configs)
t2 = time.time()
print(r6)
print(f"time: {t2 - t1:.2f}s")
res6 = [((r - mi) * 5) // (span + 1) for r in res2]
if r6.json() == {'maximum': ma, 'mapping': res6}:
    print("OK")
else:
    print(res6)
    print(r6.json())

print("\tCompute 5 Quantiles")
t1 = time.time()
r7 = requests.put("http://127.0.0.1:80/computeQuantiles/5", json=configs)
t2 = time.time()
print(r7)
print(f"time: {t2 - t1:.2f}s")
res7 = [(x, (i*5) // M) for i, x in enumerate(res3)]
res7.sort(key=(lambda x: x[0]))
res7 = [x[1] for x in res7]
if r7.json() == {'maximum': ma, 'mapping': res7}:
    print("OK")
else:
    print(res7)
    print(r7.json())
