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

COPY encode.mpc Programs/Source

ARG n
ENV n=$n

RUN python3 compile.py -F 64 encode

RUN sed -i '14s/$/ -days 365/' Scripts/setup-ssl.sh
RUN Scripts/setup-ssl.sh 3

WORKDIR /

COPY requirements.txt /

RUN pip install --break-system-packages wheel

RUN pip install --break-system-packages -r /requirements.txt

COPY encode.py /

RUN pyinstaller encode.py

FROM base

RUN apt install -y libgmp10 libsodium23 libboost-filesystem1.83.0 libboost-iostreams1.83.0 libboost-system1.83.0 libgmpxx4ldbl

ARG v

COPY --from=builder /MP-SPDZ-$v/libSPDZ.so /
COPY --from=builder /MP-SPDZ-$v/shamir-party.x /
COPY --from=builder /MP-SPDZ-$v/replicated-field-party.x /
COPY --from=builder /MP-SPDZ-$v/Player-Data /Player-Data
COPY --from=builder /MP-SPDZ-$v/Scripts/run-common.sh /Scripts/run-common.sh
COPY --from=builder /MP-SPDZ-$v/Scripts/shamir.sh /Scripts/shamir.sh
COPY --from=builder /MP-SPDZ-$v/Scripts/rep-field.sh /Scripts/rep-field.sh

COPY --from=builder /MP-SPDZ-$v/Programs/Bytecode/encode-*.bc /Programs/Bytecode/
COPY --from=builder /MP-SPDZ-$v/Programs/Schedules/encode.sch /Programs/Schedules/
RUN mkdir Programs/Public-Input

COPY --from=builder /dist /

ARG n
ENV n=$n

ENTRYPOINT exec /encode/encode
