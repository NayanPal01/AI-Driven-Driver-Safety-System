🚗 AI-Powered Driver Safety & Drowsiness Detection System

An intelligent real-time driver monitoring system designed to detect drowsiness, prevent accidents, and analyze driver behavior using AI, embedded systems, and a web dashboard.

📌 Problem Statement

Driver drowsiness is one of the leading causes of road accidents worldwide.
Most systems either warn the driver too late or provide no actionable response.

This project builds a fully automated safety system that:

Detects drowsiness in real time

Triggers alerts

Stops the vehicle engine if the driver becomes unresponsive

Displays safe nearby locations

Records all driver activity for analysis on a web dashboard

💡 Solution Overview

The system uses computer vision + embedded control to monitor the driver’s eyes continuously.

Working Flow

Camera captures driver's face

Dlib detects facial landmarks & eye state

Drowsiness is calculated using eye-closure duration

If threshold exceeded:

🔊 Buzzer alarm activates

🛑 Engine is automatically stopped via motor control

🗺️ Nearest safe locations are fetched using GPS

All events are logged and visualized on a Streamlit dashboard

🧠 Key Features

Real-time drowsiness detection

Automatic engine shutdown on prolonged drowsiness

Audio alert system using buzzer

GPS-based safe location display

Web dashboard with driver behavior analytics

Tracks most frequent drowsiness time, alert history, and safety actions

🛠️ Tech Stack & Hardware
Software

Python

Dlib – facial landmark & eye detection

Streamlit – web dashboard

OpenCV

NumPy

Hardware

Raspberry Pi

Camera Module

Motor (simulates engine control)

Buzzer

GPS Module

🧪 System Architecture
Camera → Raspberry Pi → Dlib (Eye Detection)
            ↓
    Drowsiness Analysis Engine
            ↓
    ┌────────────┬────────────┐
 Alarm (Buzzer)  Motor Control (Engine Stop)
            ↓
        GPS Location
            ↓
     Streamlit Web Dashboard

📊 Dashboard Insights

The web dashboard provides:

Driver alert history

Most frequent drowsiness time

Number of engine shutdowns

Safety intervention statistics

Live system status

🧩 Applications

Smart vehicles

Fleet management systems

Driver safety monitoring

Accident prevention systems

🚀 Future Improvements

Deep learning–based eye state classification

Cloud storage & multi-vehicle tracking

Mobile app integration

Voice alerts & adaptive safety thresholds
