from nanodet.util import cfg, load_config, Logger
from demo.demo import Predictor
import cv2
from PIL import Image
import torch
from paddleocr import PaddleOCR,draw_ocr
import re
import os
import numpy as np

"""
This script provides the complete pipeline to extracts date and amount from given receipt image by following these steps:
- load nanodet model to detect receipts and return bounding boxes which has the highest score
- crop the detected receipts from last step
- rotate the cropped receipts based on the detected orientation of the longest vertical line in the image ( if the longest vertical line falls within the specified angle range for vertical lines)
- send the results to the custom OCR pipeline (DB + CRNN)
- extract  date and total amount from the output of OCR according to the determined REGEX
- ouput the matched date and total amount
* in each step, the result images will be saved and used in the next step
"""

def load_nanodet_model(config_path, model_path):
    # Load NanoDet configuration
    load_config(cfg, config_path)
    logger = Logger(-1, use_tensorboard=False)

    # Initialize Predictor for NanoDet
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    predictor = Predictor(cfg, model_path + "/model_best/nanodet_model_best.pth", logger, device=device)
    return predictor

def perform_object_detection(predictor, image_path):
    # Perform object detection using NanoDet
    meta, res = predictor.inference(image_path)
    return res

def extract_object_with_highest_score(image_path, detection_results, output_path):
    # Extract the detection results from the dictionary
    detections = detection_results[0][0]  # Assuming res is a dictionary with the structure {0: {0: ...}}

    # Find the index of the object with the highest confidence score
    max_score_index = max(range(len(detections)), key=lambda i: detections[i][4])

    # Extract the bounding box coordinates and confidence score of the object with the highest score
    x_min, y_min, x_max, y_max, _ = detections[max_score_index]

    # Load the input image
    image = cv2.imread(image_path)

    # Extract the detected object from the image
    detected_object = image[int(y_min):int(y_max), int(x_min):int(x_max)]

    # Save the image with the bounding box
    cv2.rectangle(image, (int(x_min), int(y_min)), (int(x_max), int(y_max)), (0, 255, 0), 2)
    cv2.imwrite(output_path+'image_with_bounding_box.png', image)

    return detected_object

def extractDate(result):
    """
    Regex to match dates
    """
    # allowing for optional concatenated times
    date_regex = r'\b(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})(?:\s*\d{2}:\d{2})?'
    extracted_dates = []
    # Iterate through OCR results
    for block in result:
        if isinstance(block, list) and len(block) == 2:
            text_block = block[1]  # Expecting the OCR text to be here
            if isinstance(text_block, tuple) and len(text_block) > 0:
                text, confidence = text_block
                # Search for the regex pattern with capturing group
                matches = re.findall(date_regex, text)
                if matches:
                    print(f"Date found in the text: {matches} | Full block: {text}")
                    extracted_dates.extend(matches)
                else:
                    print(f"No date found in the text: {text}")
        else:
            print("Unexpected block structure encountered.")

    # Deduplicate dates if necessary
    extracted_unique_dates = list(set(extracted_dates))

    print("Extracted Dates:", extracted_unique_dates)

def extractTotal(result):
    """
    Regex to match an amount
    """
    amount_regex = r'(^[\d,.]+\d{2}$)'

    extracted_amounts = []
    prev_was_eur = False  # Flag indicating the preceding item was "EUR" or "EURO"

    for idx in range(len(result)):
        for item in result[idx][1:]:
            if isinstance(item, tuple) and len(item) == 2:
                text, confidence = item  # Unpacking the item
                
                if isinstance(text, str):  # Ensure the text is indeed a string
                    # Normalize the text to upper case for comparison
                    text_upper = text.strip().upper()
                    
                    # Check if the current item is specific keys
                    if text_upper in ("EUR", "EURO", "zu zahlen","Summe(EUR)","Total",
                                      "EC-Karte","EC-Cash","Betrag EUR","Summe €"):
                        print(f"Currency marker found: {text}")
                        prev_was_eur = True

                    # If the previous item was specific keys and the current matches the amount pattern
                    elif prev_was_eur and re.match(amount_regex, text.strip()):
                        extracted_amount = text.strip()
                        print(f"Amount found following currency marker: {extracted_amount}")
                        extracted_amounts.append(extracted_amount)
                        prev_was_eur = False  # Reset the flag
                    
                    # If current item is not an amount following specific keys
                    else:
                        # Only reset the flag if it was previously set; avoids unnecessary prints
                        if prev_was_eur:
                            print("Resetting flag; current item is neither specific keys nor an amount following it.")
                        prev_was_eur = False
                else:
                    print(f"Encountered non-string text: {text}")
            else:
                print(f"Unexpected item structure encountered: {item}")

    # If you're aiming to keep unique, non-repeated matches
    extracted_amounts = list(set(extracted_amounts))

    # Display the extracted total amounts
    print("Extracted Total Amounts:", extracted_amounts)

def rotate_image(image_path, output_folder):
    """
    Rotate detected receipts from object detection 
    """
    # Read the image
    original_image = cv2.imread(image_path)
    rotated_image = original_image

    # Convert the image to grayscale
    gray = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Apply adaptive thresholding
    adaptive_thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 25, 4)

    # Use morphological operations to remove noise and enhance lines
    kernel = np.ones((5, 5), np.uint8)
    opening = cv2.morphologyEx(adaptive_thresh, cv2.MORPH_OPEN, kernel)

    # Detect lines using Probabilistic Hough Transform
    lines = cv2.HoughLinesP(opening, 1, np.pi / 180, threshold=100, minLineLength=100, maxLineGap=10)

    # Initialize variables to store the longest vertical line
    max_length = 0
    longest_line = None
    if lines is None:
        print(image_path + "fail to rotate")
    else:
        # Find the longest vertical line
        for line in lines:
            x1, y1, x2, y2 = line[0]
            length = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
            if (-60 > angle >= -90) or (40 < angle <= 90):  # Consider lines with angle between 80 and 100 degrees as vertical
                if length > max_length:
                    max_length = length
                    longest_line = line

        if longest_line is not None:
            angle_from_vertical = np.arctan2(longest_line[0][3] - longest_line[0][1], longest_line[0][2] - longest_line[0][0]) * 180 / np.pi
            x1, y1, x2, y2 = longest_line[0]
            (h, w) = original_image.shape[:2]
            center = (w // 2, h // 2)

            if(angle_from_vertical < 0):
                rotation_matrix = cv2.getRotationMatrix2D(center, 90+angle_from_vertical, 1.0)  # Negative angle to rotate clockwise
            else:
                rotation_matrix = cv2.getRotationMatrix2D(center, angle_from_vertical-90, 1.0)  # Negative angle to rotate clockwise
            rotated_image = cv2.warpAffine(original_image, rotation_matrix, (w, h), flags=cv2.INTER_CUBIC)# , borderMode=cv2.BORDER_REPLICATE
            
    # Save the rotated image with the original filename
    filename = os.path.basename(image_path)
    output_path = os.path.join(output_folder, 'rotated_'+filename)
    print(output_path)
    cv2.imwrite(output_path, rotated_image)


config_path = '/Users/local_admin/Desktop/thesis/object_detection/nanodet/nanodet_custom_xml_dataset.yml'
model_path = '/Users/local_admin/Desktop/thesis/object_detection/trained_detectors/nanodet/trained_nano_det_1500_combined_to_real'
image_path = '/Users/local_admin/Desktop/thesis/data/prediction/IMG_1822.jpg'
output_path= '/Users/local_admin/Desktop/thesis/data/prediction/'


# Object Detection
predictor = load_nanodet_model(config_path, model_path)
detection_results = perform_object_detection(predictor, image_path)
detected_object = extract_object_with_highest_score(image_path, detection_results,output_path)
cv2.imwrite(output_path + 'detected_object.jpg', detected_object)

# Rotate Image if necessary
rotate_image(output_path + 'detected_object.jpg', output_path)


# Text Recognition and Text detection
ocr = PaddleOCR(use_angle_cls=True,
                rec_model_dir='/Users/local_admin/Desktop/thesis/ppocr/inference/crnn_real',
                det_model_dir='/Users/local_admin/Desktop/thesis/ppocr/inference/db_combi/Student',
                rec_char_dict_path='/Users/local_admin/Desktop/thesis/PaddleOCR/ppocr/utils/dict/german_dict.txt',
                ocr_version='PP-OCRv2',
                use_gpu=False,
                show_log=False,
                lang="german")

result = ocr.ocr(output_path + 'rotated_detected_object.jpg', cls=False)[0]

# draw result
image = Image.open(output_path + 'rotated_detected_object.jpg').convert('RGB')
boxes = [line[0] for line in result]
txts = [line[1][0] for line in result]
scores = [line[1][1] for line in result]
im_show = draw_ocr(image, boxes, txts, scores, font_path='/Users/local_admin/Desktop/thesis/receipt_generator/fonts/Arial.TTF')
im_show = Image.fromarray(im_show)
im_show.save(output_path + '/predicted.jpg')

extractDate(result)
extractTotal(result)
