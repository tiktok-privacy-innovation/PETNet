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
from enum import Enum
import json
import typing as t
from pathlib import Path

from exceptions import ServerNoAvailableConnection
import settings


class Connection:
    def __init__(self, connection: t.Dict = None):
        # Initialize a Connection object with type, url, certificates, and whitelist
        self.type: "ConnectionType" = ConnectionType(int(connection["type"]))
        self.url: str = connection["url"]
        self.certificates: str = connection.get("certificates")
        self.whitelist: t.List[str] = connection.get("whitelist", ["*"])  # accepted parties


class ConnectionType(Enum):
    # Enum for connection types
    OTHER = 0
    DIRECT = 1
    PROXY = 2


class Node:
    def __init__(self, party, config: t.List[t.Dict]):
        # Initialize a Node object with nid, connections, and description
        self.party: str = party
        self.connections: t.List["Connection"] = [Connection(v) for v in config]


class NodeManager:
    # Class to manage nodes
    def __init__(self):
        # Initialize a dictionary to store nodes
        self._nodes: t.Dict[str, "Node"] = dict()

    def load_from_json(self):
        # Load nodes from a json file
        configfile = Path(settings.CONFIG_FILE_PATH)
        if configfile.exists() and configfile.is_file():
            address_config: t.Dict = json.loads(configfile.read_text())
            for k, v in address_config.items():
                self._nodes[k] = Node(k, v["petnet"])
        return self

    def get_connection(self, receiver_id: str) -> "Connection":
        # Get the connection for a receiver
        assert receiver_id in self._nodes and receiver_id != settings.PARTY, ServerNoAvailableConnection(receiver_id)
        node: "Node" = self._nodes[receiver_id]
        for connection in node.connections:
            if settings.PARTY in connection.whitelist or "*" in connection.whitelist:
                return connection
        raise ServerNoAvailableConnection(receiver_id)

    def get_remote_connections(self, connection_type: "ConnectionType") -> t.Dict[str, "Connection"]:
        # Get all remote connections of a certain type
        ret = {}
        for nid, node in self._nodes.items():
            if nid == settings.PARTY:
                continue
            for connection in node.connections:
                if settings.PARTY in connection.whitelist and connection.type == connection_type:
                    ret[nid] = connection
        return ret


# Create a NodeManager and load nodes information from a json file
node_manager: "NodeManager" = NodeManager().load_from_json()
