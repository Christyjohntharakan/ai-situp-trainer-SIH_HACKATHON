import cv2
import mediapipe as mp
import numpy as np

mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils


def calculate_angle(a, b, c):

    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(
        c[1]-b[1],
        c[0]-b[0]
    ) - np.arctan2(
        a[1]-b[1],
        a[0]-b[0]
    )

    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180:
        angle = 360 - angle

    return angle


def start_detection():

    cap = cv2.VideoCapture(0)

    pose = mp_pose.Pose(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    counter = 0
    stage = "down"

    while cap.isOpened():

        ret, frame = cap.read()

        if not ret:
            break

        image = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        results = pose.process(image)

        image = cv2.cvtColor(
            image,
            cv2.COLOR_RGB2BGR
        )

        if results.pose_landmarks:

            landmarks = results.pose_landmarks.landmark

            shoulder = [
                landmarks[
                    mp_pose.PoseLandmark.LEFT_SHOULDER.value
                ].x,
                landmarks[
                    mp_pose.PoseLandmark.LEFT_SHOULDER.value
                ].y
            ]

            hip = [
                landmarks[
                    mp_pose.PoseLandmark.LEFT_HIP.value
                ].x,
                landmarks[
                    mp_pose.PoseLandmark.LEFT_HIP.value
                ].y
            ]

            knee = [
                landmarks[
                    mp_pose.PoseLandmark.LEFT_KNEE.value
                ].x,
                landmarks[
                    mp_pose.PoseLandmark.LEFT_KNEE.value
                ].y
            ]

            angle = calculate_angle(
                shoulder,
                hip,
                knee
            )

            if angle > 150:
                stage = "down"

            if angle < 90 and stage == "down":
                stage = "up"
                counter += 1

            mp_draw.draw_landmarks(
                image,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS
            )

            cv2.putText(
                image,
                f"Reps: {counter}",
                (20,50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0,255,0),
                2
            )

            cv2.putText(
                image,
                f"Angle: {int(angle)}",
                (20,100),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255,0,0),
                2
            )

        cv2.imshow(
            "AI Situp Trainer",
            image
        )

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    start_detection()