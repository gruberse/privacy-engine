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

COPY encode.mpc Programs/Source

RUN python3 compile.py -F 64 encode

RUN Scripts/setup-ssl.sh 3

WORKDIR /

COPY requirements.txt /

RUN pip install wheel

RUN pip install -r /requirements.txt

COPY encode.py /

RUN pyinstaller encode.py

FROM base

ARG v=0.3.7

RUN apk add bash libgmpxx libsodium

COPY --from=builder /MP-SPDZ-$v/libSPDZ.so /
COPY --from=builder /MP-SPDZ-$v/shamir-party.x /
COPY --from=builder /MP-SPDZ-$v/replicated-field-party.x /
COPY --from=builder /MP-SPDZ-$v/Player-Data /Player-Data
COPY --from=builder /MP-SPDZ-$v/Scripts/run-common.sh /Scripts/run-common.sh
COPY --from=builder /MP-SPDZ-$v/Scripts/shamir.sh /Scripts/shamir.sh
COPY --from=builder /MP-SPDZ-$v/Scripts/rep-field.sh /Scripts/rep-field.sh

COPY --from=builder /MP-SPDZ-$v/Programs/Bytecode/encode-0.bc /Programs/Bytecode/
COPY --from=builder /MP-SPDZ-$v/Programs/Schedules/encode.sch /Programs/Schedules/
RUN mkdir Programs/Public-Input

COPY --from=builder /dist /

ENTRYPOINT /encode/encode
