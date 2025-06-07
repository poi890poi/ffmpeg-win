import sys

import tkinter as tk
from tkinter import ttk, filedialog
from tkinter import messagebox

from layout import layout
import impl
from util import *


logger = get_logger("ffmpeg-win")
sys.stdout = LoggerWriter(logger)

active_page = None  # Tracks the currently active tab

class CustomFrame(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.active_page = None  # Track the active page (e.g., tab content)

    # Callback to show overwrite confirmation dialog
    def ask_user_for_overwrite(self, file_name):
        return messagebox.askyesno(
            "File Overwrite Confirmation",
            f"The file '{file_name}' already exists.\nDo you want to overwrite it?"
        )

    def find_progress_bar(self):
        # Iterate through all child widgets of the parent
        for widget in self.winfo_children():
            print(widget.winfo_name())
            # Check if the widget is a Progress Bar
            if isinstance(widget, ttk.Progressbar):
                return widget
            # Recursively search in child widgets
            if isinstance(widget, CustomFrame):
                result = widget.find_progress_bar()
                if result:
                    return result
        return None  # Return None if Progress Bar is not found

    def find_widget(self, name):
        # Iterate through all child widgets of the parent
        for widget in self.winfo_children():
            if widget.winfo_name() == name:
                return widget
            # Recursively search in child widgets
            if isinstance(widget, CustomFrame):
                result = widget.find_widget(name)
                if result:
                    return result
        return None  # Return None if Progress Bar is not found

    def set_entry(self, name, text):
        print(name, text)
        entry = self.find_widget(name)
        entry.configure(state="normal") 
        entry.delete(0, tk.END)
        entry.insert(0, text)
        entry.configure(state="readonly") 

# Function to close the window
def close_window(event=None):
    print("Escape key pressed. Closing window...")
    root.destroy()

# Helper functions
def find_component_recursive(parent, component_type):
    for widget in parent.winfo_children():
        if isinstance(widget, component_type):
            return widget
        child_result = find_component_recursive(widget, component_type)
        if child_result:
            return child_result
    return None

def find_components_recursive(parent, component_type):
    components = []
    for widget in parent.winfo_children():
        if isinstance(widget, component_type):
            components.append(widget)
        components.extend(find_components_recursive(widget, component_type))
    return components

# Refresh file metadata and update Property Viewer
def refresh_file_meta(file_path, active_page):
    try:
        table = find_component_recursive(active_page, ttk.Treeview)
        if table is not None:
            file_properties = get_file_properties(file_path)
            if file_properties:
                # Clear existing entries
                for row in table.get_children():
                    table.delete(row)
                # Insert new file properties into the table
                for key, value in file_properties.items():
                    table.insert("", "end", values=(key, value))
    except Exception as e:
        print(f"Error in refresh_file_meta: {e}")

def start(active_page, action_callback):
    try:
        input_values = {}
        input_fields = find_components_recursive(active_page, tk.Entry)
        dropdowns = find_components_recursive(active_page, ttk.Combobox)

        for field in input_fields:
            print(field)
            try:
                label = field.master.winfo_children()[0].cget("text")  # Label associated with input
                input_values[label] = field.get()
            except tk.TclError:
                ...

        for dropdown in dropdowns:
            print(dropdown)
            try:
                label = dropdown.master.winfo_children()[0].cget("text")  # Label associated with dropdown
                input_values[label] = dropdown.get()
            except tk.TclError:
                ...

        print(f"Input Values: {input_values}")
        action_callback(input_values, active_page)
    except Exception as e:
        print(f"Error in start: {e}")

# Component creation functions
def create_file_selection(parent, label, refresh_func=None):
    frame = CustomFrame(parent)
    tk.Label(frame, text=label).pack(side="left")
    entry = tk.Entry(frame, width=40, state="readonly")
    entry.pack(side="left", padx=5)
    tk.Button(frame, text="Browse", command=lambda: browse_file(
        entry, refresh_func)).pack(side="left")
    frame.pack(fill="x", pady=5)

def create_property_viewer(parent):
    frame = CustomFrame(parent)
    table = ttk.Treeview(frame, columns=("Key", "Value"),
                         show="headings", height=8)
    table.heading("Key", text="Key")
    table.heading("Value", text="Value")
    table.pack(side="left", fill="x", expand=True)
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=table.yview)
    table.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    frame.pack(fill="x", pady=5)

def create_time_input(parent, component):
    label_text = component.label
    default = component.default
    frame = CustomFrame(parent)
    tk.Label(frame, text=label_text).pack(side="left")
    input_entry = tk.Entry(frame, width=10)
    input_entry.pack(side="left", padx=5)
    frame.pack(fill="x", pady=5)
    if default is not None:
        input_entry.insert(0, default)  # Default value

def create_text_input(parent, component):
    label_text = component.label
    default = component.default
    frame = CustomFrame(parent)
    tk.Label(frame, text=label_text).pack(side="left")
    input_entry = tk.Entry(frame, width=10)
    input_entry.pack(side="left", padx=5)
    frame.pack(fill="x", pady=5)
    if default is not None:
        input_entry.insert(0, default)  # Default value

def create_button(parent, component):
    button_text = component.label
    frame = CustomFrame(parent)
    callback = None
    print(active_tab.name, ("Loop Video" in active_tab.name))
    callback = getattr(impl, active_tab.callback)
    # if "Loop Video" in active_tab.name:
    #     callback = loop_video
    # elif "Trim Audio" in active_tab.name:
    #     callback = trim_audio
    # elif "Combine A&V" in active_tab.name:
    #     callback = combine_audio_video
    tk.Button(frame, text=button_text, command=lambda: start(
        active_page, callback)).pack()
    frame.pack(fill="x", pady=5)
    root.bind("<Return>", lambda event: start(active_page, callback))

def create_options(parent, component):
    label_text = component.label
    options = component.options
    default = component.default
    frame = CustomFrame(parent)
    tk.Label(frame, text=label_text).pack(side="left")
    combo_box = ttk.Combobox(frame, values=options)
    combo_box.pack(side="left", padx=5)
    frame.pack(fill="x", pady=5)
    if default is not None:
        combo_box.set(default)  # Default value

def create_progress_bar(parent, component):
    label = component.label
    print('create_progress_bar', label)
    frame = CustomFrame(parent)
    progress = ttk.Progressbar(frame, length=200)
    progress.pack(side="left")
    tk.Entry(frame, width=60, name="progress_text", state="readonly").pack(
        side="left", padx=5)
    frame.pack(fill="x", pady=5)

def browse_file(entry, refresh_func=None):
    try:
        file_path = filedialog.askopenfilename()
        if file_path:
            entry.config(state="normal")
            entry.delete(0, "end")
            entry.insert(0, file_path)
            entry.config(state="readonly")
            if refresh_func and active_page:
                refresh_func(file_path, active_page)
    except Exception as e:
        print(f"Error in browse_file: {e}")

def display_tab_content(tab_frame, rows):
    for widget in tab_frame.winfo_children():
        widget.destroy()
    for row in rows:
        for component in row:
            if component.type == "file_selection":
                create_file_selection(tab_frame, component.label,
                                      refresh_file_meta)
            elif component.type == "time_input":
                create_time_input(tab_frame, component)
            elif component.type == "text_input":
                create_text_input(tab_frame, component)
            elif component.type == "button":
                create_button(tab_frame, component)
            elif component.type == "options":
                create_options(tab_frame, component)
            elif component.type == "property_viewer":
                create_property_viewer(tab_frame)
            elif component.type == "progress_bar":
                create_progress_bar(tab_frame, component)

def switch_tab(tab_name, tab_frame):
    global active_page
    global active_tab
    for tab in layout.tabs:
        if tab.name == tab_name:
            active_tab = tab
            active_page = tab_frame
            display_tab_content(tab_frame, tab.rows)
            break

# Main Application
root = tk.Tk()
root.title("FFMPEG for the Win")
root.geometry("800x600")
root.bind("<Escape>", close_window)

# Left and right panels
left_panel = CustomFrame(root, width=150, bg="lightgray")
left_panel.pack(side="left", fill="y")
right_panel = CustomFrame(root, bg="white")
right_panel.pack(side="right", fill="both", expand=True)

# Tab buttons
for tab in layout.tabs:
    tk.Button(left_panel, text=tab.name, command=lambda t=tab.name:
              switch_tab(t, right_panel)).pack(pady=10)

# Show first tab by default
switch_tab(layout.tabs[0].name, right_panel)

root.mainloop()
