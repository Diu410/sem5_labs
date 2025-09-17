import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import random
import time
import string
from collections import Counter
import threading


class PasswordAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Анализатор паролей")
        self.root.geometry("1200x800")

        # Алфавит: латиница строчные и прописные
        self.alphabet = string.ascii_letters  # a-z, A-Z (52 символа)

        # Инициализация генератора случайных чисел от таймера
        random.seed(int(time.time()))

        self.setup_ui()

    def setup_ui(self):
        # Главный фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Настройка весов для растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)

        # Блок ввода параметров
        ttk.Label(main_frame, text="Параметры генерации пароля:", font=('Arial', 12, 'bold')).grid(row=0, column=0,
                                                                                                   columnspan=2,
                                                                                                   sticky=tk.W,
                                                                                                   pady=(0, 10))

        # Длина пароля
        ttk.Label(main_frame, text="Длина пароля:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.length_var = tk.StringVar(value="8")
        length_entry = ttk.Entry(main_frame, textvariable=self.length_var, width=10)
        length_entry.grid(row=1, column=1, sticky=tk.W)

        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky=tk.W)

        ttk.Button(button_frame, text="Сгенерировать пароль", command=self.generate_password).pack(side=tk.LEFT,
                                                                                                   padx=(0, 10))
        ttk.Button(button_frame, text="Анализ распределения", command=self.analyze_distribution).pack(side=tk.LEFT,
                                                                                                      padx=(0, 10))
        ttk.Button(button_frame, text="График времени подбора", command=self.plot_cracking_time).pack(side=tk.LEFT,
                                                                                                      padx=(0, 10))
        ttk.Button(button_frame, text="Рекомендации", command=self.show_recommendations).pack(side=tk.LEFT)

        # Поле для отображения сгенерированного пароля
        ttk.Label(main_frame, text="Сгенерированный пароль:").grid(row=3, column=0, sticky=tk.W, pady=(10, 0))
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(main_frame, textvariable=self.password_var, width=50, state='readonly')
        password_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=(10, 0))

        # Область для графиков
        self.plot_frame = ttk.Frame(main_frame)
        self.plot_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(20, 0))
        self.plot_frame.columnconfigure(0, weight=1)
        self.plot_frame.rowconfigure(0, weight=1)

        # Информационная панель
        info_frame = ttk.LabelFrame(main_frame, text="Информация", padding="5")
        info_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        info_frame.columnconfigure(0, weight=1)

        self.info_text = tk.Text(info_frame, height=8, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=scrollbar.set)

        self.info_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Начальная информация
        self.info_text.insert(tk.END, f"Алфавит: {self.alphabet}\n")
        self.info_text.insert(tk.END, f"Размер алфавита: {len(self.alphabet)} символов\n")
        self.info_text.insert(tk.END, "Готов к работе!\n")

    def generate_password(self):
        """Генерация пароля заданной длины"""
        try:
            length = int(self.length_var.get())
            if length <= 0:
                raise ValueError("Длина должна быть положительной")
            if length > 50:
                result = messagebox.askyesno("Предупреждение",
                                             f"Вы выбрали длину пароля {length}. Это может занять время для расчета. Продолжить?")
                if not result:
                    return

            # Генерация пароля с использованием random (аналог rand() в C)
            password = ''.join(random.choice(self.alphabet) for _ in range(length))
            self.password_var.set(password)

            # Расчет времени подбора для этого пароля
            try:
                avg_time = self.calculate_average_cracking_time(length)
                time_str = self.format_time(avg_time)
            except (OverflowError, ValueError):
                time_str = "Слишком большое значение для расчета"

            self.info_text.insert(tk.END, f"\nСгенерирован пароль длины {length}: {password}\n")
            self.info_text.insert(tk.END, f"Среднее время подбора: {time_str}\n")
            self.info_text.see(tk.END)

        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректная длина пароля: {e}")

    def analyze_distribution(self):
        """Анализ равномерности распределения символов"""
        password = self.password_var.get()
        if not password:
            messagebox.showwarning("Предупреждение", "Сначала сгенерируйте пароль!")
            return

        # Подсчет частот символов
        char_counts = Counter(password)

        # Создание графика
        self.clear_plot_frame()

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Гистограмма частот символов в пароле
        chars = list(char_counts.keys())
        counts = list(char_counts.values())

        ax1.bar(chars, counts)
        ax1.set_title('Распределение символов в пароле')
        ax1.set_xlabel('Символы')
        ax1.set_ylabel('Частота')
        ax1.tick_params(axis='x', rotation=90)

        # Теоретическое равномерное распределение
        alphabet_chars = list(self.alphabet)
        uniform_prob = 1 / len(self.alphabet)
        uniform_counts = [uniform_prob] * len(self.alphabet)

        ax2.bar(alphabet_chars, uniform_counts, alpha=0.7, label='Теоретическое')

        # Эмпирическое распределение
        empirical_counts = [char_counts.get(c, 0) / len(password) for c in self.alphabet]
        ax2.bar(alphabet_chars, empirical_counts, alpha=0.7, label='Эмпирическое')

        ax2.set_title('Сравнение с равномерным распределением')
        ax2.set_xlabel('Символы алфавита')
        ax2.set_ylabel('Вероятность')
        ax2.legend()
        ax2.tick_params(axis='x', rotation=90)

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Статистический анализ
        expected_freq = len(password) / len(self.alphabet)
        chi_square = sum((count - expected_freq) ** 2 / expected_freq for count in char_counts.values())

        self.info_text.insert(tk.END, f"\nАнализ распределения символов:\n")
        self.info_text.insert(tk.END, f"Длина пароля: {len(password)}\n")
        self.info_text.insert(tk.END, f"Уникальных символов: {len(char_counts)}\n")
        self.info_text.insert(tk.END, f"Ожидаемая частота: {expected_freq:.2f}\n")
        self.info_text.insert(tk.END, f"Хи-квадрат статистика: {chi_square:.2f}\n")
        self.info_text.see(tk.END)

    def plot_cracking_time(self):
        """Построение графика зависимости времени подбора от длины пароля"""
        self.info_text.insert(tk.END, "\nПостроение графика времени подбора...\n")
        self.info_text.see(tk.END)

        # Запуск в отдельном потоке для избежания зависания UI
        thread = threading.Thread(target=self._plot_cracking_time_thread)
        thread.daemon = True
        thread.start()

    def _plot_cracking_time_thread(self):
        """Построение графика в отдельном потоке"""
        lengths = range(1, 21)  # От 1 до 20 символов для лучшей демонстрации
        times = []

        for length in lengths:
            try:
                avg_time = self.calculate_average_cracking_time(length)
                times.append(avg_time)
            except (OverflowError, ValueError) as e:
                # Для очень больших значений используем приближение
                import math
                log_time = length * math.log(len(self.alphabet)) - math.log(2) - math.log(1e9)
                times.append(math.exp(min(log_time, 700)))  # Ограничиваем exp(700) чтобы избежать inf

        # Обновление UI в главном потоке
        self.root.after(0, self._update_cracking_time_plot, lengths, times)

    def _update_cracking_time_plot(self, lengths, times):
        """Обновление графика в главном потоке"""
        self.clear_plot_frame()

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Линейный масштаб
        ax1.plot(lengths, times, 'bo-', linewidth=2, markersize=8)
        ax1.set_title('Время подбора пароля (линейный масштаб)')
        ax1.set_xlabel('Длина пароля')
        ax1.set_ylabel('Время (секунды)')
        ax1.grid(True, alpha=0.3)

        # Логарифмический масштаб
        ax2.semilogy(lengths, times, 'ro-', linewidth=2, markersize=8)
        ax2.set_title('Время подбора пароля (логарифмический масштаб)')
        ax2.set_xlabel('Длина пароля')
        ax2.set_ylabel('Время (секунды, лог. шкала)')
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.info_text.insert(tk.END, "График построен!\n")
        if len(times) > 7:
            self.info_text.insert(tk.END, f"Для пароля длины 8: {self.format_time(times[7])}\n")
        if len(times) > 11:
            self.info_text.insert(tk.END, f"Для пароля длины 12: {self.format_time(times[11])}\n")
        if len(times) > 15:
            self.info_text.insert(tk.END, f"Для пароля длины 16: {self.format_time(times[15])}\n")
        self.info_text.see(tk.END)

    def calculate_average_cracking_time(self, length):
        """Расчет среднего времени подбора пароля"""
        import math

        # Используем логарифмы для избежания переполнения
        # log(total_combinations) = length * log(alphabet_size)
        log_total_combinations = length * math.log(len(self.alphabet))

        # log(avg_attempts) = log(total_combinations) - log(2)
        log_avg_attempts = log_total_combinations - math.log(2)

        # Предполагаемая скорость подбора (попыток в секунду)
        # Современный компьютер может проверять ~10^9 паролей в секунду для простых хешей
        attempts_per_second = 1e9
        log_attempts_per_second = math.log(attempts_per_second)

        # log(avg_time_seconds) = log(avg_attempts) - log(attempts_per_second)
        log_avg_time = log_avg_attempts - log_attempts_per_second

        # Преобразуем обратно из логарифмической формы
        avg_time_seconds = math.exp(log_avg_time)

        return avg_time_seconds

    def format_time(self, seconds):
        """Форматирование времени в удобочитаемый вид"""
        import math

        # Для очень больших чисел используем научную нотацию
        if seconds == float('inf') or math.isnan(seconds):
            return "Бесконечность"
        elif seconds < 1e-6:
            return f"{seconds:.2e} секунд (мгновенно)"
        elif seconds < 60:
            return f"{seconds:.2e} секунд"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.2e} минут"
        elif seconds < 86400:
            hours = seconds / 3600
            return f"{hours:.2e} часов"
        elif seconds < 31536000:
            days = seconds / 86400
            return f"{days:.2e} дней"
        elif seconds < 31536000000:  # 1000 лет
            years = seconds / 31536000
            return f"{years:.2e} лет"
        else:
            years = seconds / 31536000
            if years > 1e100:
                return f"{years:.2e} лет (космологические времена)"
            else:
                return f"{years:.2e} лет"

    def clear_plot_frame(self):
        """Очистка области графиков"""
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

    def show_recommendations(self):
        """Показать рекомендации по выбору паролей"""
        recommendations = """
ПРАКТИЧЕСКИЕ РЕКОМЕНДАЦИИ ПО ВЫБОРУ ПАРОЛЕЙ

1. ДЛИНА ПАРОЛЯ:
   • Минимум 8 символов для обычных аккаунтов
   • 12+ символов для важных данных (банки, корпоративные системы)
   • 16+ символов для критически важной информации

2. АЛФАВИТ ПАРОЛЯ:
   • Только латиница (a-z, A-Z): 52 символа - СЛАБО
   • + Цифры (0-9): 62 символа - ЛУЧШЕ
   • + Спецсимволы (!@#$%): 94+ символов - РЕКОМЕНДУЕТСЯ

3. В ЗАВИСИМОСТИ от ЦЕННОСТИ ИНФОРМАЦИИ:
   • Низкая ценность: 8-10 символов, смешанный регистр
   • Средняя ценность: 10-12 символов + цифры + спецсимволы
   • Высокая ценность: 12+ символов + все виды символов + 2FA

4. УЧЕТ ПРОИЗВОДИТЕЛЬНОСТИ АТАКУЮЩЕГО:
   • Домашний ПК: ~10^6-10^8 попыток/сек
   • Мощная рабочая станция: ~10^9-10^10 попыток/сек
   • Кластер/облако: ~10^12+ попыток/сек

5. ВРЕМЯ АТАКИ:
   • Если данные теряют актуальность через месяц - можно короче
   • Долгосрочная защита - обязательно длинные пароли

6. ДОПОЛНИТЕЛЬНЫЕ РЕКОМЕНДАЦИИ:
   • Используйте двухфакторную аутентификацию
   • Регулярно меняйте пароли для важных систем
   • Используйте менеджеры паролей
   • Избегайте словарных слов и персональной информации

ВЫВОД: Для алфавита только из латинских букв (52 символа) рекомендуется
использовать пароли длиной не менее 12-14 символов для надежной защиты.
        """

        # Создание окна с рекомендациями
        rec_window = tk.Toplevel(self.root)
        rec_window.title("Рекомендации по паролям")
        rec_window.geometry("800x600")

        text_widget = tk.Text(rec_window, wrap=tk.WORD, padx=10, pady=10)
        scrollbar = ttk.Scrollbar(rec_window, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        text_widget.insert(tk.END, recommendations)
        text_widget.config(state=tk.DISABLED)


def main():
    root = tk.Tk()
    app = PasswordAnalyzer(root)
    root.mainloop()


if __name__ == "__main__":
    main()