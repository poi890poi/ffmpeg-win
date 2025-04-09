import tkinter as tk
from tkinter import ttk, filedialog
import os
from layout import layout

# Refresh file metadata and update Property Viewer
def refresh_file_meta(file_path, active_page):
    if not file_path:
        return

    # Locate the Property Viewer table from the active page (recursive search)
    table = find_property_viewer_recursive(active_page)
    if table:
        # Extract file metadata
        file_size = os.path.getsize(file_path)  # Get file size in bytes
        modification_time = os.path.getmtime(file_path)  # Get modification time

        # Format metadata
        file_properties = {
            "File Name": os.path.basename(file_path),
            "File Size": f"{file_size} bytes",
            "Last Modified": f"{modification_time:.0f}"
        }

        # Clear previous entries
        for row in table.get_children():
            table.delete(row)

        # Add metadata to Property Viewer
        for key, value in file_properties.items():
            table.insert("", "end", values=(key, value))

# Recursive function to locate the Property Viewer table
def find_property_viewer_recursive(parent):
    for widget in parent.winfo_children():
        if isinstance(widget, ttk.Treeview):  # If it's the desired widget (Treeview)
            return widget
        # Recursively search in child widgets
        child_result = find_property_viewer_recursive(widget)
        if child_result:
            return child_result
    return None

# Create components dynamically
def create_file_selection(parent, label_text, refresh_func=None, active_page=None):
    frame = tk.Frame(parent)
    tk.Label(frame, text=label_text).pack(side="left")
    entry = tk.Entry(frame, width=40, state="readonly")
    entry.pack(side="left", padx=5)
    tk.Button(frame, text="Browse", command=lambda: browse_file(entry, refresh_func, active_page)).pack(side="left")
    frame.pack(fill="x", pady=5)
    return frame

def create_property_viewer(parent):
    frame = tk.Frame(parent)
    table = ttk.Treeview(frame, columns=("Key", "Value"), show="headings", height=8)
    table.heading("Key", text="Key")
    table.heading("Value", text="Value")
    table.pack(side="left", fill="x", expand=True)
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=table.yview)
    table.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    frame.pack(fill="x", pady=5)
    return frame

def browse_file(entry, refresh_func=None, active_page=None):
    file_path = filedialog.askopenfilename()
    if file_path:
        entry.config(state="normal")
        entry.delete(0, tk.END)
        entry.insert(0, file_path)
        entry.config(state="readonly")
        if refresh_func and active_page:
            refresh_func(file_path, active_page)

def display_tab_content(tab_frame, rows, active_page):
    for widget in tab_frame.winfo_children():
        widget.destroy()
    for row in rows:
        for component in row:
            if component.type == "file_selection":
                create_file_selection(tab_frame, component.label, refresh_func=refresh_file_meta, active_page=active_page)
            elif component.type == "property_viewer":
                create_property_viewer(tab_frame)

def switch_tab(tab_name, tab_frame):
    for tab in layout.tabs:
        if tab.name == tab_name:
            active_page = tab_frame  # Update the active page variable
            display_tab_content(tab_frame, tab.rows, active_page)
            break

# Main Application
root = tk.Tk()
root.title("Dynamic GUI with Pydantic Layout")
root.geometry("800x600")

# Left panel for navigation
left_panel = tk.Frame(root, width=150, bg="lightgray")
left_panel.pack(side="left", fill="y")

# Right panel for content
right_panel = tk.Frame(root, bg="white")
right_panel.pack(side="right", fill="both", expand=True)

# Variable to track the active page
active_page = right_panel

# Create buttons for switching tabs
for tab in layout.tabs:
    tk.Button(left_panel, text=tab.name, command=lambda t=tab.name: switch_tab(t, right_panel)).pack(pady=10)

# Display the first tab by default
switch_tab(layout.tabs[0].name, right_panel)

# Run the application
root.mainloop()
