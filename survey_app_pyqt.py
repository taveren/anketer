#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Система анкетирования - Desktop приложение на PyQt6
Кроссплатформенное Python приложение с файловым хранилищем
"""

import sys
import json
import os
import csv
import uuid
import platform
from datetime import datetime
from typing import Dict, List, Any, Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QLabel, QPushButton, QLineEdit, QTextEdit, 
    QRadioButton, QCheckBox, QSpinBox, QProgressBar, QTableWidget, 
    QTableWidgetItem, QTabWidget, QGroupBox, QMessageBox, 
    QFileDialog, QDialog, QDialogButtonBox, QFormLayout,
    QListWidget, QListWidgetItem, QSplitter, QFrame, QInputDialog,
    QComboBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPalette, QColor

class SurveyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ASRR - Система анкетирования")
        self.setGeometry(100, 100, 400, 300)
        self.setFixedSize(400, 300)
        self.center_window() # Центрируем окно
        
        # Определяем путь к данным
        self.data_dir = self.get_data_directory()
        self.surveys_file = os.path.join(self.data_dir, "surveys.json")
        self.responses_file = os.path.join(self.data_dir, "responses.json")
        self.settings_file = os.path.join(self.data_dir, "settings.json")
        
        # Создаем директорию если не существует
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Загружаем данные
        self.surveys = self.load_surveys()
        self.responses = self.load_responses()
        self.settings = self.load_settings()
        
        # Текущий пользователь
        self.current_survey = None
        self.current_answers = {}
        self.current_question = 0
        
        self.setup_ui()
        self.setup_styles()
        self.setup_icon()
        
    def center_window(self):
        """Центрируем окно на экране"""
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        self.move(x, y)
    
    def get_data_directory(self):
        """Получаем путь к директории с данными в зависимости от ОС"""
        if platform.system() == "Windows":
            appdata = os.environ.get('APPDATA', '')
            return os.path.join(appdata, "SurveyApp", "Data")
        elif platform.system() == "Darwin":  # macOS
            home = os.path.expanduser("~")
            return os.path.join(home, "Library", "Application Support", "SurveyApp", "Data")
        else:  # Linux и другие
            home = os.path.expanduser("~")
            return os.path.join(home, ".local", "share", "SurveyApp", "Data")
    
    def load_surveys(self) -> List[Dict]:
        """Загружаем анкеты из файла"""
        if os.path.exists(self.surveys_file):
            try:
                with open(self.surveys_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Ошибка загрузки анкет: {e}")
        return []
    
    def load_responses(self) -> List[Dict]:
        """Загружаем ответы из файла"""
        if os.path.exists(self.responses_file):
            try:
                with open(self.responses_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Ошибка загрузки ответов: {e}")
        return []
    
    def load_settings(self) -> Dict:
        """Загружаем настройки из файла"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Ошибка загрузки настроек: {e}")
        return {"default_survey_id": None, "admin_password": "admin123"}
    
    def save_settings(self):
        """Сохраняем настройки в файл"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить настройки: {e}")
    
    def log_debug(self, message: str):
        """Пишем отладочную строку в файл и stdout"""
        try:
            ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            line = f"[{ts}] {message}\n"
            print(line.strip())
            log_path = os.path.join(self.data_dir, 'debug.log')
            with open(log_path, 'a', encoding='utf-8') as lf:
                lf.write(line)
        except Exception:
            # Не мешаем работе, если логирование сломалось
            pass
    
    def setup_icon(self):
        """Устанавливаем иконку приложения"""
        try:
            # Пытаемся загрузить логотип ASRR
            icon_paths = [
                os.path.join(os.path.dirname(__file__), "asrr_logo.ico"),
                os.path.join(os.path.dirname(__file__), "asrr_logo.png"),
                os.path.join(os.path.dirname(__file__), "public_icon.ico")
            ]
            
            for icon_path in icon_paths:
                if os.path.exists(icon_path):
                    self.setWindowIcon(QIcon(icon_path))
                    print(f"Иконка загружена: {icon_path}")
                    return
            
            # Если иконка не найдена, создаем простую иконку
            pixmap = QPixmap(32, 32)
            pixmap.fill(QColor("#3498db"))
            self.setWindowIcon(QIcon(pixmap))
            print("Использована стандартная иконка")
        except Exception as e:
            print(f"Ошибка загрузки иконки: {e}")
    
    def save_surveys(self):
        """Сохраняем анкеты в файл"""
        try:
            with open(self.surveys_file, 'w', encoding='utf-8') as f:
                json.dump(self.surveys, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить анкеты: {e}")
    
    def save_responses(self):
        """Сохраняем ответы в файл"""
        try:
            with open(self.responses_file, 'w', encoding='utf-8') as f:
                json.dump(self.responses, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить ответы: {e}")
    
    def setup_ui(self):
        """Настраиваем интерфейс"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Главный layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # Заголовок
        title_label = QLabel("Система анкетирования")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        main_layout.addWidget(title_label)
        
        # Кнопка настроек (шестерёнка) по центру
        settings_layout = QHBoxLayout()
        settings_layout.addStretch()
        
        self.settings_button = QPushButton("⚙")
        self.settings_button.setFont(QFont("Arial", 20))
        self.settings_button.setFixedSize(50, 50)
        self.settings_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 25px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        self.settings_button.clicked.connect(self.show_admin_panel)
        settings_layout.addWidget(self.settings_button)
        settings_layout.addStretch()
        
        main_layout.addLayout(settings_layout)
        
        # Увеличиваем расстояние между шестерёнкой и кнопкой старт
        spacer = QWidget()
        spacer.setFixedHeight(30)
        main_layout.addWidget(spacer)
        
        # Основная кнопка СТАРТ
        self.start_button = QPushButton("СТАРТ")
        self.start_button.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        self.start_button.setMinimumHeight(80)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 20px;
                font-size: 24px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        self.start_button.clicked.connect(self.start_default_survey)
        
        main_layout.addWidget(self.start_button)
        
        # Добавляем растягивающий элемент для центрирования
        main_layout.addStretch()
    
    def start_default_survey(self):
        """Запускаем анкету по умолчанию"""
        default_survey_id = self.settings.get("default_survey_id")
        
        if not default_survey_id:
            QMessageBox.warning(self, "Ошибка", 
                              "Анкета по умолчанию не установлена.\n"
                              "Пожалуйста, настройте анкету в админ-панели.")
            return
        
        # Находим анкету по умолчанию
        default_survey = None
        for survey in self.surveys:
            if survey.get("id") == default_survey_id:
                default_survey = survey
                break
        
        if not default_survey:
            QMessageBox.warning(self, "Ошибка", 
                              "Анкета по умолчанию не найдена.\n"
                              "Пожалуйста, настройте анкету в админ-панели.")
            return
        
        # Запускаем анкету
        self.start_survey_with_id(default_survey_id)
    
    def start_survey_with_id(self, survey_id):
        """Запускаем анкету по ID"""
        survey = None
        for s in self.surveys:
            if s.get("id") == survey_id:
                survey = s
                break
        
        if survey:
            self.take_survey(survey)
        else:
            QMessageBox.warning(self, "Ошибка", "Анкета не найдена")
    
    def save_default_survey(self):
        """Сохраняем анкету по умолчанию"""
        survey_id = self.default_survey_combo.currentData()
        self.settings["default_survey_id"] = survey_id
        self.save_settings()
        QMessageBox.information(self, "Успех", "Анкета по умолчанию сохранена")
    
    def change_password(self):
        """Смена пароля администратора"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Смена пароля")
        dialog.setModal(True)
        dialog.resize(400, 200)
        
        layout = QVBoxLayout(dialog)
        
        # Старый пароль
        old_password_layout = QFormLayout()
        old_password_edit = QLineEdit()
        old_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        old_password_layout.addRow("Текущий пароль:", old_password_edit)
        layout.addLayout(old_password_layout)
        
        # Новый пароль
        new_password_layout = QFormLayout()
        new_password_edit = QLineEdit()
        new_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        new_password_layout.addRow("Новый пароль:", new_password_edit)
        layout.addLayout(new_password_layout)
        
        # Подтверждение пароля
        confirm_password_layout = QFormLayout()
        confirm_password_edit = QLineEdit()
        confirm_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        confirm_password_layout.addRow("Подтвердите пароль:", confirm_password_edit)
        layout.addLayout(confirm_password_layout)
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(lambda: self.save_new_password(
            dialog, old_password_edit.text(), new_password_edit.text(), confirm_password_edit.text()
        ))
        
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(dialog.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    def save_new_password(self, dialog, old_password, new_password, confirm_password):
        """Сохраняем новый пароль"""
        # Проверяем старый пароль
        if old_password != self.settings.get("admin_password", "admin123"):
            QMessageBox.warning(self, "Ошибка", "Неверный текущий пароль")
            return
        
        # Проверяем новый пароль
        if not new_password:
            QMessageBox.warning(self, "Ошибка", "Введите новый пароль")
            return
        
        if new_password != confirm_password:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают")
            return
        
        if len(new_password) < 4:
            QMessageBox.warning(self, "Ошибка", "Пароль должен содержать минимум 4 символа")
            return
        
        # Сохраняем новый пароль
        self.settings["admin_password"] = new_password
        self.save_settings()
        
        QMessageBox.information(self, "Успех", "Пароль успешно изменен")
        dialog.accept()
    
    def setup_styles(self):
        """Настраиваем стили приложения"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ecf0f1;
            }
            QLabel {
                color: #2c3e50;
            }
        """)
    
    
    def start_survey(self):
        """Начинаем прохождение анкеты"""
        active_surveys = [s for s in self.surveys if s.get('isActive', True)]
        
        if not active_surveys:
            QMessageBox.information(self, "Информация", "Нет доступных анкет")
            return
        
        if len(active_surveys) == 1:
            self.take_survey(active_surveys[0])
        else:
            self.show_survey_selection()
    
    def show_survey_selection(self):
        """Показываем выбор анкеты"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Выберите анкету")
        dialog.setModal(True)
        dialog.resize(400, 300)
        
        layout = QVBoxLayout(dialog)
        
        label = QLabel("Выберите анкету для прохождения:")
        label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(label)
        
        list_widget = QListWidget()
        active_surveys = [s for s in self.surveys if s.get('isActive', True)]
        
        for survey in active_surveys:
            item = QListWidgetItem(survey['title'])
            item.setData(Qt.ItemDataRole.UserRole, survey)
            list_widget.addItem(item)
        
        layout.addWidget(list_widget)
        
        button_layout = QHBoxLayout()
        select_button = QPushButton("Выбрать")
        cancel_button = QPushButton("Отмена")
        
        select_button.clicked.connect(lambda: self.select_survey_from_dialog(dialog, list_widget))
        cancel_button.clicked.connect(dialog.reject)
        
        button_layout.addWidget(select_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    def select_survey_from_dialog(self, dialog, list_widget):
        """Выбираем анкету из диалога"""
        current_item = list_widget.currentItem()
        if current_item:
            survey = current_item.data(Qt.ItemDataRole.UserRole)
            dialog.accept()
            self.take_survey(survey)
    
    def take_survey_from_list(self, item):
        """Проходим анкету из списка"""
        survey = item.data(Qt.ItemDataRole.UserRole)
        if survey:
            self.take_survey(survey)
    
    def take_survey(self, survey):
        """Проходим анкету"""
        self.current_survey = survey
        self.current_answers = {}
        self.current_question = 0
        
        # Фильтруем вопросы по условиям
        self.filtered_questions = self.get_visible_questions(survey['questions'], self.current_answers)
        
        # Проверяем, есть ли вопросы
        if not self.filtered_questions:
            print(f"DEBUG: Анкета '{survey['title']}' имеет {len(survey['questions'])} вопросов")
            print(f"DEBUG: Отфильтрованных вопросов: {len(self.filtered_questions)}")
            for i, q in enumerate(survey['questions']):
                conditions = q.get('conditions', [])
                print(f"DEBUG: Вопрос {i}: {q['text']} (тип: {q['type']}, условий: {len(conditions)})")
                if conditions:
                    for j, cond in enumerate(conditions):
                        print(f"  Условие {j}: {cond}")
            QMessageBox.information(self, "Информация", f"В этой анкете нет доступных вопросов. Всего вопросов: {len(survey['questions'])}")
            return
        
        # Создаем окно прохождения анкеты
        self.survey_window = QDialog(self)
        self.survey_window.setWindowTitle(f"Анкета: {survey['title']}")
        self.survey_window.setModal(True)
        self.survey_window.resize(800, 600)
        
        layout = QVBoxLayout(self.survey_window)
        
        # Прогресс
        progress_layout = QHBoxLayout()
        progress_layout.addWidget(QLabel("Прогресс:"))
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(len(self.filtered_questions))
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel(f"Вопрос 1 из {len(self.filtered_questions)}")
        progress_layout.addWidget(self.progress_label)
        progress_layout.addStretch()
        
        layout.addLayout(progress_layout)
        
        # Область для вопросов
        self.question_widget = QWidget()
        self.question_layout = QVBoxLayout(self.question_widget)
        layout.addWidget(self.question_widget)
        
        # Кнопки навигации
        nav_layout = QHBoxLayout()
        
        self.prev_button = QPushButton("Назад")
        self.prev_button.clicked.connect(self.prev_question)
        
        self.next_button = QPushButton("Далее")
        self.next_button.clicked.connect(self.next_question)
        
        nav_layout.addWidget(self.prev_button)
        nav_layout.addStretch()
        nav_layout.addWidget(self.next_button)
        
        layout.addLayout(nav_layout)
        
        self.show_question()
        self.survey_window.exec()
    
    def show_question(self):
        """Показываем текущий вопрос"""
        # Очищаем область вопроса
        for i in reversed(range(self.question_layout.count())):
            self.question_layout.itemAt(i).widget().setParent(None)

        if not self.current_survey or self.current_question >= len(self.current_survey['questions']):
            return

        question = self.current_survey['questions'][self.current_question]
        
        # Заголовок вопроса
        question_label = QLabel(question['text'])
        question_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        question_label.setWordWrap(True)
        self.question_layout.addWidget(question_label)
        
        if question.get('required', False):
            required_label = QLabel("* Обязательный вопрос")
            required_label.setStyleSheet("color: red; font-weight: bold;")
            self.question_layout.addWidget(required_label)
        
        # Поле для ответа
        if question['type'] == 'text':
            self.answer_text = QTextEdit()
            self.answer_text.setMaximumHeight(100)
            self.answer_text.setPlainText(self.current_answers.get(question['id'], ''))
            self.question_layout.addWidget(self.answer_text)
        
        elif question['type'] == 'radio':
            self.answer_radio_group = []
            current_value = self.current_answers.get(question['id'], '')
            
            for option in question.get('options', []):
                radio = QRadioButton(option)
                radio.setChecked(option == current_value)
                self.answer_radio_group.append(radio)
                self.question_layout.addWidget(radio)
        
        elif question['type'] == 'checkbox':
            self.answer_checkboxes = {}
            current_values = self.current_answers.get(question['id'], [])
            
            for option in question.get('options', []):
                checkbox = QCheckBox(option)
                checkbox.setChecked(option in current_values)
                self.answer_checkboxes[option] = checkbox
                self.question_layout.addWidget(checkbox)
        
        elif question['type'] == 'number':
            self.answer_spinbox = QSpinBox()
            self.answer_spinbox.setRange(-999999, 999999)
            # Safely set initial value even if stored answer is '', None, or non-numeric
            stored_value = self.current_answers.get(question['id'], 0)
            try:
                if isinstance(stored_value, str) and stored_value.strip() == "":
                    numeric_value = 0
                else:
                    numeric_value = int(float(stored_value))
            except Exception:
                numeric_value = 0
            self.answer_spinbox.setValue(numeric_value)
            self.question_layout.addWidget(self.answer_spinbox)
        
        # Обновляем прогресс
        self.progress_bar.setValue(self.current_question + 1)
        self.progress_label.setText(f"Вопрос {self.current_question + 1} из {len(self.filtered_questions)}")
        
        # Обновляем кнопки навигации
        self.update_navigation_buttons()

        # Принудительно обновляем интерфейс
        self.survey_window.update()
    
    def save_current_answer(self):
        """Сохраняем текущий ответ"""
        if not self.current_survey or self.current_question >= len(self.current_survey['questions']):
            return
        
        question = self.current_survey['questions'][self.current_question]
        
        if question['type'] == 'text':
            answer = self.answer_text.toPlainText().strip()
        elif question['type'] == 'radio':
            answer = ""
            for radio in self.answer_radio_group:
                if radio.isChecked():
                    answer = radio.text()
                    break
        elif question['type'] == 'checkbox':
            answer = [option for option, checkbox in self.answer_checkboxes.items() if checkbox.isChecked()]
        elif question['type'] == 'number':
            try:
                answer = int(self.answer_spinbox.value())
            except Exception as e:
                self.log_debug(f"save_current_answer number ERROR: {e}")
                answer = 0
        else:
            answer = ''
        
        self.current_answers[question['id']] = answer
        self.log_debug(f"save_current_answer: qid={question['id']} type={question['type']} answer={answer}")
    
    def prev_question(self):
        """Предыдущий вопрос с учетом условной логики"""
        if self.current_question > 0:
            self.save_current_answer()
            
            # Находим предыдущий видимый вопрос
            prev_visible_index = None
            for i in range(self.current_question - 1, -1, -1):
                question = self.current_survey['questions'][i]
                if self.should_show_question(question, self.current_answers):
                    prev_visible_index = i
                    break
            
            if prev_visible_index is not None:
                self.current_question = prev_visible_index
                self.show_question()
    
    def next_question(self):
        """Следующий вопрос"""
        self.save_current_answer()

        # Пересчитываем видимые вопросы после сохранения ответа
        new_filtered = self.get_visible_questions(self.current_survey['questions'], self.current_answers)

        # Находим следующий видимый вопрос
        next_visible_index = None
        for i, question in enumerate(self.current_survey['questions']):
            if i > self.current_question and question in new_filtered:
                next_visible_index = i
                break

        if next_visible_index is None:
            # Завершаем анкету
            self.finish_survey()
        else:
            self.current_question = next_visible_index
            self.filtered_questions = new_filtered
            self.show_question()
            # Обновляем кнопки ПОСЛЕ показа вопроса
            self.update_navigation_buttons()
    
    def finish_survey(self):
        """Завершаем анкету"""
        # Сохраняем ответы
        response = {
            'id': str(uuid.uuid4()),
            'surveyId': self.current_survey['id'],
            'answers': self.current_answers,
            'completedAt': datetime.now().isoformat()
        }
        
        self.responses.append(response)
        self.save_responses()
        
        QMessageBox.information(self, "Успех", "Анкета успешно завершена!")
        self.survey_window.accept()
    
    def show_admin_panel(self):
        """Показываем панель администратора"""
        # Проверяем пароль
        password, ok = QInputDialog.getText(self, "Авторизация", "Введите пароль администратора:", QLineEdit.EchoMode.Password)
        if not ok or password != self.settings.get("admin_password", "admin123"):
            QMessageBox.critical(self, "Ошибка", "Неверный пароль")
            return
        
        # Создаем окно администратора
        admin_window = QDialog(self)
        admin_window.setWindowTitle("Панель администратора")
        admin_window.setModal(True)
        admin_window.resize(1000, 700)
        
        layout = QVBoxLayout(admin_window)
        
        # Заголовок
        title_label = QLabel("Управление анкетами")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Настройки по умолчанию
        settings_group = QGroupBox("Настройки по умолчанию")
        settings_layout = QHBoxLayout(settings_group)
        
        default_label = QLabel("Анкета по умолчанию:")
        settings_layout.addWidget(default_label)
        
        self.default_survey_combo = QComboBox()
        self.default_survey_combo.addItem("Не выбрана", None)
        for survey in self.surveys:
            self.default_survey_combo.addItem(survey.get("title", "Без названия"), survey.get("id"))
        
        # Устанавливаем текущую анкету по умолчанию
        current_default = self.settings.get("default_survey_id")
        if current_default:
            index = self.default_survey_combo.findData(current_default)
            if index >= 0:
                self.default_survey_combo.setCurrentIndex(index)
        
        settings_layout.addWidget(self.default_survey_combo)
        
        save_default_button = QPushButton("Сохранить")
        save_default_button.clicked.connect(self.save_default_survey)
        settings_layout.addWidget(save_default_button)
        
        settings_layout.addStretch()
        layout.addWidget(settings_group)
        
        # Кнопки управления
        button_layout = QHBoxLayout()
        
        create_button = QPushButton("Создать анкету")
        create_button.clicked.connect(self.create_survey)
        
        export_button = QPushButton("Экспорт данных")
        export_button.clicked.connect(self.export_data)
        
        import_button = QPushButton("Импорт данных")
        import_button.clicked.connect(self.import_data)
        
        change_password_button = QPushButton("Сменить пароль")
        change_password_button.clicked.connect(self.change_password)
        
        export_single_button = QPushButton("Экспорт анкеты")
        export_single_button.clicked.connect(self.export_single_survey)
        
        import_single_button = QPushButton("Импорт анкеты")
        import_single_button.clicked.connect(self.import_single_survey)
        
        button_layout.addWidget(create_button)
        button_layout.addWidget(export_button)
        button_layout.addWidget(import_button)
        button_layout.addWidget(export_single_button)
        button_layout.addWidget(import_single_button)
        button_layout.addWidget(change_password_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Таблица анкет
        self.admin_table = QTableWidget()
        self.admin_table.setColumnCount(5)
        self.admin_table.setHorizontalHeaderLabels(["Название", "Вопросов", "Ответов", "Статус", "Создана"])
        
        # Заполняем таблицу
        self.update_admin_table()
        
        layout.addWidget(self.admin_table)
        
        # Сохраняем ссылку на таблицу для обновления
        self.admin_table_ref = self.admin_table
        
        # Кнопки действий
        action_layout = QHBoxLayout()
        
        edit_button = QPushButton("Редактировать")
        edit_button.clicked.connect(lambda: self.edit_survey(admin_window))
        
        responses_button = QPushButton("Просмотр ответов")
        responses_button.clicked.connect(lambda: self.view_responses(admin_window))
        
        delete_button = QPushButton("Удалить")
        delete_button.clicked.connect(lambda: self.delete_survey(admin_window))
        
        docs_button = QPushButton("📖 Документация")
        docs_button.clicked.connect(self.show_documentation)
        docs_button.setStyleSheet("QPushButton { background-color: #9C27B0; color: white; border: none; padding: 8px; border-radius: 4px; font-weight: bold; }")
        
        action_layout.addWidget(edit_button)
        action_layout.addWidget(responses_button)
        action_layout.addWidget(delete_button)
        action_layout.addWidget(docs_button)
        action_layout.addStretch()
        
        layout.addLayout(action_layout)
        
        admin_window.exec()
    
    def update_admin_table(self):
        """Обновляем таблицу администратора"""
        self.admin_table.setRowCount(len(self.surveys))
        
        for row, survey in enumerate(self.surveys):
            responses_count = len([r for r in self.responses if r['surveyId'] == survey['id']])
            status = "Активна" if survey.get('isActive', True) else "Неактивна"
            created = datetime.fromisoformat(survey['createdAt']).strftime("%d.%m.%Y")
            
            self.admin_table.setItem(row, 0, QTableWidgetItem(survey['title']))
            self.admin_table.setItem(row, 1, QTableWidgetItem(str(len(survey['questions']))))
            self.admin_table.setItem(row, 2, QTableWidgetItem(str(responses_count)))
            self.admin_table.setItem(row, 3, QTableWidgetItem(status))
            self.admin_table.setItem(row, 4, QTableWidgetItem(created))
    
    def create_survey(self):
        """Создаем новую анкету"""
        title, ok = QInputDialog.getText(self, "Создание анкеты", "Введите название анкеты:")
        if not ok or not title:
            return
        
        survey = {
            'id': str(uuid.uuid4()),
            'title': title,
            'questions': [],
            'createdAt': datetime.now().isoformat(),
            'isActive': True
        }
        
        self.surveys.append(survey)
        self.save_surveys()
        
        QMessageBox.information(self, "Успех", "Анкета создана! Используйте 'Редактировать' для добавления вопросов.")
        
        # Обновляем таблицу в админке если она открыта
        if hasattr(self, 'admin_table_ref'):
            self.update_admin_table()
        
        # Обновляем комбобокс анкеты по умолчанию
        if hasattr(self, 'default_survey_combo'):
            self.refresh_default_survey_combo()
    
    def edit_survey(self, parent):
        """Редактируем анкету"""
        current_row = self.admin_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(parent, "Предупреждение", "Выберите анкету для редактирования")
            return
        
        survey = self.surveys[current_row]
        self.show_survey_editor(survey, parent)
    
    def view_responses(self, parent):
        """Просматриваем ответы"""
        current_row = self.admin_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(parent, "Предупреждение", "Выберите анкету для просмотра ответов")
            return
        
        QMessageBox.information(parent, "Информация", "Функция просмотра ответов будет добавлена в следующей версии")
    
    def show_documentation(self):
        """Показываем документацию по созданию анкет"""
        doc_window = QDialog(self)
        doc_window.setWindowTitle("📖 Документация - Создание анкет с условной логикой")
        doc_window.setModal(True)
        doc_window.resize(900, 700)
        
        layout = QVBoxLayout(doc_window)
        
        # Создаем текстовое поле с прокруткой
        text_area = QTextEdit()
        text_area.setReadOnly(True)
        text_area.setFont(QFont("Consolas", 10))
        
        # Подробная инструкция
        documentation = """
# 📋 ПОЛНОЕ РУКОВОДСТВО ПО СОЗДАНИЮ АНКЕТ С УСЛОВНОЙ ЛОГИКОЙ

## 🎯 ОСНОВНЫЕ ПРИНЦИПЫ

Система анкетирования поддерживает условную логику показа вопросов. Это означает, что некоторые вопросы будут показываться только при выполнении определенных условий на основе ответов на предыдущие вопросы.

## 📝 ПОШАГОВОЕ СОЗДАНИЕ АНКЕТЫ

### ШАГ 1: Создание анкеты
1. Нажмите кнопку "Админ" в главном окне
2. Введите пароль: admin123
3. Нажмите "Создать анкету"
4. Введите название анкеты
5. Нажмите "Редактировать" для добавления вопросов

### ШАГ 2: Добавление вопросов
1. В редакторе анкеты нажмите "Добавить вопрос"
2. Заполните текст вопроса
3. Выберите тип вопроса:
   - Текстовый - свободный ввод текста
   - Числовой - ввод чисел
   - Выбор (radio) - один вариант из списка
   - Множественный выбор (checkbox) - несколько вариантов

### ШАГ 3: Настройка вариантов ответов
Для вопросов типа "Выбор" и "Множественный выбор":
1. Нажмите "➕ Добавить вариант"
2. Введите текст варианта
3. Повторите для всех нужных вариантов
4. Используйте "📋 Копировать" для быстрого создания похожих вопросов

## 🔗 УСЛОВНАЯ ЛОГИКА - ПОДРОБНОЕ ОПИСАНИЕ

### КАК РАБОТАЮТ УСЛОВИЯ

Условия определяют, когда показывать вопрос. Если у вопроса несколько условий - вопрос покажется при выполнении ЛЮБОГО из них (логика OR). Если ни одно условие не выполнено - вопрос будет скрыт.

### ТИПЫ УСЛОВИЙ

1. **равно** - ответ точно совпадает с указанным значением
2. **не равно** - ответ отличается от указанного значения  
3. **содержит** - ответ содержит указанное значение (для множественного выбора)
4. **больше** - числовое значение больше указанного
5. **больше или равно** - числовое значение больше или равно указанному
6. **меньше** - числовое значение меньше указанного
7. **меньше или равно** - числовое значение меньше или равно указанному

### ПРИМЕРЫ УСЛОВИЙ

#### Пример 1: Простое условие
```
Вопрос 1: "Ваш возраст?" (числовой)
Вопрос 2: "Вы работаете?" (выбор: Да/Нет)
Условие для Вопроса 2: возраст больше 18
```

#### Пример 2: Условие с выбором
```
Вопрос 1: "Какие симптомы у вас есть?" (множественный выбор: Головная боль, Температура, Кашель)
Вопрос 2: "Как долго болеете?" (числовой)
Условие для Вопроса 2: симптомы содержат "Температура"
```

#### Пример 3: Сложная логика (решение через дублирование)
```
Вопрос 1: "Тип исследования?" (выбор: ORADS2, ORADS3)
Вопрос 2: "Результат анализа?" (числовой)
Вопрос 3: "M- (низкий риск)" (выбор: Да/Нет)
Вопрос 4: "M- (средний риск)" (выбор: Да/Нет)

Условие для Вопроса 3: Тип исследования равно "ORADS2"
Условие для Вопроса 4: Тип исследования равно "ORADS3" И Результат анализа больше 30
```

## 🛠️ ПРАКТИЧЕСКИЕ СОВЕТЫ

### СОВЕТ 1: Планирование логики
1. Сначала создайте все основные вопросы
2. Потом добавьте условия для каждого вопроса
3. Используйте кнопку "📋 Копировать" для похожих вопросов

### СОВЕТ 2: Тестирование
1. После создания анкеты обязательно протестируйте её
2. Пройдите анкету с разными вариантами ответов
3. Убедитесь, что вопросы показываются правильно

### СОВЕТ 3: Организация вопросов
1. Размещайте вопросы в логическом порядке
2. Используйте кнопки "Вверх"/"Вниз" для изменения порядка
3. Группируйте связанные вопросы

## ⚠️ ОГРАНИЧЕНИЯ СИСТЕМЫ

### ТЕКУЩИЕ ОГРАНИЧЕНИЯ:
1. Условия работают только с предыдущими вопросами
2. Нельзя создавать сложные цепочки условий (только OR логика между условиями)
3. Каждое условие проверяется независимо

### РЕШЕНИЕ ДЛЯ СЛОЖНЫХ СЛУЧАЕВ:
Если нужна сложная логика - создайте несколько похожих вопросов с разными условиями:

```
Вместо: "Если A И B ИЛИ C, то показать вопрос X"
Создайте: 
- Вопрос X1 (условие: A И B)
- Вопрос X2 (условие: C)
```

## 📋 ЧЕКЛИСТ СОЗДАНИЯ АНКЕТЫ

### ✅ ПОДГОТОВКА:
- [ ] Определить цель анкеты
- [ ] Составить список всех вопросов
- [ ] Определить логику показа вопросов
- [ ] Спланировать порядок вопросов

### ✅ СОЗДАНИЕ:
- [ ] Создать анкету в системе
- [ ] Добавить все основные вопросы
- [ ] Настроить варианты ответов
- [ ] Добавить условия показа

### ✅ ТЕСТИРОВАНИЕ:
- [ ] Пройти анкету с разными ответами
- [ ] Проверить работу всех условий
- [ ] Убедиться в корректности логики
- [ ] Исправить найденные ошибки

### ✅ ФИНАЛИЗАЦИЯ:
- [ ] Активировать анкету
- [ ] Сохранить резервную копию
- [ ] Подготовить инструкции для пользователей

## 🆘 РЕШЕНИЕ ПРОБЛЕМ

### ПРОБЛЕМА: Вопрос не показывается
**РЕШЕНИЕ:** Проверьте условия вопроса - возможно, они слишком строгие

### ПРОБЛЕМА: Вопрос показывается всегда
**РЕШЕНИЕ:** Убедитесь, что условия добавлены правильно

### ПРОБЛЕМА: Сложная логика не работает
**РЕШЕНИЕ:** Используйте дублирование вопросов с разными условиями

### ПРОБЛЕМА: Анкета зависает при редактировании
**РЕШЕНИЕ:** Перезапустите приложение и попробуйте снова

## 📞 ПОДДЕРЖКА

При возникновении проблем:
1. Проверьте этот список решений
2. Убедитесь, что условия настроены правильно
3. Протестируйте анкету с простыми ответами
4. При необходимости создайте упрощенную версию анкеты

---
**Версия документации:** 1.0  
**Дата обновления:** 2025  
**Автор:** ASRR Team
        """
        
        text_area.setPlainText(documentation)
        layout.addWidget(text_area)
        
        # Кнопка закрытия
        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(doc_window.accept)
        close_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; border: none; padding: 10px; border-radius: 5px; font-weight: bold; }")
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        doc_window.exec()
    
    def show_survey_editor(self, survey, parent):
        """Показываем редактор анкеты"""
        editor_window = QDialog(parent)
        editor_window.setWindowTitle(f"Редактор анкеты: {survey['title']}")
        editor_window.setModal(True)
        editor_window.resize(1000, 700)
        
        layout = QVBoxLayout(editor_window)
        
        # Заголовок
        title_layout = QHBoxLayout()
        title_label = QLabel(f"Редактор анкеты: {survey['title']}")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        # Кнопки управления
        add_question_btn = QPushButton("Добавить вопрос")
        add_question_btn.clicked.connect(lambda: self.add_question_to_survey(survey, editor_window))
        
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(lambda: self.save_survey_editor(survey, editor_window))
        
        title_layout.addWidget(add_question_btn)
        title_layout.addWidget(save_btn)
        layout.addLayout(title_layout)
        
        # Список вопросов
        questions_frame = QGroupBox("Вопросы анкеты")
        questions_layout = QVBoxLayout(questions_frame)
        
        self.questions_list = QListWidget()
        self.questions_list.setMinimumHeight(400)
        questions_layout.addWidget(self.questions_list)
        
        # Кнопки для вопросов
        question_buttons = QHBoxLayout()
        
        edit_question_btn = QPushButton("Редактировать")
        edit_question_btn.clicked.connect(lambda: self.edit_question(survey, editor_window))
        
        copy_question_btn = QPushButton("📋 Копировать")
        copy_question_btn.clicked.connect(lambda: self.copy_question(survey, editor_window))
        copy_question_btn.setStyleSheet("QPushButton { background-color: #FF9800; color: white; border: none; padding: 5px; border-radius: 3px; }")
        
        delete_question_btn = QPushButton("Удалить")
        delete_question_btn.clicked.connect(lambda: self.delete_question(survey, editor_window))
        
        move_up_btn = QPushButton("Вверх")
        move_up_btn.clicked.connect(lambda: self.move_question_up(survey, editor_window))
        
        move_down_btn = QPushButton("Вниз")
        move_down_btn.clicked.connect(lambda: self.move_question_down(survey, editor_window))
        
        question_buttons.addWidget(edit_question_btn)
        question_buttons.addWidget(copy_question_btn)
        question_buttons.addWidget(delete_question_btn)
        question_buttons.addWidget(move_up_btn)
        question_buttons.addWidget(move_down_btn)
        question_buttons.addStretch()
        
        questions_layout.addLayout(question_buttons)
        layout.addWidget(questions_frame)
        
        # Загружаем вопросы
        self.load_questions_to_editor(survey)
        
        editor_window.exec()
    
    def load_questions_to_editor(self, survey):
        """Загружаем вопросы в редактор"""
        self.questions_list.clear()
        
        for i, question in enumerate(survey['questions']):
            question_text = f"{i+1}. {question['text']} ({question['type']})"
            if question.get('required', False):
                question_text += " *"
            
            item = QListWidgetItem(question_text)
            item.setData(Qt.ItemDataRole.UserRole, i)
            self.questions_list.addItem(item)
    
    def add_question_to_survey(self, survey, parent):
        """Добавляем новый вопрос"""
        self.show_question_editor(survey, None, parent)
    
    def edit_question(self, survey, parent):
        """Редактируем выбранный вопрос"""
        current_item = self.questions_list.currentItem()
        if not current_item:
            QMessageBox.warning(parent, "Предупреждение", "Выберите вопрос для редактирования")
            return
        
        question_index = current_item.data(Qt.ItemDataRole.UserRole)
        question = survey['questions'][question_index]
        self.show_question_editor(survey, question_index, parent)
    
    def show_question_editor(self, survey, question_index, parent):
        """Показываем редактор вопроса"""
        editor_dialog = QDialog(parent)
        editor_dialog.setWindowTitle("Редактор вопроса")
        editor_dialog.setModal(True)
        editor_dialog.resize(600, 500)
        
        layout = QVBoxLayout(editor_dialog)
        
        # Текст вопроса
        text_layout = QFormLayout()
        self.question_text_edit = QTextEdit()
        self.question_text_edit.setMaximumHeight(100)
        text_layout.addRow("Текст вопроса:", self.question_text_edit)
        layout.addLayout(text_layout)
        
        # Тип вопроса
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Тип вопроса:"))
        
        self.question_type_combo = QComboBox()
        self.question_type_combo.addItems(["text", "radio", "checkbox", "number"])
        self.question_type_combo.currentTextChanged.connect(self.on_question_type_changed)
        type_layout.addWidget(self.question_type_combo)
        type_layout.addStretch()
        
        layout.addLayout(type_layout)
        
        # Обязательность
        self.required_checkbox = QCheckBox("Обязательный вопрос")
        layout.addWidget(self.required_checkbox)
        
        # Варианты ответов (для radio/checkbox)
        self.options_frame = QGroupBox("Варианты ответов")
        self.options_layout = QVBoxLayout(self.options_frame)
        
        # Инструкция
        options_label = QLabel("Добавьте варианты ответов для выбора:")
        options_label.setStyleSheet("color: #666; font-size: 12px;")
        self.options_layout.addWidget(options_label)
        
        self.options_list = QListWidget()
        self.options_list.setMaximumHeight(150)
        self.options_list.setMinimumHeight(80)
        self.options_layout.addWidget(self.options_list)
        
        options_buttons = QHBoxLayout()
        add_option_btn = QPushButton("➕ Добавить вариант")
        add_option_btn.clicked.connect(self.add_option)
        add_option_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; border: none; padding: 5px; border-radius: 3px; }")
        
        edit_option_btn = QPushButton("✏️ Редактировать")
        edit_option_btn.clicked.connect(self.edit_option)
        edit_option_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; border: none; padding: 5px; border-radius: 3px; }")
        
        delete_option_btn = QPushButton("🗑️ Удалить")
        delete_option_btn.clicked.connect(self.delete_option)
        delete_option_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; border: none; padding: 5px; border-radius: 3px; }")
        
        options_buttons.addWidget(add_option_btn)
        options_buttons.addWidget(edit_option_btn)
        options_buttons.addWidget(delete_option_btn)
        options_buttons.addStretch()
        
        self.options_layout.addLayout(options_buttons)
        layout.addWidget(self.options_frame)
        
        # Условия показа
        self.conditions_frame = QGroupBox("Условия показа")
        conditions_layout = QVBoxLayout(self.conditions_frame)
        
        self.conditions_list = QListWidget()
        self.conditions_list.setMaximumHeight(150)
        conditions_layout.addWidget(self.conditions_list)
        
        conditions_buttons = QHBoxLayout()
        add_condition_btn = QPushButton("Добавить условие")
        add_condition_btn.clicked.connect(lambda: self.add_condition(survey))
        
        edit_condition_btn = QPushButton("Редактировать")
        edit_condition_btn.clicked.connect(lambda: self.edit_condition(survey))
        
        delete_condition_btn = QPushButton("Удалить")
        delete_condition_btn.clicked.connect(self.delete_condition)
        
        clear_conditions_btn = QPushButton("Очистить все")
        clear_conditions_btn.clicked.connect(self.clear_all_conditions)
        
        conditions_buttons.addWidget(add_condition_btn)
        conditions_buttons.addWidget(edit_condition_btn)
        conditions_buttons.addWidget(delete_condition_btn)
        conditions_buttons.addWidget(clear_conditions_btn)
        conditions_buttons.addStretch()
        
        conditions_layout.addLayout(conditions_buttons)
        layout.addWidget(self.conditions_frame)
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(lambda: self.save_question(survey, question_index, editor_dialog))
        
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(editor_dialog.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Инициализируем пустые условия для нового вопроса
        if question_index is None:
            self.current_conditions = []
        
        # Загружаем данные если редактируем
        if question_index is not None:
            self.load_question_data(survey['questions'][question_index], survey)
        
        # Инициализируем тип вопроса
        self.on_question_type_changed()
        
        editor_dialog.exec()
    
    def on_question_type_changed(self):
        """Обработка изменения типа вопроса"""
        question_type = self.question_type_combo.currentText()
        self.options_frame.setVisible(question_type in ['radio', 'checkbox'])
    
    def add_option(self):
        """Добавляем вариант ответа"""
        # Используем None как родительское окно чтобы избежать проблем с модальностью
        option, ok = QInputDialog.getText(None, "Вариант ответа", "Введите вариант ответа:")
        if ok and option.strip():
            self.options_list.addItem(option.strip())
    
    def edit_option(self):
        """Редактируем вариант ответа"""
        current_item = self.options_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Предупреждение", "Выберите вариант для редактирования")
            return
        
        current_text = current_item.text()
        # Используем None как родительское окно чтобы избежать проблем с модальностью
        new_text, ok = QInputDialog.getText(None, "Редактирование варианта", "Введите новый текст:", text=current_text)
        if ok and new_text.strip():
            current_item.setText(new_text.strip())
    
    def delete_option(self):
        """Удаляем вариант ответа"""
        current_row = self.options_list.currentRow()
        if current_row >= 0:
            self.options_list.takeItem(current_row)
    
    def add_condition(self, survey):
        """Добавляем условие показа"""
        if len(survey['questions']) < 2:
            QMessageBox.information(self, "Информация", "Нужно минимум 2 вопроса для создания условий")
            return
        
        # Сохраняем ссылку на survey для использования в других методах
        self.current_survey_for_condition = survey
        
        condition_dialog = QDialog(self)
        condition_dialog.setWindowTitle("Добавить условие")
        condition_dialog.setModal(True)
        condition_dialog.resize(400, 300)
        
        layout = QVBoxLayout(condition_dialog)
        
        # Выбор целевого вопроса
        target_layout = QFormLayout()
        self.target_question_combo = QComboBox()
        for i, q in enumerate(survey['questions']):
            if i != len(survey['questions']) - 1:  # Не последний вопрос
                self.target_question_combo.addItem(f"{i+1}. {q['text']}", i)
        target_layout.addRow("Целевой вопрос:", self.target_question_combo)
        layout.addLayout(target_layout)
        
        # Оператор
        operator_layout = QFormLayout()
        self.operator_combo = QComboBox()
        self.operator_combo.addItems(["равно", "не равно", "содержит", "больше", "больше или равно", "меньше", "меньше или равно"])
        operator_layout.addRow("Оператор:", self.operator_combo)
        layout.addLayout(operator_layout)
        
        # Значение
        value_layout = QFormLayout()
        self.condition_value_edit = QLineEdit()
        value_layout.addRow("Значение:", self.condition_value_edit)
        layout.addLayout(value_layout)
        
        # Контейнер для чекбоксов (показывается динамически)
        self.checkbox_container = QWidget()
        self.checkbox_layout = QVBoxLayout(self.checkbox_container)
        self.checkbox_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.checkbox_container)
        
        # Обработчик изменения целевого вопроса
        self.target_question_combo.currentIndexChanged.connect(
            lambda: self.update_condition_value_options(survey)
        )
        
        # Инициализируем опции для первого вопроса
        self.update_condition_value_options(survey)
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(lambda: self.save_condition(condition_dialog))
        
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(condition_dialog.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        condition_dialog.exec()
    
    def update_condition_value_options(self, survey=None):
        """Обновляем опции для выбора значения условия"""
        # Очищаем контейнер
        for i in reversed(range(self.checkbox_layout.count())):
            self.checkbox_layout.itemAt(i).widget().setParent(None)
        
        target_index = self.target_question_combo.currentData()
        self.log_debug(f"update_condition_value_options: target_index={target_index}")
        if target_index is None:
            return
        
        # Используем переданный survey или сохраненный
        survey = survey or getattr(self, 'current_survey_for_condition', None)
        if not survey:
            return
            
        target_question = survey['questions'][target_index]
        self.log_debug(f"  target_question id={target_question.get('id')} type={target_question.get('type')} text={target_question.get('text')}")
        
        # Если вопрос имеет тип checkbox или radio, показываем опции для быстрого выбора
        if target_question.get('type') in ['checkbox', 'radio'] and target_question.get('options'):
            label = QLabel("Быстрый выбор (или введите вручную):")
            label.setStyleSheet("font-weight: bold; color: #666;")
            self.checkbox_layout.addWidget(label)
            
            for option in target_question['options']:
                if target_question.get('type') == 'checkbox':
                    checkbox = QCheckBox(option)
                    checkbox.toggled.connect(
                        lambda checked, opt=option: self.condition_value_edit.setText(opt) if checked else None
                    )
                    self.checkbox_layout.addWidget(checkbox)
                else:  # radio
                    radio = QRadioButton(option)
                    radio.toggled.connect(
                        lambda checked, opt=option: self.condition_value_edit.setText(opt) if checked else None
                    )
                    self.checkbox_layout.addWidget(radio)
    
    def save_condition(self, dialog):
        """Сохраняем условие"""
        target_index = self.target_question_combo.currentData()
        operator = self.operator_combo.currentText()
        value = self.condition_value_edit.text()
        self.log_debug(f"save_condition: target_index={target_index} operator={operator} value={value}")
        
        if not value:
            QMessageBox.warning(self, "Ошибка", "Введите значение для условия")
            return
        
        # Преобразуем оператор
        operator_map = {
            "равно": "equals",
            "не равно": "not_equals", 
            "содержит": "contains",
            "больше": "greater_than",
            "больше или равно": "greater_or_equal",
            "меньше": "less_than",
            "меньше или равно": "less_or_equal"
        }
        
        # Получаем реальный ID целевого вопроса
        survey = getattr(self, 'current_survey_for_condition', None)
        if survey and target_index is not None and 0 <= target_index < len(survey['questions']):
            target_question_id = survey['questions'][target_index]['id']
            self.log_debug(f"  resolved target_question_id={target_question_id}")
        else:
            self.log_debug(f"  ERROR: invalid target_index={target_index}, survey={survey is not None}, questions_count={len(survey['questions']) if survey else 0}")
            QMessageBox.warning(self, "Ошибка", "Неверный индекс целевого вопроса")
            return
        
        condition = {
            'id': str(uuid.uuid4()),
            'targetId': target_question_id,
            'operator': operator_map.get(operator, operator),
            'value': value
        }
        
        # Добавляем условие в список
        condition_text = f"Если {self.target_question_combo.currentText()} {operator} '{value}'"
        self.conditions_list.addItem(condition_text)
        
        # Сохраняем условие в данных
        if not hasattr(self, 'current_conditions'):
            self.current_conditions = []
        self.current_conditions.append(condition)
        self.log_debug(f"  saved condition: {condition}")
        
        dialog.accept()
    
    def edit_condition(self, survey):
        """Редактируем условие"""
        current_row = self.conditions_list.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите условие для редактирования")
            return
        
        if current_row >= len(self.current_conditions):
            QMessageBox.warning(self, "Ошибка", "Условие не найдено")
            return
        
        # Получаем условие для редактирования
        condition = self.current_conditions[current_row]
        
        # Создаем диалог редактирования
        condition_dialog = QDialog(self)
        condition_dialog.setWindowTitle("Редактировать условие")
        condition_dialog.setModal(True)
        condition_dialog.resize(400, 300)
        
        layout = QVBoxLayout(condition_dialog)
        
        # Выбор целевого вопроса
        target_layout = QFormLayout()
        self.target_question_combo = QComboBox()
        for i, q in enumerate(survey['questions']):
            if i != len(survey['questions']) - 1:  # Не последний вопрос
                self.target_question_combo.addItem(f"{i+1}. {q['text']}", i)
        target_layout.addRow("Целевой вопрос:", self.target_question_combo)
        layout.addLayout(target_layout)
        
        # Оператор
        operator_layout = QFormLayout()
        self.operator_combo = QComboBox()
        self.operator_combo.addItems(["равно", "не равно", "содержит", "больше", "больше или равно", "меньше", "меньше или равно"])
        operator_layout.addRow("Оператор:", self.operator_combo)
        layout.addLayout(operator_layout)
        
        # Значение
        value_layout = QFormLayout()
        self.condition_value_edit = QLineEdit()
        value_layout.addRow("Значение:", self.condition_value_edit)
        layout.addLayout(value_layout)
        
        # Заполняем поля данными существующего условия
        # Находим индекс целевого вопроса
        target_index = None
        for i, q in enumerate(survey['questions']):
            if q['id'] == condition['targetId']:
                target_index = i
                break
        
        if target_index is not None:
            self.target_question_combo.setCurrentIndex(target_index)
        
        # Устанавливаем оператор
        operator_map = {
            "equals": "равно",
            "not_equals": "не равно", 
            "contains": "содержит",
            "greater_than": "больше",
            "greater_or_equal": "больше или равно",
            "less_than": "меньше",
            "less_or_equal": "меньше или равно"
        }
        reverse_operator_map = {v: k for k, v in operator_map.items()}
        operator_text = reverse_operator_map.get(condition['operator'], "содержит")
        self.operator_combo.setCurrentText(operator_text)
        
        # Устанавливаем значение
        self.condition_value_edit.setText(condition['value'])
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(lambda: self.save_edited_condition(condition_dialog, current_row))
        
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(condition_dialog.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        condition_dialog.exec()
    
    def save_edited_condition(self, dialog, condition_index):
        """Сохраняем отредактированное условие"""
        target_index = self.target_question_combo.currentData()
        operator = self.operator_combo.currentText()
        value = self.condition_value_edit.text()
        
        if not value:
            QMessageBox.warning(self, "Ошибка", "Введите значение для условия")
            return
        
        # Преобразуем оператор
        operator_map = {
            "равно": "equals",
            "не равно": "not_equals", 
            "содержит": "contains",
            "больше": "greater_than",
            "больше или равно": "greater_or_equal",
            "меньше": "less_than",
            "меньше или равно": "less_or_equal"
        }
        
        # Обновляем условие
        self.current_conditions[condition_index] = {
            'id': self.current_conditions[condition_index]['id'],  # Сохраняем ID
            'targetId': f"q{target_index}",
            'operator': operator_map[operator],
            'value': value
        }
        
        # Обновляем отображение в списке
        condition_text = f"Если {self.target_question_combo.currentText()} {operator} '{value}'"
        self.conditions_list.item(condition_index).setText(condition_text)
        
        dialog.accept()
    
    def delete_condition(self):
        """Удаляем условие"""
        current_row = self.conditions_list.currentRow()
        if current_row >= 0:
            self.conditions_list.takeItem(current_row)
            if hasattr(self, 'current_conditions') and current_row < len(self.current_conditions):
                del self.current_conditions[current_row]
    
    def clear_all_conditions(self):
        """Очищаем все условия"""
        self.conditions_list.clear()
        self.current_conditions = []
    
    def load_question_data(self, question, survey=None):
        """Загружаем данные вопроса в редактор"""
        self.question_text_edit.setPlainText(question['text'])
        self.question_type_combo.setCurrentText(question['type'])
        self.required_checkbox.setChecked(question.get('required', False))
        
        # Загружаем варианты ответов
        self.options_list.clear()
        for option in question.get('options', []):
            self.options_list.addItem(option)
        
        # Загружаем условия
        self.conditions_list.clear()
        self.current_conditions = question.get('conditions', [])
        self.log_debug(f"load_question_data: question_id={question.get('id')} cond_count={len(self.current_conditions)}")
        migrated = False
        for idx, condition in enumerate(self.current_conditions):
            try:
                self.log_debug(f"  cond[{idx}] before: targetId={condition.get('targetId')} operator={condition.get('operator')} value={condition.get('value')}")
                # Миграция legacy targetId вида qN -> UUID текущего вопроса
                tgt = condition.get('targetId')
                if isinstance(tgt, str) and len(tgt) >= 2 and tgt[0] == 'q' and tgt[1:].isdigit():
                    mig_idx = int(tgt[1:])
                    questions_list_for_migration = survey['questions'] if survey else (self.current_survey['questions'] if hasattr(self, 'current_survey') and self.current_survey else [])
                    if 0 <= mig_idx < len(questions_list_for_migration):
                        condition['targetId'] = questions_list_for_migration[mig_idx]['id']
                        migrated = True
                        self.log_debug(f"    migrated targetId q{mig_idx} -> {condition['targetId']}")
                
                # Находим целевой вопрос по ID
                target_question = None
                questions_list = survey['questions'] if survey else (self.current_survey['questions'] if hasattr(self, 'current_survey') and self.current_survey else [])
                for q in questions_list:
                    if q['id'] == condition['targetId']:
                        target_question = q
                        break
                if not target_question:
                    self.log_debug(f"    WARN: target question not found for targetId={condition.get('targetId')}")
                
                # Преобразуем оператор в русский текст
                operator_map = {
                    "equals": "равно",
                    "not_equals": "не равно", 
                    "contains": "содержит",
                    "greater_than": "больше",
                    "greater_or_equal": "больше или равно",
                    "less_than": "меньше",
                    "less_or_equal": "меньше или равно",
                }
                operator_text = operator_map.get(condition.get('operator'), condition.get('operator'))
                question_text = target_question['text'] if target_question else condition.get('targetId')
                condition_text = f"Если {question_text} {operator_text} '{condition.get('value')}'"
                self.conditions_list.addItem(condition_text)
                self.log_debug(f"  cond[{idx}] display: {condition_text}")
            except Exception as e:
                self.log_debug(f"  ERROR rendering cond[{idx}]: {e}")
        
        # Сохраняем миграцию, если были изменения
        if migrated:
            try:
                question['conditions'] = self.current_conditions
                self.save_surveys()
                self.log_debug("  migration saved to surveys.json")
            except Exception as e:
                self.log_debug(f"  ERROR saving migration: {e}")
    
    def save_question(self, survey, question_index, dialog):
        """Сохраняем вопрос"""
        text = self.question_text_edit.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Ошибка", "Введите текст вопроса")
            return
        
        question_type = self.question_type_combo.currentText()
        required = self.required_checkbox.isChecked()
        
        # Собираем варианты ответов
        options = []
        for i in range(self.options_list.count()):
            options.append(self.options_list.item(i).text())
        
        # Создаем или обновляем вопрос
        if question_index is None:
            # Новый вопрос - создаем новый ID
            question = {
                'id': str(uuid.uuid4()),
                'text': text,
                'type': question_type,
                'required': required,
                'options': options if question_type in ['radio', 'checkbox'] else [],
                'conditions': getattr(self, 'current_conditions', [])
            }
            
            # Для первого вопроса убираем все условия (чтобы избежать циклических зависимостей)
            if len(survey['questions']) == 0:
                question['conditions'] = []
                print("DEBUG: Первый вопрос создан БЕЗ условий")
            
            survey['questions'].append(question)
        else:
            # Редактируем существующий вопрос - сохраняем старый ID
            question = survey['questions'][question_index]
            question.update({
                'text': text,
                'type': question_type,
                'required': required,
                'options': options if question_type in ['radio', 'checkbox'] else [],
                'conditions': getattr(self, 'current_conditions', [])
            })
        
        # Сохраняем анкету
        self.save_surveys()
        
        # Обновляем список вопросов
        self.load_questions_to_editor(survey)
        
        dialog.accept()
    
    def delete_question(self, survey, parent):
        """Удаляем вопрос"""
        current_item = self.questions_list.currentItem()
        if not current_item:
            QMessageBox.warning(parent, "Предупреждение", "Выберите вопрос для удаления")
            return
        
        reply = QMessageBox.question(parent, "Подтверждение", "Вы уверены, что хотите удалить этот вопрос?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            question_index = current_item.data(Qt.ItemDataRole.UserRole)
            del survey['questions'][question_index]
            self.save_surveys()
            self.load_questions_to_editor(survey)
    
    def copy_question(self, survey, parent):
        """Копируем вопрос"""
        current_item = self.questions_list.currentItem()
        if not current_item:
            QMessageBox.warning(parent, "Предупреждение", "Выберите вопрос для копирования")
            return
        
        question_index = current_item.data(Qt.ItemDataRole.UserRole)
        original_question = survey['questions'][question_index]
        
        # Создаем копию вопроса с новым ID
        copied_question = {
            'id': str(uuid.uuid4()),
            'text': original_question['text'] + " (копия)",
            'type': original_question['type'],
            'options': original_question.get('options', [])[:],  # Копируем список
            'required': original_question.get('required', False),
            'conditions': original_question.get('conditions', [])[:] if original_question.get('conditions') else []  # Копируем условия
        }
        
        # Вставляем копию после текущего вопроса
        survey['questions'].insert(question_index + 1, copied_question)
        
        # Сохраняем анкету
        self.save_surveys()
        
        # Обновляем список вопросов
        self.load_questions_to_editor(survey)
        
        # Выделяем скопированный вопрос
        self.questions_list.setCurrentRow(question_index + 1)
        
        QMessageBox.information(parent, "Успех", "Вопрос скопирован! Теперь вы можете отредактировать его.")
    
    def move_question_up(self, survey, parent):
        """Перемещаем вопрос вверх"""
        current_row = self.questions_list.currentRow()
        if current_row > 0:
            survey['questions'][current_row], survey['questions'][current_row-1] = \
                survey['questions'][current_row-1], survey['questions'][current_row]
            self.save_surveys()
            self.load_questions_to_editor(survey)
            self.questions_list.setCurrentRow(current_row - 1)
    
    def move_question_down(self, survey, parent):
        """Перемещаем вопрос вниз"""
        current_row = self.questions_list.currentRow()
        if current_row < len(survey['questions']) - 1:
            survey['questions'][current_row], survey['questions'][current_row+1] = \
                survey['questions'][current_row+1], survey['questions'][current_row]
            self.save_surveys()
            self.load_questions_to_editor(survey)
            self.questions_list.setCurrentRow(current_row + 1)
    
    def save_survey_editor(self, survey, parent):
        """Сохраняем изменения в анкете"""
        self.save_surveys()
        if hasattr(self, 'admin_table_ref'):
            self.update_admin_table()
        QMessageBox.information(parent, "Успех", "Анкета сохранена!")
        parent.accept()
    
    def delete_survey(self, parent):
        """Удаляем анкету"""
        current_row = self.admin_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(parent, "Предупреждение", "Выберите анкету для удаления")
            return
        
        reply = QMessageBox.question(parent, "Подтверждение", "Вы уверены, что хотите удалить эту анкету?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(parent, "Информация", "Функция удаления будет добавлена в следующей версии")
    
    def get_visible_questions(self, questions, answers):
        """Получаем видимые вопросы на основе условий"""
        visible = []
        for i, question in enumerate(questions):
            # Первый вопрос всегда показывается (принудительно убираем условия)
            if i == 0:
                question_copy = question.copy()
                question_copy['conditions'] = []
                visible.append(question_copy)
            elif self.should_show_question(question, answers):
                visible.append(question)
        return visible
    
    def get_potential_visible_questions(self, current_index, answers):
        """
        Рассчитывает видимые вопросы, игнорируя условие для текущего вопроса 
        (предполагаем, что ответ позволит открыть ветки).
        """
        potential_visible = []

        for i, question in enumerate(self.current_survey['questions']):
            if i == current_index:
                potential_visible.append(i)  # Всегда включаем текущий
                continue

            # Для других вопросов: проверяем should_show_question
            temp_answers = answers.copy()
            if self.should_show_question(question, temp_answers):
                potential_visible.append(i)
            else:
                # Если вопрос не показывается с текущими ответами, 
                # но может показаться после ответа на текущий вопрос
                # Для простоты: если вопрос имеет условия, зависящие от текущего вопроса
                current_question_id = self.current_survey['questions'][current_index]['id']
                question_conditions = question.get('conditions', [])

                # Проверяем, есть ли условия, зависящие от текущего вопроса
                depends_on_current = False
                for condition in question_conditions:
                    if condition.get('targetId') == current_question_id:
                        depends_on_current = True
                        break

                if depends_on_current:
                    potential_visible.append(i)

        return potential_visible

    def should_show_question(self, question, answers):
        """Проверяем, должен ли показываться вопрос"""
        conditions = question.get('conditions', [])

        if not conditions or len(conditions) == 0:
            return True

        # Если это первый вопрос (индекс 0), всегда показываем его
        question_index = None
        for i, q in enumerate(self.current_survey['questions']):
            if q['id'] == question['id']:
                question_index = i
                break

        if question_index == 0:
            return True

        # Любое условие должно выполняться (OR логика)
        for cidx, condition in enumerate(conditions):
            try:
                result = self.check_condition(condition, answers)
                self.log_debug(f"should_show_question: qid={question.get('id')} cond[{cidx}] => {result}")
                if result:
                    return True
            except Exception as e:
                self.log_debug(f"should_show_question ERROR cond[{cidx}]: {e}")
        
        return False
    
    def check_condition(self, condition, answers):
        """Проверяем условие"""
        target_id = condition['targetId']
        operator = condition['operator']
        value = condition['value']
        
        # Получаем ответ на целевой вопрос
        answer = answers.get(target_id)
        self.log_debug(f"check_condition: targetId={target_id} operator={operator} value={value} answer={answer}")
        if answer is None:
            return False
        
        # Проверяем условие
        if operator == 'equals':
            return answer == value
        elif operator == 'not_equals':
            return answer != value
        elif operator == 'contains':
            if isinstance(answer, list):
                return value in answer
            else:
                return str(value) in str(answer)
        elif operator in ('greater_than', 'greater_or_equal', 'less_than', 'less_or_equal'):
            try:
                a = float(answer)
                b = float(value)
                if operator == 'greater_than':
                    return a > b
                if operator == 'greater_or_equal':
                    return a >= b
                if operator == 'less_than':
                    return a < b
                if operator == 'less_or_equal':
                    return a <= b
            except (ValueError, TypeError) as e:
                self.log_debug(f"  NUMERIC CONVERT ERROR: answer={answer} value={value} err={e}")
                return False
        
        return False
    
    def update_navigation_buttons(self):
        """Обновляем кнопки навигации"""
        # Проверяем, есть ли ответ на текущий вопрос
        current_question_id = self.current_survey['questions'][self.current_question]['id']
        has_answer = current_question_id in self.current_answers

        if not has_answer:
            # Без ответа: используем потенциальные видимые вопросы
            potential_visible = self.get_potential_visible_questions(self.current_question, self.current_answers)
            current_pos = potential_visible.index(self.current_question) if self.current_question in potential_visible else -1
            has_next = current_pos < len(potential_visible) - 1
        else:
            # С ответом: пересчитываем актуальные видимые вопросы
            visible_questions = []
            for i, question in enumerate(self.current_survey['questions']):
                if self.should_show_question(question, self.current_answers):
                    visible_questions.append(i)

            # Находим индекс текущего вопроса в списке видимых
            current_visible_index = -1
            for i, question_index in enumerate(visible_questions):
                if question_index == self.current_question:
                    current_visible_index = i
                    break

            has_next = current_visible_index < len(visible_questions) - 1

        # Обновляем кнопки с учетом условной логики
        has_prev = False
        for i in range(self.current_question - 1, -1, -1):
            question = self.current_survey['questions'][i]
            if self.should_show_question(question, self.current_answers):
                has_prev = True
                break
        
        self.prev_button.setEnabled(has_prev)

        if has_next:
            self.next_button.setText("Далее")
        else:
            self.next_button.setText("Завершить")

        # Принудительно обновляем кнопку
        self.next_button.repaint()
        self.next_button.update()
    
    def export_data(self):
        """Экспортируем данные"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Экспорт данных", "", "JSON files (*.json);;All files (*.*)"
        )
        
        if filename:
            export_data = {
                'surveys': self.surveys,
                'responses': self.responses,
                'exportDate': datetime.now().isoformat(),
                'version': '1.0.0'
            }
            
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
                QMessageBox.information(self, "Успех", "Данные успешно экспортированы")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать данные: {e}")
    
    def import_data(self):
        """Импортируем данные"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Импорт данных", "", "JSON files (*.json);;All files (*.*)"
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if 'surveys' in data and 'responses' in data:
                    self.surveys = data['surveys']
                    self.responses = data['responses']
                    self.save_surveys()
                    self.save_responses()
                    QMessageBox.information(self, "Успех", "Данные успешно импортированы")
                else:
                    QMessageBox.critical(self, "Ошибка", "Неверный формат файла")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось импортировать данные: {e}")
    
    def export_single_survey(self):
        """Экспорт отдельной анкеты"""
        # Получаем выбранную анкету из таблицы
        current_row = self.admin_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите анкету для экспорта")
            return
        
        if current_row >= len(self.surveys):
            QMessageBox.warning(self, "Ошибка", "Анкета не найдена")
            return
        
        survey = self.surveys[current_row]
        
        # Выбираем файл для сохранения
        filename, _ = QFileDialog.getSaveFileName(
            self, "Экспорт анкеты", f"{survey.get('title', 'Анкета')}.json", 
            "JSON files (*.json);;All files (*.*)"
        )
        
        if filename:
            try:
                export_data = {
                    'survey': survey,
                    'exportDate': datetime.now().isoformat(),
                    'version': '1.0.0'
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
                
                QMessageBox.information(self, "Успех", f"Анкета '{survey.get('title', 'Без названия')}' успешно экспортирована")
                
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать анкету: {e}")
    
    def import_single_survey(self):
        """Импорт отдельной анкеты"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Импорт анкеты", "", "JSON files (*.json);;All files (*.*)"
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if 'survey' in data:
                    survey = data['survey']
                    
                    # Проверяем на дубликаты ID
                    existing_ids = [s.get('id') for s in self.surveys]
                    if survey.get('id') in existing_ids:
                        # Генерируем новый ID
                        survey['id'] = str(uuid.uuid4())
                        survey['title'] = f"{survey.get('title', 'Анкета')} (импорт)"
                    
                    # Добавляем анкету
                    self.surveys.append(survey)
                    self.save_surveys()
                    
                    # Обновляем интерфейс
                    if hasattr(self, 'admin_table'):
                        self.update_admin_table()
                    if hasattr(self, 'default_survey_combo'):
                        self.refresh_default_survey_combo()
                    
                    QMessageBox.information(self, "Успех", f"Анкета '{survey.get('title', 'Без названия')}' успешно импортирована")
                else:
                    QMessageBox.critical(self, "Ошибка", "Неверный формат файла анкеты")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось импортировать анкету: {e}")
    
    def refresh_default_survey_combo(self):
        """Обновляем список анкет в комбобоксе по умолчанию"""
        if hasattr(self, 'default_survey_combo'):
            # Сохраняем текущий выбор
            current_id = self.default_survey_combo.currentData()
            
            # Очищаем и заполняем заново
            self.default_survey_combo.clear()
            self.default_survey_combo.addItem("Не выбрана", None)
            
            for survey in self.surveys:
                self.default_survey_combo.addItem(survey.get("title", "Без названия"), survey.get("id"))
            
            # Восстанавливаем выбор
            if current_id:
                index = self.default_survey_combo.findData(current_id)
                if index >= 0:
                    self.default_survey_combo.setCurrentIndex(index)

def main():
    app = QApplication(sys.argv)
    
    # Настраиваем стиль приложения
    app.setStyle('Fusion')
    
    # Создаем и показываем главное окно
    window = SurveyApp()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
