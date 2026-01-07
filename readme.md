# 🚗 AI-Powered Driver Safety System

An intelligent real-time driver monitoring and accident prevention system that detects driver drowsiness using AI-based computer vision, triggers safety actions, and provides driver behavior analytics through an interactive web dashboard.

---

## 📌 Problem Statement

Driver drowsiness is one of the leading causes of road accidents worldwide.  
Traditional warning systems often react too late or fail to provide meaningful safety intervention.

This project proposes an automated driver safety solution that continuously monitors the driver's alertness, detects drowsiness in real time, and takes immediate corrective actions to prevent accidents.

---

## 💡 Solution Overview

The system integrates computer vision, embedded hardware, intelligent decision logic, and a web interface to create a complete safety platform.

### System Workflow

1. Camera captures driver's face in real time  
2. Dlib detects facial landmarks and eye state  
3. Eye-closure duration is analyzed for drowsiness detection  
4. If drowsiness exceeds the safety threshold:
   - 🔊 Buzzer alarm is activated  
   - 🛑 Vehicle engine is stopped via motor control  
   - 🗺️ Nearest safe locations are fetched using GPS  
5. All events are recorded and displayed on the Streamlit web dashboard

---

## 🧠 Key Features

- Real-time drowsiness detection using AI-based facial landmark analysis  
- Automatic engine shutdown for accident prevention  
- Audio alert system using buzzer  
- GPS-based safe location display  
- Interactive web dashboard for driver behavior monitoring  
- Analytics for most frequent drowsiness time and safety interventions  

---

## 🛠️ Technologies & Hardware

### Software
- Python  
- Dlib (Facial Landmark Detection)  
- OpenCV  
- NumPy  
- Streamlit  

### Hardware
- Raspberry Pi  
- Camera Module  
- Motor (Engine Simulation)  
- Buzzer  
- GPS Module  

---


## 🧩 System Architecture Diagram

```text
+--------------------+
|      Camera        |
| (Driver Face Feed) |
+---------+----------+
          |
          v
+---------------------------+
|     Raspberry Pi          |
|  - Video Processing       |
|  - Dlib Facial Landmarks  |
|  - Drowsiness Analysis    |
+-------------+-------------+
              |
     +--------+--------+
     |                 |
     v                 v
+------------+   +--------------+
|   Buzzer   |   |    Motor     |
| (Alarm)    |   | (Engine Ctrl)|
+------------+   +--------------+
              |
              v
        +----------------+
        |     GPS        |
        |  Location Data|
        +--------+-------+
                 |
                 v
+----------------------------------+
|     Streamlit Web Dashboard      |
|  - Alert History                 |
|  - Drowsiness Analytics          |
|  - Engine Control Events         |
|  - Safety Insights               |
+----------------------------------+

```

## 📊 Web Dashboard

The Streamlit-based dashboard provides real-time and historical insights into driver behavior and safety events:

- **Live driver status:** Alert / Drowsy / Engine Stopped  
- **Timeline of drowsiness events**  
- **Most frequent drowsiness time analysis**  
- **Engine control & alert history**  
- **GPS-based safe location display**  
- **System health and activity logs**

---

## 🧪 Applications

- Smart vehicles  
- Fleet management systems  
- Driver safety monitoring  
- Accident prevention solutions  

---

## 🚀 Future Enhancements

- Deep learning–based eye-state classification  
- Cloud-based storage and multi-vehicle tracking  
- Mobile app integration  
- Voice alerts & adaptive safety thresholds  

---

## 👨‍💻 Author

**Nayan Pal**  
AI/ML Developer | Computer Vision | Embedded Systems
