import tkinter as tk
from tkinter import filedialog, Frame, Scrollbar, Radiobutton, Scale
from PIL import Image, ImageTk
import cv2
from remove_background import remove_background
import numpy as np

class Imapulation:
    def __init__(self, root):
        self.root = root
        self.root.title("Imapulation")
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
        
        self.brush_btn = tk.Button(self.button_frame, text="Brush Tool", command=self.enable_brush, bg='#f39c12', fg='white', padx=10, pady=5)
        self.brush_btn.pack(side=tk.LEFT, padx=10)
        
        self.cursor_btn = tk.Button(self.button_frame, text="Cursor", command=self.enable_cursor, bg='#f39c12', fg='white', padx=10, pady=5)
        self.cursor_btn.pack(side=tk.LEFT, padx=10)

        # Add brush mode selection
        self.brush_mode = tk.StringVar(value='add')
        self.add_mode = Radiobutton(self.button_frame, text="Add", variable=self.brush_mode, value='add', bg='#34495e', fg='white', selectcolor='#16a085', indicatoron=0, width=10, command=self.highlight_brush_mode)
        self.add_mode.pack(side=tk.LEFT, padx=10)
        self.remove_mode = Radiobutton(self.button_frame, text="Remove", variable=self.brush_mode, value='remove', bg='#34495e', fg='white', selectcolor='#16a085', indicatoron=0, width=10, command=self.highlight_brush_mode)
        self.remove_mode.pack(side=tk.LEFT, padx=10)

        # Add brush size slider
        self.brush_size = Scale(self.button_frame, from_=1, to=50, orient=tk.HORIZONTAL, label="Brush Size", bg='#34495e', fg='white', command=self.update_cursor)
        self.brush_size.pack(side=tk.LEFT, padx=10)

        # Create a frame for the canvas and scrollbars
        self.canvas_frame = Frame(root, bg='white')
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        # Create vertical and horizontal scrollbars
        self.v_scrollbar = Scrollbar(self.canvas_frame, orient=tk.VERTICAL)
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.h_scrollbar = Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL)
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Create a canvas to display the image
        self.canvas = tk.Canvas(self.canvas_frame, bg='white', 
                                yscrollcommand=self.v_scrollbar.set, 
                                xscrollcommand=self.h_scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configure scrollbars
        self.v_scrollbar.config(command=self.canvas.yview)
        self.h_scrollbar.config(command=self.canvas.xview)
        
        # Keep track of the current image and path
        self.image = None
        self.image_path = None
        self.mask = None
        self.brush_enabled = False
        self.cursor_circle = None

    def upload_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.image = Image.open(file_path)
            self.image_path = file_path
            self.display_image(self.image)

    def display_image(self, image):
        self.canvas.delete("all")
        width, height = image.size
        self.canvas.config(width=width, height=height)
        self.canvas.config(scrollregion=(0, 0, width, height))
        image_tk = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=image_tk)
        self.canvas.image = image_tk
        
        # Update window geometry to fit the image size dynamically
        self.root.geometry(f"{width}x{height}")

    def remove_background(self):
        if self.image_path:
            processed_image = remove_background.remove_background(self.image_path)
            if processed_image:
                self.image = processed_image
                self.mask = self.image.split()[-1]  # Extract the alpha channel
                self.display_image(self.image)

    def save_image(self):
        if self.image:
            file_path = filedialog.asksaveasfilename(defaultextension=".png")
            if file_path:
                self.image.save(file_path)

    def enable_brush(self):
        self.brush_enabled = True
        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<Motion>", self.update_cursor)
        self.update_cursor()
        
    def enable_cursor(self):
        self.brush_enabled = False
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<Motion>")
        if self.cursor_circle:
            self.canvas.delete(self.cursor_circle)
        self.canvas.config(cursor="arrow")
        
    def highlight_brush_mode(self):
        if self.brush_mode.get() == 'add':
            self.add_mode.config(bg='#16a085')
            self.remove_mode.config(bg='#34495e')
        else:
            self.add_mode.config(bg='#34495e')
            self.remove_mode.config(bg='#16a085')

    def paint(self, event):
        if self.brush_enabled and self.mask is not None:
            x, y = event.x, event.y
            radius = self.brush_size.get()  # Get brush radius from slider
            mode = self.brush_mode.get()  # Get current brush mode

            color = 255 if mode == 'add' else 0

            # Ensure self.mask is in ndarray format
            if isinstance(self.mask, Image.Image):
                mask_np = np.array(self.mask)
            else:
                mask_np = np.array(self.mask)

            cv2.circle(mask_np, (x, y), radius, color, -1)  # Modify the mask
            self.mask = Image.fromarray(mask_np)
            rgba_image = Image.fromarray(np.dstack((np.array(self.image.convert('RGB')), mask_np)))
            self.image = rgba_image
            self.display_image(rgba_image)

    def update_cursor(self, event=None):
        if self.brush_enabled:
            if self.cursor_circle:
                self.canvas.delete(self.cursor_circle)
            x, y = self.canvas.winfo_pointerxy()
            x -= self.canvas.winfo_rootx()
            y -= self.canvas.winfo_rooty()
            radius = self.brush_size.get()
            self.cursor_circle = self.canvas.create_oval(x-radius, y-radius, x+radius, y+radius, outline='red')
        else:
            if self.cursor_circle:
                self.canvas.delete(self.cursor_circle)

if __name__ == "__main__":
    root = tk.Tk()
    app = Imapulation(root)
    root.mainloop()
