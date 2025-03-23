import os
import time
import cv2

def monitor_folder_and_video(folder_path, video_path):
    def get_total_frames(video_path):
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Unable to open video file: {video_path}")
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.release()
            return total_frames
        except Exception as e:
            print(f"Error: {e}")
            return -1

    def get_file_count(folder_path):
        file_count = 0
        for _, _, files in os.walk(folder_path):
            file_count += len(files)
        return file_count

    total_frames = get_total_frames(video_path)
    if total_frames == -1:
        print("Failed to retrieve total frames. Exiting.")
        return

    try:
        while True:
            number_of_files = get_file_count(folder_path)
            percentage = (number_of_files / total_frames) * 100
            yield percentage
            if number_of_files >= total_frames:
                print("Processing complete!")
                break
            time.sleep(0.1)  # Wait for 100ms
    except KeyboardInterrupt:
        print("Stopped monitoring the folder.")