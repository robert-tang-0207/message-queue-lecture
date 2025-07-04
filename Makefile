.PHONY: help install kafka-producer kafka-consumer rabbitmq-producer rabbitmq-consumer clean

# Default target
help:
	@echo "Message Queue Demo Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  install             - Install required dependencies"
	@echo "  kafka-producer      - Run Kafka producer"
	@echo "  kafka-consumer      - Run Kafka consumer"
	@echo "  rabbitmq-producer   - Run RabbitMQ producer"
	@echo "  rabbitmq-consumer   - Run RabbitMQ consumer"
	@echo "  clean               - Remove Python cache files"
	@echo ""
	@echo "Note: Make sure Kafka and RabbitMQ servers are running before starting producers/consumers"

# Install dependencies
install:
	@echo "Installing required Python packages..."
	pip install confluent-kafka pika tk

# Kafka targets
kafka-producer:
	@echo "Starting Kafka producer..."
	cd kafka/producer && python3 producer.py

kafka-consumer:
	@echo "Starting Kafka consumer..."
	cd kafka/consumer && python3 consumer.py

# RabbitMQ targets
rabbitmq-producer:
	@echo "Starting RabbitMQ producer..."
	cd rabbitmq/producer && python3 producer.py

rabbitmq-consumer:
	@echo "Starting RabbitMQ consumer..."
	cd rabbitmq/consumer && python3 consumer.py

# Clean up
clean:
	@echo "Cleaning up Python cache files..."
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
