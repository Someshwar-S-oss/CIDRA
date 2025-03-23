import os
import subprocess

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

if __name__ == "__main__":
    print("Converting AVI to MP4...")
    # Define the folder and filenames
    folder = os.path.join("runs", "detect", "track")
    avi_filename = "video.avi"  # Replace with your AVI file name
    mp4_filename = "video.mp4"  # Replace with your desired MP4 file name

    # Call the conversion function
    convert_avi_to_mp4(folder, avi_filename, mp4_filename)