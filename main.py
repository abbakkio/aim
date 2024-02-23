from utils.grabbers.mss import Grabber
from utils.fps import FPS
from utils.controls.mouse.win32 import MouseControls
from utils.win32 import WinHelper
import keyboard
from utils.time import sleep
import cv2
import multiprocessing
import numpy as np
import time

# CONFIG
GAME_WINDOW_TITLE = "Aim Trainer"  # aimlab_tb, FallGuys_client, Counter-Strike: Global Offensive - Direct3D 9, etc
ACTIVATION_HOTKEY = 58  # 58 = CAPS-LOCK
_show_cv2 = True

# used by the script
game_window_rect = WinHelper.GetWindowRect(GAME_WINDOW_TITLE, (8, 30, 16, 39))  # cut the borders
_activated = False


def grab_process(q):
    grabber = Grabber()

    while True:
        img = grabber.get_image({"left": int(game_window_rect[0]), "top": int(game_window_rect[1]), "width": int(game_window_rect[2]), "height": int(game_window_rect[3])})

        if img is None:
            continue

        q.put_nowait(img)
        q.join()


def cv2_process(q):
    global _show_cv2, game_window_rect

    fps = FPS()
    font = cv2.FONT_HERSHEY_SIMPLEX

    mouse = MouseControls()

    # Минимальный размер контура для фильтрации
    min_contour_area = 70  # Подставьте здесь свое значение

    while True:

        if not q.empty():
            img = q.get_nowait()
            q.task_done()

            # DO PROCESSING CODE HERE
            # i.e. inference, detect rects, paint stuff, log, etc
            # <PROCESSING-CODE-GOES-HERE>

            hue_point = 110
            circle_color = ((hue_point, 255, 255), (hue_point+20, 255, 255))
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, np.array(circle_color[0], dtype=np.uint8), np.array(circle_color[1], dtype=np.uint8))
            img = mask

            # Найдите контуры объектов
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Пройдите по каждому контуру и нарисуйте прямоугольник вокруг него
            for contour in contours:
                # Вычислите координаты и размеры прямоугольника
                x, y, w, h = cv2.boundingRect(contour)

                # Проверьте минимальный размер контура
                if cv2.contourArea(contour) < min_contour_area:
                    continue

                # Нарисуйте прямоугольник
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Вычислите координаты центра
                cx = x + w // 2
                cy = y + h // 2

                # Выведите координаты центра
                cv2.putText(img, f"Center: ({cx}, {cy})", (x, y - 10), font, 0.5, (0, 255, 0), 2)




            # cv stuff
            if _show_cv2:
                img = cv2.putText(img, f"{fps():.2f}", (20, 120), font,
                                  1.7, (0, 255, 0), 7, cv2.LINE_AA)

                img = cv2.resize(img, (360, 225))
                cv2.imshow("Captured & Processed image", img)
                cv2.waitKey(1)
        if (_activated == True):
            mouse.move((game_window_rect[0] + cx), (game_window_rect[1] + cy))
            mouse.click()
            




def switch_shoot_state(triggered, hotkey):
    global _activated
    _activated = not _activated  # inverse value


keyboard.add_hotkey(ACTIVATION_HOTKEY, switch_shoot_state, args=('triggered', 'hotkey'))


if __name__ == "__main__":

    q = multiprocessing.JoinableQueue()

    p1 = multiprocessing.Process(target=grab_process, args=(q,))
    p2 = multiprocessing.Process(target=cv2_process, args=(q,))

    p1.start()
    p2.start()