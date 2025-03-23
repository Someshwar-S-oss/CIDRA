# CIDRA
## Chatbot In Data Retrieval and Analysis
BITS-TechXcelerate Hackathon Project


### Problem Statement:
With the rapid increase in the number of data collected with time, managing and analyzing vast quantities of data has become a significant challenge for management, law enforcement, and other sectors. Existing systems often fail to provide an intuitive and efficient way to retrieve and analyze such data.

### Proposed Solution:
We address the challenges by developing a comprehensive solution that processes input video files to identify objects and extract details such as their license plate number, make, model, and the exact timestamp at which they were recorded. This extracted information is stored in a MySQL database for structured access.
The innovation lies in integrating this database with a Large Language Model (LLM)-powered chatbot. Users can interact with the chatbot in natural language to retrieve and analyze data without requiring SQL expertise. The chatbot seamlessly translates user queries into SQL commands, executes them on the database, and provides the results in an accessible and user-friendly format.
This project strives to simplify data retrieval and analysis while making it accessible to a broader audience, transforming complex database interactions into a conversational experience.

### Technologies and Tools Used:
- Frontend
	- React
	- NextJS
	- Tailwind CSS
- Backend
	- Python
- Libraries
	- Flask
	- CORS
	- Ollama
	- YOLOv11
	- OpenCV
	- Pillow
	- EasyOCR
	- Selenium
- Database
	- MySQL
- LLM
	- llama 3.1


### Workflow
1. **User Upload**:
    - Users upload videos via the frontend interface.
2. **Video Tracking**:
    - YOLO model tracks Number plates on the cars in the video.
    - Outputs frames, bounding boxes, and cropped images.
3. **OCR Processing**:
    - Extracts text from bounding boxes using EasyOCR.
    - Validates text against predefined patterns (e.g., license plate format).
4. **Results Export**:
    - Writes OCR results to  a csv file and uploads it to a MySQL database.
5. **Progress Monitoring**:
    - Displays real-time progress of video processing.
6. **Results Display**:
    - Ask the chatbot about the objects in the video such as Number plates,make/model,etc

### Prerequisites

1. Windows OS
2. Miniconda
3. NPM installation
4. Ollama installation

### Installation

1. Edit config.txt and set Miniconda path
2. Run install.bat

### Run the environment

1. Run start.bat

### Hardware Requirements

- Dedicated GPU with minimum 8GB VRAM
