from flask import Flask, render_template, Response, request
import cv2
import argparse
import threading
import ardriver


app = Flask(__name__)
camera = cv2.VideoCapture(0)
motor = ardriver.ArduinoDriver()


def getFramesGenerator():
    """ Генератор фреймов для вывода в веб-страницу"""
    while True:
        success, frame = camera.read()  # Получаем фрейм с камеры
        if succes:
            # уменьшаем разрешение кадров
            frame = cv2.resize(frame, (1080, 720), interpolation=cv2.INTER_AREA)
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
    direction = ''.join(((request.form['direction']).split())[-1])
    progress = int(request.form['progress'])  # [0, 100, 10]

    print([direction, progress])
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
