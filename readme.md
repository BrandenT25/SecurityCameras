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
