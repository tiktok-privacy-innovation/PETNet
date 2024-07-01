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
import os
from concurrent.futures import ThreadPoolExecutor
import logging
import logging.config
import time

import grpc

from exceptions import ServerInternalError
from pb2.simple_pb2_grpc import add_SimpleRequestServerServicer_to_server
from pb2.health_pb2_grpc import add_HealthServicer_to_server
from server.health_servicer import HealthServicer
from server.simple_servicer import SimpleRequestServerServicer
import settings
from utils.log_utils import log_worker


def set_logging():
    if "async" in settings.LOGGING_MODE:
        file_handler = logging.FileHandler(settings.DEFAULT_LOGGING_FILE)
        formatter = logging.Formatter(settings.DEFAULT_LOGGING_FORMAT)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(settings.LOGGING_LEVEL)
        log_worker.add_handler(file_handler)
        log_worker.start()
        logging.config.dictConfig(settings.PERFORMANCE_LOG_CONFIG)
    else:
        logging.config.dictConfig(settings.DEFAULT_LOG_CONFIG)


def register_servicer(grpc_server):
    # Register the servicer with the server
    add_SimpleRequestServerServicer_to_server(SimpleRequestServerServicer(), grpc_server)
    add_HealthServicer_to_server(HealthServicer(), grpc_server)


def start_server(grpc_server):
    if settings.SERVER_KEY and settings.SERVER_CERTIFICATE:
        # Load SSL/TLS credentials
        credentials = grpc.ssl_server_credentials(((settings.SERVER_KEY, settings.SERVER_CERTIFICATE),))
        # Start the gRPC server with the credentials
        grpc_server.add_secure_port("[::]:1235", credentials)
        logging.info("Set credentials success")
    else:
        if settings.ENV.lower().startswith("prod"):
            # If certificates are not found in a production environment, log an error and shut down
            logging.error("Certificates not found, shutting down...")
            raise ServerInternalError("Certificates not found")
        else:
            # If certificates are not found in a non-production environment, log a warning
            logging.warning("Certificates not found, gRPC server running in insecure mode")
            grpc_server.add_insecure_port("[::]:1235")
    register_servicer(grpc_server)
    grpc_server.start()


if __name__ == '__main__':
    set_logging()
    server = grpc.server(ThreadPoolExecutor(max_workers=os.cpu_count()))
    try:
        start_server(server)
        # Wait for a shutdown signal
        try:
            while True:
                time.sleep(86400)
        except:
            server.stop(0)
    except:
        logging.exception("Failed to start server")
        server.stop(0)
    finally:
        log_worker.close()
