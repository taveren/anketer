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
        return {"default_survey_id": None}
    
    def save_settings(self):
        """Сохраняем настройки в файл"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить настройки: {e}")
    
    def setup_icon(self):
        """Устанавливаем иконку приложения"""
        try:
            # Пытаемся загрузить иконку из favicon.ico
            icon_path = os.path.join(os.path.dirname(__file__), "favicon.ico")
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
            else:
                # Если иконка не найдена, создаем простую иконку
                pixmap = QPixmap(32, 32)
                pixmap.fill(QColor("#3498db"))
                self.setWindowIcon(QIcon(pixmap))
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
            self.answer_spinbox.setValue(int(self.current_answers.get(question['id'], 0)))
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
            answer = self.answer_spinbox.value()
        else:
            answer = ''
        
        self.current_answers[question['id']] = answer
    
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
        if not ok or password != "admin123":
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
        
        button_layout.addWidget(create_button)
        button_layout.addWidget(export_button)
        button_layout.addWidget(import_button)
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
        
        action_layout.addWidget(edit_button)
        action_layout.addWidget(responses_button)
        action_layout.addWidget(delete_button)
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
        
        delete_question_btn = QPushButton("Удалить")
        delete_question_btn.clicked.connect(lambda: self.delete_question(survey, editor_window))
        
        move_up_btn = QPushButton("Вверх")
        move_up_btn.clicked.connect(lambda: self.move_question_up(survey, editor_window))
        
        move_down_btn = QPushButton("Вниз")
        move_down_btn.clicked.connect(lambda: self.move_question_down(survey, editor_window))
        
        question_buttons.addWidget(edit_question_btn)
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
        edit_condition_btn.clicked.connect(self.edit_condition)
        
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
            self.load_question_data(survey['questions'][question_index])
        
        # Инициализируем тип вопроса
        self.on_question_type_changed()
        
        editor_dialog.exec()
    
    def on_question_type_changed(self):
        """Обработка изменения типа вопроса"""
        question_type = self.question_type_combo.currentText()
        self.options_frame.setVisible(question_type in ['radio', 'checkbox'])
    
    def add_option(self):
        """Добавляем вариант ответа"""
        option, ok = QInputDialog.getText(self, "Вариант ответа", "Введите вариант ответа:")
        if ok and option.strip():
            self.options_list.addItem(option.strip())
    
    def edit_option(self):
        """Редактируем вариант ответа"""
        current_item = self.options_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Предупреждение", "Выберите вариант для редактирования")
            return
        
        current_text = current_item.text()
        new_text, ok = QInputDialog.getText(self, "Редактирование варианта", "Введите новый текст:", text=current_text)
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
        self.operator_combo.addItems(["равно", "не равно", "содержит", "больше", "меньше"])
        operator_layout.addRow("Оператор:", self.operator_combo)
        layout.addLayout(operator_layout)
        
        # Значение
        value_layout = QFormLayout()
        self.condition_value_edit = QLineEdit()
        value_layout.addRow("Значение:", self.condition_value_edit)
        layout.addLayout(value_layout)
        
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
    
    def save_condition(self, dialog):
        """Сохраняем условие"""
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
            "меньше": "less_than"
        }
        
        condition = {
            'id': str(uuid.uuid4()),
            'targetId': f"q{target_index}",
            'operator': operator_map[operator],
            'value': value
        }
        
        # Добавляем условие в список
        condition_text = f"Если {self.target_question_combo.currentText()} {operator} '{value}'"
        self.conditions_list.addItem(condition_text)
        
        # Сохраняем условие в данных
        if not hasattr(self, 'current_conditions'):
            self.current_conditions = []
        self.current_conditions.append(condition)
        
        dialog.accept()
    
    def edit_condition(self):
        """Редактируем условие"""
        QMessageBox.information(self, "Информация", "Редактирование условий будет добавлено в следующей версии")
    
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
    
    def load_question_data(self, question):
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
        for condition in self.current_conditions:
            condition_text = f"Если q{condition['targetId']} {condition['operator']} '{condition['value']}'"
            self.conditions_list.addItem(condition_text)
    
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
        question = {
            'id': f"q{len(survey['questions']) if question_index is None else question_index}",
            'text': text,
            'type': question_type,
            'required': required,
            'options': options if question_type in ['radio', 'checkbox'] else [],
            'conditions': getattr(self, 'current_conditions', [])
        }
        
        # Для первого вопроса убираем все условия (чтобы избежать циклических зависимостей)
        if question_index is None and len(survey['questions']) == 0:
            question['conditions'] = []
            print("DEBUG: Первый вопрос создан БЕЗ условий")
        
        if question_index is None:
            # Новый вопрос
            survey['questions'].append(question)
        else:
            # Обновляем существующий
            survey['questions'][question_index] = question
        
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

        # Все условия должны выполняться (AND логика)
        for condition in conditions:
            condition_result = self.check_condition(condition, answers)
            if not condition_result:
                return False

        return True
    
    def check_condition(self, condition, answers):
        """Проверяем условие"""
        target_id = condition['targetId']
        operator = condition['operator']
        value = condition['value']
        
        # Получаем ответ на целевой вопрос
        answer = answers.get(target_id)
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
        elif operator == 'greater_than':
            try:
                return float(answer) > float(value)
            except (ValueError, TypeError):
                return False
        elif operator == 'less_than':
            try:
                return float(answer) < float(value)
            except (ValueError, TypeError):
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
