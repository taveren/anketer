#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Система анкетирования - Desktop приложение
Кроссплатформенное Python приложение с файловым хранилищем
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import csv
from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid
import sys
import platform

class SurveyApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Система анкетирования")
        self.root.geometry("1200x800")
        
        # Определяем путь к данным
        self.data_dir = self.get_data_directory()
        self.surveys_file = os.path.join(self.data_dir, "surveys.json")
        self.responses_file = os.path.join(self.data_dir, "responses.json")
        
        # Создаем директорию если не существует
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Загружаем данные
        self.surveys = self.load_surveys()
        self.responses = self.load_responses()
        
        # Текущий пользователь
        self.current_user = None
        self.current_survey = None
        self.current_answers = {}
        
        self.setup_ui()
        
    def get_data_directory(self):
        """Получаем путь к директории с данными в зависимости от ОС"""
        if platform.system() == "Windows":
            # В Windows используем AppData
            appdata = os.environ.get('APPDATA', '')
            return os.path.join(appdata, "ASRR", "SurveyApp")
        elif platform.system() == "Darwin":  # macOS
            # В macOS используем Application Support
            home = os.path.expanduser("~")
            return os.path.join(home, "Library", "Application Support", "ASRR", "SurveyApp")
        else:  # Linux и другие
            # В Linux используем .local/share
            home = os.path.expanduser("~")
            return os.path.join(home, ".local", "share", "ASRR", "SurveyApp")
    
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
    
    def save_surveys(self):
        """Сохраняем анкеты в файл"""
        try:
            with open(self.surveys_file, 'w', encoding='utf-8') as f:
                json.dump(self.surveys, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить анкеты: {e}")
    
    def save_responses(self):
        """Сохраняем ответы в файл"""
        try:
            with open(self.responses_file, 'w', encoding='utf-8') as f:
                json.dump(self.responses, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить ответы: {e}")
    
    def setup_ui(self):
        """Настраиваем интерфейс"""
        # Главное меню
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Экспорт данных", command=self.export_data)
        file_menu.add_command(label="Импорт данных", command=self.import_data)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        
        # Меню "Администрирование"
        admin_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Администрирование", menu=admin_menu)
        admin_menu.add_command(label="Управление анкетами", command=self.show_admin_panel)
        admin_menu.add_command(label="Создать анкету", command=self.create_survey)
        
        # Основной интерфейс
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Заголовок
        title_label = ttk.Label(self.main_frame, text="Система анкетирования", 
                               font=("Arial", 24, "bold"))
        title_label.pack(pady=20)
        
        # Кнопки
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=20)
        
        self.start_button = ttk.Button(button_frame, text="СТАРТ", 
                                     command=self.start_survey,
                                     style="Start.TButton")
        self.start_button.pack(side=tk.LEFT, padx=10)
        
        self.admin_button = ttk.Button(button_frame, text="Админ", 
                                     command=self.show_admin_panel)
        self.admin_button.pack(side=tk.LEFT, padx=10)
        
        # Стили
        style = ttk.Style()
        style.configure("Start.TButton", font=("Arial", 16, "bold"))
        
        # Статус
        self.status_label = ttk.Label(self.main_frame, text="Готов к работе")
        self.status_label.pack(pady=10)
        
        # Список активных анкет
        self.survey_list_frame = ttk.LabelFrame(self.main_frame, text="Доступные анкеты")
        self.survey_list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.update_survey_list()
    
    def update_survey_list(self):
        """Обновляем список анкет"""
        # Очищаем старые виджеты
        for widget in self.survey_list_frame.winfo_children():
            widget.destroy()
        
        active_surveys = [s for s in self.surveys if s.get('isActive', True)]
        
        if not active_surveys:
            ttk.Label(self.survey_list_frame, text="Нет доступных анкет").pack(pady=20)
            return
        
        for survey in active_surveys:
            survey_frame = ttk.Frame(self.survey_list_frame)
            survey_frame.pack(fill=tk.X, padx=5, pady=5)
            
            ttk.Label(survey_frame, text=survey['title'], 
                     font=("Arial", 12, "bold")).pack(side=tk.LEFT)
            
            ttk.Label(survey_frame, text=f"Вопросов: {len(survey['questions'])}").pack(side=tk.LEFT, padx=10)
            
            ttk.Button(survey_frame, text="Пройти", 
                      command=lambda s=survey: self.take_survey(s)).pack(side=tk.RIGHT)
    
    def start_survey(self):
        """Начинаем прохождение анкеты"""
        active_surveys = [s for s in self.surveys if s.get('isActive', True)]
        
        if not active_surveys:
            messagebox.showinfo("Информация", "Нет доступных анкет")
            return
        
        if len(active_surveys) == 1:
            self.take_survey(active_surveys[0])
        else:
            self.show_survey_selection()
    
    def show_survey_selection(self):
        """Показываем выбор анкеты"""
        selection_window = tk.Toplevel(self.root)
        selection_window.title("Выберите анкету")
        selection_window.geometry("400x300")
        selection_window.transient(self.root)
        selection_window.grab_set()
        
        ttk.Label(selection_window, text="Выберите анкету для прохождения:", 
                 font=("Arial", 12, "bold")).pack(pady=10)
        
        listbox = tk.Listbox(selection_window)
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        active_surveys = [s for s in self.surveys if s.get('isActive', True)]
        for survey in active_surveys:
            listbox.insert(tk.END, survey['title'])
        
        def on_select():
            selection = listbox.curselection()
            if selection:
                survey = active_surveys[selection[0]]
                selection_window.destroy()
                self.take_survey(survey)
        
        ttk.Button(selection_window, text="Выбрать", command=on_select).pack(pady=10)
    
    def take_survey(self, survey):
        """Проходим анкету"""
        self.current_survey = survey
        self.current_answers = {}
        
        # Создаем окно прохождения анкеты
        survey_window = tk.Toplevel(self.root)
        survey_window.title(f"Анкета: {survey['title']}")
        survey_window.geometry("800x600")
        survey_window.transient(self.root)
        survey_window.grab_set()
        
        # Прогресс
        progress_frame = ttk.Frame(survey_window)
        progress_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                          maximum=len(survey['questions']))
        self.progress_bar.pack(fill=tk.X)
        
        self.progress_label = ttk.Label(progress_frame, text="Вопрос 1 из {}".format(len(survey['questions'])))
        self.progress_label.pack()
        
        # Область для вопросов
        self.question_frame = ttk.Frame(survey_window)
        self.question_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Кнопки навигации
        nav_frame = ttk.Frame(survey_window)
        nav_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.prev_button = ttk.Button(nav_frame, text="Назад", command=self.prev_question)
        self.prev_button.pack(side=tk.LEFT)
        
        self.next_button = ttk.Button(nav_frame, text="Далее", command=self.next_question)
        self.next_button.pack(side=tk.RIGHT)
        
        self.current_question = 0
        self.show_question()
    
    def show_question(self):
        """Показываем текущий вопрос"""
        # Очищаем область вопроса
        for widget in self.question_frame.winfo_children():
            widget.destroy()
        
        if not self.current_survey or self.current_question >= len(self.current_survey['questions']):
            return
        
        question = self.current_survey['questions'][self.current_question]
        
        # Заголовок вопроса
        ttk.Label(self.question_frame, text=question['text'], 
                 font=("Arial", 14, "bold")).pack(anchor=tk.W, pady=10)
        
        if question.get('required', False):
            ttk.Label(self.question_frame, text="* Обязательный вопрос", 
                     foreground="red").pack(anchor=tk.W)
        
        # Поле для ответа
        if question['type'] == 'text':
            self.answer_text = tk.Text(self.question_frame, height=4, width=60)
            self.answer_text.pack(fill=tk.BOTH, expand=True, pady=5)
            self.answer_text.insert(tk.END, self.current_answers.get(question['id'], ''))
        
        elif question['type'] == 'radio':
            self.answer_var = tk.StringVar(value=self.current_answers.get(question['id'], ''))
            for option in question.get('options', []):
                ttk.Radiobutton(self.question_frame, text=option, value=option,
                              variable=self.answer_var).pack(anchor=tk.W, pady=2)
        
        elif question['type'] == 'checkbox':
            self.answer_vars = {}
            current_values = self.current_answers.get(question['id'], [])
            for i, option in enumerate(question.get('options', [])):
                var = tk.BooleanVar(value=option in current_values)
                self.answer_vars[option] = var
                ttk.Checkbutton(self.question_frame, text=option, variable=var).pack(anchor=tk.W, pady=2)
        
        elif question['type'] == 'number':
            self.answer_var = tk.StringVar(value=str(self.current_answers.get(question['id'], '')))
            ttk.Entry(self.question_frame, textvariable=self.answer_var, width=20).pack(anchor=tk.W, pady=5)
        
        # Обновляем прогресс
        self.progress_var.set(self.current_question + 1)
        self.progress_label.config(text=f"Вопрос {self.current_question + 1} из {len(self.current_survey['questions'])}")
        
        # Обновляем кнопки
        self.prev_button.config(state=tk.NORMAL if self.current_question > 0 else tk.DISABLED)
        
        if self.current_question == len(self.current_survey['questions']) - 1:
            self.next_button.config(text="Завершить")
        else:
            self.next_button.config(text="Далее")
    
    def save_current_answer(self):
        """Сохраняем текущий ответ"""
        if not self.current_survey or self.current_question >= len(self.current_survey['questions']):
            return
        
        question = self.current_survey['questions'][self.current_question]
        
        if question['type'] == 'text':
            answer = self.answer_text.get("1.0", tk.END).strip()
        elif question['type'] == 'radio':
            answer = self.answer_var.get()
        elif question['type'] == 'checkbox':
            answer = [option for option, var in self.answer_vars.items() if var.get()]
        elif question['type'] == 'number':
            answer = self.answer_var.get()
        else:
            answer = ''
        
        self.current_answers[question['id']] = answer
    
    def prev_question(self):
        """Предыдущий вопрос"""
        if self.current_question > 0:
            self.save_current_answer()
            self.current_question -= 1
            self.show_question()
    
    def next_question(self):
        """Следующий вопрос"""
        self.save_current_answer()
        
        if self.current_question == len(self.current_survey['questions']) - 1:
            # Завершаем анкету
            self.finish_survey()
        else:
            self.current_question += 1
            self.show_question()
    
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
        
        messagebox.showinfo("Успех", "Анкета успешно завершена!")
        
        # Закрываем окно анкеты
        for window in self.root.winfo_children():
            if isinstance(window, tk.Toplevel):
                window.destroy()
        
        self.update_survey_list()
    
    def show_admin_panel(self):
        """Показываем панель администратора"""
        # Проверяем пароль
        password = tk.simpledialog.askstring("Авторизация", "Введите пароль администратора:", show='*')
        if password != "admin123":
            messagebox.showerror("Ошибка", "Неверный пароль")
            return
        
        admin_window = tk.Toplevel(self.root)
        admin_window.title("Панель администратора")
        admin_window.geometry("1000x700")
        admin_window.transient(self.root)
        admin_window.grab_set()
        
        # Заголовок
        ttk.Label(admin_window, text="Управление анкетами", 
                 font=("Arial", 16, "bold")).pack(pady=10)
        
        # Кнопки управления
        button_frame = ttk.Frame(admin_window)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="Создать анкету", 
                  command=self.create_survey).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Экспорт данных", 
                  command=self.export_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Импорт данных", 
                  command=self.import_data).pack(side=tk.LEFT, padx=5)
        
        # Список анкет
        list_frame = ttk.LabelFrame(admin_window, text="Анкеты")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Таблица анкет
        columns = ("Название", "Вопросов", "Ответов", "Статус", "Создана")
        tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        # Заполняем таблицу
        for survey in self.surveys:
            responses_count = len([r for r in self.responses if r['surveyId'] == survey['id']])
            status = "Активна" if survey.get('isActive', True) else "Неактивна"
            created = datetime.fromisoformat(survey['createdAt']).strftime("%d.%m.%Y")
            
            tree.insert("", tk.END, values=(
                survey['title'],
                len(survey['questions']),
                responses_count,
                status,
                created
            ))
        
        tree.pack(fill=tk.BOTH, expand=True)
        
        # Кнопки действий
        action_frame = ttk.Frame(admin_window)
        action_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(action_frame, text="Редактировать", 
                  command=lambda: self.edit_survey(tree)).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Просмотр ответов", 
                  command=lambda: self.view_responses(tree)).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Удалить", 
                  command=lambda: self.delete_survey(tree)).pack(side=tk.LEFT, padx=5)
    
    def create_survey(self):
        """Создаем новую анкету"""
        # Упрощенная версия создания анкеты
        title = tk.simpledialog.askstring("Создание анкеты", "Введите название анкеты:")
        if not title:
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
        
        messagebox.showinfo("Успех", "Анкета создана! Используйте 'Редактировать' для добавления вопросов.")
        self.update_survey_list()
    
    def edit_survey(self, tree):
        """Редактируем анкету"""
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите анкету для редактирования")
            return
        
        # Упрощенная версия редактирования
        messagebox.showinfo("Информация", "Функция редактирования будет добавлена в следующей версии")
    
    def view_responses(self, tree):
        """Просматриваем ответы"""
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите анкету для просмотра ответов")
            return
        
        # Упрощенная версия просмотра ответов
        messagebox.showinfo("Информация", "Функция просмотра ответов будет добавлена в следующей версии")
    
    def delete_survey(self, tree):
        """Удаляем анкету"""
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите анкету для удаления")
            return
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить эту анкету?"):
            # Упрощенная версия удаления
            messagebox.showinfo("Информация", "Функция удаления будет добавлена в следующей версии")
    
    def export_data(self):
        """Экспортируем данные"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
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
                messagebox.showinfo("Успех", "Данные успешно экспортированы")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось экспортировать данные: {e}")
    
    def import_data(self):
        """Импортируем данные"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
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
                    self.update_survey_list()
                    messagebox.showinfo("Успех", "Данные успешно импортированы")
                else:
                    messagebox.showerror("Ошибка", "Неверный формат файла")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось импортировать данные: {e}")
    
    def run(self):
        """Запускаем приложение"""
        self.root.mainloop()

if __name__ == "__main__":
    # Добавляем tkinter.simpledialog
    import tkinter.simpledialog
    
    app = SurveyApp()
    app.run()
