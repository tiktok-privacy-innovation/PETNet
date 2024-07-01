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
import platform
from pathlib import Path

from utils.log_utils import QueueHandler, log_queue

LOGGING_MODE = os.environ.get("LOGGING_STYLE", "default")
DEFAULT_LOGGING_FILE = "petnet.log" if platform.system().lower() == "darwin" else "/app/logs/petnet.log"
DEFAULT_LOGGING_FORMAT = "%(asctime)s %(levelname)s %(message)s"
LOGGING_LEVEL = os.environ.get("LOGGING_LEVEL", "INFO")

DEFAULT_LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": DEFAULT_LOGGING_FORMAT
        }
    },
    "handlers": {
        "console": {
            "level": LOGGING_LEVEL,
            "class": "logging.StreamHandler",  # Log to the console
            "formatter": "default",  # Use the default format
        },
        "file": {
            "level": LOGGING_LEVEL,
            "class": "logging.FileHandler",  # Log to a file
            "filename": DEFAULT_LOGGING_FILE,
            "formatter": "default"  # Use the default format
        }
    },
    "root": {
        "handlers": ["console", "file"],
        "level": LOGGING_LEVEL
    }
}

PERFORMANCE_LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "handlers": {
        "queue": {
            "()": QueueHandler,  # handle logging in an async way
            "queue_ins": log_queue,
        }
    },
    "root": {
        "handlers": ["queue"],
        "level": LOGGING_LEVEL
    }
}

# node info
PARTY = os.environ.get("PARTY")
CONFIG_FILE_PATH = os.environ.get("CONFIG_FILE_PATH", "/app/parties/party.json")
# redis
REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379")
# certs
SERVER_CERTIFICATE = SERVER_KEY = ""
certificate_path = Path(os.environ.get("PEM_PATH", "/app/certs"))
if (certificate_path / "server.crt").exists():
    SERVER_CERTIFICATE = (certificate_path / "server.crt").read_bytes()
if (certificate_path / "server.key").exists():
    SERVER_KEY = (certificate_path / "server.key").read_bytes()

ENV = os.environ.get("ENV", "")
