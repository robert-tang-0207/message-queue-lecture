#!/usr/bin/env python3
import json
import time
import random
import os
import sys
import tkinter as tk
from tkinter import scrolledtext, ttk
import pika
from datetime import datetime
import argparse

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class RabbitMQProducerApp:
    def __init__(self, root, queue_name=None, exchange_type=None):
        self.root = root
        self.root.title("RabbitMQ Producer")
        self.root.geometry("600x500")
        self.root.configure(bg="#f0f0f0")
        
        # Load configuration
        with open('../../config.json', 'r') as f:
            self.config = json.load(f)['rabbitmq']
        
        # Override config with command line parameters if provided
        self.queue_name = queue_name if queue_name else self.config.get('queue', 'message_queue_demo')
        self.exchange_type = exchange_type if exchange_type else 'direct'
        self.exchange_name = f"message_exchange_{self.exchange_type}"
        
        # Create a unique producer ID
        self.producer_id = f"producer-{random.randint(1000, 9999)}"
        
        # Configure RabbitMQ connection
        self.setup_rabbitmq_connection()
        
        self.setup_ui()
        
    def setup_rabbitmq_connection(self):
        try:
            # Create a connection to RabbitMQ server
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=self.config['host'])
            )
            self.channel = self.connection.channel()
            
            # Declare an exchange based on the specified type
            self.channel.exchange_declare(
                exchange=self.exchange_name,
                exchange_type=self.exchange_type,
                durable=True
            )
            
            # Declare a queue
            self.channel.queue_declare(queue=self.queue_name, durable=True)
            
            # Bind the queue to the exchange
            # For direct and topic exchanges, we use the queue name as the routing key
            # For fanout exchanges, the routing key is ignored
            routing_key = self.queue_name if self.exchange_type != 'fanout' else ''
            self.channel.queue_bind(
                exchange=self.exchange_name,
                queue=self.queue_name,
                routing_key=routing_key
            )
            
            self.connection_status = "Connected"
        except Exception as e:
            self.connection_status = f"Connection Error: {str(e)}"
            self.connection = None
            self.channel = None
        
    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#FF8C00")  # Orange for RabbitMQ
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            header_frame, 
            text=f"RabbitMQ Producer ({self.producer_id})", 
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#FF8C00",
            padx=10,
            pady=10
        ).pack(fill=tk.X)
        
        # Connection info
        conn_frame = tk.Frame(self.root, bg="#f0f0f0")
        conn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.conn_label = tk.Label(
            conn_frame,
            text=f"Status: {self.connection_status} | Host: {self.config['host']} | Exchange: {self.exchange_name} ({self.exchange_type}) | Queue: {self.queue_name}",
            font=("Arial", 10),
            bg="#f0f0f0"
        )
        self.conn_label.pack(anchor="w")
        
        # Reconnect button (if connection failed)
        if self.connection is None:
            self.reconnect_button = ttk.Button(
                conn_frame,
                text="Reconnect",
                command=self.reconnect
            )
            self.reconnect_button.pack(anchor="w", pady=5)
        
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
        self.message_input.insert(tk.END, "Hello from RabbitMQ Producer!")
        
        # Buttons
        button_frame = tk.Frame(self.root, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.send_button = ttk.Button(
            button_frame,
            text="Send Message",
            command=self.send_message,
            state=tk.DISABLED if self.connection is None else tk.NORMAL
        )
        self.send_button.pack(side=tk.LEFT, padx=5)
        
        self.auto_send_var = tk.BooleanVar()
        self.auto_send_checkbox = ttk.Checkbutton(
            button_frame,
            text="Auto Send (1 msg/sec)",
            variable=self.auto_send_var,
            command=self.toggle_auto_send,
            state=tk.DISABLED if self.connection is None else tk.NORMAL
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
        
        # Log initial status
        self.log_message(f"Producer initialized with ID: {self.producer_id}")
        self.log_message(f"Connection status: {self.connection_status}")
        
    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.log_area.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_area.see(tk.END)
        
    def reconnect(self):
        self.log_message("Attempting to reconnect...")
        self.setup_rabbitmq_connection()
        
        # Update UI based on connection status
        self.conn_label.config(text=f"Status: {self.connection_status} | Host: {self.config['host']} | Exchange: {self.exchange_name} ({self.exchange_type}) | Queue: {self.queue_name}")
        
        if self.connection is not None:
            self.log_message("Reconnection successful")
            self.send_button.config(state=tk.NORMAL)
            self.auto_send_checkbox.config(state=tk.NORMAL)
            if hasattr(self, 'reconnect_button'):
                self.reconnect_button.destroy()
        else:
            self.log_message(f"Reconnection failed: {self.connection_status}")
    
    def send_message(self):
        if self.connection is None or self.channel is None:
            self.log_message("ERROR: Not connected to RabbitMQ")
            return
            
        try:
            message = self.message_input.get("1.0", tk.END).strip()
            if not message:
                self.log_message("ERROR: Cannot send empty message")
                return
                
            # Add timestamp and producer ID to message
            payload = {
                "producer_id": self.producer_id,
                "timestamp": datetime.now().isoformat(),
                "message": message,
                "counter": self.message_counter,
                "exchange_type": self.exchange_type,
                "queue": self.queue_name
            }
            
            # Convert to JSON and send
            json_payload = json.dumps(payload)
            
            # Determine routing key based on exchange type
            if self.exchange_type == 'fanout':
                routing_key = ''
            else:  # direct or topic
                routing_key = self.queue_name
            
            # Publish the message
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key=routing_key,
                body=json_payload,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                )
            )
            
            self.log_message(f"Sent: {json_payload}")
            self.message_counter += 1
            
            # If not in auto mode, update the message with a counter
            if not self.auto_send_active:
                self.message_input.delete("1.0", tk.END)
                self.message_input.insert(tk.END, f"Hello from RabbitMQ Producer! Count: {self.message_counter}")
                
        except Exception as e:
            self.log_message(f"ERROR: {str(e)}")
            
            # Check if connection is closed and try to reconnect
            if "connection closed" in str(e).lower() or "socket closed" in str(e).lower():
                self.connection = None
                self.channel = None
                self.log_message("Connection lost. Attempting to reconnect...")
                self.reconnect()
    
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
            
    def on_closing(self):
        if self.connection is not None and self.connection.is_open:
            try:
                self.connection.close()
                self.log_message("Connection closed")
            except:
                pass
        self.root.destroy()

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='RabbitMQ Producer')
    parser.add_argument('--queue', type=str, help='Queue name to use')
    parser.add_argument('--exchange-type', type=str, choices=['direct', 'topic', 'fanout'],
                        help='Exchange type to use (direct, topic, or fanout)')
    args = parser.parse_args()
    
    root = tk.Tk()
    app = RabbitMQProducerApp(root, queue_name=args.queue, exchange_type=args.exchange_type)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
