import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox
import time


class FFTApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("Быстрое преобразование Фурье (БПФ)")

        # Переменные для параметров
        self.signal_type = tk.StringVar(value="sin")
        self.frequency = tk.DoubleVar(value=5.0)
        self.sampling_rate = tk.IntVar(value=256)
        self.amplitude = tk.DoubleVar(value=1.0)
        self.phase = tk.DoubleVar(value=0.0)
        self.add_noise = tk.BooleanVar(value=False)
        self.noise_level = tk.DoubleVar(value=0.1)

        self.setup_ui()
        self.update_plots()

    def setup_ui(self):
        # Главный контейнер
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True) # Используем pack для простоты

        # --- НАЧАЛО ИЗМЕНЕНИЙ: Создание прокручиваемой области ---

        # 1. Создаем холст (Canvas)
        canvas = tk.Canvas(main_frame)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 2. Создаем полосу прокрутки (Scrollbar)
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 3. Связываем их
        canvas.configure(yscrollcommand=scrollbar.set)

        # 4. Создаем фрейм ВНУТРИ холста, в который будем помещать все виджеты
        self.scrollable_frame = ttk.Frame(canvas)

        # 5. Добавляем этот фрейм на холст
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # 6. Магия: говорим холсту обновлять свою область прокрутки, когда размер фрейма меняется
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        # --- КОНЕЦ ИЗМЕНЕНИЙ ---


        # --- ВАЖНО: Теперь все виджеты добавляем в self.scrollable_frame, а не в main_frame ---

        # Панель управления
        control_frame = ttk.LabelFrame(self.scrollable_frame, text="Параметры сигнала", padding="10")
        control_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=10)

        # Тип сигнала
        ttk.Label(control_frame, text="Тип сигнала:").grid(row=0, column=0, sticky=tk.W, padx=5)
        signal_frame = ttk.Frame(control_frame)
        signal_frame.grid(row=0, column=1, sticky=tk.W, padx=5)
        ttk.Radiobutton(signal_frame, text="sin(x)", variable=self.signal_type,
                        value="sin", command=self.update_plots).pack(side=tk.LEFT)
        ttk.Radiobutton(signal_frame, text="cos(x)", variable=self.signal_type,
                        value="cos", command=self.update_plots).pack(side=tk.LEFT, padx=10)

        # Частота
        ttk.Label(control_frame, text="Частота (Гц):").grid(row=0, column=2, sticky=tk.W, padx=5)
        freq_spinbox = ttk.Spinbox(control_frame, from_=0.5, to=50, textvariable=self.frequency,
                                   width=10, increment=0.5, command=self.update_plots)
        freq_spinbox.grid(row=0, column=3, padx=5)

        # Частота дискретизации
        ttk.Label(control_frame, text="Частота дискретизации:").grid(row=0, column=4, sticky=tk.W, padx=5)
        sampling_combo = ttk.Combobox(control_frame, textvariable=self.sampling_rate,
                                      values=[64, 128, 256, 512, 1024], width=8)
        sampling_combo.grid(row=0, column=5, padx=5)
        sampling_combo.bind('<<ComboboxSelected>>', lambda e: self.update_plots())

        # Амплитуда
        ttk.Label(control_frame, text="Амплитуда:").grid(row=1, column=0, sticky=tk.W, padx=5)
        ttk.Scale(control_frame, from_=0.1, to=2.0, variable=self.amplitude,
                  orient=tk.HORIZONTAL, length=100, command=lambda x: self.update_plots()).grid(row=1, column=1, padx=5)
        ttk.Label(control_frame, textvariable=self.amplitude).grid(row=1, column=2, sticky=tk.W)

        # Фаза
        ttk.Label(control_frame, text="Фаза (рад):").grid(row=1, column=3, sticky=tk.W, padx=5)
        ttk.Scale(control_frame, from_=0, to=2 * np.pi, variable=self.phase,
                  orient=tk.HORIZONTAL, length=100, command=lambda x: self.update_plots()).grid(row=1, column=4, padx=5)

        # Шум
        noise_frame = ttk.Frame(control_frame)
        noise_frame.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=5)
        ttk.Checkbutton(noise_frame, text="Добавить шум", variable=self.add_noise,
                        command=self.update_plots).pack(side=tk.LEFT, padx=5)
        ttk.Label(noise_frame, text="Уровень шума:").pack(side=tk.LEFT, padx=5)
        ttk.Scale(noise_frame, from_=0.01, to=0.5, variable=self.noise_level,
                  orient=tk.HORIZONTAL, length=100, command=lambda x: self.update_plots()).pack(side=tk.LEFT)

        # Кнопки
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=2, column=3, columnspan=3, pady=5)
        ttk.Button(button_frame, text="Обновить", command=self.update_plots).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Сравнить с NumPy FFT", command=self.compare_with_numpy).pack(side=tk.LEFT,
                                                                                                    padx=5)
        ttk.Button(button_frame, text="Показать алгоритм", command=self.show_algorithm).pack(side=tk.LEFT, padx=5)

        # Информационная панель
        info_frame = ttk.LabelFrame(self.scrollable_frame, text="Информация", padding="10")
        info_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=10)

        self.info_text = tk.Text(info_frame, height=4, width=80)
        self.info_text.pack(fill=tk.BOTH, expand=True)

        # Создание области для графиков
        self.figure = plt.Figure(figsize=(12, 8), dpi=80)
        self.canvas_matplotlib = FigureCanvasTkAgg(self.figure, self.scrollable_frame) # ИЗМЕНЕНО: родитель - self.scrollable_frame
        self.canvas_matplotlib.get_tk_widget().grid(row=2, column=0, columnspan=2, pady=10, padx=10)


    def generate_signal(self):
        """Генерация сигнала"""
        N = self.sampling_rate.get()
        fs = N  # Частота дискретизации
        t = np.linspace(0, 1, N, endpoint=False)
        freq = self.frequency.get()
        amp = self.amplitude.get()
        phase = self.phase.get()

        if self.signal_type.get() == "sin":
            signal = amp * np.sin(2 * np.pi * freq * t + phase)
        else:
            signal = amp * np.cos(2 * np.pi * freq * t + phase)

        if self.add_noise.get():
            noise = np.random.normal(0, self.noise_level.get(), N)
            signal = signal + noise

        return t, signal

    def fft_recursive(self, x):
        """Рекурсивная реализация БПФ (алгоритм Кули-Тьюки)"""
        N = len(x)

        # Базовый случай
        if N <= 1:
            return x

        # Проверка, что N - степень двойки
        if N % 2 != 0:
            raise ValueError("Размер должен быть степенью 2")

        # Разделение на четные и нечетные элементы
        even = self.fft_recursive(x[0::2])
        odd = self.fft_recursive(x[1::2])

        # Вычисление поворотных множителей
        T = np.zeros(N // 2, dtype=complex)
        for k in range(N // 2):
            T[k] = np.exp(-2j * np.pi * k / N) * odd[k]

        # Объединение результатов
        result = np.zeros(N, dtype=complex)
        for k in range(N // 2):
            result[k] = even[k] + T[k]
            result[k + N // 2] = even[k] - T[k]

        return result

    def fft_iterative(self, x):
        """Итеративная реализация БПФ"""
        N = len(x)

        # Проверка, что N - степень двойки
        if N & (N - 1) != 0:
            raise ValueError("Размер должен быть степенью 2")

        # Бит-реверсивная перестановка
        x = self.bit_reverse_copy(x)

        # Итеративное БПФ
        m = 1
        while m < N:
            m *= 2
            omega_m = np.exp(-2j * np.pi / m)

            for k in range(0, N, m):
                omega = 1
                for j in range(m // 2):
                    t = omega * x[k + j + m // 2]
                    u = x[k + j]
                    x[k + j] = u + t
                    x[k + j + m // 2] = u - t
                    omega *= omega_m

        return x

    def bit_reverse_copy(self, x):
        """Бит-реверсивная перестановка"""
        N = len(x)
        result = np.zeros(N, dtype=complex)

        for i in range(N):
            rev_i = self.reverse_bits(i, int(np.log2(N)))
            result[rev_i] = x[i]

        return result

    def reverse_bits(self, num, bit_count):
        """Реверс битов числа"""
        result = 0
        for i in range(bit_count):
            if num & (1 << i):
                result |= 1 << (bit_count - 1 - i)
        return result

    def update_plots(self):
        """Обновление графиков"""
        try:
            # Генерация сигнала
            t, signal = self.generate_signal()

            # Вычисление БПФ
            start_time = time.time()
            fft_result = self.fft_iterative(signal)
            fft_time = time.time() - start_time

            # Частотная ось
            N = len(signal)
            freq_axis = np.fft.fftfreq(N, d=1 / self.sampling_rate.get())[:N // 2]

            # Амплитудный спектр
            magnitude = 2.0 / N * np.abs(fft_result[:N // 2])

            # Фазовый спектр
            phase = np.angle(fft_result[:N // 2])

            # Очистка графиков
            self.figure.clear()

            # Создание подграфиков
            ax1 = self.figure.add_subplot(2, 2, 1)
            ax2 = self.figure.add_subplot(2, 2, 2)
            ax3 = self.figure.add_subplot(2, 2, 3)
            ax4 = self.figure.add_subplot(2, 2, 4)

            # График исходного сигнала
            ax1.plot(t, signal, 'b-', linewidth=1.5)
            ax1.set_title('Исходный сигнал')
            ax1.set_xlabel('Время (с)')
            ax1.set_ylabel('Амплитуда')
            ax1.grid(True, alpha=0.3)

            # Амплитудный спектр
            ax2.stem(freq_axis, magnitude, basefmt=' ')
            ax2.set_title('Амплитудный спектр')
            ax2.set_xlabel('Частота (Гц)')
            ax2.set_ylabel('Амплитуда')
            ax2.set_xlim([0, 50])
            ax2.grid(True, alpha=0.3)

            # Фазовый спектр
            ax3.plot(freq_axis, phase, 'g-', linewidth=1.5)
            ax3.set_title('Фазовый спектр')
            ax3.set_xlabel('Частота (Гц)')
            ax3.set_ylabel('Фаза (рад)')
            ax3.set_xlim([0, 50])
            ax3.grid(True, alpha=0.3)

            # Спектральная плотность мощности
            psd = np.abs(fft_result[:N // 2]) ** 2 / N
            ax4.semilogy(freq_axis, psd, 'r-', linewidth=1.5)
            ax4.set_title('Спектральная плотность мощности')
            ax4.set_xlabel('Частота (Гц)')
            ax4.set_ylabel('Мощность')
            ax4.set_xlim([0, 50])
            ax4.grid(True, alpha=0.3)

            self.figure.tight_layout()
            self.canvas_matplotlib.draw() # ИЗМЕНЕНО: self.canvas -> self.canvas_matplotlib

            # Обновление информации
            self.update_info(fft_time, magnitude, freq_axis)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

    def update_info(self, fft_time, magnitude, freq_axis):
        """Обновление информационной панели"""
        self.info_text.delete(1.0, tk.END)

        # Поиск доминирующей частоты
        peak_idx = np.argmax(magnitude)
        peak_freq = freq_axis[peak_idx]
        peak_amp = magnitude[peak_idx]

        info = f"Время выполнения БПФ: {fft_time * 1000:.3f} мс\n"
        info += f"Размер выборки: {self.sampling_rate.get()} точек\n"
        info += f"Обнаруженная частота: {peak_freq:.2f} Гц (амплитуда: {peak_amp:.3f})\n"
        info += f"Заданная частота: {self.frequency.get():.2f} Гц"

        self.info_text.insert(1.0, info)

    def compare_with_numpy(self):
        """Сравнение с NumPy FFT"""
        try:
            t, signal = self.generate_signal()

            # Наша реализация
            start_time = time.time()
            our_fft = self.fft_iterative(signal)
            our_time = time.time() - start_time

            # NumPy реализация
            start_time = time.time()
            numpy_fft = np.fft.fft(signal)
            numpy_time = time.time() - start_time

            # Вычисление ошибки
            error = np.mean(np.abs(our_fft - numpy_fft))

            result = f"Сравнение с NumPy FFT:\n\n"
            result += f"Время выполнения нашего БПФ: {our_time * 1000:.3f} мс\n"
            result += f"Время выполнения NumPy FFT: {numpy_time * 1000:.3f} мс\n"
            result += f"Средняя абсолютная ошибка: {error:.2e}\n\n"

            if error < 1e-10:
                result += "✓ Результаты практически идентичны!"
            else:
                result += "⚠ Обнаружены небольшие расхождения"

            messagebox.showinfo("Сравнение с NumPy", result)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сравнении: {str(e)}")

    def show_algorithm(self):
        """Показать описание алгоритма"""
        algorithm_text = """
АЛГОРИТМ БЫСТРОГО ПРЕОБРАЗОВАНИЯ ФУРЬЕ (БПФ)

Алгоритм Кули-Тьюки (Cooley-Tukey):

1. ПРИНЦИП РАБОТЫ:
   - Разделяй и властвуй (divide and conquer)
   - Рекурсивное разбиение ДПФ размера N на два ДПФ размера N/2
   - Сложность: O(N log N) вместо O(N²) для прямого ДПФ

2. ОСНОВНЫЕ ШАГИ:
   a) Разделение входного массива на четные и нечетные элементы
   b) Рекурсивное вычисление БПФ для каждой половины
   c) Объединение результатов с использованием поворотных множителей

3. ПОВОРОТНЫЙ МНОЖИТЕЛЬ:
   W_N^k = exp(-2πi·k/N)

4. ФОРМУЛА ОБЪЕДИНЕНИЯ:
   X[k] = E[k] + W_N^k · O[k]
   X[k+N/2] = E[k] - W_N^k · O[k]

   где E[k] - БПФ четных элементов
       O[k] - БПФ нечетных элементов

5. ОГРАНИЧЕНИЯ:
   - Размер входных данных должен быть степенью 2
   - Для других размеров используются алгоритмы Блюстейна или Рейдера

6. ПРИМЕНЕНИЕ:
   - Обработка сигналов
   - Спектральный анализ
   - Фильтрация
   - Сжатие данных
   - Умножение больших чисел
        """

        # Создание нового окна
        algo_window = tk.Toplevel(self.root)
        algo_window.title("Алгоритм БПФ")
        algo_window.geometry("600x500")

        text_widget = tk.Text(algo_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(1.0, algorithm_text)
        text_widget.config(state=tk.DISABLED)


def main():
    root = tk.Tk()
    app = FFTApplication(root)
    root.mainloop()


if __name__ == "__main__":
    main()