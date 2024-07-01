# PETNet: A Lightweight and Production-Ready Data Proxy Gateway for Privacy Computing


PETNet is a lightweight data proxy gateway designed for secure multi-party computation scenarios. It enables real-time data exchange among various parties. It features robust fault recovery and fault tolerance capabilities, making it a production-ready privacy computing data proxy gateway.

PETNet provides a gRPC API interface for client-side interactions, simplifying communication with the service. It prioritizes security with robust access control mechanisms, ensuring only authorized parties can access relevant data and services.

With its high extensibility, PETNet can be adapted to support different network protocols, making it versatile for various network environments and use cases. It has the potential ability for horizontal scaling and load balancing, ensuring service stability and availability.

The latest version of [PETAce](https://github.com/tiktok-privacy-innovation/PETAce) has integrated support for the PETNet gateway, offering a more powerful and flexible solution for secure multi-party computation scenarios.


## Getting Started


### Requirements

| System | Toolchain                     |
|--------|-------------------------------|
| Linux  | Python (==3.9), pip(>=23.3.1) |


### How to Build

To build PETNet as a docker image, execute:

```bash
docker build -t petnet:latest . -f docker/Dockerfile
```

### Configuration


#### Party Information Config

A config file is required to record all the parties and their network configuration:

```json
{
  "party_a": {
    "petnet": [{
      "type": 1,
      "url":"${ip_address_a}:1235"
    }]
  },
  "party_b": {
    "petnet": [{
      "type": 1,
      "url":"${ip_address_b}:1235"
    }]
  }
}
```


#### Environment Variables

| Environment Variables | Required | Description                           | Default                   |
|-----------------------|----------|---------------------------------------|---------------------------|
| `PARTY`               | Yes      | The party identifier                  | None                      |
| `LOGGING_MODE`        | No       | The logging style for the application | "default"                 |
| `LOGGING_LEVEL`       | No       | The logging level for the application | "INFO"                    |
| `CONFIG_FILE_PATH`    | No       | The path to the configuration file    | "/app/parties/party.json" |
| `REDIS_URL`           | No       | The URL to connect to Redis           | "redis://redis:6379"      |
| `PEM_PATH`            | No       | The path to the certificate file      | "/app/certs"              |
| `ENV`                 | No       | The environment the application is in | ""                        |


#### Docker Compose Config
Then, you need a docker-compose.yml to deploy PETNet. Here's an example:

```yaml
version: '3'

services:
  petnet:
    image: petnet:latest
    environment:
      - PARTY=party_a
    volumes:
      - ./parties:/app/parties
      - ./certes:/app/certs
    ports:
      - "1235:1235"
    depends_on:
      - redis

  redis:
    image: redis:6
    volumes:
      - redis-data:/data

volumes:
  redis-data:
```

### How to Run

To run the Docker container using docker-compose:
```bash
docker-compose up -d
```


#### Enable TLS Authentication on Production

In this gRPC service, `PEM_PATH` is an important environment variable that is used to specify the location of the TLS (Transport Layer Security) certificates. TLS certificates are used to provide security protection when transmitting data over the network, preventing data from being stolen or tampered with.

When you set the `PEM_PATH` environment variable, the gRPC service will read the TLS certificates from the specified path. These certificates are used for mutual TLS authentication, meaning that both the client and the server need to provide certificates, and both parties will verify each other's certificates. This method can ensure the security of data during transmission and can confirm the identity of the communication parties.

In mutual TLS authentication, both the server and the client need to provide three parameters: a private key (`private_key`), a certificate chain (`certificate_chain`), and root certificates (`root_certificates`). The private key and certificate chain are specific to each server and client, while the root certificates are usually issued by the same trusted certificate authority (CA) and are used to verify each other's certificates.

You need to store the private key and certificate chain as files in your `PEM_PATH` and name them `server.key` and `server.crt` respectively. Please ensure that you have correctly set `PEM_PATH` and that the specified path contains valid TLS certificates. If the gRPC service cannot find or read the certificates, it will not be able to start or process requests correctly.

When the gRPC service starts, it will attempt to load certificates from `PEM_PATH`. If no certificate files are found, the gRPC service will start in insecure mode and output a warning log. We prohibit the use of insecure mode in production. If you set the `ENV` variable to "prod", the gRPC server will throw an error and exit.

If the Petnet client needs to establish a connection with a server that has enabled TLS authentication, you need to configure the client's root certificate information in the server's `party.json` file. This allows the server to verify the client's identity during the mutual TLS authentication process, ensuring a secure connection.

```json
{
  "party_a": {
    "petnet": [{
      "type": 1,
      "url":"${ip_address_a}:1235",
      "certificates": "${root certificates of party_a}"
    }]
  },
  "party_b": {
    "petnet": [{
      "type": 1,
      "url":"${ip_address_b}:1235",
      "certificates": "${root certificates of party_b}"
    }]
  }
}
```


## User Manual


### Service Definition

The service uses gRPC for communication. 
- For proto files, see [proto files](protos).
- For pb files, see [pb files](src/pb2).


### gRPC User APIs


#### ClientSimpleSend

ClientSimpleSend is a unary RPC method that allows the client to send data to a local PETNet server, the local server then transfer the data to a remote PETNet server, according to the receiver id.

**Request:**

| Field       | Type   | Description            |
|-------------|--------|------------------------|
| message_id  | string | The ID of the message  |
| receiver_id | string | The ID of the receiver |
| payload     | bytes  | The payload to send    |

**Response:**

| Field      | Type              | Description                                         |
|------------|-------------------|-----------------------------------------------------|
| success    | bool              | Whether the operation was successful                |
| payload    | bytes (optional)  | Empty for send method                               |
| error_code | int32 (optional)  | The error code if the operation was unsuccessful    |
| error_msg  | string (optional) | The error message if the operation was unsuccessful |


#### ClientSimpleRecv

ClientSimpleRecv is a unary RPC method that allows the client to receive data from the local PETNet server.

**Request:**

| Field      | Type   | Description           |
|------------|--------|-----------------------|
| message_id | string | The ID of the message |

**Response:**

| Field      | Type              | Description                                         |
|------------|-------------------|-----------------------------------------------------|
| success    | bool              | Whether the operation was successful                |
| payload    | bytes (optional)  | The data to receive                                 |
| error_code | int32 (optional)  | The error code if the operation was unsuccessful    |
| error_msg  | string (optional) | The error message if the operation was unsuccessful |


### Examples

Here is an example to show how to send and receive data between two parties through PETNet. You can also find a more complete python client example at [client example](/src/client/client.py).

```python

import grpc

from pb2.simple_pb2 import ClientSimpleSendRequest, ClientSimpleRecvRequest
from pb2.simple_pb2_grpc import SimpleRequestServerStub


target_url = "localhost:1235"
message_id = "your_message_id"
receiver = "your_target_receiver"

# Create a gRPC channel
channel = grpc.insecure_channel(target_url)

# Create a stub (client)
stub = SimpleRequestServerStub(channel)

# Send a message
send_request = ClientSimpleSendRequest(receiver_id=receiver, message_id=message_id, payload=b"hello!")
send_response = stub.ClientSimpleSend(send_request)
print(f"Send success: {send_response.success}")

# Receive a message
recv_request = ClientSimpleRecvRequest(message_id=message_id)
recv_response = stub.ClientSimpleRecv(recv_request)
print(f"Received payload: {recv_response.payload}")

```


### Trouble Shooting

If you encounter problems while using the PETNet service, you can follow the steps below for self-check:


#### 1. Check Image Version

Ensure that the PETNet Docker image you are using is up-to-date. You can view the local Docker images by running the following command:

```bash
docker images
```

In the output list, find the PETNet image, and check if its version tag matches the version you expect.


#### 2. Check Configuration Files

Check if your configuration files (e.g., `party.json`) are correct. Ensure all keys and values are as expected, with no spelling errors or missing items. Pay particular attention to the following:

- All URLs are correct, with no spelling errors or missing parts.
- All certificates (if TLS authentication is used) exist and the paths are correct.
- All environment variables are set correctly.


#### 3. Check Docker Compose Configuration

Check if your `docker-compose.yml` file is correct. Ensure all services, environment variables, volumes, and port mappings are configured correctly. Pay particular attention to the following:

- All service names and image names are correct.
- All environment variables are set correctly.
- All volumes and port mappings are correct.


#### 4. Check if Containers are Running Normally

Run the following command to view the status of Docker containers:

```bash
docker ps -a
```

In the output list, find the PETNet container, and check if its status is "Up". If the container has not started normally, you can run the following command to view the container logs to help identify the problem:

```bash
docker logs <container_id>
```

If you have mounted the log directory on your host, you can also view the application logs via:

```bash
cd ${PATH_TO_YOUR_LOG_DIRECTORY}
cat petnet.log
```


#### 5. Check Error Logs

If the PETNet service encounters an error, it will output error information in the logs. You can determine the cause of the problem by checking the logs. Error logs usually contain an error code and an error message, and you can refer to the "Error Codes" section of this manual to understand the meaning of these error codes. 
In case of an error, the PETNet service will return one of the following error codes. If you see an unknown error code in the logs, or cannot determine the cause of the problem, you can contact our support team for help.


| Code  | Error Class                 | Description                        |
|-------|-----------------------------|------------------------------------|
| 10001 | UnknownError                | Unknown error                      |
| 10002 | RedisError                  | Redis error                        |
| 20001 | ClientInternalError         | Client internal error              |
| 30001 | ServerInternalError         | Server internal error              |
| 30002 | ServerDataNotReady          | Server data not ready              |
| 30003 | ServerNoAvailableConnection | Server has no available connection |

Please refer to the error message for more details about the specific error. If you encounter an error that is not listed here, please contact the support team, or report your bug to the community.


## Contribution

Please check [Contributing](CONTRIBUTING.md) for more details.


## Code of Conduct

Please check [Code of Conduct](CODE_OF_CONDUCT.md) for more details.


## License

This project is licensed under the [Apache-2.0 License](LICENSE).


## Disclaimers

This software is not an officially supported product of TikTok. It is provided as-is, without any guarantees or warranties, whether express or implied.
