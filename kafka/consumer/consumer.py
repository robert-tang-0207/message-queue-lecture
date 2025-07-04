#!/usr/bin/env python3
import json
import time
import random
import os
import sys
import tkinter as tk
from tkinter import scrolledtext, ttk
from confluent_kafka import Consumer, KafkaError
from datetime import datetime

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class KafkaConsumerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kafka Consumer")
        self.root.geometry("600x500")
        self.root.configure(bg="#f0f0f0")
        
        # Load configuration
        with open('../../config.json', 'r') as f:
            self.config = json.load(f)['kafka']
        
        # Create a unique consumer ID
        self.consumer_id = f"consumer-{random.randint(1000, 9999)}"
        
        # Configure Kafka consumer
        self.consumer = Consumer({
            'bootstrap.servers': self.config['bootstrap_servers'],
            'group.id': self.config['group_id'],
            'auto.offset.reset': 'latest',
            'client.id': self.consumer_id
        })
        
        # Subscribe to topic
        self.consumer.subscribe([self.config['topic']])
        
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
        
        tk.Label(
            conn_frame,
            text=f"Connected to: {self.config['bootstrap_servers']} | Topic: {self.config['topic']} | Group: {self.config['group_id']}",
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
                    if msg.error().code() != KafkaError._PARTITION_EOF:
                        self.log_message(f"Consumer error: {msg.error()}", "ERROR")
                else:
                    try:
                        # Decode and parse the message
                        message_value = msg.value().decode('utf-8')
                        data = json.loads(message_value)
                        
                        # Format the message nicely
                        producer_id = data.get('producer_id', 'unknown')
                        timestamp = data.get('timestamp', 'unknown')
                        message = data.get('message', '')
                        counter = data.get('counter', -1)
                        
                        formatted_msg = f"From: {producer_id} | Counter: {counter} | Message: {message}"
                        self.log_message(formatted_msg, "RECEIVED")
                        
                        # Update status
                        self.message_count += 1
                        self.status_var.set(f"Status: Running | Messages received: {self.message_count}")
                        
                    except json.JSONDecodeError:
                        self.log_message(f"Received non-JSON message: {message_value}", "ERROR")
                    except Exception as e:
                        self.log_message(f"Error processing message: {str(e)}", "ERROR")
                        
            except Exception as e:
                self.log_message(f"Consumption error: {str(e)}", "ERROR")
                
        # Schedule the next check
        self.root.after(100, self.start_consuming)

if __name__ == "__main__":
    root = tk.Tk()
    app = KafkaConsumerApp(root)
    root.mainloop()
