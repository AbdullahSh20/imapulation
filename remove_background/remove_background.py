import numpy as np
import tensorflow as tf
from PIL import Image, ImageFilter
import cv2

# Load the trained model
model = tf.keras.models.load_model('remove_background/remove_background_model.h5', compile=False)

def preprocess_image(image, img_size=(256, 256)):
    img = image.convert('RGB').resize(img_size)
    img_array = np.array(img) / 255.0
    return np.expand_dims(img_array, axis=0)

def postprocess_mask(mask, original_size):
    mask = (mask > 0.5).astype(np.uint8).squeeze()
    mask = Image.fromarray(mask * 255).resize(original_size, resample=Image.BILINEAR)
    
    # Convert to binary
    mask_np = np.array(mask)
    _, mask_bin = cv2.threshold(mask_np, 127, 255, cv2.THRESH_BINARY)
    
    # Apply Canny edge detection
    edges = cv2.Canny(mask_bin, 100, 200)  # Adjust thresholds as needed
    
    # Dilate the edges to include more boundary pixels
    kernel = np.ones((3, 3), np.uint8)
    mask_edges = cv2.dilate(edges, kernel, iterations=1)
    
    # Combine edges with the original mask
    mask_combined = np.maximum(mask_np, mask_edges)
    
    # Convert back to PIL Image for further processing
    mask_combined = Image.fromarray(mask_combined)
    
    # Apply Gaussian blur to smooth the edges of the mask
    mask_combined = mask_combined.filter(ImageFilter.GaussianBlur(radius=3))
    
    return np.array(mask_combined) / 255.0

def apply_mask(image, mask):
    image_np = np.array(image)
    rgba_image = np.zeros((image_np.shape[0], image_np.shape[1], 4), dtype=np.uint8)
    
    # Check if the image has 3 or 4 channels and handle accordingly
    if image_np.shape[2] == 3:
        rgba_image[..., :3] = image_np
    elif image_np.shape[2] == 4:
        rgba_image[..., :3] = image_np[..., :3]
    
    rgba_image[..., 3] = (mask * 255).astype(np.uint8)
    return Image.fromarray(rgba_image, 'RGBA')

def remove_background(image_path):
    image = Image.open(image_path)
    original_size = image.size
    input_image = preprocess_image(image)
    predicted_mask = model.predict(input_image)
    predicted_mask = postprocess_mask(predicted_mask, original_size)
    return apply_mask(image, predicted_mask)
