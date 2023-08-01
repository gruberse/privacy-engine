FROM alpine:latest as base

FROM base as builder

RUN apk add binutils py3-pip

COPY requirements.txt /

RUN pip install wheel

RUN pip install -r /requirements.txt

COPY main.py /

RUN pyinstaller main.py

FROM base

COPY --from=builder /dist /

ENTRYPOINT /main/main
