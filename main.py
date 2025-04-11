import tkinter as tk
from tkinter import ttk, filedialog
from tkinter import messagebox
from layout import layout
from impl import get_file_properties, trim_audio, loop_video, combine_audio_video

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
            # Check if the widget is a Progress Bar
            if isinstance(widget, ttk.Progressbar):
                return widget
            # Recursively search in child widgets
            if isinstance(widget, CustomFrame):
                result = widget.find_progress_bar()
                if result:
                    return result
        return None  # Return None if Progress Bar is not found

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
            label = field.master.winfo_children()[0].cget("text")  # Label associated with input
            input_values[label] = field.get()

        for dropdown in dropdowns:
            label = dropdown.master.winfo_children()[0].cget("text")  # Label associated with dropdown
            input_values[label] = dropdown.get()

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
    tk.Button(frame, text="Browse", command=lambda: browse_file(entry, refresh_func)).pack(side="left")
    frame.pack(fill="x", pady=5)

def create_property_viewer(parent):
    frame = CustomFrame(parent)
    table = ttk.Treeview(frame, columns=("Key", "Value"), show="headings", height=8)
    table.heading("Key", text="Key")
    table.heading("Value", text="Value")
    table.pack(side="left", fill="x", expand=True)
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=table.yview)
    table.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    frame.pack(fill="x", pady=5)

def create_time_input(parent, label_text):
    frame = CustomFrame(parent)
    tk.Label(frame, text=label_text).pack(side="left")
    tk.Entry(frame, width=10).pack(side="left", padx=5)
    frame.pack(fill="x", pady=5)

def create_progress_bar(parent, label, callback):
    frame = CustomFrame(parent)
    tk.Label(frame, text=label).pack(side="top")
    progress = ttk.Progressbar(frame, length=200)
    progress.pack(pady=5)
    tk.Button(frame, text="Start", command=lambda: start(active_page, callback)).pack()
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
                create_file_selection(tab_frame, component.label, refresh_file_meta)
            elif component.type == "time_input":
                create_time_input(tab_frame, component.label)
            elif component.type == "property_viewer":
                create_property_viewer(tab_frame)
            elif component.type == "progress_bar":
                if "Trimming" in component.label:
                    create_progress_bar(tab_frame, component.label, trim_audio)
                elif "Looping" in component.label:
                    create_progress_bar(tab_frame, component.label, loop_video)
                elif "Combining" in component.label:
                    create_progress_bar(tab_frame, component.label, combine_audio_video)

def switch_tab(tab_name, tab_frame):
    global active_page
    for tab in layout.tabs:
        if tab.name == tab_name:
            active_page = tab_frame
            display_tab_content(tab_frame, tab.rows)
            break

# Main Application
root = tk.Tk()
root.title("Dynamic GUI Application")
root.geometry("800x600")

# Left and right panels
left_panel = CustomFrame(root, width=150, bg="lightgray")
left_panel.pack(side="left", fill="y")
right_panel = CustomFrame(root, bg="white")
right_panel.pack(side="right", fill="both", expand=True)

# Tab buttons
for tab in layout.tabs:
    tk.Button(left_panel, text=tab.name, command=lambda t=tab.name: switch_tab(t, right_panel)).pack(pady=10)

# Show first tab by default
switch_tab(layout.tabs[0].name, right_panel)

root.mainloop()
