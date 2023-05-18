import cv2
import numpy as np
import pymongo
#import schedule
import time
import pywhatkit as pwk
import tkinter as tk
from tkinter import messagebox
from pynput import keyboard

# Set up MongoDB client and collection
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["face_recognition"]
mycol = mydb["registered_users"]

# Load face recognition model and camera
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
model = cv2.face.LBPHFaceRecognizer_create()
model.read("model.xml")
cap = cv2.VideoCapture(0)

#break using key
break_program = True
def on_press(key):
    global break_program
    if key == keyboard.Key.f1 and break_program:
        break_program = False

# Define function to recognize faces and send alerts
def recognize_and_alert():
    ret, img = cap.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x,y,w,h) in faces:
        face_img = gray[y:y+h, x:x+w]
        face_img = cv2.resize(face_img, (100, 100))
        label, confidence = model.predict(face_img)

        # Check if recognized face matches a registered user
        if confidence < 100:
            user = mycol.find_one({"label": label})
            name = user["name"]
            phone = user["phone"]
            message = f"Alert: {name} is seen in current location"
            pwk.sendwhatmsg_instantly(f"+91{phone}", message)

    # Show message box after each surveillance cycle
    messagebox.showinfo("Done", "Surveillance cycle complete")

# Define function to start surveillance loop
def start_surveillance():
    #key listner 
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    while break_program:
        #call the functions you need according to the logic and program flow
        recognize_and_alert()
        time.sleep(60)

# Define function to add a registered user to the database
def add_user():
    name = input("Enter name: ")
    phone = input("Enter phone number: ")
    label = input("Enter label: ")
    mycol.insert_one({"name": name, "phone": phone, "label": label})

# Define function to delete a registered user from the database
def delete_user():
    label = input("Enter label: ")
    mycol.delete_one({"label": label})

# Set up GUI
root = tk.Tk()
root.title("Face Recognition Surveillance System")

start_button = tk.Button(root, text="Start Surveillance", command=start_surveillance)
start_button.pack()

add_button = tk.Button(root, text="Add User", command=add_user)
add_button.pack()

delete_button = tk.Button(root, text="Delete User", command=delete_user)
delete_button.pack()

root.mainloop()
