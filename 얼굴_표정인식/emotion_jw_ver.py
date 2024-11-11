import cv2
import dlib
import numpy as np
from PIL import ImageFont, ImageDraw, Image
import os

# 파일 경로 설정 (영어 경로로 변경하지 않음)
os.chdir('C:/Users/d/Desktop/kjw/황종철강사님/실습/1일차/source/')
predictor_path = 'shape_predictor_68_face_landmarks.dat'

if not os.path.exists(predictor_path):
    print(f"Error: {predictor_path} 파일을 찾을 수 없습니다.")
    exit()

detector = dlib.get_frontal_face_detector()
try:
    predictor = dlib.shape_predictor(predictor_path)
except RuntimeError as e:
    print(f"Error loading shape predictor: {e}")
    exit()

# 웹캠 열기
cap = cv2.VideoCapture(0)

# 한글 폰트 설정
fontpath = "C:/Windows/Fonts/gulim.ttc"
if not os.path.exists(fontpath):
    print(f"Error: {fontpath} 폰트 파일을 찾을 수 없습니다.")
    exit()
font = ImageFont.truetype(fontpath, 20)

# 감정 구분 함수 (수정된 로직)
def detect_emotion(landmarks):
    mouth_width = np.linalg.norm(landmarks[48] - landmarks[54])
    mouth_height = np.linalg.norm(landmarks[51] - landmarks[57])
    left_eye_height = np.linalg.norm(landmarks[37] - landmarks[41])
    right_eye_height = np.linalg.norm(landmarks[43] - landmarks[47])

    mouth_left = landmarks[48]
    mouth_right = landmarks[54]
    mouth_center_top = landmarks[51]
    mouth_curve = ((mouth_left[1] + mouth_right[1]) / 2) - mouth_center_top[1]

    left_eyebrow_pos = landmarks[21][1] - landmarks[37][1]
    right_eyebrow_pos = landmarks[22][1] - landmarks[43][1]

    # 눈과 눈썹 간의 거리 계산
    eye_brow_distance_left = left_eye_height - left_eyebrow_pos
    eye_brow_distance_right = right_eye_height - right_eyebrow_pos

    emotion = "보통"

    # 로그 출력
    print(f"mouth_width: {mouth_width}, mouth_height: {mouth_height}, "
        f"mouth_curve: {mouth_curve:.2f}, "
        f"left_eye_height: {left_eye_height}, right_eye_height: {right_eye_height}, "
        f"left_eyebrow_pos: {left_eyebrow_pos}, right_eyebrow_pos: {right_eyebrow_pos}, "
        f"eye_brow_distance_left: {eye_brow_distance_left}, eye_brow_distance_right: {eye_brow_distance_right}")

    # 기쁨 인식 기준
    if (mouth_width > 30 and mouth_height > 15 and 
        mouth_curve < 3 or 
        (left_eyebrow_pos <-15 and right_eyebrow_pos <-15) and  # 왼쪽 또는 오른쪽 눈썹이 올라간 경우
        (left_eye_height < 5.5 and right_eye_height < 5.5) and 
        (eye_brow_distance_left < 20 and eye_brow_distance_right < 20)):  # 눈과 눈썹 간의 거리 기준
        emotion = "기쁨"

    # 슬픔 인식 기준
    elif ((left_eye_height < 4.5 and right_eye_height < 4.5) and  # 양쪽 눈이 모두 작을 때
        (mouth_curve > 9) or  # 입꼬리가 내려가면
        (-10 < left_eyebrow_pos < -2 and -10<right_eyebrow_pos < -2) and  # 두 눈썹 내려간 경우
        (eye_brow_distance_left <25 and eye_brow_distance_right < 25)):  # 눈과 눈썹 간의 거리 기준
        emotion = "슬픔"

    # 분노 인식 기준
    elif (mouth_height <15 and mouth_width >50 and
        (left_eye_height > 6 and right_eye_height > 6) and
        (left_eyebrow_pos < -5 and right_eyebrow_pos < -5)or
        (eye_brow_distance_left <20 and eye_brow_distance_right < 20)):  # 눈과 눈썹 간의 거리 기준
        emotion = "분노"

    return emotion

if not cap.isOpened():
    print("Error: 웹캠을 열 수 없습니다.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: 프레임을 가져올 수 없습니다.")
        break

    # 카메라 좌우 반전
    frame = cv2.flip(frame, 1)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    for face in faces:
        x, y, w, h = face.left(), face.top(), face.width(), face.height()

        # 얼굴 영역 랜드마크 추출
        try:
            landmarks = predictor(gray, face)
        except:
            print("Error: 얼굴 랜드마크 추출 실패")
            continue
        landmarks = np.array([[p.x, p.y] for p in landmarks.parts()])

        # 감정 인식
        emotion = detect_emotion(landmarks)

        # 얼굴에 사각형 그리기
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # 얼굴 랜드마크 시각화 (디버깅용, 필요 시 주석 처리)
        for (x_point, y_point) in landmarks:
            cv2.circle(frame, (x_point, y_point), 1, (0, 0, 255), -1)

        # 감정 텍스트 그리기 (Pillow로 한글 지원)
        img_pillow = Image.fromarray(frame)
        draw = ImageDraw.Draw(img_pillow)
        text = emotion
        draw.text((x, y - 30), text, font=font, fill=(0, 255, 0, 0))
        frame = np.array(img_pillow)

    # 영상 출력
    cv2.imshow("Emotion Recognition", frame)

    # 'q' 키를 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
