import json
import random
import requests
import time
import pandas

decoder = json.JSONDecoder()

repetitions = 10
exact = {k: [] for k in ["lap_solver", "munkres"]}

try:
    for _ in range(repetitions):
        weights = [[random.randint(0, 2 ** 12) for _ in range(100)] for _ in range(100)]
        mapping = {f"Airline {n}": [n] for n in range(100)}
        print("\tEncode Weights")
        r0 = requests.put("http://127.0.0.1:88/", json=weights)
        print(r0)
        encoded = decoder.decode(r0.content.decode())

        print("\tInstall Encoded Weights")
        r1 = requests.put("http://127.0.0.1:80/sessionSecret", json={'mapping': mapping, 'weights': encoded})
        print(r1)

        t1 = time.time()
        _ = requests.put("http://127.0.0.1:80/computeExact")
        t2 = time.time()
        exact['lap_solver'].append(t2 - t1)

        t1 = time.time()
        _ = requests.put("http://127.0.0.1:80/computeMunkres")
        t2 = time.time()
        exact['munkres'].append(t2 - t1)
finally:
    df = pandas.DataFrame(exact)
    print(df.agg("mean", axis="rows").to_markdown(floatfmt=".2f"))
