import json
import os
import platform
import subprocess
import sys
import threading
import time
import webbrowser
from concurrent.futures import ThreadPoolExecutor
from tkinter import messagebox
import customtkinter as ctk
import requests

# Поточна версія додатка
CURRENT_VERSION = "v1.1.0"
GITHUB_REPO = "dinryx-hub/DinryX-HUB"  # Твій username/repo
SITE_URL = "https://dinryx-hub.github.io/DinryX-HUB/"

# Збереження конфігурації у папку AppData (чисто і без файлів біля .exe)
APPDATA_DIR = os.path.join(
    os.environ.get("APPDATA", os.path.expanduser("~")), "DinryX_HUB"
)
os.makedirs(APPDATA_DIR, exist_ok=True)
CONFIG_FILE = os.path.join(APPDATA_DIR, "config.json")

CURRENT_OS = platform.system()

# Палітри кольорів для кастомізації
COLOR_PALETTES = {
    "Red Edition": {"main": "#ff4b2b", "hover": "#8b0000"},
    "Blue Neon": {"main": "#1f6aa5", "hover": "#144870"},
    "Green Cyber": {"main": "#2fa572", "hover": "#1e6b4a"},
    "Purple Violet": {"main": "#9b59b6", "hover": "#6c3483"},
}


# --- ФУНКЦІЇ ДЛЯ РОБОТИ З КОНФІГУРАЦІЄЮ ---
def load_config():
    # За замовчуванням при першому старті — системна тема (System)
    default_config = {"appearance_mode": "System", "accent_palette": "Red Edition"}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                if "appearance_mode" not in config:
                    config["appearance_mode"] = "System"
                if config.get("accent_palette") not in COLOR_PALETTES:
                    config["accent_palette"] = "Red Edition"
                return config
        except Exception as e:
            print(f"Помилка читання конфігу: {e}")
    return default_config


def save_config(config_data):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Помилка збереження конфігу: {e}")


def get_resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


# --- СПИСКИ ПРОГРАМ З ПРАПОРЦЯМИ ТИХОГО ВСТАНОВЛЕННЯ ---

PROGRAMS_WINDOWS = [
    {
        "name": "7-Zip",
        "desc": "Популярний і швидкий архіватор.",
        "url": "https://www.7-zip.org/a/7z2408-x64.exe",
        "file": "7z2408-x64.exe",
        "silent_args": "/S",
    },
    {
        "name": "WinRAR",
        "desc": "Класичний архіватор.",
        "url": "https://www.rarlab.com/rar/winrar-x64-621.exe",
        "file": "winrar-x64-621.exe",
        "silent_args": "/S",
    },
    {
        "name": "Google Chrome",
        "desc": "Веб-браузер від Google.",
        "url": "https://dl.google.com/chrome/install/GoogleChromeStandaloneEnterprise64.msi",
        "file": "GoogleChromeStandaloneEnterprise64.msi",
        "silent_args": "/quiet /qn /norestart",
    },
    {
        "name": "Notepad++",
        "desc": "Зручний текстовий редактор.",
        "url": "https://github.com/notepad-plus-plus/notepad-plus-plus/releases/download/v8.6.2/npp.8.6.2.Installer.x64.exe",
        "file": "npp.8.6.2.Installer.x64.exe",
        "silent_args": "/S",
    },
    {
        "name": "Sublime Text",
        "desc": "Швидкий редактор коду.",
        "url": "https://www.sublimetext.com/download_thanks?target=win-x64",
        "file": "sublime_text_build_4200_x64_setup.exe",
        "silent_args": "/VERYSILENT /NORESTART",
    },
    {
        "name": "GIMP",
        "desc": "Безкоштовний графічний редактор.",
        "url": "https://download.gimp.org/gimp/v3.2/windows/gimp-3.2.4-setup.exe",
        "file": "gimp-3.2.4-setup.exe",
        "silent_args": '/ALLUSERS /DIR="C:\\Program Files\\GIMP 3" /SILENT',
    },
    {
        "name": "LibreOffice",
        "desc": "Офісний пакет для документів.",
        "url": "https://download.documentfoundation.org/libreoffice/stable/26.2.4/win/x86_64/LibreOffice_26.2.4_Win_x86-64.msi",
        "file": "LibreOffice_26.2.4_Win_x86-64.msi",
        "silent_args": "/quiet /qn /norestart",
    },
    {
        "name": "Heroic Games Launcher",
        "desc": "Лаунчер Epic Games та GOG.",
        "url": "https://github.com/Heroic-Games-Launcher/HeroicGamesLauncher/releases/download/v2.22.0/Heroic-2.22.0-Setup-x64.exe",
        "file": "Heroic-2.22.0-Setup-x64.exe",
        "silent_args": "/S",
    },
    {
        "name": "Steam",
        "desc": "Ігрова платформа №1.",
        "url": "https://cdn.fastly.steamstatic.com/client/installer/SteamSetup.exe",
        "file": "SteamSetup.exe",
        "silent_args": "/S",
    },
    {
        "name": "Game Jolt",
        "desc": "Ігрова платформа №3. Фан ігри",
        "url": "https://download.gamejolt.net/1bf0fd4bf7795d65ea761533e74b909a65286f1664263f6fa340704e0baf2039,1784823427,7/data/games/5/162/362412/files/66bc359fe3e14/gamejoltclientsetup.exe",
        "file": "gamejoltclientsetup.exe",
        "silent_args": "",
    },
    {
        "name": "TLauncher",
        "desc": "Піратський лаунчер Minecraft.",
        "url": "https://tlauncher.org/installer",
        "file": "TLauncher-Installer-1.9.5.1.exe",
        "silent_args": "",
    },
    {
        "name": "ORACLE | Java jdk26",
        "desc": "Середовище виконання та розробка Java-додатків",
        "url": "https://download.oracle.com/java/26/latest/jdk-26_windows-x64_bin.exe",
        "file": "jdk-26_windows-x64_bin.exe",
        "silent_args": "",
    },
    {
        "name": "Discord",
        "desc": "Месенджер для ґеймерів.",
        "url": "https://dl.discordapp.net/distro/app/stable/win/x64/1.0.9152/DiscordSetup.exe",
        "file": "DiscordSetup.exe",
        "silent_args": "-s",
    },
    {
        "name": "Telegram Desktop",
        "desc": "Зручний месенджер для ПК.",
        "url": "https://telegram.org/dl/desktop/win64",
        "file": "tsetup-x64.7.0.4.exe",
        "silent_args": "/VERYSILENT /NORESTART",
    },
]

PROGRAMS_LINUX = [
    {
        "name": "Google Chrome (.deb)",
        "desc": "Веб-браузер від Google.",
        "url": "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb",
        "file": "google-chrome-stable_current_amd64.deb",
        "silent_args": "",
    },
    {
        "name": "Heroic Games Launcher",
        "desc": "Лаунчер Epic Games & GOG (AppImage).",
        "url": "https://github.com/Heroic-Games-Launcher/HeroicGamesLauncher/releases/download/v2.22.0/Heroic-2.22.0-Linux-x86_64.AppImage",
        "file": "Heroic-2.22.0-Linux-x86_64.AppImage",
        "silent_args": "Heroic-2.22.0-Linux-x86_64.AppImage",
    },
    {
        "name": "Steam",
        "desc": "Ігрова платформа №1.",
        "url": "https://cdn.fastly.steamstatic.com/client/installer/steam.deb",
        "file": "steam_latest.deb",
        "silent_args": "",
    },
    {
        "name": "TLauncher",
        "desc": "Піратський лаунчер для Minecraft.",
        "url": "https://tlauncher.org/jar",
        "silent_args": "",
    },
    {
        "name": "ORACLE | Java jdk26",
        "desc": "Середовище виконання та розробка Java-додатків",
        "url": "https://download.oracle.com/java/26/latest/jdk-26_linux-x64_bin.deb",
        "file": "jdk-26_linux-x64_bin.deb",
        "silent_args": "",
    },
    {
        "name": "Discord (.deb)",
        "desc": "Месенджер для ґеймерів.",
        "url": "https://discord.com/api/download?platform=linux&format=deb",
        "file": "discord-1.0.150.deb",
        "silent_args": "",
    },
    {
        "name": "Steam (.deb)",
        "desc": "Клієнт Steam для Linux.",
        "url": "https://cdn.fastly.steamstatic.com/client/installer/steam.deb",
        "file": "steam_latest.deb",
        "silent_args": "",
    },
    {
        "name": "Stacer",
        "desc": "Лінукс Очищювач & Моніторинг.",
        "url": "https://github.com/oguzhaninan/Stacer/releases/download/v1.1.0/Stacer-1.1.0-x64.AppImage",
        "file": "Stacer-1.1.0-x64.AppImage",
        "silent_args": "",
    },
    {
        "name": "Sublime Text (.deb)",
        "desc": "Надшвидкий текстовий редактор для коду.",
        "url": "https://download.sublimetext.com/sublime-text_build-4169_amd64.deb",
        "file": "sublime-text_build-4169_amd64.deb",
        "silent_args": "",
    },
    {
        "name": "OBS Studio (.AppImage)",
        "desc": "Запис екрана та проведення стрімів.",
        "url": "https://github.com/obsproject/obs-studio/releases/download/32.2.0/OBS-Studio-32.2.0-Ubuntu-26.04-x86_64.deb",
        "file": "OBS-Studio-32.2.0-Ubuntu-26.04-x86_64.deb",
        "silent_args": "",
    },
    {
        "name": "GIMP (.AppImage)",
        "desc": "Растровий графічний редактор (аналог Photoshop).",
        "url": "https://download.gimp.org/gimp/v3.2/linux/GIMP-3.2.0-RC1-aarch64.AppImage",
        "file": "GIMP-3.2.0-RC1-aarch64.AppImage",
        "silent_args": "",
    },
    {
        "name": "Inkscape (.AppImage)",
        "desc": "Векторна графіка (аналог Adobe Illustrator).",
        "url": "https://inkscape.org/release/inkscape-1.4.4/gnulinux/appimage/dl/",
        "file": "Inkscape-1.4.4.AppImage",
        "silent_args": "",
    },
    {
        "name": "Krita (.AppImage)",
        "desc": "Професійна програма для малювання та ілюстрацій.",
        "url": "https://download.kde.org/stable/krita/6.0.2.1/krita-6.0.2.1-x86_64.AppImage",
        "file": "krita-6.0.2.1-x86_64.AppImage",
        "silent_args": "",
    },
    {
        "name": "Kdenlive (.AppImage)",
        "desc": "Потужний відеоредактор для монтажу.",
        "url": "https://download.kde.org/stable/kdenlive/26.04/linux/kdenlive-26.04.3-x86_64.AppImage",
        "file": "kdenlive-26.04.3-x86_64.AppImage",
        "silent_args": "",
    },
]

PROGRAMS = PROGRAMS_WINDOWS if CURRENT_OS == "Windows" else PROGRAMS_LINUX
DOWNLOAD_DIR = "downloaded_installers"


class DinryXHUBApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        # Завантаження збережених налаштувань
        self.config_data = load_config()

        ctk.set_appearance_mode(self.config_data.get("appearance_mode", "System"))
        ctk.set_default_color_theme("blue")

        self.title("DinryX HUB")
        self.geometry("650x705")
        self.resizable(False, False)

        # Адаптивний фон для всього вікна (Light, Dark)
        self.configure(fg_color=("#F5F5F7", "#0a0a0a"))

        self._set_app_icon()
        self.checkbox_vars = []
        self.checkbox_widgets = []
        self.accent_labels = []

        # Поточні кольори з конфігу
        palette_name = self.config_data.get("accent_palette", "Red Edition")
        palette = COLOR_PALETTES.get(palette_name, COLOR_PALETTES["Red Edition"])
        self.current_main_color = palette["main"]
        self.current_hover_color = palette["hover"]

        # Опції
        self.var_silent = ctk.BooleanVar(value=True)
        self.var_autoclean = ctk.BooleanVar(value=False)

        self._build_ui()
        self._check_for_updates_async()

    def _set_app_icon(self):
        try:
            icon_file = "icon.ico" if CURRENT_OS == "Windows" else "icon.png"
            icon_path = get_resource_path(icon_file)
            if os.path.exists(icon_path):
                if CURRENT_OS == "Windows":
                    self.iconbitmap(icon_path)
                else:
                    img = ctk.CTkImage(file=icon_path)
                    self.wm_iconphoto(True, img)
        except Exception as e:
            print(f"Помилка іконки: {e}")

    def _build_ui(self):
        # Хедер
        header_frame = ctk.CTkFrame(
            self,
            corner_radius=15,
            fg_color=("#EAEAEA", "#151515"),
            border_width=1,
            border_color=("#CCCCCC", "#333333"),
        )
        header_frame.pack(fill="x", padx=15, pady=(15, 10))

        self.title_label = ctk.CTkLabel(
            header_frame,
            text=f"DinryX HUB Installer [{CURRENT_OS}]",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=self.current_main_color,
        )
        self.title_label.pack(side="left", padx=20, pady=15)

        self.v_label = ctk.CTkLabel(
            header_frame,
            text=f"{CURRENT_VERSION} MultiOS",
            font=ctk.CTkFont(size=11),
            text_color=("#666666", "#888888"),
        )
        self.v_label.pack(side="right", padx=20, pady=15)

        # Таби
        self.tabview = ctk.CTkTabview(
            self,
            corner_radius=15,
            fg_color=("#F0F0F2", "#0f0f0f"),
            segmented_button_fg_color=("#E0E0E5", "#151515"),
            segmented_button_selected_color=self.current_main_color,
            segmented_button_selected_hover_color=self.current_hover_color,
            segmented_button_unselected_color=("#D5D5DD", "#222222"),
        )
        self.tabview.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        # Налаштування кольору тексту вкладок
        self.tabview._segmented_button.configure(
            text_color=("#000000", "#FFFFFF"),
            selected_color=self.current_main_color,
            selected_hover_color=self.current_hover_color,
        )

        self.tab_installer = self.tabview.add("Додатки")
        self.tab_settings = self.tabview.add("Налаштування")
        self.tab_about = self.tabview.add("Про Додаток")

        self._build_installer_tab()
        self._build_settings_tab()
        self._build_about_tab()

    def _build_installer_tab(self):
        ctrl_frame = ctk.CTkFrame(self.tab_installer, fg_color="transparent")
        ctrl_frame.pack(fill="x", padx=10, pady=(5, 5))

        lbl_select = ctk.CTkLabel(
            ctrl_frame,
            text="Виберіть Додатки:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#222222", "#eee"),
        )
        lbl_select.pack(side="left")

        btn_unselect = ctk.CTkButton(
            ctrl_frame,
            text="Скинути",
            width=80,
            height=26,
            corner_radius=8,
            fg_color=("#D0D0D5", "#222222"),
            text_color=("#000000", "#FFFFFF"),
            hover_color=("#BBBBBB", "#441111"),
            command=self.unselect_all,
        )
        btn_unselect.pack(side="right", padx=(5, 0))

        btn_select = ctk.CTkButton(
            ctrl_frame,
            text="Вибрати усе",
            width=90,
            height=26,
            corner_radius=8,
            fg_color=("#D0D0D5", "#222222"),
            text_color=("#000000", "#FFFFFF"),
            hover_color=("#BBBBBB", "#441111"),
            command=self.select_all,
        )
        btn_select.pack(side="right")

        # Список програм
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.tab_installer,
            corner_radius=10,
            fg_color=("#E5E5EA", "#121212"),
            scrollbar_button_color=("#BBBBBB", "#331111"),
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=5, pady=(5, 5))

        for prog in PROGRAMS:
            var = ctk.BooleanVar(value=True)
            self.checkbox_vars.append(var)

            card = ctk.CTkFrame(
                self.scroll_frame,
                corner_radius=10,
                fg_color=("#FFFFFF", "#181818"),
                border_width=1,
                border_color=("#D0D0D0", "#252525"),
            )
            card.pack(fill="x", pady=4, padx=5)

            cb = ctk.CTkCheckBox(
                card,
                text=prog["name"],
                variable=var,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color=self.current_main_color,
                hover_color=self.current_hover_color,
                text_color=("#111111", "#ffffff"),
                corner_radius=6,
            )
            cb.pack(side="left", padx=15, pady=12)
            self.checkbox_widgets.append(cb)

            desc = ctk.CTkLabel(
                card,
                text=prog["desc"],
                font=ctk.CTkFont(size=11),
                text_color=("#555555", "#888888"),
            )
            desc.pack(side="right", padx=15, pady=12)

        # Опції інсталяції
        opt_frame = ctk.CTkFrame(self.tab_installer, fg_color="transparent")
        opt_frame.pack(fill="x", padx=10, pady=5)

        self.cb_silent = ctk.CTkCheckBox(
            opt_frame,
            text="Тихе встановлення (без вікон)",
            variable=self.var_silent,
            font=ctk.CTkFont(size=12),
            text_color=("#111111", "#ffffff"),
            fg_color=self.current_main_color,
            hover_color=self.current_hover_color,
        )
        self.cb_silent.pack(side="left", padx=5)

        self.cb_clean = ctk.CTkCheckBox(
            opt_frame,
            text="Видалити інсталятори після встановлення",
            variable=self.var_autoclean,
            font=ctk.CTkFont(size=12),
            text_color=("#111111", "#ffffff"),
            fg_color=self.current_main_color,
            hover_color=self.current_hover_color,
        )
        self.cb_clean.pack(side="right", padx=5)

        # Статус і Прогрес
        status_frame = ctk.CTkFrame(self.tab_installer, fg_color="transparent")
        status_frame.pack(fill="x", padx=10, pady=(5, 5))

        self.label_status = ctk.CTkLabel(
            status_frame,
            text="Готовий до роботи",
            font=ctk.CTkFont(size=12),
            text_color=("#555555", "#888888"),
        )
        self.label_status.pack(pady=(0, 5))

        self.progress = ctk.CTkProgressBar(
            status_frame,
            corner_radius=10,
            height=10,
            fg_color=("#D0D0D0", "#222222"),
            progress_color=self.current_main_color,
        )
        self.progress.pack(fill="x")
        self.progress.set(0)

        self.btn_start = ctk.CTkButton(
            self.tab_installer,
            text="ЗАПУСТИТИ ВСТАНОВЛЕННЯ",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=45,
            corner_radius=12,
            fg_color=self.current_main_color,
            text_color="#ffffff",
            hover_color=self.current_hover_color,
            command=self.start_process_thread,
        )
        self.btn_start.pack(fill="x", padx=5, pady=(5, 5))

    def _build_settings_tab(self):
        set_card = ctk.CTkFrame(
            self.tab_settings,
            corner_radius=12,
            fg_color=("#FFFFFF", "#151515"),
            border_width=1,
            border_color=("#D0D0D0", "#252525"),
        )
        set_card.pack(fill="both", expand=True, padx=10, pady=10)

        lbl_theme = ctk.CTkLabel(
            set_card,
            text="🎨 Тема інтерфейсу",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.current_main_color,
        )
        lbl_theme.pack(anchor="w", padx=20, pady=(20, 10))
        self.accent_labels.append(lbl_theme)

        # Перемикач Dark/Light/System
        self.theme_menu = ctk.CTkOptionMenu(
            set_card,
            values=["System", "Dark", "Light"],
            command=self.change_appearance_mode,
            fg_color=("#E0E0E0", "#222222"),
            text_color=("#000000", "#FFFFFF"),
            button_color=self.current_main_color,
            button_hover_color=self.current_hover_color,
        )
        self.theme_menu.set(self.config_data.get("appearance_mode", "System"))
        self.theme_menu.pack(anchor="w", padx=20, pady=(0, 20))

        lbl_color = ctk.CTkLabel(
            set_card,
            text="🌈 Акцентний колір",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.current_main_color,
        )
        lbl_color.pack(anchor="w", padx=20, pady=(0, 10))
        self.accent_labels.append(lbl_color)

        # Вибір кольорів
        self.color_menu = ctk.CTkOptionMenu(
            set_card,
            values=list(COLOR_PALETTES.keys()),
            command=self.change_accent_color,
            fg_color=("#E0E0E0", "#222222"),
            text_color=("#000000", "#FFFFFF"),
            button_color=self.current_main_color,
            button_hover_color=self.current_hover_color,
        )
        self.color_menu.set(self.config_data.get("accent_palette", "Red Edition"))
        self.color_menu.pack(anchor="w", padx=20, pady=(0, 20))

    def _build_about_tab(self):
        about_card = ctk.CTkFrame(
            self.tab_about,
            corner_radius=12,
            fg_color=("#FFFFFF", "#151515"),
            border_width=1,
            border_color=("#D0D0D0", "#252525"),
        )
        about_card.pack(fill="both", expand=True, padx=10, pady=10)

        lbl_desc_title = ctk.CTkLabel(
            about_card,
            text="📌 Про проєкт",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.current_main_color,
        )
        lbl_desc_title.pack(anchor="w", padx=20, pady=(15, 5))
        self.accent_labels.append(lbl_desc_title)

        desc_text = (
            f"DinryX HUB — кросплатформений менеджер софту ({CURRENT_OS}).\n"
            "Автоматично скачує та встановлює офіційні інсталятори."
        )
        lbl_desc = ctk.CTkLabel(
            about_card,
            text=desc_text,
            font=ctk.CTkFont(size=13),
            text_color=("#333333", "#ccc"),
            justify="left",
        )
        lbl_desc.pack(anchor="w", padx=20, pady=(0, 15))

        lbl_author_title = ctk.CTkLabel(
            about_card,
            text="👨‍💻 Про автора",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.current_main_color,
        )
        lbl_author_title.pack(anchor="w", padx=20, pady=(10, 5))
        self.accent_labels.append(lbl_author_title)

        author_text = (
            "• Розробник: RAIDDARK / DinryX Team\n"
            "• Версія додатка: " + CURRENT_VERSION + "\n"
            "• Платформа: CustomTkinter / Nuitka"
        )
        lbl_author = ctk.CTkLabel(
            about_card,
            text=author_text,
            font=ctk.CTkFont(size=13),
            text_color=("#333333", "#ccc"),
            justify="left",
        )
        lbl_author.pack(anchor="w", padx=20, pady=(0, 15))

        btn_site = ctk.CTkButton(
            about_card,
            text="🌐 Офіційний сайт / Оновлення",
            font=ctk.CTkFont(size=13, underline=True),
            fg_color="transparent",
            text_color="#4dabf7",
            command=lambda: webbrowser.open(SITE_URL),
        )
        btn_site.pack(anchor="w", padx=15, pady=(0, 15))

    # --- ЗМІНА ТА ЗБЕРЕЖЕННЯ ТЕМИ ---
    def change_appearance_mode(self, mode):
        ctk.set_appearance_mode(mode)
        self.config_data["appearance_mode"] = mode
        save_config(self.config_data)

    # --- ДИНАМІЧНА ЗМІНА ТА ЗБЕРЕЖЕННЯ АКЦЕНТНОГО КОЛЬОРУ ---
    def change_accent_color(self, selected_palette):
        palette = COLOR_PALETTES.get(
            selected_palette, COLOR_PALETTES["Red Edition"]
        )
        self.current_main_color = palette["main"]
        self.current_hover_color = palette["hover"]

        # Збереження
        self.config_data["accent_palette"] = selected_palette
        save_config(self.config_data)

        # Оновлення заголовка додатка
        self.title_label.configure(text_color=self.current_main_color)

        # Оновлення вкладок
        self.tabview.configure(
            segmented_button_selected_color=self.current_main_color,
            segmented_button_selected_hover_color=self.current_hover_color,
        )
        self.tabview._segmented_button.configure(
            selected_color=self.current_main_color,
            selected_hover_color=self.current_hover_color,
        )

        # Оновлення кнопки запуску
        self.btn_start.configure(
            fg_color=self.current_main_color,
            hover_color=self.current_hover_color,
        )

        # Оновлення кнопок у меню Налаштувань
        self.theme_menu.configure(
            button_color=self.current_main_color,
            button_hover_color=self.current_hover_color,
        )
        self.color_menu.configure(
            button_color=self.current_main_color,
            button_hover_color=self.current_hover_color,
        )

        # Оновлення прогрес-бару
        self.progress.configure(progress_color=self.current_main_color)

        # Оновлення чекбоксів опцій
        self.cb_silent.configure(
            fg_color=self.current_main_color,
            hover_color=self.current_hover_color,
        )
        self.cb_clean.configure(
            fg_color=self.current_main_color,
            hover_color=self.current_hover_color,
        )

        # Оновлення всіх чекбоксів програм
        for cb in self.checkbox_widgets:
            cb.configure(
                fg_color=self.current_main_color,
                hover_color=self.current_hover_color,
            )

        # Оновлення заголовків
        for lbl in self.accent_labels:
            lbl.configure(text_color=self.current_main_color)

    def select_all(self):
        for var in self.checkbox_vars:
            var.set(True)

    def unselect_all(self):
        for var in self.checkbox_vars:
            var.set(False)

    def update_status(self, text, progress_val):
        self.label_status.configure(text=text)
        self.progress.set(progress_val)

    # --- ПЕРЕВІРКА ОНОВЛЕНЬ ---
    def _check_for_updates_async(self):
        threading.Thread(target=self._check_updates_logic, daemon=True).start()

    def _check_updates_logic(self):
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                latest_tag = res.json().get("tag_name", "").strip()

                def parse_version(v_str):
                    clean_str = v_str.lower().lstrip("v")
                    return tuple(map(int, clean_str.split(".")))

                if latest_tag and parse_version(latest_tag) > parse_version(
                    CURRENT_VERSION
                ):
                    self.v_label.configure(
                        text=f"Доступно {latest_tag}!", text_color="#4dabf7"
                    )
                else:
                    self.v_label.configure(
                        text=f"{CURRENT_VERSION} MultiOS", text_color=("#666666", "#888888")
                    )
        except Exception:
            pass

    # --- ПАРАЛЕЛЬНЕ ЗАВАНТАЖЕННЯ ТА ВСТАНОВЛЕННЯ ---
    def download_file(self, prog):
        target_path = os.path.join(DOWNLOAD_DIR, prog["file"])
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            res = requests.get(
                prog["url"], headers=headers, stream=True, timeout=25
            )
            if res.status_code == 200:
                with open(target_path, "wb") as f:
                    for chunk in res.iter_content(chunk_size=8192):
                        f.write(chunk)
                return prog, target_path
        except Exception as e:
            print(f"Помилка завантаження {prog['name']}: {e}")
        return prog, None

    def open_installer(self, path, silent_args=""):
        try:
            if CURRENT_OS == "Windows":
                is_silent = self.var_silent.get() and silent_args
                if is_silent:
                    cmd = f'"{path}" {silent_args}'
                    subprocess.run(cmd, shell=True)
                else:
                    os.startfile(path)
            else:
                if path.endswith(".AppImage"):
                    os.chmod(path, 0o755)
                subprocess.run(["xdg-open", path])
        except Exception as e:
            print(f"Помилка запуску {path}: {e}")

    def start_process_thread(self):
        selected = [i for i, var in enumerate(self.checkbox_vars) if var.get()]
        if not selected:
            messagebox.showwarning("Увага", "Виберіть хоча б одну програму!")
            return
        self.btn_start.configure(state="disabled", fg_color="#331111")
        threading.Thread(
            target=self.run_installer_logic, args=(selected,), daemon=True
        ).start()

    def run_installer_logic(self, indices):
        if not os.path.exists(DOWNLOAD_DIR):
            os.makedirs(DOWNLOAD_DIR)

        selected_progs = [PROGRAMS[i] for i in indices]
        total = len(selected_progs)
        downloaded = []

        # 1. Паралельне скачування (до 3 файлів одночасно)
        self.update_status(
            f"Завантаження {total} програм у кількох потоках...", 0.2
        )
        with ThreadPoolExecutor(max_workers=3) as executor:
            results = list(executor.map(self.download_file, selected_progs))

        for prog, path in results:
            if path:
                downloaded.append((prog, path))

        # 2. Послідовне встановлення
        for idx, (prog, path) in enumerate(downloaded, 1):
            progress_val = 0.5 + (idx / len(downloaded)) * 0.5
            self.update_status(
                f"Встановлення: {prog['name']}...", progress_val
            )
            self.open_installer(path, prog.get("silent_args", ""))

            # Якщо увімкнено авто-очищення
            if self.var_autoclean.get() and os.path.exists(path):
                try:
                    os.remove(path)
                except Exception:
                    pass

        self.update_status("Усі завдання виконано!", 1.0)
        messagebox.showinfo("DinryX HUB", "Процес успішно завершено!")
        self.btn_start.configure(
            state="normal", fg_color=self.current_main_color
        )


if __name__ == "__main__":
    app = DinryXHUBApp()
    app.mainloop()
