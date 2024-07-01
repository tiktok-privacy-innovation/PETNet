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
import time

import grpc

from server.node_manager import node_manager
import settings
from utils.singleton import MySingleton


class ConnectionPool(MySingleton):
    def __init__(self, max_idle_time=60):
        # A dictionary to store all grpc channels
        self.grpc_channels = {}
        # Maximum time a channel can stay idle before it is closed
        self.max_idle_time = max_idle_time

    def get_channel(self, receiver_id: str):
        now = time.time()
        # Get the connection details for the receiver
        connection = node_manager.get_connection(receiver_id)
        url, certificates = connection.url, connection.certificates
        # If a channel does not exist for this receiver, create one
        if receiver_id not in self.grpc_channels:
            if not certificates:
                # Create an insecure channel if no certificates are provided
                self.grpc_channels[receiver_id] = {"channel": grpc.insecure_channel(url), "last_used": now}
            else:
                # Create a secure channel if certificates are provided
                credentials = grpc.ssl_channel_credentials(
                    private_key=settings.SERVER_KEY,
                    certificate_chain=settings.SERVER_CERTIFICATE,
                    root_certificates=certificates
                )
                self.grpc_channels[receiver_id] = {
                    "channel": grpc.secure_channel(url, credentials),
                    "last_used": now
                }
        else:
            # Update the last used time for this channel
            self.grpc_channels[receiver_id]["last_used"] = now
        # Close channels that have been idle for too long
        close_idle_channels(self)
        # Return the channel for this receiver
        return self.grpc_channels[receiver_id]["channel"]


def close_idle_channels(connection_pool: "ConnectionPool"):
    now = time.time()
    # Close channels that have been idle for too long
    for k in list(connection_pool.grpc_channels.keys()):  # Create a copy of the keys
        info = connection_pool.grpc_channels[k]
        # If the channel has been idle for more than the max idle time, close it
        if now - info["last_used"] > connection_pool.max_idle_time:
            info["channel"].close()
            # Remove this channel from the pool
            del connection_pool.grpc_channels[k]
