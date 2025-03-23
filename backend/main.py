# from ultralytics import YOLO
# model = YOLO("my_model.pt")
# results=model.track("./youtube_Gr0HpDM8Ki8_1920x1080_h264.mp4",conf=0.6,save=True,save_frames=True,save_txt=True,save_crop=True)

from ultralytics import YOLO
import cv2
import easyocr
import os
import csv
import re
import subprocess
import numpy as np
from datetime import timedelta
from per import monitor_folder_and_video
from PIL import Image,ImageOps,ImageEnhance

def start_monitoring():
    folder_path = "./runs/detect/track/video_frames"
    video_path = "./uploads/video.mp4"
    for percent in monitor_folder_and_video(folder_path, video_path):
        yield f"Progress: {percent:.2f}%"


def process_video(file_path):
    print("Processing video:", file_path)
    
    # Initialize YOLO model
    model = YOLO("my_model.pt")

    # Initialize EasyOCR reader with GPU support
    reader = easyocr.Reader(['en'], gpu=True)

    video_path = file_path
    results = model.track(video_path, conf=0.6, save=True, save_frames=True, save_txt=True,tracker="bytetrack.yaml",save_crop=True,project="runs/detect",name="track",exist_ok=True)

    # Extract video title from the path
    video_title = os.path.splitext(os.path.basename(file_path))[0]

    # Directories for saved frames and labels
    run_dir = "runs/detect/track"  # Adjust this if needed
    frames_dir = os.path.join(run_dir, "video_frames")
    labels_dir = os.path.join(run_dir, "labels")

    # Check if directories exist
    if not os.path.exists(frames_dir):
        os.makedirs(frames_dir)
    if not os.path.exists(labels_dir):
        os.makedirs(labels_dir)
    avi_output_path = os.path.join(run_dir, "video.avi")
    mp4_output_path = os.path.join(run_dir, "video.mp4")
    def convert_avi_to_mp4(input_folder, input_filename, output_filename):
        input_path = os.path.join(input_folder, input_filename)
        output_path = os.path.join(input_folder, output_filename)

        if not os.path.exists(input_path):
            print(f"Error: File '{input_path}' does not exist.")
            return

        try:
            # Run ffmpeg command to convert AVI to MP4
            command = [
                "ffmpeg",
                "-i", input_path,  # Input file
                "-c:v", "libx264",  # Video codec
                "-preset", "fast",  # Encoding speed
                "-crf", "23",  # Quality (lower is better, 23 is default)
                output_path  # Output file
            ]
            subprocess.run(command, check=True)
            print(f"Conversion successful! MP4 file saved at: {output_path}")
        except subprocess.CalledProcessError as e:
            print(f"An error occurred during conversion: {e}")
    convert_avi_to_mp4(run_dir, "video.avi", "video.mp4")


    # Function to preprocess the image for OCR
    def preprocess_image(image):
        pil_image = Image.fromarray(image)
        gray_image = ImageOps.grayscale(pil_image)
       
        enhancer = ImageEnhance.Contrast(gray_image)
        enhanced_image = enhancer.enhance(2.5)  # Adjust the factor as needed
        return np.array(enhanced_image)

    # Function to perform OCR on bounding boxes
    def segment_characters(image):
        # Find contours in the binary image
        contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Sort contours from left to right
        contours = sorted(contours, key=lambda ctr: cv2.boundingRect(ctr)[0])

        # Extract bounding boxes for each character
        char_images = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if h > 10 and w > 5:  # Filter out small contours (noise)
                char_images.append(image[y:y+h, x:x+w])

        return char_images

    # Function to validate and differentiate between 5 and S
    def validate_character(text, confidence):
        # Use confidence threshold to filter ambiguous results
        if len(text) == 1 and confidence > 0.7:  # Adjust confidence threshold as needed
            return text
        return text  # Return as-is if no specific rule applies

    # Function to perform OCR on bounding boxes
    def perform_ocr(image, bbox):
        x_center, y_center, width, height = bbox  # Extract the bounding box coordinates
        img_height, img_width = image.shape[:2]
        x1 = int((x_center - width / 2) * img_width)
        y1 = int((y_center - height / 2) * img_height)
        x2 = int((x_center + width / 2) * img_width)
        y2 = int((y_center + height / 2) * img_height)
        x1, y1, x2, y2 = max(0, x1), max(0, y1), min(img_width, x2), min(img_height, y2)
        roi = image[y1:y2, x1:x2]
        if roi.size == 0:
            return ""

        # Preprocess the region of interest
        preprocessed_roi = preprocess_image(roi)

        # Segment characters from the preprocessed image
        char_images = segment_characters(preprocessed_roi)

        # Perform OCR on segmented characters
        preprocessed_text = []
        for char_image in char_images:
            char_results = reader.readtext(char_image, detail=1, allowlist="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")
            for result in char_results:
                text, confidence = result[1], result[2]
                validated_text = validate_character(text, confidence)
                preprocessed_text.append(validated_text)

        return "".join(preprocessed_text)

    def validate_ocr_text(text):
        # Define the pattern: 2 alphabets, 2 numbers, 2 alphabets, 4 numbers
        pattern = r"^[A-Z]{2}[0-9]{2}[A-Z]{2}[0-9]{4}$"
        if re.match(pattern, text):
            return text
        return None

    # Function to clean OCR text
    def clean_text(text):
        cleaned_text = text.strip().replace("\n", "").replace("\r", "")
        return cleaned_text

    def calculate_timestamp(frame_number, fps):
        seconds = frame_number / fps
        return str(timedelta(seconds=seconds))

    # Function to write OCR results to a CSV file with timestamps
    def write_results_to_csv(results, output_file, fps):
        valid_prefixes = {
        "AN", "AP", "AR", "AS", "BR", "CH", "CG", "DN", "DD", "DL", "GA", "GJ", "HR", "HP", 
        "JK", "JH", "KA", "KL", "LA", "LD", "MP", "MH", "MN", "ML", "MZ", "NL", "OD", "OR", 
        "PY", "PB", "RJ", "SK", "TN", "TS", "TR", "UP", "UK", "WB", "TG"
    }
        written_plates=set()
        with open(output_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Write the header
            writer.writerow(["frame_nmr", "timestamp", "number_plate"])
            # Write the results
            for frame_number, texts in results.items():
                timestamp = calculate_timestamp(int(frame_number), fps)
                for text in texts:
                    if text[:2] in valid_prefixes and text not in written_plates:
                        writer.writerow([frame_number, timestamp, text])
                        written_plates.add(text)

    # Dictionary to store OCR results
    ocr_results = {}

    cap = cv2.VideoCapture(file_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()

    # Process each saved frame and extract text from bounding boxes
    for frame_file in sorted(os.listdir(frames_dir)):
        frame_path = os.path.join(frames_dir, frame_file)
        label_file = os.path.join(labels_dir, f"{video_title}_{os.path.splitext(frame_file)[0]}.txt")

        # Debugging: Print paths
        print(f"Processing frame: {frame_path}")
        print(f"Looking for label file: {label_file}")

        # Check if the label file exists
        if not os.path.exists(label_file):
            print(f"Label file not found: {label_file}")
            continue

        # Read the frame image
        image = cv2.imread(frame_path)

        # Read the bounding boxes from the label file
        with open(label_file, 'r') as f:
            boxes = [list(map(float, line.strip().split()[1:5])) for line in f.readlines()]

        frame_number = os.path.splitext(frame_file)[0]
        ocr_results[frame_number] = []
        for bbox in boxes:
            text = perform_ocr(image, bbox)
            cleaned_text = clean_text(text)
            validated_text = validate_ocr_text(cleaned_text)
            if validated_text:
                print(f"Frame {frame_number}, Validated text: {validated_text}")
                ocr_results[frame_number].append(validated_text)

            # Draw bounding box and text on the image
            x_center, y_center, width, height = bbox
            x1 = int((x_center - width / 2) * image.shape[1])
            y1 = int((y_center - height / 2) * image.shape[0])
            x2 = int((x_center + width / 2) * image.shape[1])
            y2 = int((y_center + height / 2) * image.shape[0])
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            if validated_text:
                cv2.putText(image, validated_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # Write OCR results to a CSV file
    output_csv_file = "ocr_results_with_timestamps.csv"
    write_results_to_csv(ocr_results, output_csv_file, fps)
    print(f"OCR results have been written to {output_csv_file}")
    return(output_csv_file)

