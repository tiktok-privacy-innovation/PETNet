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
from server.connection_pool import ConnectionPool
from constants import TimeDuration
from pb2.simple_pb2 import ClientSimpleSendRequest, ClientSimpleRecvRequest, ServerSimpleSendRequest, Response
from pb2.simple_pb2_grpc import SimpleRequestServerServicer, SimpleRequestServerStub
from exceptions import RedisError
from utils.redis_utils import redis_client
from utils.decorators import handle_exceptions


def create_simple_error_response(error_code, error_msg):
    # Function to create a simple error response
    return Response(success=False, error_msg=error_msg, error_code=error_code)


class SimpleRequestServerServicer(SimpleRequestServerServicer):
    # This class inherits from SimpleRequestServerServicer and implements its methods
    # A connection pool is created for the servicer
    connection_pool = ConnectionPool()

    @handle_exceptions(create_simple_error_response)
    def ClientSimpleSend(self, request: "ClientSimpleSendRequest", context) -> "Response":
        # ClientSimpleSend method implementation
        # It gets a channel from the connection pool and uses it to send a request to the server
        channel = self.connection_pool.get_channel(request.receiver_id)
        stub = SimpleRequestServerStub(channel)
        server_request = ServerSimpleSendRequest(message_id=request.message_id, payload=request.payload)
        return stub.ServerSimpleSend(server_request)

    @handle_exceptions(create_simple_error_response)
    def ClientSimpleRecv(self, request: "ClientSimpleRecvRequest", context) -> "Response":
        # ClientSimpleRecv method implementation
        # It gets a message from Redis and returns it. If the message does not exist, it returns an error
        message_id = request.message_id
        payload = redis_client.get(message_id) or b""
        return Response(success=True, payload=payload)

    @handle_exceptions(create_simple_error_response)
    def ServerSimpleSend(self, request: "ServerSimpleSendRequest", context) -> "Response":
        # ServerSimpleSend method implementation
        # It saves a message to Redis and returns a success response. If the save fails, it raises an error
        message_id, payload = request.message_id, request.payload
        # exchanged data may be cleaned by redis after expiration
        ret = redis_client.set(message_id, payload, ex=TimeDuration.HOUR)
        if not ret:
            raise RedisError(f"save message fail: {message_id}")
        return Response(success=True)
