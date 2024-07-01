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
from pb2.health_pb2_grpc import HealthServicer
from pb2.health_pb2 import HealthCheckResponse


class HealthServicer(HealthServicer):
    def Check(self, request, context):
        # Implement your logic here
        return HealthCheckResponse(status=HealthCheckResponse.SERVING)

    def Watch(self, request, context):
        # This is for streaming health check. You can ignore this if you don't need streaming
        return
