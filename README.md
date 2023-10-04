# HARMONIC Privacy Engine

## Docker

A simple `docker-compose build` followed by `docker-compose up` (maybe including `--force-recreate`) should be enough  
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

| | SlotMachine | HARMONIC<br> Shamir 0ms  | HARMONIC<br> Shamir 1ms | HARMONIC<br> Shamir 2ms | HARMONIC<br> Shamir 3ms | HARMONIC<br> Replicated Field 0ms | HARMONIC<br> Replicated Field 1ms | HARMONIC<br> Replicated Field 2ms | HARMONIC<br> Replicated Field 3ms |
| -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Clear | 0.63 | 0.55 | 0.58 | 0.69 | 0.75 | 0.54 | 0.57 | 0.52 | 0.52 |
| Order | 100.15 | 10.84 | 19.15 | 32.07 | 41.78 | 1.93 | 2.00 | 2.03 | 1.97 |
| Classification<sup>*</sup> | 11.22 | 0.86 | 1.52 | 2.26 | 3.00 | 1.21 | 1.21 | 1.21 | 1.23 |

<sup>*</sup> without "improvement over last run", "best run so far"
