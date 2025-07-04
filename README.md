# Message Queue Lecture - Example Projects

This repository contains example projects demonstrating the usage of popular message queue systems: Apache Kafka and RabbitMQ. The examples are implemented in Python with GUI interfaces to visualize the producer-consumer pattern in action.

## Project Structure

```
message-queue-lecture/
├── config.json           # Configuration for both Kafka and RabbitMQ
├── Makefile              # Commands to run the applications
├── PRESENTATION.md       # Lecture presentation in Markdown format
├── images/               # Images used in the presentation
├── kafka/
│   ├── producer/         # Kafka producer application
│   │   └── producer.py
│   └── consumer/         # Kafka consumer application
│       └── consumer.py
└── rabbitmq/
    ├── producer/         # RabbitMQ producer application
    │   └── producer.py
    └── consumer/         # RabbitMQ consumer application
        └── consumer.py
```

## Prerequisites

Before running the examples, make sure you have the following installed:

1. **Python 3.6+**
2. **Apache Kafka** - A running Kafka broker on localhost:9092
3. **RabbitMQ** - A running RabbitMQ server on localhost
4. **Python packages**: confluent-kafka, pika, and tkinter

### Installing Kafka (Quick Start)

```bash
# Download Kafka
wget https://downloads.apache.org/kafka/3.5.1/kafka_2.13-3.5.1.tgz
tar -xzf kafka_2.13-3.5.1.tgz
cd kafka_2.13-3.5.1

# Start ZooKeeper
bin/zookeeper-server-start.sh config/zookeeper.properties

# In another terminal, start Kafka
bin/kafka-server-start.sh config/server.properties

# Create the topic used in the examples
bin/kafka-topics.sh --create --topic message_queue_demo --bootstrap-server localhost:9092
```

### Installing RabbitMQ (Quick Start)

```bash
# For Ubuntu/Debian
sudo apt-get install rabbitmq-server

# Start RabbitMQ
sudo service rabbitmq-server start

# Enable management plugin (optional but recommended)
sudo rabbitmq-plugins enable rabbitmq_management
```

## Installation

Clone this repository and install the required Python packages:

```bash
git clone https://github.com/robert-tang-0207/message-queue-lecture.git
cd message-queue-lecture
make install
```

## Running the Examples

The project includes a Makefile to easily run each component:

```bash
# Run Kafka producer
make kafka-producer

# Run Kafka consumer
make kafka-consumer

# Run RabbitMQ producer
make rabbitmq-producer

# Run RabbitMQ consumer
make rabbitmq-consumer
```

You can run multiple instances of each component by opening multiple terminals and running the same command. This allows you to see how multiple producers and consumers interact with the message queue.

## Features

### Producer Applications

- Send messages to Kafka topics or RabbitMQ queues
- Auto-send mode to generate messages automatically (1 per second)
- Real-time logging of sent messages
- Unique producer ID for each instance

### Consumer Applications

- Receive and display messages from Kafka topics or RabbitMQ queues
- Pause/resume consumption
- Clear log functionality
- Real-time display of received messages
- Unique consumer ID for each instance

## Configuration

The `config.json` file contains settings for both messaging systems:

```json
{
  "kafka": {
    "bootstrap_servers": "localhost:9092",
    "topic": "message_queue_demo",
    "group_id": "demo_group"
  },
  "rabbitmq": {
    "host": "localhost",
    "queue": "message_queue_demo"
  }
}
```

You can modify this file to change connection settings or queue/topic names.

## Key Differences Between Kafka and RabbitMQ

These examples demonstrate some fundamental differences between Kafka and RabbitMQ:

1. **Connection Model**: 
   - Kafka uses a pull-based model where consumers poll for messages
   - RabbitMQ uses a push-based model with callbacks

2. **Message Consumption**:
   - Kafka maintains consumer offsets, allowing multiple consumers to read the same messages
   - RabbitMQ typically delivers each message to only one consumer in a group

3. **Implementation Complexity**:
   - Kafka requires more configuration and has a steeper learning curve
   - RabbitMQ offers a simpler API and is easier to get started with

## Presentation

The repository includes a comprehensive presentation (`PRESENTATION.md`) about message queues, covering:

- Basic concepts of messaging queues
- Types of messaging patterns (P2P, Pub/Sub)
- Detailed overview of RabbitMQ and Kafka
- AWS messaging services
- Example use cases

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Robert Tang, July 2025
