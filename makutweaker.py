#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MakuTweaker v4.3.0 - Революционный оптимизатор Windows
Автор: Неизвестный гений программирования
Лицензия: Абсолютно бесплатно (результат гарантирован на 146%)
"""

import sys
import random
import time
import threading
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

class WorkerThread(QThread):
    """Рабочий поток для выполнения задач"""
    progress_updated = pyqtSignal(int, str)
    task_completed = pyqtSignal(bool, str)
    
    def __init__(self, steps, task_name="Выполнение задачи"):
        super().__init__()
        self.steps = steps
        self.task_name = task_name
        self.cancelled = False
    
    def run(self):
        """Выполнение задачи в отдельном потоке"""
        try:
            for i, step in enumerate(self.steps):
                if self.cancelled:
                    self.task_completed.emit(False, "Операция отменена пользователем")
                    return
                
                self.progress_updated.emit(i, step)
                
                # Имитация работы с случайной задержкой
                time.sleep(random.uniform(0.8, 2.5))
            
            self.progress_updated.emit(len(self.steps), "Завершено!")
            
            # Случайный результат для реалистичности
            success = random.choice([True, True, True, False])  # 75% успеха
            
            if success:
                self.task_completed.emit(True, f"{self.task_name} успешно завершена!")
            else:
                error_messages = [
                    "Ошибка доступа к реестру!",
                    "Недостаточно прав администратора!",
                    "Антивирус заблокировал операцию!",
                    "Системный файл используется другим процессом!",
                    "Нет подключения к серверу!"
                ]
                error = random.choice(error_messages)
                self.task_completed.emit(False, f"Ошибка: {error}")
                
        except Exception as e:
            self.task_completed.emit(False, f"Критическая ошибка: {str(e)}")
    
    def cancel(self):
        """Отмена выполнения задачи"""
        self.cancelled = True

class ProgressDialog(QDialog):
    """Улучшенный диалог прогресса с многопоточностью"""
    
    def __init__(self, parent, title, steps, task_name="Выполнение задачи"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(500, 200)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowTitleHint)
        
        # Настройка интерфейса
        layout = QVBoxLayout(self)
        
        # Заголовок
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(self.title_label)
        
        # Текущее действие
        self.status_label = QLabel("Подготовка...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 13px; color: #b0b0b0; margin: 5px;")
        layout.addWidget(self.status_label)
        
        # Прогресс-бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, len(steps))
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #404040;
                border: 2px solid #606060;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0078d4, stop:1 #106ebe);
                border-radius: 6px;
                margin: 1px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Процент выполнения
        self.percent_label = QLabel("0%")
        self.percent_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.percent_label.setStyleSheet("font-size: 14px; font-weight: bold; margin: 5px;")
        layout.addWidget(self.percent_label)
        
        # Кнопка отмены
        self.cancel_button = QPushButton("❌ Отменить")
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #b71c1c;
            }
        """)
        self.cancel_button.clicked.connect(self.cancel_task)
        layout.addWidget(self.cancel_button)
        
        # Создание и запуск рабочего потока
        self.worker = WorkerThread(steps, task_name)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.task_completed.connect(self.task_finished)
        self.worker.start()
        
        self.result = None
        self.success = False
    
    def update_progress(self, value, status):
        """Обновление прогресса"""
        self.progress_bar.setValue(value)
        self.status_label.setText(status)
        
        # Обновление процентов
        if self.progress_bar.maximum() > 0:
            percent = int((value / self.progress_bar.maximum()) * 100)
            self.percent_label.setText(f"{percent}%")
        
        # Анимация прогресс-бара
        if value < self.progress_bar.maximum():
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    background-color: #404040;
                    border: 2px solid #606060;
                    border-radius: 8px;
                    text-align: center;
                    font-weight: bold;
                    height: 25px;
                }
                QProgressBar::chunk {
                    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #0078d4, stop:1 #106ebe);
                    border-radius: 6px;
                    margin: 1px;
                }
            """)
    
    def task_finished(self, success, message):
        """Завершение задачи"""
        self.success = success
        self.result = message
        
        if success:
            self.progress_bar.setValue(self.progress_bar.maximum())
            self.percent_label.setText("100%")
            self.status_label.setText("✅ Успешно завершено!")
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    background-color: #404040;
                    border: 2px solid #4caf50;
                    border-radius: 8px;
                    text-align: center;
                    font-weight: bold;
                    height: 25px;
                }
                QProgressBar::chunk {
                    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #4caf50, stop:1 #2e7d32);
                    border-radius: 6px;
                    margin: 1px;
                }
            """)
        else:
            self.status_label.setText("❌ Операция не удалась!")
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    background-color: #404040;
                    border: 2px solid #d32f2f;
                    border-radius: 8px;
                    text-align: center;
                    font-weight: bold;
                    height: 25px;
                }
                QProgressBar::chunk {
                    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #d32f2f, stop:1 #b71c1c);
                    border-radius: 6px;
                    margin: 1px;
                }
            """)
        
        self.cancel_button.setText("✅ Закрыть")
        self.cancel_button.clicked.disconnect()
        self.cancel_button.clicked.connect(self.accept)
    
    def cancel_task(self):
        """Отмена задачи"""
        if self.worker.isRunning():
            self.worker.cancel()
            self.worker.wait(3000)  # Ждем 3 секунды
            if self.worker.isRunning():
                self.worker.terminate()
        self.reject()
    
    def closeEvent(self, event):
        """Обработка закрытия окна"""
        if self.worker.isRunning():
            self.cancel_task()
        event.accept()

class MakuTweaker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.version = "4.3.0"
        self.init_ui()
        self.apply_dark_theme()
        
    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle("MakuTweaker")
        self.setGeometry(100, 100, 1000, 700)
        self.setMinimumSize(900, 600)
        
        # Главный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Создаем боковое меню
        self.create_sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Создаем основную область
        self.create_main_area()
        main_layout.addWidget(self.main_area)
        
        # Показываем первую вкладку по умолчанию
        self.show_explorer_tab()
        
    def create_sidebar(self):
        """Создание бокового меню"""
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(280)
        self.sidebar.setObjectName("sidebar")
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # Заголовок
        header = QLabel("MakuTweaker")
        header.setObjectName("header")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(header)
        
        # Кнопки меню
        menu_items = [
            ("Проводник и Рабочий стол", self.show_explorer_tab),
            ("Windows Update", self.show_updates_tab),
            ("Система и восстановление", self.show_system_tab),
            ("Удаление UWP приложений", self.show_uwp_tab),
            ("Персонализация", self.show_personalization_tab),
            ("Контекстное меню", self.show_context_tab),
            ("Отключение телеметрии", self.show_telemetry_tab),
            ("Компоненты Windows", self.show_components_tab),
            ("Активация Windows", self.show_activation_tab),
            ("Установка приложений", self.show_apps_tab),
            ("Быстрая настройка Windows", self.show_quick_tab),
            ("Таймер выключения", self.show_timer_tab),
            ("Информация о ПК", self.show_info_tab)
        ]
        
        self.menu_buttons = []
        for text, callback in menu_items:
            btn = QPushButton(text)
            btn.setObjectName("menuButton")
            btn.clicked.connect(callback)
            btn.setCheckable(True)
            self.menu_buttons.append(btn)
            sidebar_layout.addWidget(btn)
        
        # Первая кнопка активна по умолчанию
        self.menu_buttons[0].setChecked(True)
        
        sidebar_layout.addStretch()
        
        # Нижние кнопки
        bottom_layout = QHBoxLayout()
        
        restart_btn = QPushButton("🔄 Перезапустить проводник")
        restart_btn.setObjectName("bottomButton")
        restart_btn.clicked.connect(self.restart_explorer)
        
        settings_btn = QPushButton("⚙️ Настройки / О программе")
        settings_btn.setObjectName("bottomButton")
        settings_btn.clicked.connect(self.show_about)
        
        bottom_layout.addWidget(restart_btn)
        bottom_layout.addWidget(settings_btn)
        sidebar_layout.addLayout(bottom_layout)
        
    def create_main_area(self):
        """Создание основной области"""
        self.main_area = QWidget()
        self.main_area.setObjectName("mainArea")
        
        self.main_layout = QVBoxLayout(self.main_area)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок текущей вкладки
        self.tab_title = QLabel("Проводник и Рабочий стол")
        self.tab_title.setObjectName("tabTitle")
        self.main_layout.addWidget(self.tab_title)
        
        # Область содержимого
        self.content_area = QScrollArea()
        self.content_area.setWidgetResizable(True)
        self.content_area.setObjectName("contentArea")
        self.main_layout.addWidget(self.content_area)
        
    def set_active_button(self, active_button):
        """Устанавливает активную кнопку меню"""
        for btn in self.menu_buttons:
            btn.setChecked(btn == active_button)
    
    def show_explorer_tab(self):
        """Вкладка Проводник и Рабочий стол"""
        self.set_active_button(self.menu_buttons[0])
        self.tab_title.setText("Проводник и Рабочий стол")
        
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # Опции проводника
        options = [
            ("Показывать скрытые файлы и папки", True),
            ("Показывать расширения файлов", True),
            ("Открывать в проводнике страницу \"Этот ПК\" вместо \"Главная\"", True),
            ("Скрыть раздел \"Галерея\"", True),
            ("Показывать иконку \"Этот ПК\" на рабочем столе", True),
            ("Убрать окончания \"-Ярлык\" у новых ярлыков", True)
        ]
        
        self.explorer_checkboxes = []
        for text, checked in options:
            cb = QCheckBox(text)
            cb.setChecked(checked)
            cb.setObjectName("optionCheckbox")
            self.explorer_checkboxes.append(cb)
            layout.addWidget(cb)
        
        # Специальные опции
        layout.addWidget(QLabel("Скрыть буквы дисков в разделе \"Этот ПК\""))
        
        disk_layout = QHBoxLayout()
        select_btn = QPushButton("Выбрать")
        select_btn.setObjectName("actionButton")
        select_btn.clicked.connect(self.select_disks)
        
        show_all_btn = QPushButton("Показать все буквы")
        show_all_btn.setObjectName("actionButton")
        show_all_btn.clicked.connect(self.show_all_disks)
        
        disk_layout.addWidget(select_btn)
        disk_layout.addWidget(show_all_btn)
        disk_layout.addStretch()
        layout.addLayout(disk_layout)
        
        layout.addWidget(QLabel("Исправить дублирование дисков в проводнике"))
        fix_btn = QPushButton("Исправить")
        fix_btn.setObjectName("actionButton")
        fix_btn.clicked.connect(self.fix_disk_duplication)
        layout.addWidget(fix_btn)
        
        layout.addStretch()
        self.content_area.setWidget(content)
    
    def show_updates_tab(self):
        """Вкладка Windows Update"""
        self.set_active_button(self.menu_buttons[1])
        self.tab_title.setText("Windows Update")
        
        content = QWidget()
        layout = QVBoxLayout(content)
        
        options = [
            "Отключить автоматические обновления Windows",
            "Отключить обновления драйверов через Windows Update", 
            "Отключить принудительные перезагрузки",
            "Отключить обновления Microsoft Store",
            "Заблокировать обновление до Windows 11"
        ]
        
        self.update_checkboxes = []
        for text in options:
            cb = QCheckBox(text)
            cb.setObjectName("optionCheckbox")
            self.update_checkboxes.append(cb)
            layout.addWidget(cb)
        
        apply_btn = QPushButton("🛡️ Применить настройки обновлений")
        apply_btn.setObjectName("primaryButton")
        apply_btn.clicked.connect(self.apply_update_settings)
        layout.addWidget(apply_btn)
        
        layout.addStretch()
        self.content_area.setWidget(content)
    
    def show_system_tab(self):
        """Вкладка Система и восстановление"""
        self.set_active_button(self.menu_buttons[2])
        self.tab_title.setText("Система и восстановление")
        
        content = QWidget()
        layout = QVBoxLayout(content)
        
        options = [
            "Отключить контроль учётных записей (UAC)",
            "Включить сторонние скрипты PowerShell",
            "Отключить защитник Windows навсегда",
            "Очистить временные файлы",
            "Дефрагментировать жёсткий диск", 
            "Оптимизировать автозагрузку",
            "Увеличить файл подкачки",
            "Отключить визуальные эффекты",
            "Включить режим высокой производительности"
        ]
        
        self.system_checkboxes = []
        for text in options:
            cb = QCheckBox(text)
            cb.setObjectName("optionCheckbox")
            self.system_checkboxes.append(cb)
            layout.addWidget(cb)
        
        # Предупреждение
        warning = QLabel("⚠️ ВНИМАНИЕ: На Windows 11 отключение UAC приведет к неработоспособности Drag-and-Drop на панели задач!")
        warning.setObjectName("warningLabel")
        warning.setWordWrap(True)
        layout.addWidget(warning)
        
        optimize_btn = QPushButton("⚡ СУПЕР ОПТИМИЗАЦИЯ СИСТЕМЫ")
        optimize_btn.setObjectName("dangerButton")
        optimize_btn.clicked.connect(self.super_optimize_system)
        layout.addWidget(optimize_btn)
        
        layout.addStretch()
        self.content_area.setWidget(content)
    
    def show_uwp_tab(self):
        """Вкладка Удаление UWP приложений"""
        self.set_active_button(self.menu_buttons[3])
        self.tab_title.setText("Удаление UWP приложений")
        
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # Три колонки приложений
        columns_widget = QWidget()
        columns_layout = QHBoxLayout(columns_widget)
        
        # Мусорные приложения (слева)
        trash_group = QGroupBox("💀 Мусорные (заброшенные Microsoft)")
        trash_group.setObjectName("trashGroup")
        trash_layout = QVBoxLayout(trash_group)
        
        trash_apps = [
            "3D Viewer", "Groove Music", "Movies & TV",
            "Paint 3D", "Skype", "Xbox Console Companion", 
            "Mixed Reality Portal", "Your Phone", "Get Help"
        ]
        
        self.trash_checkboxes = []
        for app in trash_apps:
            cb = QCheckBox(app)
            cb.setChecked(True)  # По умолчанию выбраны
            cb.setObjectName("trashCheckbox")
            self.trash_checkboxes.append(cb)
            trash_layout.addWidget(cb)
        
        # Терпимые приложения (посередине)
        ok_group = QGroupBox("😐 Терпимые")
        ok_group.setObjectName("okGroup")
        ok_layout = QVBoxLayout(ok_group)
        
        ok_apps = [
            "Calculator", "Camera", "Mail", "Calendar",
            "Microsoft Store", "Photos", "Outlook", "Weather",
            "Maps", "Voice Recorder"
        ]
        
        self.ok_checkboxes = []
        for app in ok_apps:
            cb = QCheckBox(app)
            cb.setObjectName("okCheckbox")
            self.ok_checkboxes.append(cb)
            ok_layout.addWidget(cb)
        
        # Важные приложения (справа)
        important_group = QGroupBox("⚠️ Важные (не трогать!)")
        important_group.setObjectName("importantGroup")
        important_layout = QVBoxLayout(important_group)
        
        important_apps = [
            "Microsoft Edge", "Windows Security",
            "Settings", "Windows Terminal", "Notepad"
        ]
        
        for app in important_apps:
            label = QLabel(f"🔒 {app}")
            label.setObjectName("importantLabel")
            important_layout.addWidget(label)
        
        columns_layout.addWidget(trash_group)
        columns_layout.addWidget(ok_group)
        columns_layout.addWidget(important_group)
        
        layout.addWidget(columns_widget)
        
        remove_btn = QPushButton("🗑️ УДАЛИТЬ ВЫБРАННЫЕ UWP ПРИЛОЖЕНИЯ")
        remove_btn.setObjectName("dangerButton")
        remove_btn.clicked.connect(self.remove_uwp_apps)
        layout.addWidget(remove_btn)
        
        layout.addStretch()
        self.content_area.setWidget(content)
    
    def show_personalization_tab(self):
        """Вкладка Персонализация"""
        self.set_active_button(self.menu_buttons[4])
        self.tab_title.setText("Персонализация")
        
        content = QWidget()
        layout = QVBoxLayout(content)
        
        options = [
            "Отключить анимации в Windows",
            "Включить темную тему для всех приложений",
            "Отключить прозрачность в Windows",
            "Скрыть кнопку поиска на панели задач",
            "Скрыть кнопку представления задач",
            "Отключить уведомления Windows"
        ]
        
        self.personalization_checkboxes = []
        for text in options:
            cb = QCheckBox(text)
            cb.setObjectName("optionCheckbox")
            self.personalization_checkboxes.append(cb)
            layout.addWidget(cb)
        
        apply_btn = QPushButton("🎨 Применить настройки персонализации")
        apply_btn.setObjectName("primaryButton")
        apply_btn.clicked.connect(self.apply_personalization)
        layout.addWidget(apply_btn)
        
        layout.addStretch()
        self.content_area.setWidget(content)
    
    def show_context_tab(self):
        """Вкладка Контекстное меню"""
        self.set_active_button(self.menu_buttons[5])
        self.tab_title.setText("Контекстное меню")
        
        content = QWidget()
        layout = QVBoxLayout(content)
        
        layout.addWidget(QLabel("Настройка контекстного меню Windows"))
        
        options = [
            "Включить классическое контекстное меню Windows 10",
            "Добавить \"Открыть в Windows Terminal\"",
            "Добавить \"Копировать путь к файлу\"",
            "Удалить \"Изменить с помощью Paint 3D\"",
            "Удалить \"Поделиться\" из контекстного меню"
        ]
        
        self.context_checkboxes = []
        for text in options:
            cb = QCheckBox(text)
            cb.setObjectName("optionCheckbox")
            self.context_checkboxes.append(cb)
            layout.addWidget(cb)
        
        apply_btn = QPushButton("📝 Применить настройки контекстного меню")
        apply_btn.setObjectName("primaryButton")
        apply_btn.clicked.connect(self.apply_context_menu)
        layout.addWidget(apply_btn)
        
        layout.addStretch()
        self.content_area.setWidget(content)
    
    def show_telemetry_tab(self):
        """Вкладка Отключение телеметрии"""
        self.set_active_button(self.menu_buttons[6])
        self.tab_title.setText("Отключение телеметрии")
        
        content = QWidget()
        layout = QVBoxLayout(content)
        
        layout.addWidget(QLabel("🛡️ Защита приватности и отключение слежки Microsoft"))
        
        options = [
            "Отключить телеметрию Windows полностью",
            "Отключить сбор диагностических данных",
            "Заблокировать серверы Microsoft Telemetry",
            "Отключить рекламу в Windows",
            "Отключить Cortana навсегда",
            "Отключить геолокацию",
            "Отключить синхронизацию с Microsoft"
        ]
        
        self.telemetry_checkboxes = []
        for text in options:
            cb = QCheckBox(text)
            cb.setChecked(True)  # По умолчанию все включены
            cb.setObjectName("optionCheckbox")
            self.telemetry_checkboxes.append(cb)
            layout.addWidget(cb)
        
        disable_btn = QPushButton("🛡️ ОТКЛЮЧИТЬ ВСЮ ТЕЛЕМЕТРИЮ")
        disable_btn.setObjectName("primaryButton")
        disable_btn.clicked.connect(self.disable_telemetry)
        layout.addWidget(disable_btn)
        
        layout.addStretch()
        self.content_area.setWidget(content)
    
    def show_components_tab(self):
        """Вкладка Компоненты Windows"""
        self.set_active_button(self.menu_buttons[7])
        self.tab_title.setText("Компоненты Windows")
        
        content = QWidget()
        layout = QVBoxLayout(content)
        
        layout.addWidget(QLabel("🔧 Управление компонентами Windows"))
        
        options = [
            "Отключить Internet Explorer",
            "Отключить Windows Media Player",
            "Отключить факс и сканирование",
            "Отключить XPS Viewer",
            "Отключить Work Folders Client",
            "Включить .NET Framework 3.5",
            "Включить Hyper-V (только Pro версии)"
        ]
        
        self.components_checkboxes = []
        for text in options:
            cb = QCheckBox(text)
            cb.setObjectName("optionCheckbox")
            self.components_checkboxes.append(cb)
            layout.addWidget(cb)
        
        apply_btn = QPushButton("🔧 Применить изменения компонентов")
        apply_btn.setObjectName("primaryButton")
        apply_btn.clicked.connect(self.manage_components)
        layout.addWidget(apply_btn)
        
        layout.addStretch()
        self.content_area.setWidget(content)
    
    def show_activation_tab(self):
        """Вкладка Активация Windows"""
        self.set_active_button(self.menu_buttons[8])
        self.tab_title.setText("Активация Windows")
        
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # Windows активация
        windows_group = QGroupBox("🔑 Активация Windows")
        windows_group.setObjectName("activationGroup")
        windows_layout = QVBoxLayout(windows_group)
        
        activate_win_btn = QPushButton("🔑 Активировать Windows через KMS")
        activate_win_btn.setObjectName("primaryButton")
        activate_win_btn.clicked.connect(self.activate_windows)
        windows_layout.addWidget(activate_win_btn)
        
        check_win_btn = QPushButton("🔍 Проверить статус активации Windows")
        check_win_btn.setObjectName("secondaryButton")
        check_win_btn.clicked.connect(self.check_windows_activation)
        windows_layout.addWidget(check_win_btn)
        
        # Office активация
        office_group = QGroupBox("📄 Активация Microsoft Office")
        office_group.setObjectName("activationGroup")
        office_layout = QVBoxLayout(office_group)
        
        activate_office_btn = QPushButton("🔑 Активировать Microsoft Office")
        activate_office_btn.setObjectName("primaryButton")
        activate_office_btn.clicked.connect(self.activate_office)
        office_layout.addWidget(activate_office_btn)
        
        check_office_btn = QPushButton("🔍 Проверить статус активации Office")
        check_office_btn.setObjectName("secondaryButton")
        check_office_btn.clicked.connect(self.check_office_activation)
        office_layout.addWidget(check_office_btn)
        
        layout.addWidget(windows_group)
        layout.addWidget(office_group)
        
        # Предупреждение
        warning = QLabel("⚠️ Мёртвые KMS сервера удалены! Используются только рабочие сервера!")
        warning.setObjectName("warningLabel")
        warning.setWordWrap(True)
        layout.addWidget(warning)
        
        layout.addStretch()
        self.content_area.setWidget(content)
    
    def show_apps_tab(self):
        """Вкладка Установка приложений"""
        self.set_active_button(self.menu_buttons[9])
        self.tab_title.setText("Установка приложений")
        
        content = QWidget()
        layout = QVBoxLayout(content)
        
        layout.addWidget(QLabel("📦 Быстрая установка популярных приложений"))
        
        apps = [
            ("🌐 Google Chrome", "Быстрый браузер от Google"),
            ("🦊 Mozilla Firefox", "Приватный браузер"),
            ("💬 Discord", "Общение с друзьями"),
            ("🎵 Spotify", "Музыкальный стриминг"),
            ("📝 Notepad++", "Продвинутый текстовый редактор"),
            ("🎮 Steam", "Игровая платформа"),
            ("📹 VLC Media Player", "Универсальный медиаплеер"),
            ("🗜️ 7-Zip", "Архиватор файлов"),
            ("🎨 GIMP", "Графический редактор"),
            ("📊 LibreOffice", "Офисный пакет")
        ]
        
        self.app_checkboxes = []
        for app_name, description in apps:
            widget = QWidget()
            hlayout = QHBoxLayout(widget)
            hlayout.setContentsMargins(0, 0, 0, 0)
            
            cb = QCheckBox(app_name)
            cb.setObjectName("optionCheckbox")
            self.app_checkboxes.append(cb)
            
            desc_label = QLabel(f"- {description}")
            desc_label.setObjectName("descriptionLabel")
            
            hlayout.addWidget(cb)
            hlayout.addWidget(desc_label)
            hlayout.addStretch()
            
            layout.addWidget(widget)
        
        install_btn = QPushButton("📦 УСТАНОВИТЬ ВЫБРАННЫЕ ПРИЛОЖЕНИЯ")
        install_btn.setObjectName("primaryButton")
        install_btn.clicked.connect(self.install_apps)
        layout.addWidget(install_btn)
        
        layout.addStretch()
        self.content_area.setWidget(content)
    
    def show_quick_tab(self):
        """Вкладка Быстрая настройка Windows"""
        self.set_active_button(self.menu_buttons[10])
        self.tab_title.setText("Быстрая настройка Windows")
        
        content = QWidget()
        layout = QVBoxLayout(content)
        
        layout.addWidget(QLabel("⚡ Быстрые настройки для оптимальной работы Windows"))
        
        # Предустановленные конфигурации
        configs = [
            ("🎮 Игровая конфигурация", "Оптимизация для игр"),
            ("💼 Рабочая конфигурация", "Настройки для работы"),
            ("🔒 Приватная конфигурация", "Максимальная приватность"),
            ("⚡ Максимальная производительность", "Все настройки на скорость"),
            ("🛡️ Безопасная конфигурация", "Повышенная безопасность")
        ]
        
        for config_name, description in configs:
            widget = QWidget()
            hlayout = QHBoxLayout(widget)
            
            btn = QPushButton(config_name)
            btn.setObjectName("configButton")
            btn.clicked.connect(lambda checked, name=config_name: self.apply_quick_config(name))
            
            desc_label = QLabel(description)
            desc_label.setObjectName("descriptionLabel")
            
            hlayout.addWidget(btn)
            hlayout.addWidget(desc_label)
            hlayout.addStretch()
            
            layout.addWidget(widget)
        
        layout.addStretch()
        self.content_area.setWidget(content)
    
    def show_timer_tab(self):
        """Вкладка Таймер выключения"""
        self.set_active_button(self.menu_buttons[11])
        self.tab_title.setText("Таймер выключения")
        
        content = QWidget()
        layout = QVBoxLayout(content)
        
        layout.addWidget(QLabel("⏰ Таймер выключения компьютера"))
        
        # Настройки времени
        time_group = QGroupBox("Время выключения")
        time_group.setObjectName("timerGroup")
        time_layout = QHBoxLayout(time_group)
        
        time_layout.addWidget(QLabel("Выключить через:"))
        
        self.hours_spin = QSpinBox()
        self.hours_spin.setRange(0, 23)
        self.hours_spin.setValue(0)
        self.hours_spin.setSuffix(" ч")
        
        self.minutes_spin = QSpinBox()
        self.minutes_spin.setRange(0, 59)
        self.minutes_spin.setValue(30)
        self.minutes_spin.setSuffix(" мин")
        
        time_layout.addWidget(self.hours_spin)
        time_layout.addWidget(self.minutes_spin)
        time_layout.addStretch()
        
        # Тип действия
        action_group = QGroupBox("Действие")
        action_group.setObjectName("timerGroup")
        action_layout = QVBoxLayout(action_group)
        
        self.action_group = QButtonGroup()
        
        shutdown_radio = QRadioButton("🔌 Выключение")
        shutdown_radio.setChecked(True)
        restart_radio = QRadioButton("🔄 Перезагрузка")
        sleep_radio = QRadioButton("😴 Спящий режим")
        
        self.action_group.addButton(shutdown_radio, 0)
        self.action_group.addButton(restart_radio, 1)
        self.action_group.addButton(sleep_radio, 2)
        
        action_layout.addWidget(shutdown_radio)
        action_layout.addWidget(restart_radio)
        action_layout.addWidget(sleep_radio)
        
        layout.addWidget(time_group)
        layout.addWidget(action_group)
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        
        start_btn = QPushButton("⏰ ЗАПУСТИТЬ ТАЙМЕР")
        start_btn.setObjectName("primaryButton")
        start_btn.clicked.connect(self.start_timer)
        
        cancel_btn = QPushButton("❌ ОТМЕНИТЬ ТАЙМЕР")
        cancel_btn.setObjectName("dangerButton")
        cancel_btn.clicked.connect(self.cancel_timer)
        
        buttons_layout.addWidget(start_btn)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
        layout.addStretch()
        self.content_area.setWidget(content)
    
    def show_info_tab(self):
        """Вкладка Информация о ПК"""
        self.set_active_button(self.menu_buttons[12])
        self.tab_title.setText("Информация о ПК")
        
        content = QWidget()
        layout = QVBoxLayout(content)
        
        layout.addWidget(QLabel("💻 Информация о системе"))
        
        # Фейковая информация о системе
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setObjectName("infoText")
        
        fake_info = f"""
🖥️ ИНФОРМАЦИЯ О СИСТЕМЕ

Операционная система: Windows 11 Pro 22H2
Процессор: Intel Core i7-12700K @ 3.60GHz (12 ядер)
Оперативная память: 32 GB DDR4-3200
Видеокарта: NVIDIA GeForce RTX 4080 (16 GB)
Материнская плата: ASUS ROG STRIX Z690-E
Жёсткий диск: Samsung 980 PRO 1TB NVMe SSD

🔧 СТАТУС ОПТИМИЗАЦИИ

Применено оптимизаций: {random.randint(15, 45)}
Ускорение системы: +{random.randint(200, 900)}%
Освобождено места: {random.randint(5, 50)} GB
Статус активации: ✅ Активирован навсегда
Защита от телеметрии: ✅ Включена

⚡ ПРОИЗВОДИТЕЛЬНОСТЬ

Загрузка CPU: {random.randint(5, 25)}%
Использование RAM: {random.randint(30, 60)}%
Температура CPU: {random.randint(35, 55)}°C
Скорость SSD: {random.randint(3000, 7000)} MB/s
        """
        
        info_text.setPlainText(fake_info.strip())
        layout.addWidget(info_text)
        
        refresh_btn = QPushButton("🔄 Обновить информацию")
        refresh_btn.setObjectName("secondaryButton")
        refresh_btn.clicked.connect(lambda: self.show_info_tab())  # Перезагружает вкладку
        layout.addWidget(refresh_btn)
        
        layout.addStretch()
        self.content_area.setWidget(content)
    
    # Фейковые функции с многопоточностью
    
    def show_progress_dialog(self, title, steps, task_name=None):
        """Показывает многопоточный диалог прогресса"""
        if task_name is None:
            task_name = title
            
        dialog = ProgressDialog(self, title, steps, task_name)
        result = dialog.exec()
        
        if result == QDialog.DialogCode.Accepted:
            return dialog.success, dialog.result
        else:
            return False, "Операция отменена пользователем"
    
    def select_disks(self):
        """Выбор дисков для скрытия"""
        disks = ["C:", "D:", "E:", "F:", "G:"]
        selected, ok = QInputDialog.getItem(self, "Выбор диска", 
                                          "Выберите диск для скрытия:", 
                                          disks, 0, False)
        if ok:
            QMessageBox.information(self, "Успех", f"Диск {selected} будет скрыт!")
    
    def show_all_disks(self):
        """Показать все диски"""
        QMessageBox.information(self, "Успех", "Все диски теперь видимы в проводнике!")
    
    def fix_disk_duplication(self):
        """Исправить дублирование дисков"""
        steps = [
            "Сканирование реестра Windows...",
            "Поиск дублированных записей дисков...",
            "Анализ структуры проводника...",
            "Удаление лишних записей...",
            "Очистка кэша проводника...",
            "Перезапуск службы проводника..."
        ]
        
        success, message = self.show_progress_dialog("Исправление дублирования дисков", steps)
        
        if success:
            QMessageBox.information(self, "Успех", "✅ Дублирование дисков исправлено!\n\nПроводник обновлен.")
        else:
            QMessageBox.warning(self, "Ошибка", f"❌ {message}")
    
    def apply_update_settings(self):
        """Применить настройки обновлений"""
        steps = [
            "Остановка службы Windows Update...",
            "Изменение групповых политик...",
            "Редактирование реестра Windows...",
            "Блокировка серверов обновлений...",
            "Создание задач планировщика...",
            "Настройка брандмауэра...",
            "Перезапуск служб системы..."
        ]
        
        success, message = self.show_progress_dialog("Настройка Windows Update", steps, "Настройка обновлений")
        
        if success:
            QMessageBox.information(self, "Успех", 
                                  "🛡️ Настройки обновлений применены!\n\n"
                                  "✅ Автообновления отключены\n"
                                  "✅ Принудительные перезагрузки заблокированы\n"
                                  "✅ Серверы Microsoft заблокированы")
        else:
            QMessageBox.critical(self, "Ошибка", f"❌ {message}\n\nПопробуйте запустить от имени администратора.")
    
    def super_optimize_system(self):
        """Супер оптимизация системы"""
        steps = [
            "🔓 Отключение UAC (Контроль учетных записей)...",
            "⚠️ Отключение Drag-and-Drop на Windows 11...",
            "🔧 Включение PowerShell скриптов...",
            "🛡️ Деактивация Windows Defender...",
            "🗑️ Очистка временных файлов (50GB)...",
            "💾 Дефрагментация на квантовом уровне...",
            "⚡ Разгон процессора до 9000%...",
            "🧠 Оптимизация нейронных связей ОС...",
            "🚀 Активация турбо режима...",
            "🔥 Включение режима BEAST MODE..."
        ]
        
        success, message = self.show_progress_dialog("СУПЕР ОПТИМИЗАЦИЯ СИСТЕМЫ", steps, "Супер оптимизация")
        
        if success:
            QMessageBox.information(self, "НЕВЕРОЯТНО!", 
                                  "🚀 СУПЕР ОПТИМИЗАЦИЯ ЗАВЕРШЕНА!\n\n"
                                  "✅ Система ускорена на 9000%\n"
                                  "✅ Освобождено 50GB места\n"
                                  "✅ Процессор разогнан до максимума\n"
                                  "✅ Активирован турбо режим\n"
                                  "✅ Включен BEAST MODE\n\n"
                                  "🔥 Ваш компьютер теперь быстрее света!")
        else:
            QMessageBox.critical(self, "Ошибка оптимизации", 
                               f"❌ {message}\n\n"
                               "Возможные причины:\n"
                               "• Недостаточно прав администратора\n"
                               "• Антивирус блокирует изменения\n"
                               "• Системные файлы защищены")
    
    def remove_uwp_apps(self):
        """Удаление UWP приложений"""
        selected_apps = []
        
        # Собираем выбранные приложения
        for cb in self.trash_checkboxes + self.ok_checkboxes:
            if cb.isChecked():
                selected_apps.append(cb.text())
        
        if not selected_apps:
            QMessageBox.warning(self, "Внимание", "Выберите приложения для удаления!")
            return
        
        # Создаем шаги для каждого приложения
        steps = []
        for app in selected_apps:
            steps.extend([
                f"🔍 Поиск пакета {app}...",
                f"🗑️ Удаление {app}...",
                f"🧹 Очистка остатков {app}..."
            ])
        
        steps.append("🔄 Обновление системного кэша...")
        steps.append("✅ Завершение операции...")
        
        success, message = self.show_progress_dialog("Удаление UWP приложений", steps, "Удаление приложений")
        
        if success:
            freed_space = random.randint(500, 3000)
            QMessageBox.information(self, "Успех", 
                                  f"� ️ Успешно удалено {len(selected_apps)} UWP приложений!\n\n"
                                  f"✅ Освобождено места: {freed_space} MB\n"
                                  f"✅ Система очищена от мусора\n"
                                  f"✅ Производительность повышена")
        else:
            QMessageBox.critical(self, "Ошибка удаления", 
                               f"❌ {message}\n\n"
                               "Некоторые приложения могут быть защищены системой.")
    
    def apply_personalization(self):
        """Применить настройки персонализации"""
        steps = [
            "🎨 Изменение темы оформления...",
            "✨ Настройка анимаций и эффектов...",
            "📱 Изменение панели задач...",
            "🖼️ Настройка рабочего стола...",
            "🔍 Конфигурация поиска...",
            "📢 Настройка уведомлений...",
            "🎭 Применение персонализации..."
        ]
        
        success, message = self.show_progress_dialog("Применение персонализации", steps)
        
        if success:
            QMessageBox.information(self, "Успех", 
                                  "🎨 Настройки персонализации применены!\n\n"
                                  "✅ Интерфейс оптимизирован\n"
                                  "✅ Анимации настроены\n"
                                  "✅ Темная тема активирована")
        else:
            QMessageBox.warning(self, "Ошибка", f"❌ {message}")
    
    def apply_context_menu(self):
        """Применить настройки контекстного меню"""
        steps = [
            "📝 Сканирование текущего контекстного меню...",
            "🔧 Изменение записей реестра...",
            "➕ Добавление новых пунктов меню...",
            "➖ Удаление ненужных пунктов...",
            "🔄 Перезапуск проводника...",
            "✅ Применение изменений..."
        ]
        
        success, message = self.show_progress_dialog("Настройка контекстного меню", steps)
        
        if success:
            QMessageBox.information(self, "Успех", 
                                  "📝 Контекстное меню настроено!\n\n"
                                  "✅ Классическое меню включено\n"
                                  "✅ Полезные пункты добавлены\n"
                                  "✅ Мусорные пункты удалены")
        else:
            QMessageBox.warning(self, "Ошибка", f"❌ {message}")
    
    def disable_telemetry(self):
        """Отключить телеметрию"""
        steps = [
            "🛡️ Остановка служб телеметрии Microsoft...",
            "🚫 Блокировка серверов сбора данных...",
            "📋 Изменение групповых политик...",
            "🗑️ Очистка логов телеметрии...",
            "🎤 Отключение Cortana навсегда...",
            "📍 Деактивация геолокации...",
            "🔒 Настройка брандмауэра...",
            "🔐 Усиление приватности...",
            "🛡️ Активация защиты данных..."
        ]
        
        success, message = self.show_progress_dialog("Отключение телеметрии", steps, "Защита приватности")
        
        if success:
            QMessageBox.information(self, "Успех", 
                                  "🛡️ Телеметрия полностью отключена!\n\n"
                                  "✅ Сбор данных заблокирован\n"
                                  "✅ Серверы Microsoft заблокированы\n"
                                  "✅ Cortana деактивирована\n"
                                  "✅ Ваша приватность защищена!")
        else:
            QMessageBox.critical(self, "Ошибка", f"❌ {message}")
    
    def manage_components(self):
        """Управление компонентами Windows"""
        steps = [
            "🔍 Сканирование установленных компонентов...",
            "📋 Анализ зависимостей системы...",
            "❌ Отключение ненужных компонентов...",
            "✅ Включение полезных компонентов...",
            "🔄 Обновление конфигурации системы...",
            "🛠️ Применение изменений..."
        ]
        
        success, message = self.show_progress_dialog("Управление компонентами", steps)
        
        if success:
            QMessageBox.information(self, "Успех", 
                                  "🔧 Компоненты Windows настроены!\n\n"
                                  "✅ Ненужные компоненты отключены\n"
                                  "✅ Полезные функции включены\n"
                                  "✅ Система оптимизирована")
        else:
            QMessageBox.warning(self, "Ошибка", f"❌ {message}")
    
    def activate_windows(self):
        """Активация Windows"""
        steps = [
            "🔍 Проверка версии Windows...",
            "🌐 Подключение к KMS серверу...",
            "🔑 Получение лицензионного ключа...",
            "⚙️ Применение активации...",
            "✅ Проверка статуса активации...",
            "🛡️ Регистрация в системе Microsoft..."
        ]
        
        success, message = self.show_progress_dialog("Активация Windows", steps, "Активация Windows")
        
        if success:
            QMessageBox.information(self, "Успех!", 
                                  "🔑 Windows успешно активирован!\n\n"
                                  "✅ Лицензия: Подлинная\n"
                                  "✅ Статус: Активирован навсегда\n"
                                  "✅ KMS сервер: Подключен\n"
                                  "✅ Все функции разблокированы")
        else:
            QMessageBox.critical(self, "Ошибка активации!", 
                               f"❌ {message}\n\n"
                               "Возможные причины:\n"
                               "• Нет подключения к интернету\n"
                               "• KMS сервер недоступен\n"
                               "• Антивирус блокирует активацию\n"
                               "• Неподдерживаемая версия Windows")
    
    def activate_office(self):
        """Активация Office"""
        steps = [
            "🔍 Поиск установленного Microsoft Office...",
            "📋 Определение версии Office...",
            "🌐 Подключение к KMS серверу...",
            "🔑 Получение лицензии Office...",
            "⚙️ Применение активации...",
            "✅ Проверка статуса лицензии..."
        ]
        
        success, message = self.show_progress_dialog("Активация Microsoft Office", steps, "Активация Office")
        
        if success:
            office_versions = ["Office 365 Pro Plus", "Office 2021 Professional", "Office 2019 Enterprise"]
            version = random.choice(office_versions)
            
            QMessageBox.information(self, "Успех!", 
                                  f"🔑 Microsoft Office успешно активирован!\n\n"
                                  f"✅ Версия: {version}\n"
                                  "✅ Статус: Активирован навсегда\n"
                                  "✅ Все приложения разблокированы\n"
                                  "✅ Премиум функции доступны")
        else:
            if "не установлен" in message:
                QMessageBox.warning(self, "Office не найден!", 
                                  "⚠️ Microsoft Office не установлен!\n\n"
                                  "Установите любую версию Office и повторите активацию.")
            else:
                QMessageBox.critical(self, "Ошибка активации!", f"❌ {message}")
    
    def install_apps(self):
        """Установка приложений"""
        selected_apps = [cb for cb in self.app_checkboxes if cb.isChecked()]
        
        if not selected_apps:
            QMessageBox.warning(self, "Внимание", "Выберите приложения для установки!")
            return
        
        # Создаем детальные шаги для каждого приложения
        steps = []
        for cb in selected_apps:
            app_name = cb.text().split()[1] if len(cb.text().split()) > 1 else cb.text()
            steps.extend([
                f"🌐 Загрузка {app_name}...",
                f"📦 Установка {app_name}...",
                f"⚙️ Настройка {app_name}..."
            ])
        
        steps.append("🔄 Обновление системного реестра...")
        steps.append("✅ Завершение установки...")
        
        success, message = self.show_progress_dialog("Установка приложений", steps, "Установка программ")
        
        if success:
            QMessageBox.information(self, "Успех!", 
                                  f"📦 Успешно установлено {len(selected_apps)} приложений!\n\n"
                                  "✅ Все приложения готовы к использованию\n"
                                  "✅ Ярлыки созданы на рабочем столе\n"
                                  "✅ Автозапуск настроен")
        else:
            QMessageBox.critical(self, "Ошибка установки", 
                               f"❌ {message}\n\n"
                               "Некоторые приложения могли не установиться.")
    
    def apply_quick_config(self, config_name):
        """Применить быструю конфигурацию"""
        configs = {
            "🎮 Игровая конфигурация": [
                "🎮 Активация игрового режима Windows...",
                "⚡ Отключение визуальных эффектов...",
                "🚀 Настройка приоритета игровых процессов...",
                "🖥️ Оптимизация GPU и DirectX...",
                "🔇 Отключение ненужных служб...",
                "💾 Настройка файла подкачки для игр...",
                "🌐 Оптимизация сетевых настроек..."
            ],
            "💼 Рабочая конфигурация": [
                "💼 Настройка рабочего окружения...",
                "🔋 Оптимизация энергосбережения...",
                "📊 Настройка для офисных задач...",
                "🛡️ Усиление безопасности системы...",
                "🌐 Конфигурация корпоративной сети...",
                "📁 Настройка файлового доступа...",
                "⏰ Конфигурация автоматических задач..."
            ],
            "🔒 Приватная конфигурация": [
                "🔒 Максимальная защита приватности...",
                "🛡️ Отключение всей телеметрии Microsoft...",
                "🚫 Блокировка трекеров и рекламы...",
                "🔐 Настройка VPN и прокси...",
                "🗝️ Усиление шифрования данных...",
                "👁️ Отключение слежки за пользователем...",
                "🔒 Активация анонимного режима..."
            ],
            "⚡ Максимальная производительность": [
                "⚡ ЭКСТРЕМАЛЬНЫЙ разгон системы...",
                "🚀 Разгон CPU до предельных частот...",
                "💾 Оптимизация оперативной памяти...",
                "🖥️ Разгон видеокарты до максимума...",
                "⚙️ Отключение всех лимитов Windows...",
                "🔥 Активация BEAST MODE...",
                "🌪️ Включение TURBO OVERDRIVE..."
            ],
            "🛡️ Безопасная конфигурация": [
                "🛡️ Максимальное усиление защиты...",
                "🔒 Настройка продвинутого брандмауэра...",
                "🦠 Обновление антивирусных баз...",
                "🔍 Глубокая проверка системы на угрозы...",
                "🚫 Блокировка подозрительных процессов...",
                "🔐 Активация военного шифрования...",
                "🛡️ Включение режима FORTRESS..."
            ]
        }
        
        steps = configs.get(config_name, ["Применение настроек..."])
        
        success, message = self.show_progress_dialog(f"Применение: {config_name}", steps, config_name)
        
        if success:
            QMessageBox.information(self, "Конфигурация применена!", 
                                  f"✅ {config_name} успешно применена!\n\n"
                                  "🔄 Рекомендуется перезагрузить компьютер\n"
                                  "для полного применения всех изменений.")
        else:
            QMessageBox.critical(self, "Ошибка конфигурации", f"❌ {message}")
    
    def start_timer(self):
        """Запуск таймера"""
        hours = self.hours_spin.value()
        minutes = self.minutes_spin.value()
        
        if hours == 0 and minutes == 0:
            QMessageBox.warning(self, "Внимание", "Установите время больше 0!")
            return
        
        actions = ["выключение", "перезагрузка", "спящий режим"]
        action = actions[self.action_group.checkedId()]
        
        total_minutes = hours * 60 + minutes
        
        # Имитируем установку таймера
        steps = [
            f"⏰ Создание задачи в планировщике...",
            f"🔧 Настройка параметров {action}...",
            f"✅ Активация таймера на {total_minutes} минут..."
        ]
        
        success, message = self.show_progress_dialog("Установка таймера", steps, "Таймер выключения")
        
        if success:
            QMessageBox.information(self, "Таймер запущен!", 
                                  f"⏰ Таймер успешно установлен!\n\n"
                                  f"🎯 Действие: {action.title()}\n"
                                  f"⏱️ Время: {hours}ч {minutes}мин\n"
                                  f"🔔 Компьютер будет {action} через {total_minutes} минут\n\n"
                                  "💡 Вы получите предупреждение за 5 минут до выполнения.")
        else:
            QMessageBox.critical(self, "Ошибка таймера", f"❌ {message}")
    
    def cancel_timer(self):
        """Отмена таймера"""
        steps = [
            "🔍 Поиск активных таймеров...",
            "❌ Отмена запланированных задач...",
            "🗑️ Очистка планировщика..."
        ]
        
        success, message = self.show_progress_dialog("Отмена таймера", steps, "Отмена таймера")
        
        if success:
            QMessageBox.information(self, "Таймер отменён", 
                                  "✅ Все таймеры выключения отменены!\n\n"
                                  "Компьютер не будет автоматически выключаться.")
        else:
            QMessageBox.warning(self, "Внимание", "⚠️ Активные таймеры не найдены!")
    
    def restart_explorer(self):
        """Перезапуск проводника"""
        steps = [
            "🔍 Поиск процесса explorer.exe...",
            "⏹️ Завершение процесса проводника...",
            "⏳ Ожидание полного завершения...",
            "🚀 Запуск нового процесса explorer.exe...",
            "⚙️ Восстановление рабочего стола...",
            "✅ Проверка работоспособности..."
        ]
        
        success, message = self.show_progress_dialog("Перезапуск проводника", steps, "Перезапуск Explorer")
        
        if success:
            QMessageBox.information(self, "Успех", 
                                  "🔄 Проводник успешно перезапущен!\n\n"
                                  "✅ Рабочий стол обновлен\n"
                                  "✅ Панель задач восстановлена\n"
                                  "✅ Все изменения применены")
        else:
            QMessageBox.critical(self, "Ошибка", f"❌ {message}")
    
    def show_about(self):
        """О программе"""
        about_text = f"""
MakuTweaker v{self.version}
Революционный оптимизатор Windows

🚀 Возможности:
• Ускорение системы до 9000%
• Полное отключение телеметрии
• Активация Windows и Office
• Удаление мусорных UWP приложений
• Быстрая установка программ

⚠️ ВНИМАНИЕ: Это пародия!
Программа ничего не делает, только показывает интерфейс.

Автор: Неизвестный гений программирования
Лицензия: Абсолютно бесплатно
        """
        
        QMessageBox.about(self, "О программе", about_text.strip())
    
    def apply_dark_theme(self):
        """Применяет темную тему как в оригинале"""
        self.setStyleSheet("""
            /* Основные цвета */
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            
            /* Боковое меню */
            QWidget#sidebar {
                background-color: #1e1e1e;
                border-right: 1px solid #404040;
            }
            
            QLabel#header {
                background-color: #1e1e1e;
                color: #ffffff;
                font-size: 18px;
                font-weight: bold;
                padding: 20px;
                border-bottom: 1px solid #404040;
            }
            
            /* Кнопки меню */
            QPushButton#menuButton {
                background-color: transparent;
                color: #ffffff;
                border: none;
                padding: 12px 20px;
                text-align: left;
                font-size: 13px;
            }
            
            QPushButton#menuButton:hover {
                background-color: #404040;
            }
            
            QPushButton#menuButton:checked {
                background-color: #0078d4;
                color: #ffffff;
            }
            
            /* Нижние кнопки */
            QPushButton#bottomButton {
                background-color: #404040;
                color: #ffffff;
                border: 1px solid #606060;
                padding: 8px;
                font-size: 11px;
                margin: 2px;
            }
            
            QPushButton#bottomButton:hover {
                background-color: #505050;
            }
            
            /* Основная область */
            QWidget#mainArea {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            
            QLabel#tabTitle {
                font-size: 24px;
                font-weight: bold;
                color: #ffffff;
                margin-bottom: 20px;
            }
            
            QScrollArea#contentArea {
                background-color: #2b2b2b;
                border: none;
            }
            
            /* Чекбоксы */
            QCheckBox#optionCheckbox {
                color: #ffffff;
                font-size: 13px;
                padding: 5px;
            }
            
            QCheckBox#optionCheckbox::indicator {
                width: 18px;
                height: 18px;
            }
            
            QCheckBox#optionCheckbox::indicator:unchecked {
                background-color: #404040;
                border: 2px solid #606060;
                border-radius: 3px;
            }
            
            QCheckBox#optionCheckbox::indicator:checked {
                background-color: #0078d4;
                border: 2px solid #0078d4;
                border-radius: 3px;
            }
            
            QCheckBox#trashCheckbox {
                color: #ff6b6b;
                font-size: 13px;
                padding: 3px;
            }
            
            QCheckBox#okCheckbox {
                color: #ffa726;
                font-size: 13px;
                padding: 3px;
            }
            
            /* Кнопки действий */
            QPushButton#primaryButton {
                background-color: #0078d4;
                color: #ffffff;
                border: none;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 4px;
                margin: 10px 0;
            }
            
            QPushButton#primaryButton:hover {
                background-color: #106ebe;
            }
            
            QPushButton#secondaryButton {
                background-color: #404040;
                color: #ffffff;
                border: 1px solid #606060;
                padding: 10px 20px;
                font-size: 13px;
                border-radius: 4px;
                margin: 5px 0;
            }
            
            QPushButton#secondaryButton:hover {
                background-color: #505050;
            }
            
            QPushButton#dangerButton {
                background-color: #d32f2f;
                color: #ffffff;
                border: none;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 4px;
                margin: 10px 0;
            }
            
            QPushButton#dangerButton:hover {
                background-color: #b71c1c;
            }
            
            QPushButton#actionButton {
                background-color: #606060;
                color: #ffffff;
                border: none;
                padding: 8px 16px;
                font-size: 12px;
                border-radius: 3px;
                margin: 2px;
            }
            
            QPushButton#actionButton:hover {
                background-color: #707070;
            }
            
            QPushButton#configButton {
                background-color: #2e7d32;
                color: #ffffff;
                border: none;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: bold;
                border-radius: 4px;
                margin: 5px 0;
                min-width: 200px;
            }
            
            QPushButton#configButton:hover {
                background-color: #388e3c;
            }
            
            /* Группы */
            QGroupBox {
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #404040;
                border-radius: 5px;
                margin: 10px 0;
                padding-top: 10px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
            
            QGroupBox#trashGroup {
                border-color: #d32f2f;
            }
            
            QGroupBox#trashGroup::title {
                color: #ff6b6b;
            }
            
            QGroupBox#okGroup {
                border-color: #ff9800;
            }
            
            QGroupBox#okGroup::title {
                color: #ffa726;
            }
            
            QGroupBox#importantGroup {
                border-color: #4caf50;
            }
            
            QGroupBox#importantGroup::title {
                color: #66bb6a;
            }
            
            QGroupBox#activationGroup {
                border-color: #2196f3;
            }
            
            QGroupBox#timerGroup {
                border-color: #9c27b0;
            }
            
            /* Лейблы */
            QLabel#importantLabel {
                color: #66bb6a;
                font-size: 12px;
                padding: 2px;
            }
            
            QLabel#descriptionLabel {
                color: #b0b0b0;
                font-size: 11px;
                font-style: italic;
            }
            
            QLabel#warningLabel {
                color: #ff6b6b;
                font-size: 12px;
                font-weight: bold;
                background-color: #3d1a1a;
                border: 1px solid #d32f2f;
                border-radius: 4px;
                padding: 10px;
                margin: 10px 0;
            }
            
            /* Спинбоксы */
            QSpinBox {
                background-color: #404040;
                color: #ffffff;
                border: 1px solid #606060;
                border-radius: 3px;
                padding: 5px;
                font-size: 13px;
            }
            
            QSpinBox:focus {
                border-color: #0078d4;
            }
            
            /* Радиокнопки */
            QRadioButton {
                color: #ffffff;
                font-size: 13px;
                padding: 5px;
            }
            
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
            }
            
            QRadioButton::indicator:unchecked {
                background-color: #404040;
                border: 2px solid #606060;
                border-radius: 8px;
            }
            
            QRadioButton::indicator:checked {
                background-color: #0078d4;
                border: 2px solid #0078d4;
                border-radius: 8px;
            }
            
            /* Текстовые области */
            QTextEdit#infoText {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #404040;
                border-radius: 4px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                padding: 10px;
            }
            
            /* Диалоги прогресса */
            QProgressDialog {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            
            QProgressBar {
                background-color: #404040;
                border: 1px solid #606060;
                border-radius: 4px;
                text-align: center;
            }
            
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 3px;
            }
        """)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("MakuTweaker")
    app.setApplicationVersion("4.3.0")
    
    # Устанавливаем иконку приложения (если есть)
    try:
        app.setWindowIcon(QIcon("makutweaker.ico"))
    except:
        pass
    
    window = MakuTweaker()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
    
    def check_windows_activation(self):
        """Проверка активации Windows"""
        # Быстрая проверка без прогресса
        statuses = [
            ("✅ Активирован", "Windows активирован навсегда\nЛицензия: Подлинная\nТип: Retail/OEM"),
            ("⚠️ Не активирован", "Требуется активация Windows\nОсталось дней: 30\nСтатус: Пробная версия"),
            ("🔄 Временная лицензия", "Осталось 30 дней пробного периода\nТребуется постоянная активация")
        ]
        
        status, description = random.choice(statuses)
        QMessageBox.information(self, "Статус активации Windows", f"{status}\n\n{description}")
    
    def check_office_activation(self):
        """Проверка активации Office"""
        if random.choice([True, False]):
            office_versions = ["Office 365 Pro Plus", "Office 2021 Professional", "Office 2019 Enterprise"]
            version = random.choice(office_versions)
            QMessageBox.information(self, "Статус активации Office", 
                                  f"✅ Microsoft Office активирован\n\n"
                                  f"Версия: {version}\n"
                                  f"Лицензия: Подлинная\n"
                                  f"Статус: Активирован навсегда")
        else:
            QMessageBox.information(self, "Статус активации Office", 
                                  "❌ Microsoft Office не установлен\n\n"
                                  "Установите любую версию Office\n"
                                  "для проверки активации")