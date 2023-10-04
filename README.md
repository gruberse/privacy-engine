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
| Clear | 0.63 | 0.55 | 0.58 | 0.69 | 0.75 | 0.54 | 0.66 | 0.66 | 0.73 |
| Order | 100.15 | 10.84 | 19.15 | 32.07 | 41.78 | 1.93 | 4.68 | 7.97 | 11.03 |
| Classification | 11.22 | 0.86<sup>*</sup> | 1.52<sup>*</sup> | 2.26<sup>*</sup> | 3.00<sup>*</sup> | 1.21<sup>*</sup> | 4.28<sup>*</sup> | 7.43<sup>*</sup> | 10.66<sup>*</sup> |

<sup>*</sup> without "improvement over last run", "best run so far"
