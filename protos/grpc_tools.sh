#!/usr/bin/env bash
python3 -m grpc_tools.protoc -I. --python_out=. --mypy_out=. --grpc_python_out=. ./*.proto
