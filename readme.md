# Security Camera System with Facial Recognition

A modular security camera system built with Python that handles real-time object detection, facial recognition, and automatic person clustering with configurable alerts.

## Overview

This project started as a way to learn more about computer vision and multi-threaded Python applications. It's grown into a working security camera system that can detect objects, recognize faces, automatically group unknown people together, and send alerts based on who it sees.

The whole thing is built around a pipeline architecture using Python queues to pass frames between different processing scripts. Right now it works well for a single camera setup, but I'm planning to refactor it into a more scalable microservices architecture.

## What It Does

The system captures video from a camera and splits the processing into parallel pipelines. One pipeline handles object detection with YOLO and feeds into FFmpeg for live streaming to a web interface. The other pipeline records video while also processing faces.

For facial recognition, I'm using InsightFace to detect and encode faces. MediaPipe handles the cropping and filtering to clean up the face images before they get processed. Once I have clean face embeddings, I use cosine similarity to automatically cluster similar faces together and store them as numpy arrays.

There's also a simple alert system built on a JSON database. You can mark faces as verified, give them names, and set whether they should trigger alerts. When the system detects a face marked for alerts, it sends a notification.

The web interface is pretty basic right now but it shows the live camera feed with the YOLO detections overlaid.

## Current Architecture

```
Camera Feed
    |
    +-- YOLO Detection --> FFmpeg Stream --> Web Interface
    |
    +-- Video Recording
         |
         +-- Face Detection (InsightFace)
              |
              +-- Face Cropping (MediaPipe)
                   |
                   +-- Cosine Similarity Clustering
                        |
                        +-- NPY Storage & Alert Check --> Notifications
```

## Tech Stack

- Python with threading and queues
- OpenCV for video capture
- YOLO for object detection
- InsightFace for facial recognition
- MediaPipe for face preprocessing
- FFmpeg for video streaming
- NumPy for clustering and storage

## Installation

You'll need Python 3.8 or higher and the following packages:

```
opencv-python
insightface
mediapipe
numpy
```

FFmpeg also needs to be installed on your system for the streaming functionality.

You'll also need to download the YOLO and InsightFace model files and place them in the `models/` directory.

## Project Structure

```
project/
├── data/
│   ├── clusters/              # NPY cluster files with JSON metadata
│   ├── faces/
│   │   ├── unverified/        # Detected faces pending verification
│   │   └── verified/          # Verified face images and embeddings (NPY)
│   └── people/                # JSON database of known people and metadata
│
├── models/                    # YOLO and InsightFace model files
│
├── pipelines/
│   ├── alert.py              # Alert checking and notification system
│   ├── camera.py             # Camera capture and frame distribution
│   ├── enroll.py             # Face enrollment pipeline
│   ├── faceRecognition.py    # Face detection and recognition
│   ├── ffmpegProducer.py     # FFmpeg stream generation
│   ├── recorder.py           # Video recording pipeline
│   ├── retrievePerson.py     # Person lookup from database
│   ├── server.py             # Web server
│   └── yolo.py               # YOLO object detection
│
├── recordings/               # Video recordings organized by day (hourly segments)
│
└── tools/
    ├── merge.py              # Merge people clusters
    └── verify_clusters.py    # Verify and name face clusters
```

## Future Plans

The current implementation works but isn't designed to scale beyond a single camera. Here's what I'm working on next:

### Microservices with Docker

Breaking down the camera processing into individual Docker containers. Each camera will run in its own container with just the capture, recording, YOLO, and FFmpeg components. This should make it way easier to add multiple cameras without everything running in one process.

### Redis for Pipeline Communication

Replacing the Python queues with Redis. This is necessary for the Docker setup and should also improve performance when dealing with multiple camera streams.

### Proper Database Layer

Right now everything is stored in JSON files and numpy arrays which isn't great. Planning to move to PostgreSQL for storing face vectors and SQLite for the metadata like names, verification status, and reference images.

### Flask API and Better Web Interface

Building out a proper Flask backend with REST APIs for managing cameras, verifying faces, setting alerts, and all the other management tasks. The web interface will be rebuilt to actually use these APIs instead of the hacky helper functions it uses now.

## Notes

This is still pretty rough around the edges. The code needs cleanup and the architecture needs the refactor I mentioned above. But it works for what I need right now and it's been a good learning project for understanding video processing pipelines and facial recognition systems.

## License

MIT License

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.