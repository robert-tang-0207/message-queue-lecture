#!/usr/bin/env python3
import json
import time
import random
import os
import sys
import tkinter as tk
from tkinter import scrolledtext, ttk
import pika
import threading
from datetime import datetime

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class RabbitMQConsumerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RabbitMQ Consumer")
        self.root.geometry("600x500")
        self.root.configure(bg="#f0f0f0")
        
        # Load configuration
        with open('../../config.json', 'r') as f:
            self.config = json.load(f)['rabbitmq']
        
        # Create a unique consumer ID
        self.consumer_id = f"consumer-{random.randint(1000, 9999)}"
        
        # Setup UI first so we can log connection status
        self.setup_ui()
        
        # Configure RabbitMQ connection
        self.setup_rabbitmq_connection()
        
        # Start consuming in a separate thread
        if self.connection is not None:
            self.start_consuming()
        
    def setup_rabbitmq_connection(self):
        try:
            # Create a connection to RabbitMQ server
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=self.config['host'])
            )
            self.channel = self.connection.channel()
            
            # Declare a queue
            self.channel.queue_declare(queue=self.config['queue'], durable=True)
            
            # Set QoS
            self.channel.basic_qos(prefetch_count=1)
            
            self.connection_status = "Connected"
            self.log_message(f"Successfully connected to RabbitMQ at {self.config['host']}")
            
            # Update UI
            self.conn_label.config(text=f"Status: {self.connection_status} | Host: {self.config['host']} | Queue: {self.config['queue']}")
            if hasattr(self, 'reconnect_button'):
                self.reconnect_button.config(state=tk.NORMAL)
            self.pause_checkbox.config(state=tk.NORMAL)
            
            return True
            
        except Exception as e:
            self.connection_status = f"Connection Error: {str(e)}"
            self.connection = None
            self.channel = None
            self.log_message(f"Failed to connect to RabbitMQ: {str(e)}", "ERROR")
            
            # Update UI
            self.conn_label.config(text=f"Status: {self.connection_status}")
            if hasattr(self, 'reconnect_button'):
                self.reconnect_button.config(state=tk.NORMAL)
            
            return False
        
    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#9370DB")  # Purple for RabbitMQ Consumer
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            header_frame, 
            text=f"RabbitMQ Consumer ({self.consumer_id})", 
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#9370DB",
            padx=10,
            pady=10
        ).pack(fill=tk.X)
        
        # Connection info
        conn_frame = tk.Frame(self.root, bg="#f0f0f0")
        conn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.conn_label = tk.Label(
            conn_frame,
            text="Status: Initializing...",
            font=("Arial", 10),
            bg="#f0f0f0"
        )
        self.conn_label.pack(anchor="w")
        
        # Reconnect button
        self.reconnect_button = ttk.Button(
            conn_frame,
            text="Reconnect",
            command=self.reconnect,
            state=tk.DISABLED
        )
        self.reconnect_button.pack(anchor="w", pady=5)
        
        # Control frame
        control_frame = tk.Frame(self.root, bg="#f0f0f0")
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.pause_var = tk.BooleanVar()
        self.pause_checkbox = ttk.Checkbutton(
            control_frame,
            text="Pause Consumption",
            variable=self.pause_var,
            command=self.toggle_pause,
            state=tk.DISABLED
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
        
        # Configure tags for message coloring
        self.message_area.tag_configure("error", foreground="red")
        self.message_area.tag_configure("received", foreground="blue")
        self.message_area.tag_configure("info", foreground="black")
        self.message_area.tag_configure("timestamp", foreground="gray")
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Status: Initializing...")
        
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
        self.consumer_thread = None
        self.consumer_tag = None
        
        # Log initial status
        self.log_message(f"Consumer initialized with ID: {self.consumer_id}")
        
    def log_message(self, message, message_type="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        # Determine tag based on message type
        if message_type == "ERROR":
            tag = "error"
        elif message_type == "RECEIVED":
            tag = "received"
        else:
            tag = "info"
            
        # Add message to UI thread-safely
        self.root.after(0, lambda: self._append_to_log(timestamp, message, tag))
        
    def _append_to_log(self, timestamp, message, tag):
        self.message_area.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.message_area.insert(tk.END, f"{message}\n", tag)
        self.message_area.see(tk.END)
        
    def toggle_pause(self):
        self.paused = self.pause_var.get()
        if self.paused:
            self.log_message("Consumption paused")
            self.status_var.set("Status: Paused")
            
            # Cancel consumer if we have a consumer tag
            if self.channel and self.consumer_tag:
                try:
                    self.channel.basic_cancel(consumer_tag=self.consumer_tag)
                    self.consumer_tag = None
                except:
                    pass
        else:
            self.log_message("Consumption resumed")
            self.status_var.set("Status: Running")
            
            # Restart consumer
            if self.channel:
                self.start_consuming()
            
    def clear_log(self):
        self.message_area.delete(1.0, tk.END)
        self.log_message("Log cleared")
        
    def reconnect(self):
        self.log_message("Attempting to reconnect...")
        self.reconnect_button.config(state=tk.DISABLED)
        
        # Try to close existing connection
        if self.connection is not None and self.connection.is_open:
            try:
                self.connection.close()
            except:
                pass
                
        # Setup new connection
        if self.setup_rabbitmq_connection():
            # If connection successful and not paused, start consuming
            if not self.paused:
                self.start_consuming()
        
    def callback(self, ch, method, properties, body):
        if self.paused:
            # If paused while callback is processing, don't acknowledge
            return
            
        try:
            # Decode and parse the message
            message_value = body.decode('utf-8')
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
            self.root.after(0, lambda: self.status_var.set(f"Status: Running | Messages received: {self.message_count}"))
            
        except json.JSONDecodeError:
            self.log_message(f"Received non-JSON message: {body}", "ERROR")
        except Exception as e:
            self.log_message(f"Error processing message: {str(e)}", "ERROR")
        finally:
            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)
    
    def consume_messages(self):
        try:
            # Start consuming
            self.consumer_tag = self.channel.basic_consume(
                queue=self.config['queue'],
                on_message_callback=self.callback
            )
            
            self.log_message("Started consuming messages")
            self.status_var.set("Status: Running")
            
            # Start consuming (blocking call)
            self.channel.start_consuming()
            
        except Exception as e:
            self.log_message(f"Consumption error: {str(e)}", "ERROR")
            self.status_var.set("Status: Error")
            
            # Try to reconnect if connection was lost
            if "connection closed" in str(e).lower() or "socket closed" in str(e).lower():
                self.root.after(5000, self.reconnect)  # Try to reconnect after 5 seconds
    
    def start_consuming(self):
        if self.consumer_thread is not None and self.consumer_thread.is_alive():
            self.log_message("Consumer thread is already running")
            return
            
        # Create and start the consumer thread
        self.consumer_thread = threading.Thread(target=self.consume_messages)
        self.consumer_thread.daemon = True  # Thread will exit when main thread exits
        self.consumer_thread.start()
            
    def on_closing(self):
        # Stop consuming
        if self.channel and self.consumer_tag:
            try:
                self.channel.basic_cancel(consumer_tag=self.consumer_tag)
            except:
                pass
                
        # Close connection
        if self.connection is not None and self.connection.is_open:
            try:
                self.connection.close()
                self.log_message("Connection closed")
            except:
                pass
                
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = RabbitMQConsumerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
