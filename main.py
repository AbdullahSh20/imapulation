import tkinter as tk
from tkinter import filedialog, Frame
from PIL import Image, ImageTk
import cv2
import numpy as np
import tensorflow as tf

class Imapulation:
    def __init__(self, root):
        self.root = root
        self.root.title("Imapulation")
        self.root.geometry("800x600")
        self.root.configure(bg='#2c3e50')
        
        # Create a frame for buttons
        self.button_frame = Frame(root, bg='#34495e', pady=10)
        self.button_frame.pack(side=tk.TOP, fill=tk.X)
        
        self.upload_btn = tk.Button(self.button_frame, text="Upload Image", command=self.upload_image, bg='#3498db', fg='white', padx=10, pady=5)
        self.upload_btn.pack(side=tk.LEFT, padx=10)
        
        self.process_btn = tk.Button(self.button_frame, text="Remove Background", command=self.remove_background, bg='#e74c3c', fg='white', padx=10, pady=5)
        self.process_btn.pack(side=tk.LEFT, padx=10)
        
        self.save_btn = tk.Button(self.button_frame, text="Save Image", command=self.save_image, bg='#2ecc71', fg='white', padx=10, pady=5)
        self.save_btn.pack(side=tk.LEFT, padx=10)
        
        # Create a canvas to display the image
        self.canvas = tk.Canvas(root, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Keep track of the current image
        self.image = None

    def upload_image(self):
        file_path = filedialog.askopenfilename()
        self.image = Image.open(file_path)
        self.display_image(self.image)

    def display_image(self, image):
        self.canvas.delete("all")
        image_tk = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=image_tk)
        self.canvas.image = image_tk

    def remove_background(self):
        pass

    def save_image(self):
        if self.image:
            file_path = filedialog.asksaveasfilename(defaultextension=".png")
            self.image.save(file_path)

if __name__ == "__main__":
    root = tk.Tk()
    app = Imapulation(root)
    root.mainloop()
