import cv2
import mediapipe as mp
import numpy as np
import gradio as gr
import pandas as pd
import time
from datetime import datetime

from database import init_db, save_result, get_leaderboard

init_db()

leaderboard = pd.DataFrame(columns=["Name", "Reps", "Time"])

# ---------------- ANGLE ----------------
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = abs(radians * 180.0 / np.pi)

    if angle > 180:
        angle = 360 - angle

    return angle


# ---------------- MAIN FUNCTION ----------------
def analyze(video, name):

    cap = cv2.VideoCapture(video if video else 0)

    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()
    mp_draw = mp.solutions.drawing_utils

    counter = 0
    stage = "down"
    rep_times = []
    start_time = time.time()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.pose_landmarks:

            lm = results.pose_landmarks.landmark

            shoulder = [lm[11].x, lm[11].y]
            hip = [lm[23].x, lm[23].y]
            knee = [lm[25].x, lm[25].y]

            angle = calculate_angle(shoulder, hip, knee)
            print("Angle:", int(angle))

            if angle > 160:
                stage = "down"

            if angle < 90 and stage == "down":
                stage = "up"
                counter += 1
                rep_times.append(time.time() - start_time)

            mp_draw.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            cv2.putText(image, f"Reps: {counter}", (30,50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

        yield image, counter, stage

    cap.release()

    # ---------------- SAVE TO DB ----------------
    save_result(
        name,
        counter,
        "Gold" if counter > 20 else "Silver" if counter > 10 else "Bronze",
        "Good performance"
    )

    yield image, counter, "DONE"


# ---------------- LEADERBOARD ----------------
def show_board():
    data = get_leaderboard()
    return pd.DataFrame(data, columns=["Name","Reps","Badge","Time"])


# ---------------- UI ----------------
with gr.Blocks() as demo:

    gr.Markdown("# 🏆 AI Sit-Up Trainer (Placement Version)")

    video = gr.Video()
    name = gr.Textbox(label="Name")

    btn = gr.Button("Start")

    output_video = gr.Image()
    reps = gr.Number()
    stage = gr.Textbox()

    board = gr.DataFrame()

    btn.click(
        analyze,
        inputs=[video, name],
        outputs=[output_video, reps, stage]
    )

    gr.Button("Show Leaderboard").click(
        show_board,
        outputs=board
    )

demo.launch()