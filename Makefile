.PHONY: help install kafka-producer kafka-consumer rabbitmq-producer rabbitmq-consumer clean

# Default target
help:
	@echo "Message Queue Demo Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  install             - Install required dependencies"
	@echo "  kafka-producer      - Run Kafka producer"
	@echo "  kafka-consumer      - Run Kafka consumer"
	@echo "  kafka-demo          - Run Kafka demo (2 producers, 4 consumers in 2 groups)"
	@echo "  rabbitmq-producer   - Run RabbitMQ producer"
	@echo "  rabbitmq-consumer   - Run RabbitMQ consumer"
	@echo "  clean               - Remove Python cache files"
	@echo ""
	@echo "Note: Make sure Kafka and RabbitMQ servers are running before starting producers/consumers"

# Install dependencies
install:
	@echo "Installing required Python packages..."
	@echo "Note: You may need sudo privileges for some of these commands"
	@echo "Installing tkinter (requires sudo)..."
	sudo apt-get update && sudo apt-get install -y python3-tk
	@echo "Installing Python packages..."
	pip install confluent-kafka pika

# Kafka targets
kafka-producer:
	@echo "Starting Kafka producer..."
	cd kafka/producer && python3 producer.py

kafka-consumer:
	@echo "Starting Kafka consumer..."
	@if [ -z "$(GROUP_ID)" ]; then \
		echo "No GROUP_ID specified, using random group ID"; \
		cd kafka/consumer && python3 consumer.py; \
	elif [ -z "$(PARTITION)" ]; then \
		echo "Using GROUP_ID: $(GROUP_ID)"; \
		cd kafka/consumer && python3 consumer.py --group-id $(GROUP_ID); \
	else \
		echo "Using GROUP_ID: $(GROUP_ID) and PARTITION: $(PARTITION)"; \
		cd kafka/consumer && python3 consumer.py --group-id $(GROUP_ID) --partition $(PARTITION); \
	fi

# RabbitMQ targets
rabbitmq-producer:
	@echo "Starting RabbitMQ producer..."
	cd rabbitmq/producer && python3 producer.py

rabbitmq-consumer:
	@echo "Starting RabbitMQ consumer..."
	cd rabbitmq/consumer && python3 consumer.py

# Kafka demo - runs multiple producers and consumers
kafka-demo:
	@echo "Starting Kafka demo with 2 producers and 4 consumers (2 groups with specific partitions)..."
	@echo "Opening terminals for each component..."
	@echo "\033[1;33mNote: You'll need to close each terminal window manually when done\033[0m"
	@gnome-terminal --title="Kafka Producer 1" -- bash -c "cd $(CURDIR) && make kafka-producer; exec bash"
	@sleep 1
	@gnome-terminal --title="Kafka Producer 2" -- bash -c "cd $(CURDIR) && make kafka-producer; exec bash"
	@sleep 1
	@gnome-terminal --title="Kafka Consumer - Group A - Partition 0" -- bash -c "cd $(CURDIR) && make kafka-consumer GROUP_ID=group-A PARTITION=0; exec bash"
	@sleep 1
	@gnome-terminal --title="Kafka Consumer - Group A - Partition 1" -- bash -c "cd $(CURDIR) && make kafka-consumer GROUP_ID=group-A PARTITION=1; exec bash"
	@sleep 1
	@gnome-terminal --title="Kafka Consumer - Group B - Partition 0" -- bash -c "cd $(CURDIR) && make kafka-consumer GROUP_ID=group-B PARTITION=0; exec bash"
	@sleep 1
	@gnome-terminal --title="Kafka Consumer - Group B - Partition 1" -- bash -c "cd $(CURDIR) && make kafka-consumer GROUP_ID=group-B PARTITION=1; exec bash"
	@sleep 1
	@echo "\033[1;32mAll components started!\033[0m"
	@echo "\033[1;34mEach consumer is assigned to a specific partition (0 or 1)\033[0m"
	@echo "\033[1;34mGroup A consumers will only receive messages from their assigned partition\033[0m"
	@echo "\033[1;34mGroup B consumers will also only receive messages from their assigned partition\033[0m"
	@echo "\033[1;34mBoth groups will receive all messages independently\033[0m"

# Clean up
clean:
	@echo "Cleaning up Python cache files..."
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
