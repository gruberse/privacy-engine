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

### lap_solver (exact solution; average of 10 runs with random matrices)

| latency | SlotMachine | HARMONIC Shamir | HARMONIC Replicated Field |
|---------|-------------|-----------------|---------------------------|
| 0 ms    | -           | -               | 35                        |
| 1 ms    | -           | -               | -                         |
| 5 ms    | -           | -               | -                         |
| 10 ms   | -           | -               | -                         |
