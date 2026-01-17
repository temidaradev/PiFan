import customtkinter as ctk
from . import config
from typing import Callable, Any

class FanControlUI:
    def __init__(self, root: ctk.CTk, 
                 callbacks: dict[str, Callable]) -> None:
        self.root = root
        self.callbacks = callbacks
        
        self.setup_ui()

    def setup_ui(self) -> None:
        self.header_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="FAN COMMAND", 
            font=config.FONT_HEADER_LARGE,
            text_color=config.COLOR_HEADER_TEXT
        )
        self.title_label.pack(side="left")

        self.status_badge = ctk.CTkLabel(
            self.header_frame,
            text="ACTIVE",
            font=config.FONT_BODY,
            text_color=config.COLOR_HIGHLIGHT,
            fg_color=config.COLOR_BADGE_BG,
            corner_radius=6,
            padx=10, pady=2
        )
        self.status_badge.pack(side="right")

        self.main_card = ctk.CTkFrame(self.root, fg_color=config.COLOR_CARD, corner_radius=15)
        self.main_card.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.main_card.grid_columnconfigure((0, 1), weight=1)

        self.setup_temp_section()
        self.setup_control_section()

        self.footer_label = ctk.CTkLabel(self.root, text="Pi 5 System Controller", text_color=config.COLOR_FOOTER_TEXT, font=config.FONT_FOOTER)
        self.footer_label.grid(row=2, column=0, pady=10)

    def setup_temp_section(self) -> None:
        self.temp_frame = ctk.CTkFrame(self.main_card, fg_color="transparent")
        self.temp_frame.grid(row=0, column=0, columnspan=2, pady=(20, 10), sticky="ew")

        self.temp_title = ctk.CTkLabel(self.temp_frame, text="CPU TEMPERATURE", font=config.FONT_BODY, text_color=config.COLOR_SUBTEXT)
        self.temp_title.pack()

        self.temp_value = ctk.CTkLabel(self.temp_frame, text="--°C", font=config.FONT_TEMP_VALUE, text_color="white")
        self.temp_value.pack()

        self.temp_bar = ctk.CTkProgressBar(self.temp_frame, height=8, corner_radius=4)
        self.temp_bar.pack(fill="x", padx=40, pady=5)
        self.temp_bar.set(0)

    def setup_control_section(self) -> None:
        self.sep = ctk.CTkFrame(self.main_card, height=2, fg_color="#3a3a3a")
        self.sep.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=10)

        self.mode_frame = ctk.CTkFrame(self.main_card, fg_color="transparent")
        self.mode_frame.grid(row=2, column=0, columnspan=2, pady=10)

        self.mode_label = ctk.CTkLabel(self.mode_frame, text="Control Mode", font=config.FONT_BODY_LARGE)
        self.mode_label.pack(side="left", padx=10)

        self.mode_switch = ctk.CTkSwitch(
            self.mode_frame, 
            text="Automatic", 
            command=self.callbacks.get('toggle_mode'),
            font=config.FONT_BODY_LARGE,
            progress_color=config.COLOR_ACCENT
        )
        self.mode_switch.select()
        self.mode_switch.pack(side="left", padx=10)
        
        self.speed_frame = ctk.CTkFrame(self.main_card, fg_color="transparent")
        self.speed_frame.grid(row=3, column=0, columnspan=2, pady=10, padx=20, sticky="ew")

        self.speed_label = ctk.CTkLabel(self.speed_frame, text="Fan Speed", font=config.FONT_BODY, text_color=config.COLOR_SUBTEXT)
        self.speed_label.pack(anchor="w")

        self.slider_wrapper = ctk.CTkFrame(self.speed_frame, fg_color="transparent")
        self.slider_wrapper.pack(fill="x", pady=5)

        self.speed_slider = ctk.CTkSlider(
            self.slider_wrapper, 
            from_=0, 
            to=100, 
            number_of_steps=100,
            command=self.callbacks.get('slider_event'),
            progress_color=config.COLOR_ACCENT,
            button_color=config.COLOR_ACCENT
        )
        self.speed_slider.pack(fill="x")
        self.speed_slider.set(0)
        self.speed_slider.configure(state="disabled")

        self.speed_value_label = ctk.CTkLabel(self.speed_frame, text="Auto", font=config.FONT_HEADER_SMALL)
        self.speed_value_label.pack(anchor="e")

        self.setup_presets()

    def setup_presets(self) -> None:
        self.preset_frame = ctk.CTkFrame(self.main_card, fg_color="transparent")
        self.preset_frame.grid(row=4, column=0, columnspan=2, pady=(0, 20), padx=20, sticky="ew")

        self.preset_label = ctk.CTkLabel(self.preset_frame, text="Presets", font=config.FONT_BODY, text_color=config.COLOR_SUBTEXT)
        self.preset_label.pack(anchor="w", pady=(0, 5))

        self.create_preset_btn("Silent", config.COLOR_PRESET_SILENT, config.COLOR_PRESET_SILENT_HOVER, 30)
        self.create_preset_btn("Balanced", config.COLOR_PRESET_NORMAL, config.COLOR_PRESET_NORMAL_HOVER, 60)
        self.create_preset_btn("Max", config.COLOR_PRESET_MAX, config.COLOR_PRESET_MAX_HOVER, 100)

    def create_preset_btn(self, text: str, color: str, hover: str, value: int) -> None:
        apply_fn = self.callbacks.get('apply_preset')
        btn = ctk.CTkButton(
            self.preset_frame, text=text, 
            fg_color=color, 
            hover_color=hover, 
            width=80, 
            command=lambda: apply_fn(value) if apply_fn else None
        )
        btn.pack(side="left", padx=5, expand=True)

    def update_temp_display(self, temp: float) -> None:
        self.temp_value.configure(text=f"{temp:.1f}°C")
        
        if temp < config.TEMP_THRESHOLD_WARN:
            color = config.COLOR_HIGHLIGHT
        elif temp < config.TEMP_THRESHOLD_CRIT:
            color = config.COLOR_WARN
        else:
            color = config.COLOR_CRIT
            
        self.temp_value.configure(text_color=color)
        self.temp_bar.configure(progress_color=color)
        
        norm_temp = max(0.0, min(1.0, temp / config.TEMP_SCALE_MAX))
        self.temp_bar.set(norm_temp)

    def update_speed_display(self, speed: int, is_auto: bool) -> None:
        if is_auto:
            self.speed_value_label.configure(text=f"{speed}% (System)")
            self.speed_slider.set(speed)
        else:
            self.speed_value_label.configure(text=f"{speed}%")

    def set_mode_manual(self, speed: int) -> None:
        self.speed_slider.configure(state="normal", button_color=config.COLOR_ACCENT)
        self.mode_switch.configure(text="Manual")
        self.mode_switch.deselect() # Ensure visual sync

    def set_mode_auto(self) -> None:
        self.speed_slider.configure(state="disabled", button_color="gray")
        self.speed_value_label.configure(text="Auto")
        self.mode_switch.configure(text="Automatic")
        self.mode_switch.select() # Ensure visual sync
