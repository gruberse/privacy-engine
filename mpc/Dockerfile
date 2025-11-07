FROM ubuntu:24.04 AS base

RUN apt update
RUN apt upgrade -y

FROM base AS builder

RUN apt install -y wget clang libsodium-dev python3-pip libgmp-dev libssl-dev libboost1.83-dev libboost-iostreams1.83-dev libboost-filesystem1.83-dev

ARG v

RUN wget https://github.com/data61/MP-SPDZ/archive/refs/tags/v$v.tar.gz

RUN tar xvfz v$v.tar.gz

WORKDIR MP-SPDZ-$v

RUN echo "MOD = -DGFP_MOD_SZ=5" >> CONFIG.mine
RUN echo "USE_NTL = 0" >> CONFIG.mine

RUN make shamir-party.x replicated-field-party.x

COPY fitness_clear.mpc Programs/Source
COPY population_order.mpc Programs/Source
COPY classification.mpc Programs/Source
COPY lap_solver.mpc Programs/Source
COPY buckets.mpc Programs/Source
COPY quantiles.mpc Programs/Source
COPY top_individuals.mpc Programs/Source

ARG n
ENV n=$n

RUN python3 compile.py -Ol -F 64 fitness_clear 100
RUN python3 compile.py -Ol -F 64 population_order 100
RUN python3 compile.py -Ol -F 64 classification 100
# RUN python3 compile.py -Ol -F 64 lap_solver 100
RUN python3 compile.py -Ol -F 64 buckets 100
RUN python3 compile.py -Ol -F 64 quantiles 100
RUN python3 compile.py -Ol -F 64 top_individuals 100

RUN python3 compile.py -Ol -F 64 fitness_clear 200
RUN python3 compile.py -Ol -F 64 population_order 200
RUN python3 compile.py -Ol -F 64 classification 200
# RUN python3 compile.py -Ol -F 64 lap_solver 200
RUN python3 compile.py -Ol -F 64 buckets 200
RUN python3 compile.py -Ol -F 64 quantiles 200
RUN python3 compile.py -Ol -F 64 top_individuals 200

RUN python3 compile.py -Ol -F 64 fitness_clear 300
RUN python3 compile.py -Ol -F 64 population_order 300
RUN python3 compile.py -Ol -F 64 classification 300
# RUN python3 compile.py -Ol -F 64 lap_solver 300
RUN python3 compile.py -Ol -F 64 buckets 300
RUN python3 compile.py -Ol -F 64 quantiles 300
RUN python3 compile.py -Ol -F 64 top_individuals 300

RUN python3 compile.py -Ol -F 64 fitness_clear 400
RUN python3 compile.py -Ol -F 64 population_order 400
RUN python3 compile.py -Ol -F 64 classification 400
# RUN python3 compile.py -Ol -F 64 lap_solver 400
RUN python3 compile.py -Ol -F 64 buckets 400
RUN python3 compile.py -Ol -F 64 quantiles 400
RUN python3 compile.py -Ol -F 64 top_individuals 400

RUN python3 compile.py -Ol -F 64 fitness_clear 500
RUN python3 compile.py -Ol -F 64 population_order 500
RUN python3 compile.py -Ol -F 64 classification 500
# RUN python3 compile.py -Ol -F 64 lap_solver 500
RUN python3 compile.py -Ol -F 64 buckets 500
RUN python3 compile.py -Ol -F 64 quantiles 500
RUN python3 compile.py -Ol -F 64 top_individuals 500

RUN sed -i '14s/$/ -days 365/' Scripts/setup-ssl.sh
RUN Scripts/setup-ssl.sh 3

WORKDIR /

COPY requirements.txt /

RUN pip install --break-system-packages wheel

RUN pip install --break-system-packages -r /requirements.txt

COPY mpc_node.py /

RUN pyinstaller mpc_node.py

FROM base

RUN apt install -y libgmp10 libsodium23 libboost-filesystem1.83.0 libboost-iostreams1.83.0 libboost-system1.83.0 libgmpxx4ldbl

ARG v

COPY --from=builder /MP-SPDZ-$v/libSPDZ.so /
COPY --from=builder /MP-SPDZ-$v/shamir-party.x /
COPY --from=builder /MP-SPDZ-$v/replicated-field-party.x /
COPY --from=builder /MP-SPDZ-$v/Player-Data /Player-Data

COPY --from=builder /MP-SPDZ-$v/Programs/Bytecode/fitness_clear-*.bc /Programs/Bytecode/
COPY --from=builder /MP-SPDZ-$v/Programs/Schedules/fitness_clear*.sch /Programs/Schedules/
COPY --from=builder /MP-SPDZ-$v/Programs/Bytecode/population_order-*.bc /Programs/Bytecode/
COPY --from=builder /MP-SPDZ-$v/Programs/Schedules/population_order*.sch /Programs/Schedules/
COPY --from=builder /MP-SPDZ-$v/Programs/Bytecode/classification-*.bc /Programs/Bytecode/
COPY --from=builder /MP-SPDZ-$v/Programs/Schedules/classification*.sch /Programs/Schedules/
COPY --from=builder /MP-SPDZ-$v/Programs/Bytecode/lap_solver-*.bc /Programs/Bytecode/
COPY --from=builder /MP-SPDZ-$v/Programs/Schedules/lap_solver*.sch /Programs/Schedules/
COPY --from=builder /MP-SPDZ-$v/Programs/Bytecode/buckets-*.bc /Programs/Bytecode/
COPY --from=builder /MP-SPDZ-$v/Programs/Schedules/buckets*.sch /Programs/Schedules/
COPY --from=builder /MP-SPDZ-$v/Programs/Bytecode/quantiles-*.bc /Programs/Bytecode/
COPY --from=builder /MP-SPDZ-$v/Programs/Schedules/quantiles*.sch /Programs/Schedules/
COPY --from=builder /MP-SPDZ-$v/Programs/Bytecode/top_individuals-*.bc /Programs/Bytecode/
COPY --from=builder /MP-SPDZ-$v/Programs/Schedules/top_individuals*.sch /Programs/Schedules/

COPY --from=builder /dist /

ARG n
ARG m
ENV n=$n
ENV m=$m

# RUN apt install -y iproute2
# ENTRYPOINT tc qdisc add dev eth0 root netem delay 0ms && /mpc_node/mpc_node

ENTRYPOINT /mpc_node/mpc_node
