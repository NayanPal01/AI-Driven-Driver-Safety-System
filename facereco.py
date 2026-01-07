import os
os.environ["QT_QPA_PLATFORM"] = "xcb"

import cv2
import numpy as np
import dlib
from imutils import face_utils
import time
import serial
import json
import requests
from math import radians, cos, sin, asin, sqrt

# ================= CONFIG =================
SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 9600
SEARCH_RADIUS_KM = 5.0
GOOGLE_MAPS_API_KEY = "API_KEY"
# ========================================

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371
    dLat, dLon = radians(lat2-lat1), radians(lon2-lon1)
    a = sin(dLat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dLon/2)**2
    return R * 2 * asin(sqrt(a))

def find_nearby_services(lat, lng):
    if lat == 0.0 or lng == 0.0:
        print("⚠️ GPS Fix not yet acquired.")
        return

    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": int(SEARCH_RADIUS_KM * 1000),
        "type": "gas_station|parking|police|hospital",
        "key": GOOGLE_MAPS_API_KEY
    }

    try:
        print(f"🛰️ Searching safe spots at {lat},{lng}")
        res = requests.get(url, params=params, timeout=10)

        if res.status_code == 200:
            results = res.json().get("results", [])

            if results:
                msg = f"EMERGENCY: {len(results)} safe spots found:\n"
                for p in results[:4]:
                    msg += f"- {p.get('name')} ({p.get('vicinity')})\n"

                os.system(f'zenity --info --title="SAFE SPOTS" --text="{msg}" --timeout=15 &')
            else:
                print("❌ No spots found.")
        else:
            print("⚠️ Google API Error", res.status_code)

    except Exception as e:
        print("❌ GPS Search Error:", e)

# ================= SYSTEM INIT =================
try:
    arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
    time.sleep(2)
    print("✅ System Online")
except:
    print("❌ Serial Connection Failed")
    exit()

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
cap = cv2.VideoCapture(0)

sleep = drowsy = active = 0
status = "Initializing"
curr_lat = curr_lng = 0.0
motor_stopped = False
drowsy_frames = 0

def compute(p1, p2):
    return np.linalg.norm(p1 - p2)

def blinked(a,b,c,d,e,f):
    up = compute(b,d) + compute(c,e)
    down = compute(a,f)
    ratio = up / (2.0 * down)
    if ratio > 0.25: return 2
    if ratio > 0.21: return 1
    return 0

# ================= MAIN LOOP =================
try:
    arduino.write(b'M')

    while True:
        ret, frame = cap.read()
        if not ret: break

        if arduino.in_waiting:
            try:
                data = json.loads(arduino.readline().decode())
                curr_lat, curr_lng = data['lat'], data['lng']
            except:
                pass

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)

        if faces:
            lm = face_utils.shape_to_np(predictor(gray, faces[0]))
            l = blinked(lm[36],lm[37],lm[38],lm[41],lm[40],lm[39])
            r = blinked(lm[42],lm[43],lm[44],lm[47],lm[46],lm[45])

            if l == 0 or r == 0:
                sleep += 1; drowsy = active = 0
                if sleep > 6: status = "SLEEPING"
            elif l == 1 or r == 1:
                drowsy += 1; sleep = active = 0
                if drowsy > 6: status = "DROWSY"
            else:
                active += 1; sleep = drowsy = 0
                if active > 6: status = "ACTIVE"

            if status in ["SLEEPING", "DROWSY"]:
                drowsy_frames += 1

                if drowsy_frames == 40:
                    arduino.write(b'B')
                    find_nearby_services(curr_lat, curr_lng)

                if drowsy_frames >= 80 and not motor_stopped:
                    arduino.write(b'S')
                    motor_stopped = True
            else:
                if motor_stopped:
                    arduino.write(b'M')
                    motor_stopped = False
                arduino.write(b'b')
                drowsy_frames = 0

        cv2.putText(frame, f"Status: {status}", (20,40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)
        cv2.imshow("Driver Monitor", frame)

        if cv2.waitKey(1) == 27:
            break

finally:
    print("Shutting down...")
    if 'arduino' in locals():
        arduino.write(b'O')
        arduino.close()
    cap.release()
    cv2.destroyAllWindows()
