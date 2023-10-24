FROM alpine:latest as base

FROM base as builder

ARG v=0.3.7

RUN wget https://github.com/data61/MP-SPDZ/archive/refs/tags/v$v.tar.gz

RUN tar xvfz v$v.tar.gz

RUN apk add make g++ libsodium-dev musl-dev bash openssl openssl-dev ca-certificates gmp-dev python3-dev py3-pip boost-dev

WORKDIR MP-SPDZ-$v

# RUN echo "MOD = -DGFP_MOD_SZ=5" >> CONFIG.mine
RUN echo "CXX = g++" >> CONFIG.mine
RUN echo "USE_NTL = 0" >> CONFIG.mine
RUN echo "MY_CFLAGS += -I/usr/local/include" >> CONFIG.mine
RUN echo "MY_LDLIBS += -Wl,-rpath -Wl,/usr/local/lib -L/usr/local/lib" >> CONFIG.mine

RUN make shamir-party.x replicated-field-party.x

COPY fitness_clear.mpc Programs/Source
COPY population_order.mpc Programs/Source
COPY classification.mpc Programs/Source
COPY lap_solver.mpc Programs/Source

RUN python3 compile.py -F 64 fitness_clear
RUN python3 compile.py -F 64 population_order
RUN python3 compile.py -F 64 classification
RUN python3 compile.py -F 64 lap_solver

RUN Scripts/setup-ssl.sh 3

WORKDIR /

COPY requirements.txt /

RUN pip install wheel

RUN pip install -r /requirements.txt

COPY mpc_node.py /

RUN pyinstaller mpc_node.py

FROM base

ARG v=0.3.7

RUN apk add bash libgmpxx libsodium

COPY --from=builder /MP-SPDZ-$v/libSPDZ.so /
COPY --from=builder /MP-SPDZ-$v/shamir-party.x /
COPY --from=builder /MP-SPDZ-$v/replicated-field-party.x /
COPY --from=builder /MP-SPDZ-$v/Player-Data /Player-Data

COPY --from=builder /MP-SPDZ-$v/Programs/Bytecode/fitness_clear-0.bc /Programs/Bytecode/
COPY --from=builder /MP-SPDZ-$v/Programs/Schedules/fitness_clear.sch /Programs/Schedules/
COPY --from=builder /MP-SPDZ-$v/Programs/Bytecode/population_order-0.bc /Programs/Bytecode/
COPY --from=builder /MP-SPDZ-$v/Programs/Schedules/population_order.sch /Programs/Schedules/
COPY --from=builder /MP-SPDZ-$v/Programs/Bytecode/classification-0.bc /Programs/Bytecode/
COPY --from=builder /MP-SPDZ-$v/Programs/Schedules/classification.sch /Programs/Schedules/
COPY --from=builder /MP-SPDZ-$v/Programs/Bytecode/lap_solver-0.bc /Programs/Bytecode/
COPY --from=builder /MP-SPDZ-$v/Programs/Schedules/lap_solver.sch /Programs/Schedules/

COPY --from=builder /dist /

RUN apk add iproute2
ENTRYPOINT tc qdisc add dev eth0 root netem delay 0ms && /mpc_node/mpc_node
