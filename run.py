import torch
from transformers import SamModel, SamProcessor
from PIL import Image
import numpy as np
import argparse

def segment_object(image_path, class_prompt, output_path):
    # Load SAM model and processor
    processor = SamProcessor.from_pretrained('segment-anything')
    model = SamModel.from_pretrained('segment-anything')

    # Load and preprocess the input image
    image = Image.open(image_path)
    inputs = processor(images=image, return_tensors="pt")
    
    # Generate segmentation mask
    outputs = model(**inputs)
    mask = outputs.logits.sigmoid() > 0.5  # Binary mask for object

    # Load the image into numpy for editing
    image_np = np.array(image)
    
    # Apply red mask to the segmented object
    image_np[mask[0, 0]] = [255, 0, 0]  # Red color

    # Save the output image with red mask
    Image.fromarray(image_np).save(output_path)


def shift_object(image_path, class_prompt, x_shift, y_shift, output_path):
    # Load SAM model and processor
    processor = SamProcessor.from_pretrained('segment-anything')
    model = SamModel.from_pretrained('segment-anything')

    # Load image and generate segmentation mask
    image = Image.open(image_path)
    inputs = processor(images=image, return_tensors="pt")
    outputs = model(**inputs)

    # Extract mask and apply to the object
    mask = outputs.logits.sigmoid() > 0.5
    image_np = np.array(image)
    object_pixels = image_np[mask[0, 0]]

    # Create a blank image and shift the object position
    new_image_np = np.zeros_like(image_np)
    new_x, new_y = max(0, x_shift), max(0, y_shift)
    new_image_np[new_y:new_y + object_pixels.shape[0], new_x:new_x + object_pixels.shape[1]] = object_pixels

    # Save the output image
    Image.fromarray(new_image_np).save(output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Segment and shift objects in an image")
    
    # Define common arguments
    parser.add_argument('--image', type=str, required=True, help="Path to the input image")
    parser.add_argument('--object_class', type=str, required=True, help="Object class to segment")
    parser.add_argument('--output', type=str, required=True, help="Path to save the output image")

    # Define task-specific arguments
    parser.add_argument('--x', type=int, default=0, help="Pixels to shift the object horizontally")
    parser.add_argument('--y', type=int, default=0, help="Pixels to shift the object vertically")

    args = parser.parse_args()

    # If x or y is provided, perform shifting, otherwise do segmentation only
    if args.x != 0 or args.y != 0:
        shift_object(args.image, args.object_class, args.x, args.y, args.output)
    else:
        segment_object(args.image, args.class, args.output)
