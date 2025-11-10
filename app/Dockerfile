FROM ubuntu:24.04 AS base

RUN apt update
RUN apt upgrade -y

FROM base AS builder

RUN apt install -y python3-pip

COPY requirements.txt /

RUN pip install --break-system-packages wheel

RUN pip install --break-system-packages -r /requirements.txt

COPY main.py /

RUN pyinstaller main.py

FROM base

COPY --from=builder /dist /

ENTRYPOINT exec /main/main
