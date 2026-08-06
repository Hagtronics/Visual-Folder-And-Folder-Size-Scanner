"""
A useful(?) utility for examining what folders / directories on a disk are taking up space.
Written in Pure Python 3.12+ with the only dependency being ttkbootstrap
for a prettier GUI experience.
Source,
https://github.com/Hagtronics/Visual-Folder-And-Folder-Size-Scanner

Written 5Aug26 - Absolute Freeware (See the: Unlicense)
https://github.com/Hagtronics/Visual-Folder-And-Folder-Size-Scanner?tab=Unlicense-1-ov-file

"""
import csv
import ctypes
import os
import tkinter as tk
from pathlib import Path
from tkinter import END, filedialog, ttk

import ttkbootstrap as tb

# Initial Window Geometry (Scaled in __main__)
WIN_WIDTH = 570
WIN_HEIGHT = 800
WIN_SF = 100


#$ ===== Helper functions =====
def set_dpi_awareness()->int:
    """
    Set the apps DPI awareness (if possible) - This works for Windows only
    Must be run before any windows are spawned.
    If Win 10 or 11, returns the current text scale factor. Else returns 100
    """
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2) # '2' scales across all windows.
        # print("Info: DPI Awareness set for Win 8.1, 10 or 11.")

        # Returns: 100, 125, 150, etc. Can be used later to help resize windows, etc.
        win_sf = ctypes.windll.shcore.GetScaleFactorForDevice(0)
        # print(f'Info: Current Text Scale Factor = {win_sf}.')
        return win_sf
    except:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
            return 100
            # print("info: DPI set for Win 7, 8")
        except:
            print('Info: DPI Awareness could not be set!')
            return 100


def get_directory_sizes(root: Path) -> tuple[list[Path], dict[Path, int]]:
    sizes: dict[Path, int] = {}
    order: list[Path] = []

    def walk(path: Path) -> int:
        order.append(path)

        total = 0

        try:
            with os.scandir(path) as it:
                entries = sorted(it, key=lambda e: e.name.lower())

            for entry in entries:
                try:
                    if entry.is_symlink():
                        continue

                    if entry.is_file(follow_symlinks=False):
                        total += entry.stat(follow_symlinks=False).st_size

                    elif entry.is_dir(follow_symlinks=False):
                        total += walk(Path(entry.path))

                except (PermissionError, FileNotFoundError, OSError):
                    pass

        except (PermissionError, FileNotFoundError, OSError):
            pass

        sizes[path] = total
        return total

    walk(root)
    return order, sizes


def format_size(size: int) -> str:
    if size == 0:
        return '0 bytes'

    units = [
        ('TB', 1 << 40),
        ('GB', 1 << 30),
        ('MB', 1 << 20),
        ('KB', 1 << 10),
        ('bytes', 1),
    ]

    for suffix, factor in units:
        if size >= factor:
            value = size / factor
            return f'{value:.3g} {suffix}'

    return '0 bytes   '


def parse_size(size_str: str) -> int:
    parts = size_str.split()
    if len(parts) != 2:
        return 0

    value, suffix = parts
    value = float(value)

    factors = {
        'bytes': 1,
        'KB': 1 << 10,
        'MB': 1 << 20,
        'GB': 1 << 30,
        'TB': 1 << 40,
    }

    return int(value * factors.get(suffix, 1))


#$ ===== Main Application Class =====
class DirectorySizeApp:

    def __init__(self):
        self.root = tb.Window(themename='bootstrap-light')

        self.root.title('Folder Size Viewer')
        self.root.geometry(str(WIN_WIDTH) + 'x' + str(WIN_HEIGHT))
        self.root.minsize(640, 480)
        self.root.position_center()

        self.original_data = [["No folder selected yet...", "0     "]]
        self.sort_states = {'path': False, 'size': False}

        self.style = self.root.style
        self.style.configure('Toolbar.TFrame', background='#e0e0e0')

        self.build_toolbar()
        self.build_treeview()
        self.build_context_menu()


    # Data loading
    def scan_directories(self, root: Path):
        order, sizes = get_directory_sizes(root)

        return [
            [str(path), format_size(sizes[path])]
            for path in order
        ]

    # UI Construction
    def build_toolbar(self):
        toolbar = ttk.Frame(self.root, padding=5) #, style='Toolbar.TFrame')
        toolbar.pack(fill='x')

        ttk.Button(toolbar, text='Select Folder', command=self.choose_folder).pack(side='left', padx=10)
        ttk.Button(toolbar, text='Toggle Theme', command=self.toggle_theme).pack(side='left', padx=10)
        ttk.Button(toolbar, text='Reset Sort', command=self.reset_table).pack(side='left', padx=10)
        ttk.Button(toolbar, text='Save to CSV', command=self.save_to_csv).pack(side='left', padx=10)
        ttk.Separator(toolbar, orient='vertical').pack(side='left', fill='y', padx=10)
        ttk.Button(toolbar, text='Exit', command=self.root.destroy).pack(side='left', padx=10)

    def build_treeview(self):
        frame = ttk.Frame(self.root)
        frame.pack(fill='both', expand=True, padx=10, pady=10)

        columns = ('path', 'size')
        self.tree = tb.Treeview(frame, bootstyle='primary', columns=columns, show='headings')

        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')

        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        self.tree.heading('path', text='Path ⇅', command=lambda: self.sort_by_column('path'))
        self.tree.heading('size', text='Size ⇅', command=lambda: self.sort_by_column('size'))

        self.tree.column('path', width=500, anchor='w')
        self.tree.column('size', width=50, minwidth=50, anchor='e')

        self.reload_tree(self.original_data)

    def build_context_menu(self):
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label='Copy Row', command=self.copy_row)
        self.menu.add_command(label='Copy Path', command=lambda: self.copy_cell(0))
        self.menu.add_command(label='Copy Size', command=lambda: self.copy_cell(1))
        self.menu.add_command(label='Copy Full Path', command=self.copy_full_path)
        self.menu.add_command(label='Open Folder', command=self.open_folder)

        self.tree.bind('<Button-3>', self.show_context_menu)


    # Treeview operations
    def reload_tree(self, data):
        self.tree.delete(*self.tree.get_children())

        # Configure row styles (theme‑aware)
        style = tb.Style()
        style.configure("Treeview", rowheight=24)

        # Add themed colors
        current = self.root.style.theme.name
        if 'dark' in current:
            self.tree.tag_configure("oddrow", background="#363636")
            self.tree.tag_configure("evenrow", background="#1e1e1e")
        else:
            self.tree.tag_configure("oddrow", background="#e5e5e5")
            self.tree.tag_configure("evenrow", background="#ffffff")

        # Now odd/even color the rows.
        for index, row in enumerate(data):
            display_row = list(row)
            display_row[1] = display_row[1] + "\u2009"   # Add thin space to right edge of Size Column

            tag = "oddrow" if index % 2 else "evenrow"
            self.tree.insert("", END, values=display_row, tags=(tag,))

        # Force a repaint
        self.tree.update()


    def sort_by_column(self, col):
        reverse = self.sort_states[col]
        self.sort_states[col] = not reverse

        if col == 'path':
            sorted_data = sorted(self.original_data, key=lambda x: x[0], reverse=reverse)
        else:
            sorted_data = sorted(self.original_data, key=lambda x: parse_size(x[1]), reverse=reverse)

        self.reload_tree(sorted_data)

        arrow = ' ▲' if not reverse else ' ▼'
        for c in ('path', 'size'):
            label = c.capitalize()
            self.tree.heading(c, text=label + arrow if c == col else label)


    def reset_table(self):
        self.reload_tree(self.original_data)
        self.tree.heading('path', text='Path ⇅')
        self.tree.heading('size', text='Size ⇅')
        self.sort_states = {'path': False, 'size': False}


    # Toolbar actions
    def choose_folder(self):
        folder = filedialog.askdirectory(title='Choose a folder')
        if folder:
            self.start_path = Path(folder)
            self.original_data = [["Working - Please Be Patient...", "0     "]]
            self.reset_table()
            self.original_data = self.scan_directories(self.start_path)
            self.reset_table()


    def toggle_theme(self):
        """ Note: The theme colors for the treeview are also changed in reload_tree() """
        current = self.root.style.theme.name
        if 'dark' in current:
            self.root.style.theme_use('bootstrap-light')
            self.style.configure('Toolbar.TFrame', background='#e0e0e0')
        else:
            self.root.style.theme_use('bootstrap-dark')
            self.style.configure('Toolbar.TFrame', background='#202020')

        self.reload_tree(self.original_data)


    def save_to_csv(self) -> None:
        # Ask user for filename
        filename = filedialog.asksaveasfilename(
        parent=self.root,
        title="Save CSV File",
        defaultextension=".csv",
        filetypes=[("CSV", "*.csv"), ("All", "*.*")]
        )

        # User pressed cancel
        if not filename:
            return

        # Ensure correct extension
        _, ext = os.path.splitext(filename)
        if not ext:
            # If no extension was typed, default to .csv
            filename = filename + ".csv"

        headers = ["Path", "Size"]

        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(self.original_data)

        return


    # Context menu actions
    def show_context_menu(self, event):
        row_id = self.tree.identify_row(event.y)
        if row_id:
            self.tree.selection_set(row_id)
            self.menu.tk_popup(event.x_root, event.y_root)

    def copy_row(self):
        sel = self.tree.selection()
        if sel:
            values = self.tree.item(sel[0], 'values')
            self.root.clipboard_clear()
            self.root.clipboard_append('\t'.join(values))

    def copy_cell(self, col_index):
        sel = self.tree.selection()
        if sel:
            values = self.tree.item(sel[0], 'values')
            self.root.clipboard_clear()
            self.root.clipboard_append(values[col_index])

    def copy_full_path(self):
        sel = self.tree.selection()
        if sel:
            full_path = self.tree.item(sel[0], 'values')[0]
            self.root.clipboard_clear()
            self.root.clipboard_append(full_path)

    def open_folder(self):
        sel = self.tree.selection()
        if sel:
            full_path = self.tree.item(sel[0], 'values')[0]
            try:
                os.startfile(full_path)
            except Exception as e:
                print('Error opening folder:', e)


    # Main loop
    def run(self):
        self.root.mainloop()


#$ ===== Program Start =====
if __name__ == '__main__':

    # Scale app for DPI if possible
    WIN_SF = set_dpi_awareness()
    if WIN_SF == 125:
        WIN_WIDTH = 690
    elif WIN_SF == 150:
        WIN_WIDTH = 790

    app = DirectorySizeApp()
    app.run()

# Fini
