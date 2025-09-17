# gui.py
# Простой GUI на tkinter: ввод/вывод, выбор языка, шифровать/дешифровать, атака
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from cipher import vigenere_encrypt, vigenere_decrypt
from attack import brute_force
import threading

class VigenereGUI:
    def __init__(self, root):
        self.root = root
        root.title("Vigenere — шифр (encrypt/decrypt) + brute-force attack")
        self.lang_var = tk.StringVar(value="ru")
        self.key_var = tk.StringVar()
        self.max_key_len_var = tk.IntVar(value=3)
        self.known_plain_var = tk.StringVar()
        self.top_n_var = tk.IntVar(value=10)

        # Frames
        top = ttk.Frame(root, padding=10)
        top.pack(fill="both", expand=True)

        # Text areas
        lbl_in = ttk.Label(top, text="Входной текст (plaintext / ciphertext):")
        lbl_in.grid(row=0, column=0, sticky="w")
        self.txt_in = scrolledtext.ScrolledText(top, width=80, height=10)
        self.txt_in.grid(row=1, column=0, columnspan=4, pady=5)

        lbl_out = ttk.Label(top, text="Результат:")
        lbl_out.grid(row=2, column=0, sticky="w")
        self.txt_out = scrolledtext.ScrolledText(top, width=80, height=10)
        self.txt_out.grid(row=3, column=0, columnspan=4, pady=5)

        # Controls
        ttk.Label(top, text="Язык:").grid(row=4, column=0, sticky="e")
        ttk.Radiobutton(top, text="Русский", variable=self.lang_var, value="ru").grid(row=4, column=1, sticky="w")
        ttk.Radiobutton(top, text="Английский", variable=self.lang_var, value="en").grid(row=4, column=2, sticky="w")

        ttk.Label(top, text="Ключ:").grid(row=5, column=0, sticky="e")
        ttk.Entry(top, textvariable=self.key_var, width=30).grid(row=5, column=1, sticky="w")
        ttk.Button(top, text="Зашифровать", command=self.encrypt).grid(row=5, column=2)
        ttk.Button(top, text="Расшифровать", command=self.decrypt).grid(row=5, column=3)

        # Attack controls
        ttk.Separator(top, orient="horizontal").grid(row=6, column=0, columnspan=4, sticky="ew", pady=8)
        ttk.Label(top, text="Атака (brute-force):").grid(row=7, column=0, sticky="w")
        ttk.Label(top, text="max длина ключа:").grid(row=8, column=0, sticky="e")
        ttk.Entry(top, textvariable=self.max_key_len_var, width=5).grid(row=8, column=1, sticky="w")
        ttk.Label(top, text="top N кандидатов:").grid(row=8, column=2, sticky="e")
        ttk.Entry(top, textvariable=self.top_n_var, width=5).grid(row=8, column=3, sticky="w")

        ttk.Label(top, text="Известный фрагмент (поиск совпадения):").grid(row=9, column=0, sticky="e")
        ttk.Entry(top, textvariable=self.known_plain_var, width=40).grid(row=9, column=1, columnspan=2, sticky="w")
        self.btn_attack = ttk.Button(top, text="Запустить атаку", command=self.run_attack_thread)
        self.btn_attack.grid(row=9, column=3)

        # Results table
        ttk.Label(top, text="Кандидаты: (score, key, plaintext preview)").grid(row=10, column=0, sticky="w")
        self.tree = ttk.Treeview(top, columns=("score", "key", "preview"), show="headings", height=8)
        self.tree.heading("score", text="score")
        self.tree.heading("key", text="key")
        self.tree.heading("preview", text="plaintext (preview)")
        self.tree.column("score", width=80)
        self.tree.column("key", width=120)
        self.tree.column("preview", width=500)
        self.tree.grid(row=11, column=0, columnspan=4, pady=5)

        self.tree.bind("<Double-1>", self.on_candidate_select)

    def encrypt(self):
        txt = self.txt_in.get("1.0", "end").rstrip("\n")
        key = self.key_var.get()
        lang = self.lang_var.get()
        try:
            out = vigenere_encrypt(txt, key, lang=lang)
            self.txt_out.delete("1.0", "end")
            self.txt_out.insert("1.0", out)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def decrypt(self):
        txt = self.txt_in.get("1.0", "end").rstrip("\n")
        key = self.key_var.get()
        lang = self.lang_var.get()
        try:
            out = vigenere_decrypt(txt, key, lang=lang)
            self.txt_out.delete("1.0", "end")
            self.txt_out.insert("1.0", out)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def run_attack_thread(self):
        # запускаем брутфорс в отдельном потоке, чтобы GUI не завис
        t = threading.Thread(target=self.run_attack)
        t.daemon = True
        t.start()

    def run_attack(self):
        self.btn_attack.config(state="disabled")
        self.tree.delete(*self.tree.get_children())
        ciphertext = self.txt_in.get("1.0", "end").rstrip("\n")
        if not ciphertext.strip():
            messagebox.showwarning("Warning", "Введите шифртекст в поле выше.")
            self.btn_attack.config(state="normal")
            return
        max_len = self.max_key_len_var.get()
        top_n = self.top_n_var.get()
        known = self.known_plain_var.get().strip() or None
        lang = self.lang_var.get()
        # предупреждение для пользователя
        if max_len > 5:
            if not messagebox.askyesno("Warning", "max_key_len > 5 — пространство ключей очень велико. Продолжить?"):
                self.btn_attack.config(state="normal")
                return
        res = brute_force(ciphertext, lang=lang, max_key_len=max_len, top_n=top_n, known_plaintext=known)
        if res.get("found"):
            messagebox.showinfo("Found", f"Найден ключ: {res['key']}\nПример расшифровки в поле результата.")
            self.txt_out.delete("1.0", "end")
            self.txt_out.insert("1.0", res["plaintext"])
        else:
            # показать кандидатов
            for sc, key, dec in res.get("candidates", []):
                preview = dec[:120].replace("\n", " ")
                self.tree.insert("", "end", values=(f"{sc:.2f}", key, preview))
            messagebox.showinfo("Done", f"Тестов: {res.get('tested', 'n/a')}. Топ кандидатов показан в таблице.")
        self.btn_attack.config(state="normal")

    def on_candidate_select(self, event):
        sel = self.tree.selection()
        if not sel: return
        item = self.tree.item(sel[0])['values']
        key = item[1]
        # дешифруем полностью и поместим в output
        ciphertext = self.txt_in.get("1.0", "end").rstrip("\n")
        dec = vigenere_decrypt(ciphertext, key, lang=self.lang_var.get())
        self.txt_out.delete("1.0", "end")
        self.txt_out.insert("1.0", f"Key: {key}\n\n{dec}")
