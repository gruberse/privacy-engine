import json
import random
import requests
import statistics
import time
import matplotlib.pyplot as plt
import pandas

decoder = json.JSONDecoder()

def generate_configs(n, m):
    res = []
    for _ in range(m):
        config = list(range(n))
        random.shuffle(config)
        res.append(config)
    return res

xs = []
ys = []

Ns = [20, 40, 60, 80, 100]
Ms = [100, 200, 300, 400, 500]
repetitions = 10
methods = ["order", "classification", "buckets", "quantiles", "top"]

order = {n: {m: [] for m in Ms} for n in Ns}
classification = {n: {m: [] for m in Ms} for n in Ns}
buckets = {n: {m: [] for m in Ms} for n in Ns}
quantiles = {n: {m: [] for m in Ms} for n in Ns}
top = {n: {m: [] for m in Ms} for n in Ns}

for N in Ns:
    weights = [[random.randint(0, 2**12) for _ in range(N)] for _ in range(N)]
    mapping = {f"Airline {n}": [n] for n in range(N)}
    print("\tEncode Weights")
    r0 = requests.put("http://127.0.0.1:88/", json=weights)
    print(r0)
    encoded = decoder.decode(r0.content.decode())

    print("\tInstall Encoded Weights")
    r1 = requests.put("http://127.0.0.1:80/sessionSecret", json={'mapping': mapping, 'weights': encoded})
    print(r1)
    for M in Ms:
        for _ in range(repetitions):
            xs.append(N)
            ys.append(M)
            configs = generate_configs(N, M)

            t1 = time.time()
            r3 = requests.put("http://127.0.0.1:80/computePopulationOrder", json=configs)
            t2 = time.time()
            order[N][M].append(t2 - t1)

            t1 = time.time()
            r4 = requests.put("http://127.0.0.1:80/computeClassification/75", json=configs)
            t2 = time.time()
            classification[N][M].append(t2 - t1)

            t1 = time.time()
            r6 = requests.put("http://127.0.0.1:80/computeBuckets/5", json=configs)
            t2 = time.time()
            buckets[N][M].append(t2 - t1)

            t1 = time.time()
            r7 = requests.put("http://127.0.0.1:80/computeQuantiles/5", json=configs)
            t2 = time.time()
            quantiles[N][M].append(t2 - t1)

            t1 = time.time()
            r8 = requests.put("http://127.0.0.1:80/computeTopIndividuals/10", json=configs)
            t2 = time.time()
            top[N][M].append(t2 - t1)

for name, zs in zip(methods, [order, classification, buckets, quantiles, top]):
    print(name)
    df = pandas.DataFrame(zs)
    print(df.map(statistics.mean).to_markdown(floatfmt=".2f"))
    fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
    fig.suptitle(name)
    ax.scatter(xs, ys, df.values.flatten().tolist())
    ax.set_xticks(Ns)
    ax.set_yticks(Ms)
    plt.savefig(f"{name}-no_latency.png", format="png")
