"""
This holds all of the functionality for the menu bar options in the GUI
"""

import tkinter as tk
from tkinter import ttk, messagebox
try:
    import sv_ttk
except ImportError:
    messagebox.showerror("Error", "sv_ttk theme library not found.\nPlease install it: pip install sv-ttk")
    sv_ttk = None


# --- Theme Functions ---

def set_theme(app_instance):
    """
    Opens the theme selection window. Requires the main App instance.
    """
    if not app_instance:
        print("Error: set_theme called without App instance.")
        messagebox.showerror("Error", "Application context missing for theme setting.")
        return
    if not sv_ttk:
         messagebox.showwarning("Theme Warning", "sv_ttk library not available. Cannot change theme.")
         return


    theme_window = tk.Toplevel(app_instance)
    theme_window.geometry("300x200")
    theme_window.title("Set Theme")
    theme_window.transient(app_instance)  # Keep it on top
    theme_window.grab_set()  # Make it modal

    label = ttk.Label(theme_window, text="Select a theme:")
    label.pack(pady=10)

    # --- CRITICAL: Pass the app_instance to apply_theme via lambda ---
    dark_button = ttk.Button(theme_window, text="Dark Mode",
                             command=lambda: apply_theme("dark", app_instance, theme_window))
    dark_button.pack(pady=5)

    light_button = ttk.Button(theme_window, text="Light Mode",
                              command=lambda: apply_theme("light", app_instance, theme_window))
    light_button.pack(pady=5)

    close_button = ttk.Button(theme_window, text="Close", command=theme_window.destroy)
    close_button.pack(pady=10)

    # Center the popup window relative to the parent (app_instance)
    theme_window.update_idletasks() 
    parent_x = app_instance.winfo_x()
    parent_y = app_instance.winfo_y()
    parent_width = app_instance.winfo_width()
    parent_height = app_instance.winfo_height()
    win_width = theme_window.winfo_width()
    win_height = theme_window.winfo_height()
    x = parent_x + (parent_width // 2) - (win_width // 2)
    y = parent_y + (parent_height // 2) - (win_height // 2)
    theme_window.geometry(f'+{x}+{y}')


def apply_theme(theme, app, theme_window):
    """
    Applies the selected theme using sv_ttk and triggers UI updates in the App instance.

    :param theme: The theme to apply ("dark" or "light").
    :param app: The main App instance.
    :param theme_window: The Toplevel window for theme selection (to close it).
    """
  #  print(f"Applying theme: {theme} to App: {app}") # Debug print
    if not sv_ttk:
        print("sv_ttk not available.")
        theme_window.destroy()
        return
    if not app:
        print("Error: apply_theme called without App instance.")
        messagebox.showerror("Internal Error", "Application context lost.")
        theme_window.destroy()
        return

    try:
        # 1. Apply the sv_ttk theme (affects ttk widgets)
        sv_ttk.set_theme(theme)

        # 2. Update the application's ColorPalette mode
        if hasattr(app, 'colors') and hasattr(app.colors, 'set_mode'):
            app.colors.set_mode(theme)
        else:
             print("Error: App instance or color palette not set up correctly.")
             messagebox.showerror("Theme Error", "Could not update color palette.")
             theme_window.destroy()
             return

        # 3. Trigger the UI update method within the App instance
        if hasattr(app, 'update_ui_colors'):
            app.update_ui_colors()
        else:
             print("Error: App instance does not have update_ui_colors method.")
             messagebox.showerror("Theme Error", "Could not trigger UI update.")

        # 4. Close the theme selection window
        theme_window.destroy()

    except Exception as e:
        messagebox.showerror("Theme Error", f"Failed to apply theme: {e}")
        print(f"Error applying theme: {e}")
        if theme_window.winfo_exists():
            theme_window.destroy()


# -- About --
def about_the_app():
    """
    Displays information about the application including 
    the version and the author
    """
    messagebox.showinfo("About STAT", "Statistical Tracking and Analysis Toolkit\nVersion 1.0\nAuthor: Group 6 <3")

# -- Help 
def show_help():
    """
    includes a link to documention 
    and the command keys for the app
    """
    # pop up window with help information
    help_window = tk.Toplevel()
    help_window.title("Help")
    help_window.geometry("400x300")
    help_window.transient()  # Keep it on top
    help_window.grab_set()  # Make it modal

    help_label = ttk.Label(help_window, text="Help Information")
    help_label.pack(pady=10)
    # add the help text within the help window
    help_text = (
        "Documentation: https://github.com/sarahibsen/CS499\n\n"
        "Command Keys:\n"
        "Ctrl + C: Quit Application\n"
        "Esc: Quit application\n"
    )
    help_text_widget = tk.Text(help_window, wrap=tk.WORD, height=10)
    help_text_widget.insert(tk.END, help_text)
    help_text_widget.config(state=tk.DISABLED)  # Make it read-only
    help_text_widget.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
    