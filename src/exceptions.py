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


class PETNetError(Exception):
    code = None
    message = None

    def __init__(self, message: str = None):
        if message is not None:
            self.message = self.message + ": " + message

    def __str__(self):
        return self.message

    def __repr__(self):
        return "<%s>" % self.__class__.__name__


class UnknownError(PETNetError):
    code = 10001
    message = "unknown error"


class RedisError(PETNetError):
    code = 10002
    message = "redis error"


class ClientInternalError(PETNetError):
    code = 20001
    message = "client internal error"


class ServerInternalError(PETNetError):
    code = 30001
    message = "server internal error"


class ServerDataNotReady(PETNetError):
    code = 30002
    message = "server data not ready"


class ServerNoAvailableConnection(PETNetError):
    code = 30003
    message = "server has available connection"
