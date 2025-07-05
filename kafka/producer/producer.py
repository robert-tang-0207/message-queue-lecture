#!/usr/bin/env python3
import json
import time
import random
import os
import sys
import tkinter as tk
from tkinter import scrolledtext, ttk
from confluent_kafka import Producer
from datetime import datetime

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class KafkaProducerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kafka Producer")
        self.root.geometry("600x500")
        self.root.configure(bg="#f0f0f0")
        
        # Load configuration
        with open('../../config.json', 'r') as f:
            self.config = json.load(f)['kafka']
        
        # Create a unique producer ID
        self.producer_id = f"producer-{random.randint(1000, 9999)}"
        
        # Configure Kafka producer
        self.producer = Producer({
            'bootstrap.servers': self.config['bootstrap_servers'],
            'client.id': self.producer_id
        })
        
        self.setup_ui()
        
    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#007BFF")
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            header_frame, 
            text=f"Kafka Producer ({self.producer_id})", 
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#007BFF",
            padx=10,
            pady=10
        ).pack(fill=tk.X)
        
        # Connection info
        conn_frame = tk.Frame(self.root, bg="#f0f0f0")
        conn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            conn_frame,
            text=f"Connected to: {self.config['bootstrap_servers']} | Topic: {self.config['topic']}",
            font=("Arial", 10),
            bg="#f0f0f0"
        ).pack(anchor="w")
        
        # Message input area
        input_frame = tk.Frame(self.root, bg="#f0f0f0")
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            input_frame,
            text="Message:",
            font=("Arial", 12),
            bg="#f0f0f0"
        ).pack(anchor="w")
        
        self.message_input = tk.Text(input_frame, height=5, width=50, font=("Arial", 12))
        self.message_input.pack(fill=tk.X, pady=5)
        self.message_input.insert(tk.END, "Hello from Kafka Producer!")
        
        # Buttons
        button_frame = tk.Frame(self.root, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.send_button = ttk.Button(
            button_frame,
            text="Send Message",
            command=self.send_message
        )
        self.send_button.pack(side=tk.LEFT, padx=5)
        
        self.auto_send_var = tk.BooleanVar()
        self.auto_send_checkbox = ttk.Checkbutton(
            button_frame,
            text="Auto Send (1 msg/sec)",
            variable=self.auto_send_var,
            command=self.toggle_auto_send
        )
        self.auto_send_checkbox.pack(side=tk.LEFT, padx=5)
        
        # Log area
        log_frame = tk.Frame(self.root, bg="#f0f0f0")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(
            log_frame,
            text="Log:",
            font=("Arial", 12),
            bg="#f0f0f0"
        ).pack(anchor="w")
        
        self.log_area = scrolledtext.ScrolledText(log_frame, height=10, font=("Courier", 10))
        self.log_area.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Auto-send related variables
        self.auto_send_active = False
        self.message_counter = 0
        
    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.log_area.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_area.see(tk.END)
        
    def delivery_callback(self, err, msg):
        if err:
            self.log_message(f"ERROR: Message delivery failed: {err}")
        else:
            self.log_message(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")
    
    def send_message(self):
        try:
            message = self.message_input.get("1.0", tk.END).strip()
            if not message:
                self.log_message("ERROR: Cannot send empty message")
                return
                
            # Choose a random partition (0 or 1)
            partition = random.randint(0, 1)
            
            # Create a message with metadata
            message_data = {
                "producer_id": self.producer_id,
                "timestamp": datetime.now().isoformat(),
                "message": message,
                "counter": self.message_counter,
                "partition": partition  # Store the partition we're sending to
            }
            
            # Convert message to JSON
            json_message = json.dumps(message_data)
            
            # Send message to Kafka with explicit partition
            self.producer.produce(
                self.config['topic'],
                value=json_message.encode('utf-8'),
                partition=partition,  # Explicitly specify which partition to use
                callback=self.delivery_callback
            )
            self.producer.poll(0)  # Trigger delivery reports
            
            self.log_message(f"Sending: {json_message}")
            self.message_counter += 1
            
            # If not in auto mode, update the message with a counter
            if not self.auto_send_active:
                self.message_input.delete("1.0", tk.END)
                self.message_input.insert(tk.END, f"Hello from Kafka Producer! Count: {self.message_counter}")
                
        except Exception as e:
            self.log_message(f"ERROR: {str(e)}")
    
    def toggle_auto_send(self):
        self.auto_send_active = self.auto_send_var.get()
        if self.auto_send_active:
            self.log_message("Auto-send enabled - sending 1 message per second")
            self.auto_send()
        else:
            self.log_message("Auto-send disabled")
    
    def auto_send(self):
        if self.auto_send_active:
            self.send_message()
            self.root.after(1000, self.auto_send)

if __name__ == "__main__":
    root = tk.Tk()
    app = KafkaProducerApp(root)
    root.mainloop()
