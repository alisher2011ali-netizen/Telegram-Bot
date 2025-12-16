import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext 
from tkinter import font as tkFont
from tkinter import messagebox
import csv

def load_terms_from_csv(file_path):
    terms_dict = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                terms_dict[row['terms']] = {
                    'definition': row['definition'],
                    'example': row['example'].replace('\\n', '\n')
                }
    except FileNotFoundError:
        print(f"Ошибка: Файл {file_path} не найден.")
        return {}
    return terms_dict

class PythonDictionaryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Словарь")
        self.root.geometry("800x500")
        self.root.iconbitmap("icon-python.ico")
        self.font = tkFont.Font(family="Hack-BondItalic.ttf", size=16)

        self.terms_data = load_terms_from_csv("terms_data.csv")
        self.all_terms = self.terms_data.keys()

        self.create_widgets()
        self.update_list()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10 10 10 10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Левая панель
        left_frame = ttk.Frame(main_frame, width=200)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))
        left_frame.pack_propagate(False)

        ttk.Label(left_frame, text="Поиск термина:", font=self.font).pack(side=tk.TOP, anchor=tk.W, pady=(0, 5))
        
        self.search_entry = ttk.Entry(left_frame)
        self.search_entry.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        self.search_entry.bind('<KeyRelease>', self.update_list)

        self.terms_listbox = tk.Listbox(left_frame, width=40, font=self.font)
        self.terms_listbox.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.terms_listbox.bind('<<ListboxSelect>>', self.display_definition)

        # Правая панель
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        ttk.Label(right_frame, text="Определение:", font=self.font).pack(side=tk.TOP, anchor=tk.W, pady=(0, 5))
        self.definition_area = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, state=tk.DISABLED, height=10)
        self.definition_area.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(0, 10))

        ttk.Label(right_frame, text="Пример кода:", font=self.font).pack(side=tk.TOP, anchor=tk.W, pady=(0, 5))
        self.example_area = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, state=tk.DISABLED, height=8, background='#f0f0f0')
        self.example_area.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.definition_area.tag_configure('custom_style', font=self.font)
        self.example_area.tag_configure('custom_style', font=self.font)

    # Методы класса для логики

    def display_definition(self, event=None):
        try:
            selection = self.terms_listbox.curselection()
            if selection:
                selected_term = self.terms_listbox.get(selection) 
                data = self.terms_data.get(selected_term, None)
            
                if data:
                    self.definition_area.config(state=tk.NORMAL)
                    self.definition_area.delete('1.0', tk.END)
                    self.definition_area.insert(tk.END, data["definition"], 'custom_style')
                    self.definition_area.config(state=tk.DISABLED)

                    self.example_area.config(state=tk.NORMAL)
                    self.example_area.delete('1.0', tk.END)
                    self.example_area.insert(tk.END, data["example"], 'custom_style')
                    self.example_area.config(state=tk.DISABLED)
                else:
                    messagebox.showerror("Ошибка данных", f"Не удалось найти данные для термина: {selected_term}")

        except Exception as e:
            messagebox.showerror("Критическая ошибка", f"Произошла непредвиденная ошибка при отображении: {e}")


    def update_list(self, event=None):
        search_term = self.search_entry.get().lower()
        self.terms_listbox.delete(0, tk.END)
        for term in self.all_terms:
            if search_term in term.lower():
                self.terms_listbox.insert(tk.END, term)

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = PythonDictionaryApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Критическая ошибка запуска приложения: {e}")