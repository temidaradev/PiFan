import RPi.GPIO as GPIO
import time
import os
import glob
from typing import Optional
from . import config

class FanController:
    def __init__(self) -> None:
        self.FAN_PIN: int = config.FAN_PIN
        self.PWM_FREQ: int = config.PWM_FREQ
        self.max_speed: int = config.MAX_SPEED
        self.current_speed: int = 0
        self.sys_cooling_device: Optional[str] = self._find_sys_device()
        self.sys_max_state: int = self._get_sys_max_state()
        self.active: bool = False
        self.pwm: Optional[GPIO.PWM] = None
        
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.FAN_PIN, GPIO.OUT)
            self.pwm = GPIO.PWM(self.FAN_PIN, self.PWM_FREQ)
            self.pwm.start(100)
            print(f"GPIO {self.FAN_PIN} initialized for PWM.")
            self.active = True
        except Exception as e:
            print(f"Failed to initialize GPIO: {e}")
            self.active = False
            self.pwm = None

    def _find_sys_device(self) -> Optional[str]:
        try:
            base_path = '/sys/class/thermal/'
            devices = glob.glob(os.path.join(base_path, 'cooling_device*'))
            for dev in devices:
                with open(os.path.join(dev, 'type'), 'r') as f:
                    if 'fan' in f.read().strip().lower():
                        return dev
        except Exception:
            pass
        return None

    def _get_sys_max_state(self) -> int:
        if not self.sys_cooling_device:
            return 255
        try:
            with open(os.path.join(self.sys_cooling_device, 'max_state'), 'r') as f:
                return int(f.read().strip())
        except Exception:
            return 255

    def get_temp(self) -> float:
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                return float(f.read().strip()) / 1000.0
        except Exception:
            import random
            return 45.0 + random.random() * 5

    def get_speed(self) -> int:
        return self.current_speed

    def calculate_target_speed(self, temp: float) -> int:
        if temp < config.TEMP_THRESHOLD_WARN:  # 50.0
            return 30  # Silent / Min speed
        elif temp < 55.0:
            return 40
        elif temp < 60.0:
            return 50
        elif temp < 65.0:
            return 60
        elif temp < config.TEMP_THRESHOLD_CRIT: # 70.0
            return 80
        else:
            return 100

    def set_speed(self, percentage: int) -> None:
        percentage = max(0, min(100, percentage))
        self.current_speed = percentage
        
        # Ensure PWM is active
        if not self.active or self.pwm is None:
            try:
                GPIO.setup(self.FAN_PIN, GPIO.OUT)
                self.pwm = GPIO.PWM(self.FAN_PIN, self.PWM_FREQ)
                self.pwm.start(100)
                self.active = True
            except Exception:
                return

        dc = 100.0 - float(percentage)
        try:
            self.pwm.ChangeDutyCycle(dc)
        except Exception:
            pass
            
    # Removed set_auto as we now control it via main loop
    def _noop(self):
        pass

    def cleanup(self) -> None:
        if self.active and self.pwm:
            try:
                self.pwm.stop()
                GPIO.cleanup()
            except Exception:
                pass
