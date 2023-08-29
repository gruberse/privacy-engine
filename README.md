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
no delay/packet loss

| | SlotMachine | HARMONIC Shamir  | HARMONIC Replicated |
| -- | -- | -- | -- |
| Clear | 0.63 | 0.55 | . |
| Order | 100.15 | 10.84 | . |
| Classification | 11.22 | 0.86<sup>*</sup> | . |

<sup>*</sup> without "improvement over last run", "best run so far"
