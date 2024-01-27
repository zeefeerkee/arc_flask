from flask import Flask, render_template, Response, request
import cv2
import argparse
import numpy as np
import threading
from pyiArduinoI2Cexpander import *
import RPi.GPIO as GPIO

GPIO.setwarnings(False) # отключаем показ любых предупреждений
GPIO.cleanup() # Подготавливаем пины GPIO.
GPIO.setmode (GPIO.BCM) # 


app = Flask(__name__)
camera = cv2.VideoCapture(0)
expander = pyiArduinoI2Cexpander(0x09)

for pin in range(3):
    expander.pinMode(pin, OUTPUT,  ANALOG)

motors = {'A': [21, 7], 'B': [10, 6], 'C': [11, 23]}
control_dict = {'f': [1, 0], 'b': [0, 1], 'm': [
    0, 0], 'e': [0, 0], 'c': [0, 0], 's': [0, 0]}

for motor in motors:
    for pin in motors[motor]:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)
GPIO.setup(12, GPIO.OUT)
s = GPIO.PWM(12, 150)
s.start(0)


def getFramesGenerator():
    """ Генератор фреймов для вывода в веб-страницу"""
    while True:
        success, frame = camera.read()  # Получаем фрейм с камеры
        if succes:
            # уменьшаем разрешение кадров
            frame = cv2.resize(frame, (1080, 720), interpolation=cv2.INTER_AREA)
	   # frame = frame.astype(np.float32) + (frame.astype(np.float32) * 0.3)
           # frame = np.clip(frame, 0, 255).astype(np.uint8)
            _, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')


def servo():
    global direction, servo
    if direction in 'c':
        s.ChangeDutyCycle(10)
    elif direction in 'e':
        s.ChangeDutyCycle(50)
    elif direction in 's':
        s.ChangeDutyCycle(0)
    

def control():
    global direction, control_dict, motors
    for motor in motors:
        pins = motors[motor]
        dir = control_dict[direction]
        GPIO.output(pins[0], dir[0])
        GPIO.output(pins[1], dir[1])


@app.route('/video_feed')
def video_feed():
    """ Генерируем и отправляем изображения с камеры"""
    return Response(getFramesGenerator(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/update_values', methods=['POST'])
def update_values():
    """ Обработка обновления значений direction и progress """
    global direction, progress, expander
    direction = (''.join(((request.form['direction']).split())[-1]).lower())[0]
    progress = int(request.form['progress'])
    
    control()
    servo()

    for pin in range(3):
        expander.analogWrite(pin, progress * 4095 / 100)
    
    print([direction, progress])
    return 'Success'


@app.route('/')
def index():
    """ Крутим html страницу """
    return render_template('index.html')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int,
                        default=5000, help="Running port")
    parser.add_argument("-i", "--ip", type=str,
                        default='127.0.0.1', help="Ip address")
    args = parser.parse_args()

    # Запускаем тред с демоном
    threading.Thread(target=update_values, daemon=True).start()
    # Запускаем flask приложение
    app.run(debug=False, host=args.ip, port=args.port)
