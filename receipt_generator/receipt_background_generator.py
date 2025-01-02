from PIL import Image, ImageDraw
import numpy as np
import imgaug.augmenters as iaa
import pathlib
import sys 
import os
import math
import xml.etree.ElementTree as ET

"""
This script provides a final generator 
The generated receipts from 3 receipt generators are used hier and applied augmentation techniques.
They are placed onto a background from collected background photos at a random position.
The final generator also generates corresponding annotations of images for oboject detection.
"""

def create_annotation_xml(filename, path, width, height, depth, xmin, ymin, xmax, ymax):
    # Create the root element
    annotation = ET.Element("annotation")

    # Add sub-elements
    folder_elem = ET.SubElement(annotation, "folder")
    folder_elem.text = "regular"

    filename_elem = ET.SubElement(annotation, "filename")
    filename_elem.text = filename

    path_elem = ET.SubElement(annotation, "path")
    path_elem.text = path

    source_elem = ET.SubElement(annotation, "source")
    database_elem = ET.SubElement(source_elem, "database")
    database_elem.text = "Unknown"

    size_elem = ET.SubElement(annotation, "size")
    width_elem = ET.SubElement(size_elem, "width")
    width_elem.text = str(width)
    height_elem = ET.SubElement(size_elem, "height")
    height_elem.text = str(height)
    depth_elem = ET.SubElement(size_elem, "depth")
    depth_elem.text = str(depth)

    segmented_elem = ET.SubElement(annotation, "segmented")
    segmented_elem.text = "0"

    object_elem = ET.SubElement(annotation, "object")
    name_elem = ET.SubElement(object_elem, "name")
    name_elem.text = "receipt"
    pose_elem = ET.SubElement(object_elem, "pose")
    pose_elem.text = "Unspecified"
    truncated_elem = ET.SubElement(object_elem, "truncated")
    truncated_elem.text = "0"
    difficult_elem = ET.SubElement(object_elem, "difficult")
    difficult_elem.text = "0"
    bndbox_elem = ET.SubElement(object_elem, "bndbox")
    xmin_elem = ET.SubElement(bndbox_elem, "xmin")
    xmin_elem.text = str(xmin)
    ymin_elem = ET.SubElement(bndbox_elem, "ymin")
    ymin_elem.text = str(ymin)
    xmax_elem = ET.SubElement(bndbox_elem, "xmax")
    xmax_elem.text = str(xmax)
    ymax_elem = ET.SubElement(bndbox_elem, "ymax")
    ymax_elem.text = str(ymax)


    # Add newlines and indentation to the XML content
    xml_content = ET.tostring(annotation, encoding="unicode", method="xml")
    formatted_xml = xml_content.replace("><", ">\n<")
    formatted_xml = formatted_xml.replace("\n<", "\n    <")
    formatted_xml = formatted_xml.replace("  ", "    ")  # Adjust indentation
    formatted_xml += "\n"  # Add newline at the end

    # Write the XML to a file
    xml_filename = os.path.splitext(filename)[0] + ".xml"
    output_folder = "output/annotations"
    os.makedirs(output_folder, exist_ok=True)  # Create the output folder if it doesn't exist
    output_path = os.path.join(output_folder, xml_filename)
    with open(output_path, "w") as f:
        f.write(formatted_xml)


# Load background image
image_output_name = sys.argv[2]
filename = sys.argv[1]
background = Image.open(filename)

# Load image to be placed
image_to_place = Image.open('tmp_output.png')

# Calculate new dimensions for the enlarged canvas
canvas_width = max(background.width, image_to_place.width*1.5)
canvas_height = max(background.height, image_to_place.height*1.5)

# Create a new blank canvas with enlarged boundaries
new_background = Image.new('RGBA', (canvas_width, canvas_height), color=(0, 0, 0, 0))

# Calculate offset to paste the original image onto the enlarged canvas
offset = ((canvas_width - image_to_place.width) // 2, (canvas_height - image_to_place.height) // 2)

# Paste the original image onto the new canvas, centered
new_background.paste(image_to_place, offset, image_to_place)

# debug  
#new_background.save(f"output/test/{image_output_name}")

rotated_width = abs(math.cos(35) * image_to_place.width) + abs(math.sin(35) * image_to_place.height)
max_scale_factor_width = new_background.width / 1.7 / rotated_width

rotated_height = abs(math.sin(35) * image_to_place.width) + abs(math.cos(35) * image_to_place.height)
max_scale_factor_height = new_background.height / 2 / rotated_height
max_scale_factor = min(max_scale_factor_width, max_scale_factor_height)

# Define augmentation sequence
seq = iaa.Sequential([
    iaa.PerspectiveTransform(scale=(0, 0.1)),  # apply perspective transformation
    iaa.Affine(  
        rotate=(-35, 35),  # rotate by -35 to 35 degrees
        scale=(max_scale_factor - 0.2,max_scale_factor), # scale images to max_scale_factor of their size
    )
], random_order=False)

# Apply augmentation sequence to the enlarged canvas
image_augmented = seq.augment_image(np.array(new_background))

# Convert numpy array to PIL Image
augmented_image_pil = Image.fromarray(image_augmented)

# debug 
#augmented_image_pil.save(f"output/test2/{image_output_name}")

# Convert the image to RGBA and create a mask
image_augmented = Image.fromarray(image_augmented)
image_augmented = image_augmented.convert("RGBA")
datas = image_augmented.getdata()

# Create a mask
newData = []
for item in datas:
    # Remove black pixels
    if item[0] == 0 and item[1] == 0 and item[2] == 0:
        newData.append((255, 255, 255, 0))
    else:
        newData.append(item)

# Update the image with the new data
image_augmented.putdata(newData)

# Get the bounding box of the non-transparent pixels
bbox = image_augmented.getbbox()

# Crop the image to the bounding box
cropped_image = image_augmented.crop(bbox)

bbox = cropped_image.getbbox()

center_x = background.width // 2
center_y = background.height // 2

# Calculate the maximum offset from the center for random placement
max_offset = min(center_x, center_y) // 4  # Adjust this factor for slight variations

# Generate random offsets within the maximum limits
offset_x = center_x + np.random.randint(-max_offset, max_offset + 1)
offset_y = center_y + np.random.randint(-max_offset, max_offset + 1)

# Calculate the position to paste the augmented image
paste_position = (offset_x - bbox[2] // 2, offset_y - bbox[3] // 2)

# Paste the augmented image onto the background at the calculated position
background.paste(cropped_image, paste_position, cropped_image)

start_x = paste_position[0] + 1
start_y = paste_position[1] + 1
end_x = start_x + bbox[2] - bbox[0] + 1
end_y = start_y + bbox[3] - bbox[1] + 1

#draw = ImageDraw.Draw(background)
#draw.rectangle([start_x, start_y, end_x, end_y], outline='orange')

# Display the result (optional)
#background.show()

pathlib.Path('output/images').mkdir(parents=True, exist_ok=True) 


# Save the result
background.save(f"output/images/{image_output_name}")

width, height = background.size

create_annotation_xml(
    filename=image_output_name,
    path=f"/Users/local_admin/Desktop/thesis/realreceipts/data/regular/{image_output_name}",
    width=width,
    height=height,
    depth=3,
    xmin=start_x,
    ymin=start_y,
    xmax=end_x,
    ymax=end_y
)
