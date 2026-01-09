import os
import re
import json
import shutil
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
try:
    from PIL import Image
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(ROOT, 'data', 'data.json')
UPLOADS_DIR = os.path.join(ROOT, 'uploads')

ALLOWED_IMAGE_EXT = ('.png', '.jpg', '.jpeg', '.webp')


def make_id(name: str, creator: str | None) -> str:
    s = (creator or 'unknown') + '.' + name
    s = s.lower()
    s = re.sub(r"[^a-z0-9._-]", '-', s)
    s = re.sub(r"-+", '-', s)
    return s.strip('-')


class AddPackApp:
    def __init__(self, root):
        self.root = root
        root.title('Adicionar Texture Pack')

        self.fields = {}
        labels = [
            ('Nome', 'name'),
            ('Versão', 'version'),
            ('Descrição', 'description'),
            ('Criadores (vírgula separado)', 'creators'),
            ('Resoluções (vírgula)', 'resolution'),
            ('Tipos (vírgula)', 'types'),
            ('URL de download', 'download'),
            ('ID (opcional)', 'pack_id')
        ]

        for i, (label_text, key) in enumerate(labels):
            lbl = tk.Label(root, text=label_text)
            lbl.grid(row=i, column=0, sticky='w', padx=6, pady=4)
            entry = tk.Entry(root, width=60)
            entry.grid(row=i, column=1, padx=6, pady=4)
            self.fields[key] = entry

        # Buttons for images
        self.icon_path = None
        self.screenshot_path = None

        btn_icon = tk.Button(root, text='Selecionar Icon', command=self.select_icon)
        btn_icon.grid(row=len(labels), column=0, padx=6, pady=6)
        self.icon_label = tk.Label(root, text='Nenhum arquivo selecionado')
        self.icon_label.grid(row=len(labels), column=1, sticky='w')

        btn_shot = tk.Button(root, text='Selecionar Screenshot', command=self.select_screenshot)
        btn_shot.grid(row=len(labels)+1, column=0, padx=6, pady=6)
        self.shot_label = tk.Label(root, text='Nenhum arquivo selecionado')
        self.shot_label.grid(row=len(labels)+1, column=1, sticky='w')

        # Submit
        submit = tk.Button(root, text='Adicionar Pack', command=self.submit)
        submit.grid(row=len(labels)+2, column=0, columnspan=2, pady=12)

    def select_icon(self):
        path = filedialog.askopenfilename(title='Selecionar Icon', filetypes=[('Images', '*'+a) for a in ALLOWED_IMAGE_EXT])
        if path:
            if not path.lower().endswith(ALLOWED_IMAGE_EXT):
                messagebox.showerror('Erro', 'Formato de imagem não suportado para o icon')
                return
            self.icon_path = path
            self.icon_label.config(text=os.path.basename(path))

    def select_screenshot(self):
        path = filedialog.askopenfilename(title='Selecionar Screenshot', filetypes=[('Images', '*'+a) for a in ALLOWED_IMAGE_EXT])
        if path:
            if not path.lower().endswith(ALLOWED_IMAGE_EXT):
                messagebox.showerror('Erro', 'Formato de imagem não suportado para o screenshot')
                return
            self.screenshot_path = path
            self.shot_label.config(text=os.path.basename(path))

    def submit(self):
        name = self.fields['name'].get().strip()
        version = self.fields['version'].get().strip() or 'v1.0.0'
        description = self.fields['description'].get().strip()
        creators = [c.strip() for c in self.fields['creators'].get().split(',') if c.strip()]
        resolution = [r.strip() for r in self.fields['resolution'].get().split(',') if r.strip()]
        types = [t.strip() for t in self.fields['types'].get().split(',') if t.strip()]
        download = self.fields['download'].get().strip()
        pack_id_field = self.fields['pack_id'].get().strip()

        if not name:
            messagebox.showerror('Erro', 'Nome é obrigatório')
            return
        if not creators:
            messagebox.showerror('Erro', 'Pelo menos um creator é obrigatório')
            return
        if not self.icon_path or not self.screenshot_path:
            messagebox.showerror('Erro', 'Icon e Screenshot são obrigatórios')
            return

        pack_id = pack_id_field or make_id(name, creators[0])

        # Prepare uploads folder
        dest_dir = os.path.join(UPLOADS_DIR, pack_id)
        os.makedirs(dest_dir, exist_ok=True)

        # Normalize and save images as PNG with fixed names
        if not PIL_AVAILABLE:
            messagebox.showerror('Erro', 'A biblioteca Pillow é necessária para processar imagens. Instale com: pip install pillow')
            return

        try:
            dest_icon = os.path.join(dest_dir, 'pack.png')
            dest_shot = os.path.join(dest_dir, 'image.png')

            with Image.open(self.icon_path) as im:
                im.convert('RGBA').save(dest_icon, format='PNG')

            with Image.open(self.screenshot_path) as im:
                im.convert('RGBA').save(dest_shot, format='PNG')
        except Exception as e:
            messagebox.showerror('Erro', f'Falha ao processar imagens: {e}')
            return

        # Update data.json
        try:
            with open(DATA_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            data = []

        new_entry = {
            'id': pack_id,
            'name': name,
            'resolution': resolution,
            'download': download,
            'description': description,
            'version': version,
            'icon': f'/uploads/{pack_id}/pack.png',
            'screenshot': f'/uploads/{pack_id}/image.png',
            'featured': False,
            'type': types,
            'creators': creators,
            'date': datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'
        }

        data.append(new_entry)

        try:
            with open(DATA_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror('Erro', f'Falha ao atualizar data.json: {e}')
            return

        messagebox.showinfo('Sucesso', f'Pack {name} adicionado com id {pack_id}')
        self.root.destroy()


if __name__ == '__main__':
    root = tk.Tk()
    app = AddPackApp(root)
    root.mainloop()
