#!/usr/bin/env python3
"""add_texture_pack_gui.py
Pequena interface Tkinter para adicionar texture packs ao data/data.json.
- Preencha `Name`, `ID (path)`, `Author`, `Description`, `Version`, `Download`.
- Use os botões "Escolher ícone" e "Escolher screenshot" para selecionar arquivos locais.
- O botão "Adicionar" copia os arquivos selecionados para `uploads/<id>/` (renomeando para icon.png / image.png quando aplicável) e atualiza `data/data.json`.
"""

import json
import os
import shutil
import sys
import datetime
import tkinter as tk
from tkinter import filedialog, messagebox

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(ROOT, 'data', 'data.json')
UPLOADS_DIR = os.path.join(ROOT, 'uploads')


def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_data(data):
    if os.path.exists(DATA_FILE):
        bak = DATA_FILE + '.bak.' + datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        shutil.copy2(DATA_FILE, bak)
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def find_duplicate(data, name, path):
    for item in data:
        if item.get('id') == path:
            return f"id '{path}'"
        if item.get('name','').lower() == name.lower():
            return f"name '{name}'"
    return None


class App:
    def __init__(self, root):
        self.root = root
        root.title('Adicionar Texture Pack')

        frm = tk.Frame(root, padx=8, pady=8)
        frm.pack(fill=tk.BOTH, expand=True)

        # fields
        self.entries = {}
        for i, (label, key) in enumerate([
            ('Name', 'name'),
            ('ID (path) — pasta em uploads/', 'id'),
            ('Creators (comma-separated)', 'creators'),
            ('Version', 'version'),
            ('Download URL', 'download')
        ]):
            tk.Label(frm, text=label).grid(row=i, column=0, sticky='w')
            e = tk.Entry(frm, width=50)
            e.grid(row=i, column=1, sticky='we', pady=2)
            self.entries[key] = e

        # type field
        tk.Label(frm, text='Type (comma-separated)').grid(row=5, column=0, sticky='w')
        e_type = tk.Entry(frm, width=50)
        e_type.grid(row=5, column=1, sticky='we', pady=2)
        self.entries['type'] = e_type

        # featured checkbox
        self.featured_var = tk.BooleanVar()
        tk.Checkbutton(frm, text='Featured', variable=self.featured_var).grid(row=6, column=1, sticky='w')

        # description (multiline)
        tk.Label(frm, text='Description').grid(row=7, column=0, sticky='nw')
        self.description = tk.Text(frm, width=50, height=6)
        self.description.grid(row=7, column=1, sticky='we', pady=4)

        # icon/screenshot selectors
        self.icon_path = tk.StringVar()
        self.screenshot_path = tk.StringVar()

        tk.Button(frm, text='Escolher ícone...', command=self.choose_icon).grid(row=8, column=0, sticky='w')
        tk.Label(frm, textvariable=self.icon_path).grid(row=8, column=1, sticky='w')

        tk.Button(frm, text='Escolher screenshot...', command=self.choose_screenshot).grid(row=9, column=0, sticky='w')
        tk.Label(frm, textvariable=self.screenshot_path).grid(row=9, column=1, sticky='w')

        # action buttons
        btn_frame = tk.Frame(frm)
        btn_frame.grid(row=8, column=0, columnspan=2, pady=8)
        tk.Button(btn_frame, text='Adicionar', command=self.add_pack, bg='#4CAF50', fg='white').pack(side=tk.LEFT, padx=6)
        tk.Button(btn_frame, text='Fechar', command=root.quit).pack(side=tk.LEFT)

    def choose_icon(self):
        p = filedialog.askopenfilename(title='Escolher ícone', filetypes=[('Image files', '*.png *.jpg *.jpeg *.webp *.gif'), ('All files','*.*')])
        if p:
            self.icon_path.set(p)

    def choose_screenshot(self):
        p = filedialog.askopenfilename(title='Escolher screenshot', filetypes=[('Image files', '*.png *.jpg *.jpeg *.webp *.gif'), ('All files','*.*')])
        if p:
            self.screenshot_path.set(p)

    def add_pack(self):
        name = self.entries['name'].get().strip()
        path = self.entries['id'].get().strip()
        creators_raw = self.entries['creators'].get().strip()
        version = self.entries['version'].get().strip()
        download = self.entries['download'].get().strip()
        type_raw = self.entries.get('type', tk.Entry()).get().strip()
        featured = bool(self.featured_var.get())
        description = self.description.get('1.0', tk.END).strip()

        if not name or not path:
            messagebox.showerror('Erro', 'Os campos `Name` e `ID (path)` são obrigatórios.')
            return

        # normalize path
        path = path.replace('\\', '/').lstrip('/')

        # ensure uploads dir exists
        target_dir = os.path.join(UPLOADS_DIR, path)
        try:
            os.makedirs(target_dir, exist_ok=True)
        except Exception as e:
            messagebox.showerror('Erro', f'Não foi possível criar pasta uploads/{path}: {e}')
            return

        data = load_data()
        dup = find_duplicate(data, name, path)
        if dup:
            messagebox.showerror('Duplicado', f'Já existe um item com {dup}. Abortando.')
            return

        entry = {'id': path, 'name': name}
        if description:
            entry['description'] = description
        if version:
            entry['version'] = version
        if download:
            entry['download'] = download
        # parse creators (comma-separated)
        creators = [c.strip() for c in creators_raw.split(',') if c.strip()]
        if creators:
            entry['creators'] = creators

        # parse type
        if type_raw:
            types = [t.strip() for t in type_raw.split(',') if t.strip()]
            if types:
                entry['type'] = types if len(types) > 1 else types[0]

        # featured flag
        if featured:
            entry['featured'] = True

        # copy icon
        if self.icon_path.get():
            src = self.icon_path.get()
            try:
                dst_name = 'icon' + os.path.splitext(src)[1]
                dst_final = os.path.join(target_dir, 'icon.png')
                shutil.copy2(src, dst_final)
                entry['icon'] = f"/uploads/{path}/icon.png"
            except Exception as e:
                messagebox.showwarning('Aviso', f'Falha ao copiar ícone: {e}')

        # copy screenshot
        if self.screenshot_path.get():
            src = self.screenshot_path.get()
            try:
                dst_final = os.path.join(target_dir, 'image.png')
                shutil.copy2(src, dst_final)
                entry['screenshot'] = f"/uploads/{path}/image.png"
            except Exception as e:
                messagebox.showwarning('Aviso', f'Falha ao copiar screenshot: {e}')

        data.append(entry)
        try:
            save_data(data)
        except Exception as e:
            messagebox.showerror('Erro', f'Falha ao salvar data.json: {e}')
            return

        messagebox.showinfo('Concluído', f'Pack "{name}" adicionado com sucesso.')
        self.root.quit()


if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop()
