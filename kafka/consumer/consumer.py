#!/usr/bin/env python3
import json
import time
import random
import os
import sys
import argparse
import tkinter as tk
from tkinter import scrolledtext, ttk
from confluent_kafka import Consumer, KafkaError, TopicPartition
from datetime import datetime

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class KafkaConsumerApp:
    def __init__(self, root, group_id=None, partition=None):
        self.root = root
        self.root.title("Kafka Consumer")
        self.root.geometry("600x500")
        self.root.configure(bg="#f0f0f0")
        
        # Load configuration
        with open('../../config.json', 'r') as f:
            self.config = json.load(f)['kafka']
        
        # Use provided group_id or generate a unique one
        self.group_id = group_id if group_id else f"group-{random.randint(1000, 9999)}"
        
        # Create a unique consumer ID
        self.consumer_id = f"consumer-{random.randint(1000, 9999)}"
        
        # Configure Kafka consumer
        self.consumer = Consumer({
            'bootstrap.servers': self.config['bootstrap_servers'],
            'group.id': self.group_id,
            'auto.offset.reset': 'latest',
            'client.id': self.consumer_id,
            'partition.assignment.strategy': 'range'
        })
        
        # Handle specific partition if provided
        self.specific_partition = partition
        if self.specific_partition is not None:
            # Assign to specific partition instead of subscribing
            topic_partition = TopicPartition(self.config['topic'], int(self.specific_partition))
            self.consumer.assign([topic_partition])
            self.root.title(f"Kafka Consumer - Group {self.group_id} - Partition {self.specific_partition}")
        else:
            # Subscribe to topic (let Kafka handle partition assignment)
            self.consumer.subscribe([self.config['topic']])
            self.root.title(f"Kafka Consumer - Group {self.group_id} - All Partitions")
        
        self.setup_ui()
        self.start_consuming()
        
    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#28a745")
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            header_frame, 
            text=f"Kafka Consumer ({self.consumer_id})", 
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#28a745",
            padx=10,
            pady=10
        ).pack(fill=tk.X)
        
        # Connection info
        conn_frame = tk.Frame(self.root, bg="#f0f0f0")
        conn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        partition_info = f"Partition: {self.specific_partition}" if self.specific_partition is not None else "All Partitions"
        
        tk.Label(
            conn_frame,
            text=f"Connected to: {self.config['bootstrap_servers']} | Topic: {self.config['topic']} | Group: {self.group_id} | {partition_info}",
            font=("Arial", 10),
            bg="#f0f0f0"
        ).pack(anchor="w")
        
        # Control frame
        control_frame = tk.Frame(self.root, bg="#f0f0f0")
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.pause_var = tk.BooleanVar()
        self.pause_checkbox = ttk.Checkbutton(
            control_frame,
            text="Pause Consumption",
            variable=self.pause_var,
            command=self.toggle_pause
        )
        self.pause_checkbox.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = ttk.Button(
            control_frame,
            text="Clear Log",
            command=self.clear_log
        )
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # Message display area
        message_frame = tk.Frame(self.root, bg="#f0f0f0")
        message_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(
            message_frame,
            text="Received Messages:",
            font=("Arial", 12),
            bg="#f0f0f0"
        ).pack(anchor="w")
        
        self.message_area = scrolledtext.ScrolledText(message_frame, height=20, font=("Courier", 10))
        self.message_area.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Status: Ready to receive messages")
        
        status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Consumer related variables
        self.paused = False
        self.message_count = 0
        
    def log_message(self, message, message_type="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        # Set color based on message type
        if message_type == "ERROR":
            tag = "error"
            color = "red"
        elif message_type == "RECEIVED":
            tag = "received"
            color = "blue"
        else:
            tag = "info"
            color = "black"
            
        self.message_area.tag_config(tag, foreground=color)
        self.message_area.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.message_area.insert(tk.END, f"{message}\n", tag)
        self.message_area.see(tk.END)
        
    def toggle_pause(self):
        self.paused = self.pause_var.get()
        if self.paused:
            self.log_message("Consumption paused")
            self.status_var.set("Status: Paused")
        else:
            self.log_message("Consumption resumed")
            self.status_var.set("Status: Running")
            
    def clear_log(self):
        self.message_area.delete(1.0, tk.END)
        self.log_message("Log cleared")
        
    def start_consuming(self):
        if not self.paused:
            try:
                msg = self.consumer.poll(0.1)
                
                if msg is None:
                    pass
                elif msg.error():
                    self.log_message(f"ERROR: {msg.error()}", "ERROR")
                else:
                    # Process received message
                    try:
                        # Get partition information from the message
                        partition = msg.partition()
                        topic = msg.topic()
                        offset = msg.offset()
                        
                        # Parse the message content
                        message_data = json.loads(msg.value().decode('utf-8'))
                        producer_id = message_data.get('producer_id', 'unknown')
                        timestamp = message_data.get('timestamp', 'unknown')
                        message = message_data.get('message', 'No message')
                        counter = message_data.get('counter', 0)
                        msg_partition = message_data.get('partition', 'unknown')
                        
                        # Check if this message is for our assigned partition
                        if self.specific_partition is not None and partition != int(self.specific_partition):
                            # This should not happen with manual assignment, but log it if it does
                            self.log_message(
                                f"WARNING: Received message for partition {partition} but we're assigned to {self.specific_partition}", 
                                "ERROR"
                            )
                        
                        self.log_message(
                            f"From {producer_id} [{counter}] on partition {partition}: {message}", 
                            "RECEIVED"
                        )
                        self.message_count += 1
                        self.status_var.set(f"Status: Received {self.message_count} messages | Topic: {topic} | Consumer Group: {self.group_id}")
                    except Exception as e:
                        self.log_message(f"Error processing message: {e}", "ERROR")
            except Exception as e:
                self.log_message(f"Error polling Kafka: {e}", "ERROR")
                
        # Schedule next poll
        self.root.after(100, self.start_consuming)

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Kafka Consumer')
    parser.add_argument('--group-id', dest='group_id', help='Consumer group ID')
    parser.add_argument('--partition', dest='partition', help='Specific partition to consume from')
    args = parser.parse_args()
    
    root = tk.Tk()
    app = KafkaConsumerApp(root, args.group_id, args.partition)
    root.mainloop()
