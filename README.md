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

# Create the topic used in the examples with 2 partitions
bin/kafka-topics.sh --create --topic message_queue_demo --partitions 2 --replication-factor 1 --bootstrap-server localhost:9092

# Verify the topic was created with 2 partitions
bin/kafka-topics.sh --describe --topic message_queue_demo --bootstrap-server localhost:9092
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

# Run Kafka consumer with a specific group ID
make kafka-consumer GROUP_ID=my-group

# Run Kafka consumer with a specific group ID and partition
make kafka-consumer GROUP_ID=my-group PARTITION=0

# Run RabbitMQ producer
make rabbitmq-producer

# Run RabbitMQ producer with specific queue and exchange type
make rabbitmq-producer QUEUE=my_queue EXCHANGE_TYPE=direct

# Run RabbitMQ consumer
make rabbitmq-consumer

# Run RabbitMQ consumer with specific queue and exchange type
make rabbitmq-consumer QUEUE=my_queue EXCHANGE_TYPE=fanout
```

You can run multiple instances of each component by opening multiple terminals and running the same command. This allows you to see how multiple producers and consumers interact with the message queue.

### Kafka Demo Command

The project includes a special `kafka-demo` command that demonstrates Kafka's partitioning and consumer group behavior:

```bash
make kafka-demo
```

This command automatically launches:

1. **Two Kafka producers**: Each randomly sends messages to either partition 0 or partition 1
2. **Four Kafka consumers**:
   - Two consumers in Group A (one assigned to partition 0, one to partition 1)
   - Two consumers in Group B (one assigned to partition 0, one to partition 1)

#### What the Demo Shows

This demo illustrates several key Kafka concepts:

1. **Partitioning**: Messages are distributed across two partitions (0 and 1)
2. **Partition Assignment**: Each consumer is explicitly assigned to a specific partition
3. **Consumer Groups**: Two separate consumer groups (A and B) receive the same messages independently
4. **Parallel Processing**: Within each group, consumers process different partitions simultaneously

#### Expected Behavior

When you run the demo and send messages from the producers:

- Messages sent to partition 0 will appear in:
  - Group A's partition 0 consumer
  - Group B's partition 0 consumer
  
- Messages sent to partition 1 will appear in:
  - Group A's partition 1 consumer
  - Group B's partition 1 consumer

This demonstrates how Kafka enables:
- Horizontal scaling (multiple consumers in a group process different partitions)
- Multiple independent consumer applications (different groups process the same data)

### RabbitMQ Demo Commands

The project includes separate commands to demonstrate each RabbitMQ exchange type:

```bash
# Run the Direct Exchange demo
make rabbitmq-demo-direct

# Run the Topic Exchange demo
make rabbitmq-demo-topic

# Run the Fanout Exchange demo
make rabbitmq-demo-fanout

# Run all three demos at once
make rabbitmq-demo
```

These commands launch:

1. **Direct Exchange Demo** (`rabbitmq-demo-direct`):
   - One producer sending to a direct exchange with queue `direct_queue`
   - One consumer receiving from `direct_queue`

2. **Topic Exchange Demo** (`rabbitmq-demo-topic`):
   - One producer sending to a topic exchange with queue `topic_queue`
   - Two consumers:
     - One consumer with matching queue name `topic_queue` (will receive messages)
     - One consumer with different queue name `different_topic_queue` (won't receive messages)

3. **Fanout Exchange Demo** (`rabbitmq-demo-fanout`):
   - One producer sending to a fanout exchange with queue `fanout_queue1`
   - Two consumers: one receiving from `fanout_queue1` and another from `fanout_queue2`

#### RabbitMQ Exchange Types

The demo illustrates three key RabbitMQ exchange types:

1. **Direct Exchange**: Messages are routed to queues based on an exact match of the routing key
   - Good for direct point-to-point messaging

2. **Topic Exchange**: Messages are routed to queues based on pattern matching of the routing key
   - Good for selective multicast messaging

3. **Fanout Exchange**: Messages are broadcast to all bound queues regardless of routing key
   - Good for broadcast messaging

#### Expected Behavior

When you run the demo and send messages from the producers:

- Messages sent by the Direct Producer will only be received by the Direct Consumer
- Messages sent by the Topic Producer will only be received by the Topic Consumer
- Messages sent by the Fanout Producer will be received by BOTH Fanout Consumers

This demonstrates how RabbitMQ's exchange types enable different messaging patterns.

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
