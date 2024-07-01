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
import logging
import queue
import threading


class QueueHandler(logging.Handler):
    def __init__(self, queue_ins):
        super().__init__()
        self.queue_ins = queue_ins

    def emit(self, record):
        self.queue_ins.put(record)


class LogWorker(threading.Thread):
    def __init__(self, queue_ins):
        super().__init__(daemon=True)
        self.queue_ins = queue_ins
        self.handlers = []

    def add_handler(self, handler):
        self.handlers.append(handler)

    def close(self):
        self.queue_ins.put(None)
        if self.is_alive():
            self.join()

    def run(self):
        while True:
            record = self.queue_ins.get()
            if record is None:
                break
            for handler in self.handlers:
                handler.emit(record)


log_queue = queue.Queue(-1)
log_worker = LogWorker(log_queue)
