
import face_recognition
import cv2
import numpy as np
import threading
import pygame
import os
import speech_recognition as sr
import pyttsx3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load images of the owner and other individuals
owner_image = face_recognition.load_image_file(r"#insert the path of the image(.jpg)")
other_image = face_recognition.load_image_file(r"#insert the path of the image(.jpg)")

# Encode face features
owner_encoding = face_recognition.face_encodings(owner_image)[0]
other_encoding = face_recognition.face_encodings(other_image)[0]

known_face_encodings = [owner_encoding]
known_face_names = ["surya"]

# Initialize the alarm status and password
alarm_triggered = False
correct_password = "surya"

# Initialize pygame mixer
pygame.mixer.init()

# Initialize text-to-speech engine
engine = pyttsx3.init()

def send_security_alert_email():
    sender_email = 'codecrackersno1@gmail.com'
    sender_password = 'jkcqjnigkynhtatn'
    receiver_email = 'suryavardhankarella@gmail.com'
    subject = 'Security Breach Alert'
    message = 'An incorrect password was entered to stop the alarm.'

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # Attach the message body
    msg.attach(MIMEText(message, 'plain'))

    # Connect to the SMTP server
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)

        # Send the email
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        print('Email sent successfully.')

    except Exception as e:
        print('Email could not be sent. Error:', str(e))

    finally:
        server.quit()                                              

def speak_text(text):
    engine.say(text)
    engine.runAndWait()

def play_alarm_sound():
    global alarm_triggered
    pygame.mixer.music.load(r'#insert alarm sound(.wav')
    pygame.mixer.music.play(-1)  # Play in a loop
    while alarm_triggered:
        print("Listening for password...")
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()

        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

        try:
            entered_password = recognizer.recognize_google(audio).strip()
            print("Recognized:", entered_password)
            if entered_password.lower() == correct_password.lower():
                alarm_triggered = False
                print("Access granted. Password correct.")
                speak_text("Access granted. Password correct.")
                pygame.mixer.music.stop()  # Stop the alarm sound
                break
            else:
                print("Incorrect password. Alarm still active.")
                speak_text("Incorrect password. Alarm still active.")
                send_security_alert_email()

        except sr.UnknownValueError:
            print("Sorry, could not understand audio.")
        except sr.RequestError as e:
            print("Could not request results: {0}".format(e))

# Create a thread for the alarm sound
alarm_thread = threading.Thread(target=play_alarm_sound)

# Initialize camera
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()

    # Find all face locations and encodings in the frame
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # Compare face encoding with known face encodings
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

        name = "Unknown"

        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]

        # Draw rectangle and label on the frame
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)

        if name == "Unknown":
            if not alarm_triggered:
                alarm_triggered = True
                alarm_thread = threading.Thread(target=play_alarm_sound)
                alarm_thread.start()
        else:
            if alarm_triggered:
                alarm_triggered = False
                pygame.mixer.music.stop()  # Stop the alarm sound

    cv2.imshow("Face Recognition", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
