FROM alpine:latest as base

FROM base as builder

RUN wget https://github.com/data61/MP-SPDZ/archive/refs/tags/v0.3.6.tar.gz

RUN tar xvfz v0.3.6.tar.gz

RUN apk add make g++ libsodium-dev musl-dev bash openssl openssl-dev ca-certificates gmp-dev python3-dev py3-pip boost-dev

WORKDIR MP-SPDZ-0.3.6

# RUN echo "MOD = -DGFP_MOD_SZ=5" >> CONFIG.mine
RUN echo "CXX = g++" >> CONFIG.mine
RUN echo "USE_NTL = 0" >> CONFIG.mine
RUN echo "MY_CFLAGS += -I/usr/local/include" >> CONFIG.mine
RUN echo "MY_LDLIBS += -Wl,-rpath -Wl,/usr/local/lib -L/usr/local/lib" >> CONFIG.mine

RUN make shamir-party.x

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

RUN apk add bash libgmpxx libsodium

COPY --from=builder /MP-SPDZ-0.3.6/libSPDZ.so /
COPY --from=builder /MP-SPDZ-0.3.6/shamir-party.x /
COPY --from=builder /MP-SPDZ-0.3.6/Player-Data /Player-Data
COPY --from=builder /MP-SPDZ-0.3.6/Scripts/run-common.sh /Scripts/run-common.sh
COPY --from=builder /MP-SPDZ-0.3.6/Scripts/shamir.sh /Scripts/shamir.sh

COPY --from=builder /MP-SPDZ-0.3.6/Programs/Bytecode/encode-0.bc /Programs/Bytecode/
COPY --from=builder /MP-SPDZ-0.3.6/Programs/Schedules/encode.sch /Programs/Schedules/
RUN mkdir Programs/Public-Input

COPY --from=builder /dist /

ENTRYPOINT /encode/encode
