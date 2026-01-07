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

# --- CONFIGURATION ---
SERIAL_PORT = '/dev/ttyACM0'  
BAUD_RATE = 9600
SEARCH_RADIUS_KM = 5.0      

def haversine_km(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates in KM"""
    R = 6371
    dLat, dLon = radians(lat2 - lat1), radians(lon2 - lon1)
    a = sin(dLat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dLon / 2)**2
    return R * 2 * asin(sqrt(a))

# --- ADD TO CONFIGURATION ---
GOOGLE_MAPS_API_KEY = 'API_KEY'

def find_nearby_services(lat, lng):
    """Searches for safe spots using Google Places API"""
    if lat == 0.0 or lng == 0.0:
        print("⚠️ GPS Fix not yet acquired.")
        return

    
    endpoint = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    
    params = {
        'location': f"{lat},{lng}",
        'radius': SEARCH_RADIUS_KM * 1000,
        'type': 'gas_station|parking|police|hospital',
        'key': GOOGLE_MAPS_API_KEY
    }

    try:
        print(f"🛰️ Scanning Google Maps for Safe Spots at {lat}, {lng}...")
        response = requests.get(endpoint, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            
            if results:
                msg = f"EMERGENCY: {len(results)} spots found nearby:\\n"
                
                # Process top 4 results
                for place in results[:4]:
                    name = place.get('name', 'Unknown Spot').replace("&", "&amp;")
                    address = place.get('vicinity', 'Nearby')
                    # Get the primary type and clean it up
                    place_type = place.get('types', ['Spot'])[0].replace("_", " ").upper()
                    
                    msg += f"- {place_type}: {name} ({address})\\n"
                
                os.system(f'zenity --info --title="GOOGLE MAPS: SAFE SPOTS" --text="{msg}" --timeout=15 &')
                print("✅ Found spots via Google and triggered pop-up.")
            else:
                print("❌ No spots found in radius via Google.")
                os.system(f'zenity --warning --title="No Spots" --text="No safe spots found within {SEARCH_RADIUS_KM}km" --timeout=5 &')
        else:
            print(f"⚠️ Google API Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Google Search Error: {e}")

    radius_m = int(SEARCH_RADIUS_KM * 1000)
    
    # Expanded query: Parking, Fuel, Police, Rest Areas, Hospitals
    query = f"""[out:json][timeout:25];
    (
      node["amenity"~"parking|fuel|police|rest_area|hospital"](around:{radius_m},{lat},{lng});
      way["amenity"~"parking|fuel|police|rest_area|hospital"](around:{radius_m},{lat},{lng});
    );
    out center;"""
    
    overpass_url = "https://overpass.kumi.systems/api/interpreter"
    
    try:
        print(f"🛰️ Scanning {SEARCH_RADIUS_KM}km for Safe Spots at {lat}, {lng}...")
        response = requests.get(overpass_url, params={'data': query}, timeout=25)
        
        if response.status_code == 200:
            data = response.json()
            elements = data.get('elements', [])
            
            if elements:
                msg = f"EMERGENCY: {len(elements)} spots found nearby:\\n"
                # Process top 4 results
                for e in elements[:4]:
                    amenity = e.get('tags', {}).get('amenity', 'Safe Spot').replace("_", " ").upper()
                    raw_name = e.get('tags', {}).get('name', f"Nearby {amenity}")
                    # Fix for Zenity crash on '&'
                    safe_name = raw_name.replace("&", "&amp;")
                    msg += f"- {amenity}: {safe_name}\\n"
                
                os.system(f'zenity --info --title="SAFE SPOTS DETECTED" --text="{msg}" --timeout=15 &')
                print("✅ Found spots and triggered pop-up.")
            else:
                print("❌ No spots found in radius.")
                os.system(f'zenity --warning --title="No Spots" --text="No safe spots found within {SEARCH_RADIUS_KM}km" --timeout=5 &')
        else:
            print(f"⚠️ API Error: {response.status_code}")
    except Exception as e:
        print(f"❌ GPS Search Error: {e}")

# --- INITIALIZE SYSTEM ---
try:
    arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
    time.sleep(2)
    print("✅ System Online")
except:
    print("❌ Serial Connection Failed. Check USB.")
    exit()

detector = dlib.get_frontal_face_detector()
# Ensure this file is in the same directory
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
cap = cv2.VideoCapture(0)

# State Variables
sleep = drowsy = active = 0
status = "Initializing"
curr_lat = curr_lng = 0.0
motor_stopped = False
drowsy_or_sleep_frame_count = 0

def compute(ptA, ptB):
    return np.linalg.norm(ptA - ptB)

def blinked(a, b, c, d, e, f):
    up = compute(b, d) + compute(c, e)
    down = compute(a, f)
    ratio = up / (2.0 * down)
    return 2 if ratio > 0.25 else (1 if 0.21 < ratio <= 0.25 else 0)

# --- MAIN LOOP ---
try:
    arduino.write(b'M') # Start Motor
    while True:
        ret, frame = cap.read()
        if not ret: break

        # 1. Update GPS coordinates from Arduino
        if arduino.in_waiting > 0:
            try:
                line = arduino.readline().decode('utf-8', errors='ignore').strip()
                if line.startswith('{'):
                    data = json.loads(line)
                    curr_lat, curr_lng = data['lat'], data['lng']
            except: pass

        # 2. Face Landmark Processing
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)

        if len(faces) > 0:
            landmarks = face_utils.shape_to_np(predictor(gray, faces[0]))
            left_blink = blinked(landmarks[36], landmarks[37], landmarks[38], landmarks[41], landmarks[40], landmarks[39])
            right_blink = blinked(landmarks[42], landmarks[43], landmarks[44], landmarks[47], landmarks[46], landmarks[45])

            if left_blink == 0 or right_blink == 0:
                sleep += 1
                drowsy = active = 0
                if sleep > 6: status = "SLEEPING !!!"
            elif left_blink == 1 or right_blink == 1:
                drowsy += 1
                sleep = active = 0
                if drowsy > 6: status = "Drowsy !"
            else:
                active += 1
                sleep = drowsy = 0
                if active > 6: status = "Active :)"

            # 3. Decision Control Logic
            if status in ["SLEEPING !!!", "Drowsy !"]:
                drowsy_or_sleep_frame_count += 1
                
                # Action at Frame 40: Buzzer + Search
                if drowsy_or_sleep_frame_count == 40:
                    arduino.write(b'B') 
                    find_nearby_services(curr_lat, curr_lng)
                
                # Action at Frame 80: Stop Motor
                if drowsy_or_sleep_frame_count >= 80 and not motor_stopped:
                    arduino.write(b'S') 
                    motor_stopped = True
            else:
                # Driver is Active: Reset
                if motor_stopped:
                    arduino.write(b'M') 
                    motor_stopped = False
                
                if drowsy_or_sleep_frame_count > 0:
                    arduino.write(b'b') # Stop Buzzer
                
                drowsy_or_sleep_frame_count = 0

        # UI Visualization
        cv2.putText(frame, f"Status: {status}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)
        cv2.putText(frame, f"GPS Fix: {'YES' if curr_lat != 0 else 'SEARCHING'}", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)
        
        cv2.imshow("Driver Monitor", frame)
        if cv2.waitKey(1) == 27: break

finally:
    print("\nShutting down...")
    if 'arduino' in locals():
        arduino.write(b'O') # Emergency Stop
        arduino.close()
    cap.release()
    cv2.destroyAllWindows()
