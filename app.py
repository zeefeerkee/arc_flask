from flask import Flask, render_template, Response, request
import cv2
import argparse
import threading
import ardriver
import time
import motors


app = Flask(__name__)
camera = cv2.VideoCapture(0)
driver = ardriver.Driver()
my_motors = [motors.Motor(0), motors.Motor(1), motors.Motor(2)]


def getFramesGenerator():
    """ Генератор фреймов для вывода в веб-страницу"""
    while True:
        time.sleep(0.01)    # ограничение fps (если видео тупит, можно убрать)
        success, frame = camera.read()  # Получаем фрейм с камеры
        if success:
            frame = cv2.resize(frame, (320, 240), interpolation=cv2.INTER_AREA)
            _, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """
    Генерируем и отправляем изображения с камеры
    """
    return Response(getFramesGenerator(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/update_values', methods=['POST'])
def update_values():
    """
    Обработка обновления значений direction и progress
    """
    direction = request.form['direction']
    progress = int(request.form['progress'])  # [0, 100, 10]

    # Скоро будет вынесено в класс Control
    if direction in ("FORWARD", "BACKWARD"):
        for motor in my_motors:
            motor.direction = 1 if direction in "FORWARD" else 0
            motor.velocity = progress * 31 // 100

    if "STOP" in direction:
        for motor in my_motors:
            motor.velocity = 0

    print(f"\n\nПолучен запрос {[direction, progress]}\n")

    values = [hash(motor) for motor in my_motors]
    package = ardriver.combine_bytes(*values)
    driver.write(package)

    print(f"Отправленный пакет {package}\nПолученный пакет {driver.read}")
    return 'Success'


@app.route('/')
def index():
    """
    Крутим html страницу 
    """
    return render_template('index.html')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-p', '--port', type=int, default=5000, help="Running port"
        )
    parser.add_argument(
        "-i", "--ip", type=str, default='127.0.0.1', help="Ip address"
        )
    args = parser.parse_args()

    # Запускаем тред демоном
    threading.Thread(target=update_values, daemon=True).start()
    # Запускаем flask приложение
    app.run(debug=False, host=args.ip, port=args.port)
