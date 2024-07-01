FROM python:3.9-bullseye

COPY requirements.txt src /app/
WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends wget && \
    pip install -r /app/requirements.txt && \
    rm -rf /root/.cache/pip && \
    wget -q https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/v0.4.27/grpc_health_probe-linux-amd64 && \
    chmod +x grpc_health_probe-linux-amd64 && \
    mv grpc_health_probe-linux-amd64 /usr/local/bin/grpc_health_probe && \
    rm -rf /var/lib/apt/lists/*

EXPOSE 1235
HEALTHCHECK --interval=30s --timeout=3s CMD /usr/local/bin/grpc_health_probe -addr=[::]:1235 || exit 1
RUN adduser --disabled-password --gecos '' petnetuser
USER petnetuser ENTRYPOINT ["python", "main.py"]