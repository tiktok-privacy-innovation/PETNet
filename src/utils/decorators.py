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

from exceptions import PETNetError, ServerInternalError


def handle_exceptions(error_response_creator):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                start = time.time()
                # Convert args and kwargs to a string representation

                result = func(*args, **kwargs)

                time_cost = round((time.time() - start) * 1000, 2)
                # Log the result of the function
                logging.debug(f"{func.__name__}|{result.success}|{time_cost}ms")
                return result
            except PETNetError as e:
                logging.exception(f"server error [{e.code}]: {e.message}")
                return error_response_creator(e.code, e.message)
            except Exception as e:
                error = ServerInternalError(str(e))
                logging.exception(f"server error [{error.code}]: {error.message}")
                return error_response_creator(error.code, str(error))
        return wrapper
    return decorator
