import json
import random
import requests
import time
import pandas

decoder = json.JSONDecoder()

repetitions = 2
methods = ["order", "classification", "buckets", "quantiles", "top"]

def generate_configs(n, m):
    res = []
    for _ in range(m):
        config = list(range(n))
        random.shuffle(config)
        res.append(config)
    return res

yes_latency = {k: [] for k in methods}
try:
    weights = [[random.randint(0, 2 ** 12) for _ in range(100)] for _ in range(100)]
    mapping = {f"Airline {n}": [n] for n in range(100)}
    print("\tEncode Weights")
    r0 = requests.put("http://127.0.0.1:88/", json=weights)
    print(r0)
    encoded = decoder.decode(r0.content.decode())

    print("\tInstall Encoded Weights")
    r1 = requests.put("http://127.0.0.1:80/sessionSecret", json={'mapping': mapping, 'weights': encoded})
    print(r1)

    for _ in range(repetitions):
        configs = generate_configs(100, 500)

        t1 = time.time()
        r3 = requests.put("http://127.0.0.1:80/computePopulationOrder", json=configs)
        t2 = time.time()
        yes_latency['order'].append(t2 - t1)

        t1 = time.time()
        r4 = requests.put("http://127.0.0.1:80/computeClassification/75", json=configs)
        t2 = time.time()
        yes_latency['classification'].append(t2 - t1)

        t1 = time.time()
        r6 = requests.put("http://127.0.0.1:80/computeBuckets/5", json=configs)
        t2 = time.time()
        yes_latency['buckets'].append(t2 - t1)

        t1 = time.time()
        r7 = requests.put("http://127.0.0.1:80/computeQuantiles/5", json=configs)
        t2 = time.time()
        yes_latency['quantiles'].append(t2 - t1)

        t1 = time.time()
        r8 = requests.put("http://127.0.0.1:80/computeTopIndividuals/10", json=configs)
        t2 = time.time()
        yes_latency['top'].append(t2 - t1)
finally:
    df = pandas.DataFrame(yes_latency)
    print(df.agg("mean", axis="rows").to_markdown(floatfmt=".2f"))
