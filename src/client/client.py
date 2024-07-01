# Copyright 2024 TikTok Pte. Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import functools
import logging
import time

import grpc
from grpc import RpcError
import snappy

from pb2.health_pb2 import HealthCheckRequest, HealthCheckResponse
from pb2.health_pb2_grpc import HealthStub
from pb2.simple_pb2 import ClientSimpleSendRequest, ClientSimpleRecvRequest, Response
from pb2.simple_pb2_grpc import SimpleRequestServerStub


logging.basicConfig(level=logging.INFO)


def log_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        try:
            result = func(*args, **kwargs)
            time_cost = round((time.time() - start) * 1000, 2)
            logging.debug(f"{func.__name__}|{time_cost}ms")
            return result
        except Exception:
            args_str = ", ".join(map(str, args))[:100]
            kwargs_str = ", ".join(f"{k}={v}" for k, v in kwargs.items())[:100]
            logging.exception(f"|{args_str}|{kwargs_str}|")
    return wrapper


class PETNetClient:
    def __init__(
            self,
            target_party: str,
            target_url: str = "localhost:1235",
            ca_certificates=None,
            client_key=None,
            client_certificates=None
    ):
        self._target_party = target_party
        self._target_url = target_url
        self._credentials = None
        if ca_certificates and client_key and client_certificates:
            self._credentials = grpc.ssl_channel_credentials(
                root_certificates=ca_certificates,
                private_key=client_key,
                certificate_chain=client_certificates
            )
        self._channel = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()

    def close(self):
        if self._channel:
            self._channel.close()
        self._channel = None

    def _setup_channel(self):
        if self._credentials:
            channel = grpc.secure_channel(
                target=self._target_url,
                credentials=self._credentials
            )
        else:
            channel = grpc.insecure_channel(
                target=self._target_url
            )
        return channel

    @property
    def channel(self):
        if self._channel is None:
            self._channel = self._setup_channel()
        return self._channel

    def _compress(self, payload: bytes):
        return snappy.compress(payload)

    def _decompress(self, payload: bytes):
        return snappy.decompress(payload)

    @log_decorator
    def call(self, stub_class, request, method: str, max_retry: int = 3):
        stub = stub_class(self.channel)
        if not hasattr(stub, method):
            raise ValueError(f"{method} is not a method of {stub_class.__name__}")
        for _ in range(max_retry):
            try:
                return getattr(stub, method)(request)
            except RpcError as e:
                logging.error(f"RPC error occurred: {e}")
                time.sleep(0.001)
            except Exception:
                raise
        else:
            raise RpcError(f"Failed to call {method} after {max_retry} attempts")

    def health_check(self) -> str:
        request = HealthCheckRequest(service="")
        response: "HealthCheckResponse" = self.call(
            stub_class=HealthStub,
            request=request,
            method="Check"
        )
        return response.status

    def send(self, receiver: str, message_id: str, payload: bytes) -> bool:
        request = ClientSimpleSendRequest(
            receiver_id=receiver,
            message_id=message_id,
            payload=self._compress(payload)
        )
        response: "Response" = self.call(
            SimpleRequestServerStub,
            request,
            "ClientSimpleSend"
        )
        return response.success

    def recv(self, message_id: str) -> bytes:
        request = ClientSimpleRecvRequest(message_id=message_id)
        response = self.call(
            SimpleRequestServerStub,
            request,
            "ClientSimpleRecv"
        )
        payload = response.payload
        return self._decompress(response.payload) if payload else payload


if __name__ == '__main__':
    client = PETNetClient("my_server")
    client.health_check()

    num = 10
    payload = b"hello" * 1024 * 1000

    mid = f"m_test"
    start = time.time()
    for i in range(num):
        mid = f"m_test_{i}"
        ret = client.send(receiver="party_b", message_id=mid, payload=payload)
    total = round((time.time() - start) * 1000, 2)
    average = round(total / num, 2)
    print(f"total: {total}ms, average: {average}ms")

    start = time.time()
    for i in range(num):
        mid = f"m_test_{i}"
        payload_1 = client.recv(message_id=mid)
    total = round((time.time() - start) * 1000, 2)
    average = round(total / num, 2)
    print(f"total: {total}ms, average: {average}ms")

    assert payload_1 == payload
