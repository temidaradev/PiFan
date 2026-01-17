import customtkinter as ctk
import threading
import time
from typing import Optional
from . import config
from .fan_control import FanController
from .ui import FanControlUI

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class App(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        print("--- Pi 5 Fan Controller v5.0 (UI Split) ---")

        self.title(config.WINDOW_TITLE)
        self.geometry(config.WINDOW_GEOMETRY)
        self.resizable(False, False)
        self.configure(fg_color=config.COLOR_BG)
        
        # Grid config needed for full window frame
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        self.fan_controller: FanController = FanController()
        self.auto_mode: bool = True
        self.running: bool = True

        # Initialize UI with callbacks
        callbacks = {
            'toggle_mode': self.toggle_mode,
            'slider_event': self.slider_event,
            'apply_preset': self.apply_preset
        }
        self.ui = FanControlUI(self, callbacks)
        
        self.update_thread: threading.Thread = threading.Thread(target=self.update_loop, daemon=True)
        self.update_thread.start()

    def toggle_mode(self) -> None:
        self.auto_mode = not self.auto_mode
        if self.auto_mode:
            self.ui.set_mode_auto()
            # self.fan_controller.set_auto() # Removed, handled in loop
        else:
            # When switching to manual, default to current speed or 50?
            # Let's read slider value or default
            val = int(self.ui.speed_slider.get())
            self.ui.set_mode_manual(val)
            self.fan_controller.set_speed(val)

    def slider_event(self, value: float) -> None:
        if self.auto_mode:
            self.toggle_mode()
        
        val = int(value)
        self.ui.update_speed_display(val, is_auto=False)
        self.fan_controller.set_speed(val)

    def apply_preset(self, value: int) -> None:
        if self.auto_mode:
            self.toggle_mode()
        
        self.ui.speed_slider.set(value)
        self.slider_event(float(value))

    def update_loop(self) -> None:
        while self.running:
            temp = self.fan_controller.get_temp()
            if self.auto_mode:
                speed = self.fan_controller.calculate_target_speed(temp)
                self.fan_controller.set_speed(speed)
            else:
                speed = self.fan_controller.get_speed()
                
            self.after(0, self.update_gui, temp, speed)
            time.sleep(2)

    def update_gui(self, temp: float, speed: int) -> None:
        self.ui.update_temp_display(temp)
        self.ui.update_speed_display(speed, self.auto_mode)

    def on_closing(self) -> None:
        self.running = False
        try:
            self.fan_controller.cleanup()
        except:
            pass
        self.destroy()

def main():
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    try:
        app.mainloop()
    except KeyboardInterrupt:
        app.on_closing()

if __name__ == "__main__":
    main()
