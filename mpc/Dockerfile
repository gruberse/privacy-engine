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
ARG m
ENV n=$n
ENV m=$m

RUN python3 compile.py -F 64 fitness_clear
RUN python3 compile.py -F 64 population_order
RUN python3 compile.py -F 64 classification
RUN python3 compile.py -F 64 lap_solver
RUN python3 compile.py -F 64 buckets
RUN python3 compile.py -F 64 quantiles
RUN python3 compile.py -F 64 top_individuals

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
COPY --from=builder /MP-SPDZ-$v/Programs/Schedules/fitness_clear.sch /Programs/Schedules/
COPY --from=builder /MP-SPDZ-$v/Programs/Bytecode/population_order-*.bc /Programs/Bytecode/
COPY --from=builder /MP-SPDZ-$v/Programs/Schedules/population_order.sch /Programs/Schedules/
COPY --from=builder /MP-SPDZ-$v/Programs/Bytecode/classification-*.bc /Programs/Bytecode/
COPY --from=builder /MP-SPDZ-$v/Programs/Schedules/classification.sch /Programs/Schedules/
COPY --from=builder /MP-SPDZ-$v/Programs/Bytecode/lap_solver-*.bc /Programs/Bytecode/
COPY --from=builder /MP-SPDZ-$v/Programs/Schedules/lap_solver.sch /Programs/Schedules/
COPY --from=builder /MP-SPDZ-$v/Programs/Bytecode/buckets-*.bc /Programs/Bytecode/
COPY --from=builder /MP-SPDZ-$v/Programs/Schedules/buckets.sch /Programs/Schedules/
COPY --from=builder /MP-SPDZ-$v/Programs/Bytecode/quantiles-*.bc /Programs/Bytecode/
COPY --from=builder /MP-SPDZ-$v/Programs/Schedules/quantiles.sch /Programs/Schedules/
COPY --from=builder /MP-SPDZ-$v/Programs/Bytecode/top_individuals-*.bc /Programs/Bytecode/
COPY --from=builder /MP-SPDZ-$v/Programs/Schedules/top_individuals.sch /Programs/Schedules/

COPY --from=builder /dist /

ARG n
ARG m
ENV n=$n
ENV m=$m

# RUN apt install -y iproute2
# ENTRYPOINT tc qdisc add dev eth0 root netem delay 0ms && /mpc_node/mpc_node

ENTRYPOINT /mpc_node/mpc_node
