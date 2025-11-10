# HARMONIC Privacy Engine

## Docker

A simple `docker-compose build --build-arg v=□ --build-arg n=□ --build-arg m=□` (with `v` being the MP-SPDZ version, `n` the maximum size of the matrices and `m` the maximum size of the populations) followed by `docker-compose up` (maybe including `--force-recreate`) should be enough  
The Swagger UI will then be at `127.0.0.1/docs`

There is a very basic test/benchmark script (`test.py`)

## Benchmarks

Ubuntu 22.04.3 LTS  
2 x Intel Core2 DUO E8400 @ 3GHz

SlotMachine: MPyC 0.8  
HARMONIC: MP-SPDZ 0.3.7

Results in seconds for `test.py` @ 78a6bd35  
matrix size 100; population size 500  
variable one-way delay (`tc qdisc add dev eth0 root netem delay □ms`)

### Clear (fitness value of a single configuration)

| latency | SlotMachine | HARMONIC Shamir | HARMONIC Replicated Field |
|---------|-------------|-----------------|---------------------------|
| 0 ms    | 0.63        | 0.55            | 0.54                      |
| 1 ms    | -           | 0.58            | 0.66                      |
| 2 ms    | -           | 0.69            | 0.66                      |
| 3 ms    | -           | 0.75            | 0.73                      |

### Order (sorted fitness values of 500 configurations)

| latency | SlotMachine | HARMONIC Shamir | HARMONIC Replicated Field |
|---------|-------------|-----------------|---------------------------|
| 0 ms    | 100.15      | 10.84           | 1.93                      |
| 1 ms    | -           | 19.15           | 4.68                      |
| 2 ms    | -           | 32.07           | 7.97                      |
| 3 ms    | -           | 41.78           | 11.03                     |

### Classification (500 configurations, 2 classes)

| latency | SlotMachine | HARMONIC Shamir<sup>*</sup> | HARMONIC Replicated Field<sup>*</sup> |
|---------|-------------|-----------------------------|---------------------------------------|
| 0 ms    | 11.22       | 0.86                        | 1.21                                  |
| 1 ms    | -           | 1.52                        | 4.28                                  |
| 2 ms    | -           | 2.26                        | 7.43                                  |
| 3 ms    | -           | 3.00                        | 10.66                                 |

<sup>*</sup> without "improvement over last run", "best run so far"

### lap_solver (exact solution; average of 10 runs with random matrices)

| latency | SlotMachine | HARMONIC Shamir | HARMONIC Replicated Field |
|---------|-------------|-----------------|---------------------------|
| 0 ms    | -           | -               | 175                       |
| 1 ms    | -           | -               | 650                       |
| 2 ms    | -           | -               | -                         |
| 3 ms    | -           | -               | -                         |


## Benchmarks on l3dss2302

Ubuntu 24.04.3 LTS  
16 x Intel(R) Xeon(R) W-2245 CPU @ 3.90GHz  
MP-SPDZ 0.4.1  
`bench.py` @ 13cfd282

### Order

| Population | 20x20 | 40x40 | 60x60 | 80x80 | 100x100 |
|-----------:|------:|------:|------:|------:|--------:|
|        100 | 0.44s | 0.46s | 0.47s | 0.45s |   0.50s |
|        200 | 0.60s | 0.61s | 0.63s | 0.64s |   0.63s |
|        300 | 0.74s | 0.75s | 0.77s | 0.77s |   0.78s |
|        400 | 0.84s | 0.87s | 0.89s | 0.88s |   0.90s |
|        500 | 0.99s | 1.01s | 1.04s | 1.04s |   1.06s |

### Classification (75%)

| Population | 20x20 | 40x40 | 60x60 | 80x80 | 100x100 |
|-----------:|------:|------:|------:|------:|--------:|
|        100 | 0.54s | 0.56s | 0.56s | 0.58s |   0.57s |
|        200 | 0.63s | 0.70s | 0.63s | 0.64s |   0.66s |
|        300 | 0.68s | 0.69s | 0.70s | 0.72s |   0.73s |
|        400 | 0.76s | 0.80s | 0.79s | 0.80s |   0.80s |
|        500 | 0.82s | 0.83s | 0.87s | 0.87s |   0.90s |

### Buckets (5)

| Population | 20x20 | 40x40 | 60x60 | 80x80 | 100x100 |
|-----------:|------:|------:|------:|------:|--------:|
|        100 | 1.16s | 1.20s | 1.17s | 1.13s |   1.20s |
|        200 | 1.80s | 1.86s | 1.84s | 1.82s |   1.84s |
|        300 | 2.46s | 2.47s | 2.46s | 2.45s |   2.48s |
|        400 | 3.08s | 3.04s | 3.08s | 3.09s |   3.10s |
|        500 | 3.69s | 3.73s | 3.73s | 3.77s |   3.79s |

### Quantiles (5)

| Population | 20x20 | 40x40 | 60x60 | 80x80 | 100x100 |
|-----------:|------:|------:|------:|------:|--------:|
|        100 | 0.69s | 0.70s | 0.70s | 0.69s |   0.71s |
|        200 | 0.92s | 0.95s | 0.94s | 0.94s |   0.98s |
|        300 | 1.15s | 1.18s | 1.20s | 1.22s |   1.22s |
|        400 | 1.38s | 1.39s | 1.40s | 1.41s |   1.43s |
|        500 | 1.57s | 1.61s | 1.63s | 1.67s |   1.68s |

### Top (10)

| Population | 20x20 | 40x40 | 60x60 | 80x80 | 100x100 |
|-----------:|------:|------:|------:|------:|--------:|
|        100 | 0.46s | 0.48s | 0.48s | 0.49s |   0.49s |
|        200 | 0.59s | 0.62s | 0.61s | 0.63s |   0.63s |
|        300 | 0.73s | 0.75s | 0.76s | 0.77s |   0.77s |
|        400 | 0.87s | 0.88s | 0.90s | 0.90s |   0.92s |
|        500 | 0.98s | 1.03s | 1.03s | 1.04s |   1.05s |

### Latency (100x100 matrix, population 500, 2 repetitions)

Latency is one-way delay from `tc qdisc add dev eth0 root netem delay □ms`

| Method         |     0 |      1 |      2 |      5 |      10 |
|:---------------|------:|-------:|-------:|-------:|--------:|
| order          | 1.04s |  2.40s |  3.77s |  7.70s |  14.19s |
| classification | 0.88s |  3.53s |  5.86s | 12.68s |  23.99s |
| buckets        | 3.71s | 24.02s | 42.40s | 96.66s | 186.30s |
| quantiles      | 1.64s |  3.92s |  6.17s | 12.80s |  23.74s |
| top            | 1.04s |  2.38s |  3.70s |  7.53s |  13.93s |

## Cannot replicate at the moment

### lap_solver (exact solution; average of 10 runs with random matrices)

| latency | SlotMachine | HARMONIC Shamir | HARMONIC Replicated Field |
|---------|-------------|-----------------|---------------------------|
| 0 ms    | -           | -               | 35                        |
| 1 ms    | -           | -               | -                         |
| 5 ms    | -           | -               | -                         |
| 10 ms   | -           | -               | -                         |
