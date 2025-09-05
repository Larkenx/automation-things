from PIL import ImageGrab

import win32gui  # https://stackoverflow.com/questions/7142342/get-window-position-size-with-python
import pyautogui
from pynput import mouse, keyboard
from pynput.keyboard import Key
from pynput.mouse import Controller, Button
import cv2
import numpy as np
import random
import time


class MouseMacro:
    mouse_controller = None
    mouse_listener = None
    key_listener = None
    macro_recording = []
    last_event_time_ms = None
    macro_is_playing = False
    macro_repeat_toggle = False

    def __init__(self):
        self.start_program()

    def start_program(self):
        # Simple keybinding based program, output to terminal
        # F9 will be start recording macro, F10 will be stop recording macro, f12 will execute macro
        self.key_listener = keyboard.Listener(on_release=self.on_key_release)
        with self.key_listener:
            self.key_listener.join()

    def on_key_press(self, key):
        pass

    def on_key_release(self, key):
        if key == keyboard.Key.esc:
            return False  # end program

        if key == keyboard.Key.f9:
            self.start_recording_macro()

        if key == keyboard.Key.f10:
            self.stop_recording_macro()

        if key == keyboard.Key.f12:
            self.play_macro()

        if key == keyboard.Key.f1:
            for i in range(0, 10):
                self.play_macro()

        if key == keyboard.Key.f2:
            for i in range(0, 100):
                self.play_macro()

        if key == keyboard.Key.f3:
            for i in range(0, 100):
                self.play_macro()

    def on_mouse_move(self, x, y):
        self.record_delay_since_last_macro_event()
        self.macro_recording.append({"type": "mouse_move", "x": x, "y": y})

    def on_mouse_click(self, x, y, button, pressed):
        if pressed:
            self.record_delay_since_last_macro_event()
            self.macro_recording.append(
                {"type": "mouse_click", "x": x, "y": y, "button": button}
            )

    def record_delay_since_last_macro_event(self):
        if self.last_event_time_ms:
            time_passed = time.time() - self.last_event_time_ms
            self.macro_recording.append({"type": "delay", "duration": time_passed})
            self.last_event_time_ms = time.time()

    def start_recording_macro(self):
        print("Recording new macro")
        self.mouse_listener = mouse.Listener(
            on_move=self.on_mouse_move, on_click=self.on_mouse_click
        )
        self.last_event_time_ms = time.time()
        self.mouse_listener.start()
        self.macro_recording = []  # array of delays, mouse movements, mouse clicks

    def stop_recording_macro(self):
        print(f"New macro recorded with {len(self.macro_recording)} steps")
        if self.mouse_listener:
            self.mouse_listener.stop()

    def play_actions(self):
        for action in self.macro_recording:
            match action["type"]:
                case "delay":
                    time.sleep(action["duration"])
                case "mouse_click":
                    self.mouse_controller.position = (action["x"], action["y"])
                    self.mouse_controller.press(Button.left)
                    self.mouse_controller.release(Button.left)
                case "mouse_move":
                    self.mouse_controller.position = (action["x"], action["y"])

    def stop_repeat(self):
        self.macro_repeat_toggle = False

    def play_macro(self):
        print("Starting macro playback")
        self.mouse_controller = Controller()
        self.macro_is_playing = True
        self.play_actions()
        print("Macro playback ended")

    def save_recording(self):
        pass


MouseMacro()
