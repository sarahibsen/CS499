import tkinter as tk
from tkinter import *
from tkinter import Canvas, Button, PhotoImage, filedialog, ttk, messagebox, Label, simpledialog
from tkinter.ttk import Button, Style
import scipy.stats as stats
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import seaborn as sns
from PIL import Image, ImageTk
from Table import TableView
from colors import ColorPalette
from statisticsLogic import statistic

# using the controller class to handle the communication between all components
from main_controller import Controller
import pathlib
import os
import sys
from menu_functions import set_theme, about_the_app, show_help


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # In development or --onedir mode, use the script's directory
        # Use pathlib to ensure the path is absolute and correct
        base_path = pathlib.Path(__file__).parent.absolute()
        # If assets are relative to the *project root* instead of the script file, adjust:
        # base_path = pathlib.Path('.').absolute() 

    return os.path.join(base_path, relative_path)

# ----- Supplementary Functions ----- #
def relative_to_assets(path: str) -> Path:
    """
    Get the full path to a resource file located in the assets directory.
    """
    assets_path = Path(__file__).parent / Path(
        r"assets"

    )
    return assets_path / Path(path)


def add_button(canvas, x, y, w, h, normal_image, hover_image, message, callback=None):
    """
    Add a button with hover effects to the canvas using ttk.Button.
    Args:
        canvas (Canvas): The canvas to add the button to.
        x (float): X-coordinate for button placement.
        y (float): Y-coordinate for button placement.
        w (float): Width for button.
        h (float): Height for button.
        normal_image (str): Path to the normal state button image.
        hover_image (str): Path to the hover state button image.
        message (str): Message to print on button click.
        callback (function): Optional function to execute on button click.
    """
    normal_image_file = PhotoImage(file=relative_to_assets(normal_image))
    hover_image_file = PhotoImage(file=relative_to_assets(hover_image))

    def button_command():
        print(message)
        if callback:
            callback()

    button = ttk.Button(
        canvas,
        image=normal_image_file,
        command=button_command,  # Use the defined command
        style="TButton"  # Use TButton style to manage button appearance
    )

    button.place(x=x, y=y, width=w, height=h)
    button.image = normal_image_file  # Keep reference to avoid garbage collection

    def on_hover(event):
        button.config(image=hover_image_file)

    def on_leave(event):
        button.config(image=normal_image_file)

    button.bind('<Enter>', on_hover)
    button.bind('<Leave>', on_leave)

    return button


class App(tk.Tk):
    """
    Main application class to handle multiple pages.
    """

    def __init__(self):
        super().__init__()

        # Default mode is light
        self.colors = ColorPalette(mode="light")

        # Configure window
        self.configure(bg=self.colors.get_color("background"))
        self.title("STAT")

        # Bind Escape key to close the application
        self.bind("<Escape>", lambda event: self.quit())

        # --- Creation of the menu bar here ---
        menubar = Menu(self)
        self.config(menu=menubar) # Assign the menu to the window

        # File Menu
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.quit) # Use self.quit 
        menubar.add_cascade(label="File", menu=filemenu) # Add the cascade to the menubar
        # Help Menu
        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command= about_the_app) 
        helpmenu.add_command(label = "Help", command = show_help)
        menubar.add_cascade(label="Help", menu=helpmenu)
        viewmenu = Menu(menubar, tearoff=0)
        viewmenu.add_command(label="Set Theme",
                            command=lambda: set_theme(self)) 
        menubar.add_cascade(label="View", menu=viewmenu)
        #----
        # Create a container to hold pages
        self.container = tk.Frame(self, bg="white")
        self.container.grid(row=0, column=0, sticky="nsew")

        # Allow container to expand
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Dictionary to store pages
        self.pages = {}

        # Initialize pages
        for page_name, page_class in [
            ("LaunchPage", LaunchPage),
            ("MeasureSelectionPage", MeasureSelectionPage),
            ("DashboardPage", DashboardPage),
            ("ResultsPage", ResultsPage)
        ]:
            self.add_page(page_name, page_class)

        # Show the initial page
        self.show_page("LaunchPage")

    def add_page(self, page_name, page_class):
        """Add a new page to the application."""
        page = page_class(self.container, self)
        self.pages[page_name] = page
        page.grid(row=0, column=0, sticky="nsew")

    def show_page(self, page_name):
        """Display the specified page."""
        page = self.pages.get(page_name)
        if page:
            page.tkraise()

    def get_page(self, page_name):
        """Retrieves the stored instance of a page."""
        return self.pages.get(page_name)

    # --- This method is called by menu_functions to make sure that the theme is applied to the whole application ---
    def update_ui_colors(self):
        """Updates colors for the main window and all pages."""
        print("App updating UI colors...")
        new_bg = self.colors.get_color("background")
        self.configure(bg=new_bg)
        if hasattr(self, 'container') and self.container.winfo_exists():
            self.container.configure(bg=new_bg)

        for page_name, page in self.pages.items():
             # Check if page exists and has the update method
            if page and hasattr(page, 'update_colors') and callable(page.update_colors):
                try:
                     page.update_colors()
                except Exception as e:
                     print(f"Error updating colors for page {page_name}: {e}")
            else:
                 print(f"Warning: Page {page_name} ({type(page).__name__}) has no update_colors method or doesn't exist.")
        print("App finished updating UI colors.")

class BasePage(tk.Frame):
    """Base class for all pages."""

    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller
    def update_colors(self):
        """Updates the background of the base page frame."""
        # Check if controller and colors exist
        if hasattr(self.controller, 'colors'):
            new_bg = self.controller.colors.get_color("background")
            try:
                self.configure(bg=new_bg)
            except tk.TclError as e:
                print(f"Error configuring BasePage background for {type(self).__name__}: {e}")
        else:
            print(f"Warning: Cannot update colors for {type(self).__name__}, controller or colors missing.")

class LaunchPage(BasePage):
    """Start page of the application."""

    def __init__(self, parent, controller):
        super().__init__(parent, controller)


        # ----- Initialize colors ----- #
        background_color = controller.colors.get_color("background")
        primary_color = controller.colors.get_color("primary")
        text_color = controller.colors.get_color("text")
        button_hover = controller.colors.get_color("button_hover")
        button_text = controller.colors.get_color("button_text")

        # Set the background color of the window
        self.configure(bg=background_color)

        # ----- Configure grid, canvas, and frames ----- #
        # Configure row weights
        for i in range(7):
            self.rowconfigure(i, weight=1)

        # Configure column weights
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Button style
        style = Style()
        style.configure(
            "TButton", font=("Arial", 20), background=primary_color, height=50,
            width=20, pady=20, ipadx=20, ipady=10, relief="groove",
        )

        # ----- Image Area ----- #
        image = resource_path("assets/features.png")
        pil_image = Image.open(image)
        photo = ImageTk.PhotoImage(pil_image)
        self.image_label = Label(self, image=photo, bg=background_color, fg=text_color, bd=0, highlightthickness=0)
        self.image_label.image = photo  # keep a reference
        self.image_label.grid(column=1, rowspan=7, sticky="nsew", padx=20, pady=20)

        # self.canvas = Canvas(self, bg="lightblue", bd=0, highlightthickness=0, relief="ridge")
        # self.canvas.grid(column=1, rowspan=7, sticky="nsew", padx=20, pady=20)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)

        # ----- Text Area ----- #
        tk.Label(self, text="STAT", bg=background_color, fg=text_color,  font=("Arial", 40)).grid(column=0, row=1, sticky="nsew")
        tk.Label(self, text="Statistical Tracking and \n Analysis Toolkit", bg=background_color, fg=text_color,
                 font=("Arial", 25)).grid(column=0, row=2, sticky="nsew")
        # Continue Button
        Button(self, text="Start", style="TButton",
               command=lambda: controller.show_page("MeasureSelectionPage")).grid(column=0, row=5)


class MeasureSelectionPage(BasePage):
    """
    Measure selection page of the application. Users will select what statistical measures
    they want to perform on the dataset.

    """

    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.gui_controller = controller
        self.selected_stats = []  # Store selected measures

        # ----- Configure grid, canvas, and frames ----- #
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)  # Toolbar column
        self.grid_columnconfigure(2, weight=2)

        self.measurement_frame = tk.Frame(self, bg="#FFFFFF")
        self.measurement_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nw")

        # Button style
        style = Style()
        style.configure(
            "TButton", font=("Arial", 20), background="white", height=50,
            width=20, pady=20, ipadx=20, ipady=10, relief="groove",
        )

        # ----- Toolbar ----- #
        # Create a canvas to hold toolbar
        self.canvas = Canvas(self, bg="#FFFFFF", bd=0, highlightthickness=0, relief="ridge")
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.toolbarBackground = self.canvas.create_rectangle(0, 0, 100, self.winfo_height(), fill="#D9D9D9",
                                                              outline="")
        self.canvas.bind("<Configure>", self.resize_toolbar)  # Bind the resize event

        self.data_page_button = add_button(
            self.canvas, 18, 50, 63, 63, "button_4.png", "button_hover_4.png",
            "Data page button clicked!"
        )
        self.data_page_button.grid(row=0, column=0, padx=10, pady=10, sticky="ns")

        self.dashboard_page_button = add_button(
            self.canvas, 18, 163, 63, 63, "button_5.png", "button_hover_5.png",
            "Dashboard page button clicked!", lambda: controller.show_page("ResultsPage")
        )
        self.dashboard_page_button.grid(row=1, column=0, padx=10, pady=10, sticky="ns")

        self.update_colors()
        
        # ----- Data Table ----- #
        self.table_frame = tk.Frame(self)

        self.table_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)

        self.table = TableView(self.table_frame)
        self.table.grid(row=0, column=0, sticky='nsew')

        # ----- Measure Selection Area ----- #
        # Calculate Meaasures Button
        self.calculate_button = Button(self.measurement_frame, text="Calculate Measures", style="TButton",
               command=self.calculate_statistics)
        self.calculate_button.grid(row=4, column=1, padx=10, pady=10, sticky='w')

        ## TODO: change this to grab data types from main.py
        # ComboBox for Data Types
        self.data_type_options = ["Nominal", "Ordinal", "Discrete", "Continuous"]
        self.data_type_dropdown = ttk.Combobox(self.measurement_frame, values=self.data_type_options,
                                               font=("Roboto", 14), state="readonly")
        self.data_type_dropdown.grid(row=1, column=1, padx=10, pady=10, sticky='nw')
        self.data_type_dropdown.set("Select Data Type")
        self.data_type_dropdown.bind("<<ComboboxSelected>>", self.on_data_type_selected)

        # Statistical Measures Listbox
        self.stat_measures_listbox = tk.Listbox(self.measurement_frame, font=("Roboto", 14), selectmode="multiple",
                                                exportselection=False)

        # self.stat_measures_listbox.place(x=151, y=380, width=351, height=100)
        self.stat_measures_listbox.grid(row=2, column=1, padx=10, pady=10, sticky='nw')

        # Label to show selected measures
        self.selected_stat_label = tk.Label(
            self.measurement_frame,
            text="Selected: None",
            font=("Roboto", 12), 
            # REMOVED: bg="#FFFFFF", 
            wraplength=300,
            justify="left",
            anchor="nw"
        )
        # self.selected_stat_label.place(x=151, y=500, width=351, height=50)
        self.selected_stat_label.grid(row=3, column=1, padx=10, pady=10, sticky='nw')

        # Bind listbox selection
        self.stat_measures_listbox.bind("<<ListboxSelect>>", self.on_stat_measure_selected)

    def resize_toolbar(self, event):
        """Resize the rectangle dynamically when the window changes size."""
        self.canvas.coords(self.toolbarBackground, 0, 0, 100, event.height)  # Adjust height dynamically

    def resize_elements(self, event):
        """
        Adjust measurement frame dynamically to fill the remaining canvas area.
        """
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # Ensure canvas has a valid width before setting
        if canvas_width > 100:
            new_width = canvas_width - 100
        else:
            new_width = 0  # Prevent negative width

        # Update the window inside the canvas
        self.canvas.coords(self.measurement_window, 100, 0)  # Ensure it starts at (100,0)
        self.canvas.itemconfig(self.measurement_window, width=new_width, height=canvas_height)
    def update_colors(self):
        """Updates colors for non-ttk widgets and specific configurations."""
        # If BasePage only sets its own bg, call it:
        if hasattr(super(), 'update_colors'):
             super().update_colors()

        # Check if controller and colors palette exist
        if not (hasattr(self.controller, 'colors') and self.controller.colors):
            print(f"Warning: Cannot update colors for {type(self).__name__}, controller or colors missing.")
            return

        # Get colors from the central palette
        background_color = self.controller.colors.get_color("background")
        text_color = self.controller.colors.get_color("text")
        toolbar_bg_color = self.controller.colors.get_color("toolbar_bg")


        # Update Frames 
        if hasattr(self, 'toolbar_frame'): self.toolbar_frame.configure(bg=toolbar_bg_color)
        if hasattr(self, 'measurement_frame'): self.measurement_frame.configure(bg=background_color)
        if hasattr(self, 'table_frame'): self.table_frame.configure(bg=background_color)
        if hasattr(self, 'stat_measures_listbox'):
             listbox_parent = self.stat_measures_listbox.master
             if isinstance(listbox_parent, tk.Frame):
                 listbox_parent.configure(bg=background_color) # Match measurement frame bg


        if hasattr(self, 'label_data_type'): self.label_data_type.configure(bg=background_color, fg=text_color)
        if hasattr(self, 'label_measures'): self.label_measures.configure(bg=background_color, fg=text_color)
        if hasattr(self, 'label_selected'): self.label_selected.configure(bg=background_color, fg=text_color)

        if hasattr(self, 'selected_stat_label') and self.selected_stat_label.winfo_exists():
            self.selected_stat_label.configure(bg=background_color, fg=text_color)

        if hasattr(self, 'table') and hasattr(self.table, 'update_theme') and callable(self.table.update_theme):
            self.table.update_theme(self.controller.colors)

    # def import_csv(self):
    #     file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    #     if file_path:
    #         try:
    #             data = pd.read_csv(file_path)
    #             # Show data in the table
    #             self.display_table(data)

    #         except Exception as e:
    #             print(f"Error importing CSV: {e}")

    def on_data_type_selected(self, event):
        selected_data_type = self.data_type_dropdown.get()

        # Clear existing options
        self.stat_measures_listbox.delete(0, tk.END)

        # Populate the statistical measures list based on the selected data type
        self.measure_name_map = Controller.measures_for_data_type(selected_data_type)

        for display_name in self.measure_name_map.keys():
            self.stat_measures_listbox.insert(tk.END, display_name)

    def on_stat_measure_selected(self, event):
        # Get selected items from the listbox
        selected_indices = self.stat_measures_listbox.curselection()
        self.selected_stats = [self.stat_measures_listbox.get(i) for i in selected_indices]  # Update the stored list

        # Limit selection to 3 measures
        if len(self.selected_stats) > 3:
            self.stat_measures_listbox.selection_clear(selected_indices[0])  # Remove the first selected item
            self.selected_stats.pop(0)  # Remove from the stored list as well

        # Update the label with selected measures
        self.selected_stat_label.config(
            text=f"Selected Measures: {', '.join(self.selected_stats)}"
            if self.selected_stats else "Selected Measures: None"
        )

    def get_selected_measures(self):
        """Return the selected measures so other classes can retrieve them."""
        return self.selected_stats

    def calculate_statistics(self):
        if not hasattr(self.table.controller, 'get_table_selection'):
            messagebox.showerror("Error", "Table not initialized.")
            return

        self.controller = Controller()

        selected_data_type = self.data_type_dropdown.get()
        selected_measures = [self.stat_measures_listbox.get(i) for i in self.stat_measures_listbox.curselection()]

        data_frame = self.controller.load_data_from_table(self.table.controller)
        #print(f"Final Data Before Validation:\n{data_frame}")  # Final confirmation

        if data_frame.empty:
            messagebox.showerror("Error", "No data to analyze.")
            return

        if not self.controller.validate_data(data_frame):
            messagebox.showerror("Error", "Data validation failed.")
            return

        results = self.controller.perform_statistics(data_frame, selected_measures, selected_data_type)
        # send the results, as well as the chosen selected measures to the table controller log_operation 
        self.table.controller.log_operation(selected_measures, selected_data_type, results)

        if results:
            result_str = "\n".join([f"{key}: {value}" for key, value in results.items()])
            messagebox.showinfo("Calculated Statistics", result_str)
            # self.controller.export_results(results)

            self.gui_controller.pages["ResultsPage"].display_results(results)
            self.gui_controller.show_page("ResultsPage")

            # Notify Dashboard Page to update measure dropdown
            dashboard_page = self.gui_controller.get_page("DashboardPage")
            dashboard_page.update_dropdowns(self.selected_stats, selected_data_type)

    def get_table_data(self):
        # Fetch table data from the CustomTable widget
        return self.table.celldType()


class DashboardPage(BasePage):
    """Dashboard page of the application. Users can select what graphs they would like to display."""

    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.controller = controller
        self.main_control = Controller()

        self.result_headers = []
        self.result_rows = {}

        # Configure rows and columns
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)  # Toolbar column
        self.grid_columnconfigure(1, weight=0)  # Controls column
        self.grid_columnconfigure(2, weight=1)  # Graph column

        # ----- Toolbar ----- #
        self.canvas = Canvas(self, bg="#FFFFFF", bd=0, highlightthickness=0, relief="ridge")
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Background
        self.toolbarBackground = self.canvas.create_rectangle(0, 0, 100, self.winfo_height(),
                                                              fill="#D9D9D9", outline="")
        self.canvas.bind("<Configure>", self.resize_toolbar)

        # Buttons
        self.data_page_button = add_button(
            self.canvas, 18, 50, 63, 63, "button_4.png", "button_hover_4.png",
            "Data page button clicked!", lambda: controller.show_page("MeasureSelectionPage")
        )
        self.data_page_button.grid(row=0, column=0, padx=10, pady=10, sticky="ns")

        self.dashboard_page_button = add_button(
            self.canvas, 18, 163, 63, 63, "button_5.png", "button_hover_5.png",
            "Dashboard page button clicked!", lambda: controller.show_page("ResultsPage")
        )
        self.dashboard_page_button.grid(row=1, column=0, padx=10, pady=10, sticky="ns")

        # ----- Selection Area ----- #
        self.control_frame = tk.Frame(self, bg="#FFFFFF")
        self.control_frame.grid(row=0, column=1, padx=10, pady=(10, 0), sticky="nw")

        spacer1 = tk.Label(self.control_frame, text="", bg="#FFFFFF")
        spacer1.grid(row=0, column=1)

        # Measure selection dropdown
        tk.Label(self.control_frame, text="Select Measure:", font=("Roboto", 18), bg="#FFFFFF").grid(
            row=1, column=0, sticky="w", pady=(10, 0)
        )
        self.measure_dropdown = ttk.Combobox(self.control_frame, state="readonly", font=("Roboto", 14))
        self.measure_dropdown.bind("<<ComboboxSelected>>", self.on_measure_change)
        self.measure_dropdown.grid(row=2, column=0, sticky="ew", pady=(0, 10))

        # Column selection dropdown
        tk.Label(self.control_frame, text="Group By Column:", font=("Roboto", 18), bg="#FFFFFF").grid(row=3, column=0,
                    sticky="w", pady=(0, 5))
        self.column_dropdown = ttk.Combobox(self.control_frame, state="readonly", font=("Roboto", 14))
        self.column_dropdown.grid(row=4, column=0, sticky="ew", pady=(0, 10))

        # Graph selection dropdown
        tk.Label(self.control_frame, text="Graph Type:", font=("Roboto", 18), bg="#FFFFFF").grid(row=5, column=0,
                                                                                                 sticky="w",
                                                                                                 pady=(0, 5))
        self.graph_dropdown = ttk.Combobox(self.control_frame, state="readonly", font=("Roboto", 14))
        self.graph_dropdown.grid(row=6, column=0, sticky="ew")

        # Create button
        self.create_viz_button = Button(
            self.control_frame,
            text="Graph it",
            style="TButton",
            command=lambda: self.get_grouped_data() #self.plot_graph() #command=self.create_visualization
        )
        self.create_viz_button.grid(row=7, column=0, sticky="ew", pady=100)

        # ----- Graph Area ----- #
        self.dashboard_frame = tk.Frame(self, bg="#FFFFFF")
        self.dashboard_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

        # Create a container frame for the graph and toolbar that will use pack
        self.graph_container = tk.Frame(self.dashboard_frame)
        self.graph_container.pack(fill=tk.BOTH, expand=True)

        # Figure and canvas
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas_widget = FigureCanvasTkAgg(self.figure, master=self.graph_container)
        self.canvas_widget.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Matplotlib toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas_widget, self.graph_container)
        self.toolbar.update()

        # --- Initial Color Update ---
        self.update_colors()

    def on_measure_change(self, event=None):
        selected_measure = self.measure_dropdown.get()
        print(f"Selected Measure: {selected_measure}")
        graph_types = Controller.plots_for_measure(selected_measure)

        self.graph_dropdown.set("")
        self.graph_dropdown["values"] = graph_types
        if graph_types:
            self.graph_dropdown.set(graph_types[0])

    def get_table_controller(self):
        """Retrieve the table controller from MeasureSelectionPage."""
        measure_page = self.controller.get_page("MeasureSelectionPage")

        if not measure_page or not hasattr(measure_page, 'table'):
            print("Error: Unable to access MeasureSelectionPage or table.")
            return None

        if not hasattr(measure_page.table, 'controller'):
            print("Error: Table controller is not available.")
            return None

        return measure_page.table.controller

    def resize_toolbar(self, event):
        """Resize the rectangle dynamically when the window changes size."""
        self.canvas.coords(self.toolbarBackground, 0, 0, 100, event.height)  # Adjust height dynamically

    def update_dropdowns(self, selected_measures, selected_measure):
        """Update the measure and column dropdowns with available options while excluding selected columns."""

        # Ensure the table controller is available
        table_controller = self.get_table_controller()
        if not table_controller:
            print("Error: Table controller not found.")
            return

         # Load data from the table
        data_frame = self.main_control.load_entire_table(table_controller)
        selected_table = self.main_control.load_data_from_table(table_controller)

        if data_frame.empty:
            messagebox.showerror("Error", "Data frame is empty, cannot populate dropdown.")
            return

        # Get column info
        all_columns = list(data_frame.columns)
        selected_columns = list(selected_table.columns)
        available_columns = [col for col in all_columns if col not in selected_columns]

        # Reset dropdowns
        self.column_dropdown.set("")
        self.measure_dropdown.set("")
        self.graph_dropdown.set("")

        # Set column dropdown
        self.column_dropdown["values"] = available_columns
        if available_columns:
            self.column_dropdown.set(available_columns[0])

        # Set measure dropdown
        if selected_measures:
            measure_options = ["Select value"] + selected_measures
            self.measure_dropdown["values"] = measure_options
            self.measure_dropdown.set("Select value")
        else:
            self.measure_dropdown.set("")  # Clear if no measures available
            self.measure_dropdown["values"] = []

        # Set graph dropdown based on selected measure
        if selected_measures:
            graph_types = Controller.plots_for_measure(selected_measure)
            self.graph_dropdown["values"] = graph_types
            self.graph_dropdown.set("")
        else:
            self.graph_dropdown.set("")  # Clear if no measures available
            self.graph_dropdown["values"] = []


    def update_colors(self):
        """Updates colors for non-ttk widgets and Matplotlib elements."""
        if not (hasattr(self.controller, 'colors') and self.controller.colors):
            print(f"Warning: Cannot update colors for {type(self).__name__}, controller or colors missing.")
            return
        if hasattr(super(), 'update_colors'):
            super().update_colors()

        background_color = self.controller.colors.get_color("background")
        text_color = self.controller.colors.get_color("text")
        toolbar_bg_color = self.controller.colors.get_color("toolbar_bg")
        # Use a slightly different color for axes background? Or match primary/background??
        plot_bg_color = background_color # Figure background matches window

        # Update Frames
        if hasattr(self, 'toolbar_frame'): self.toolbar_frame.configure(bg=toolbar_bg_color)
        if hasattr(self, 'control_frame'): self.control_frame.configure(bg=background_color)
        if hasattr(self, 'dashboard_frame'): self.dashboard_frame.configure(bg=background_color)
        if hasattr(self, 'graph_container'): self.graph_container.configure(bg=background_color)

        # Update tk Labels in control_frame
        if hasattr(self, 'label_measure'): self.label_measure.configure(bg=background_color, fg=text_color)
        if hasattr(self, 'label_group_by'): self.label_group_by.configure(bg=background_color, fg=text_color)
        if hasattr(self, 'label_graph_type'): self.label_graph_type.configure(bg=background_color, fg=text_color)

        # Update Matplotlib colors
        try:
            # Set figure and axes background
            self.figure.patch.set_facecolor(plot_bg_color)

            # Update text colors (title, labels, ticks)
            self.ax.title.set_color(text_color)
            self.ax.xaxis.label.set_color(text_color)
            self.ax.yaxis.label.set_color(text_color)
            self.ax.tick_params(axis='x', colors=text_color)
            self.ax.tick_params(axis='y', colors=text_color)

            # Update spines (axes borders) color
            self.ax.spines['top'].set_color(text_color)
            self.ax.spines['bottom'].set_color(text_color)
            self.ax.spines['left'].set_color(text_color)
            self.ax.spines['right'].set_color(text_color)

            # Update the canvas widget background itself (the tk part)
            if hasattr(self, 'canvas_tk_widget'):
                  self.canvas_tk_widget.configure(bg=plot_bg_color)

            # Redraw the canvas
            self.canvas_widget.draw_idle()

        except Exception as e:
             print(f"Error updating plot colors: {e}")

    def get_grouped_data(self):
        """Retrieve the selected measure and column, apply groupby() to the DataFrame, and create a plot."""

        # Ensure the table controller is available
        table_controller = self.get_table_controller()
        if not table_controller:
            print("Error: Table controller not found.")
            return

        # Load data from the table
        data_frame = self.main_control.load_entire_table(table_controller)
        if data_frame.empty:
            messagebox.showerror("Error", "Table is empty.")
            return None

        # Load table selection
        selected_table = self.main_control.load_data_from_table(table_controller)

        # Get selected rows
        selected_rows = table_controller.get_table_selection()
        if not selected_rows.empty:
            data_frame = data_frame.loc[selected_rows.index]

        # Check if data was successfully retrieved
        if selected_table.empty:
            print("Error: Data frame is empty, cannot populate dropdown.")
            return

        # Get selected columns from table
        selected_columns = list(selected_table.columns)

        # Get selected values from dropdowns
        selected_measure = self.measure_dropdown.get()
        groupby_column = self.column_dropdown.get()
        graph_type = self.graph_dropdown.get()

        # Validate selections
        if selected_measure == "Select value":
            messagebox.showerror("Error", "Please select a measure.")
            return None

        if not groupby_column:
            messagebox.showerror("Error", "Please select a column.")
            return None

        if not graph_type:
            messagebox.showerror("Error", "Please select a graph.")
            return None


        # Filter the dataframe to only include rows with indices from selected_rows
        if not selected_rows.empty:
            # Get the indices from the selected rows
            selected_indices = selected_rows.index
            # Filter the original dataframe
            data_frame = data_frame.loc[selected_indices]


        grouped = data_frame.groupby([groupby_column])[selected_columns]
        # Get probability distribution plot type if applicable
        prob_dist_plot_type = None

        # Perform statistical measure on grouped data and create dataframe
        if selected_measure == "Mean":
            grouped_data = grouped.mean()
        elif selected_measure == "Median":
            grouped_data = grouped.median()
        elif selected_measure == "Mode":
            grouped_data = grouped.agg(lambda x: x.mode().iloc[0] if not x.mode().empty else None)
        elif selected_measure == "Standard Deviation":
            # have to grab x and y values and then find the std deviation of those values 
            try:
                # Extract X and Y values from the grouped data
                grouped_data = grouped.apply(lambda x: x)
                x = pd.to_numeric(grouped_data.iloc[:, 0], errors='coerce').dropna().astype(int).values
                y = pd.to_numeric(grouped_data.iloc[:, 1], errors='coerce').dropna().astype(int).values
                
                # Calculate standard deviation
                std_deviation = np.std(y)
                
                # Create a DataFrame for plotting
                grouped_data = pd.DataFrame({
                    "X": x,
                    "Y": y
                })
                grouped_data["Standard Deviation"] = std_deviation  
                #std_deviation_value = {"Standard Deviation": std_deviation}
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while calculating Standard Deviation: {e}")

           # print(grouped_data)
        elif selected_measure == "Variance":
            try:
                grouped_data = grouped.apply(lambda x: x)

                var_list = []
                for index, row in grouped_data.iterrows(): # Get variance for each row in dataframe
                    var_list.append({[index][0][0] : np.var(row)})

                grouped_data = pd.DataFrame(var_list)
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while calculating Variance: {e}")

        elif selected_measure == "Coefficient Of Variation":
            try:
                grouped_data = grouped.apply(lambda x: x)

                var_list = []
                for index, row in grouped_data.iterrows():
                    var_std = np.std(row)
                    var_mean = np.mean(row)
                    var_list.append({[index][0][0] : var_std / var_mean})

                grouped_data = pd.DataFrame(var_list)
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while calculating Coefficient of Variance: {e}")

        elif selected_measure == "Percentiles":
            #TODO: Either grouped.quantile needs the "psequence"
            # from user or grouped_data needs to pull percentiles_df (without default index)
            label, values = Controller.get_last_selected_percentiles()
            values = [v / 100 for v in values] # convert selected psequence to decimals
            grouped_data = grouped.quantile(values)

        elif selected_measure == "Probability Distribution":
            # calculating the frequency of each group
            group_counts = grouped.size()  # Get counts for each group
            total_count = group_counts.sum()  # Total number of rows
            grouped_data = group_counts / total_count
               
        elif selected_measure == "Binomial Distribution":
            n_trails, prob = Controller.get_last_binomial_params()
            print(n_trails)
            print(prob)
            k = np.arange(0, n_trails + 1)
            print("k:", k)
            grouped_data = stats.binom.pmf(k, n_trails, prob)

        elif selected_measure == "Least Square Line":
           # slope, y_int = np.polyfit(x, y, 1)
            grouped_data = grouped.mean()
            # x values is on the horizontal and y-vlaues on the vertical. the slope and y int will be used as the regression line 
                     

        elif selected_measure == "Chi Square":
            grouped_data = grouped.apply(lambda x: x)
            grouped_data.iloc[:,0] = pd.to_numeric(grouped_data.iloc[:,0], errors='coerce').dropna().astype(int).values
            grouped_data.iloc[:,1] = pd.to_numeric(grouped_data.iloc[:,1], errors='coerce').dropna().astype(int).values

        elif selected_measure == "Correlation":
            grouped_data = grouped.corr()

        elif selected_measure == "Sign Test":
            if len(selected_columns) >= 2:
                col1, col2 = selected_columns[:2]
                data_frame[col1] = pd.to_numeric(data_frame[col1], errors='coerce')
                data_frame[col2] = pd.to_numeric(data_frame[col2], errors='coerce')
                data_frame['diff'] = data_frame[col1] - data_frame[col2]
                value_col = 'diff'
            elif len(selected_columns) == 1:
                col = selected_columns[0]
                data_frame[col] = pd.to_numeric(data_frame[col], errors='coerce')
                value_col = col
            else:
                messagebox.showerror("Error", "Select at least one column for Sign Test.")
                return
            def sign_counts(series):
                pos = (series > 0).sum()
                neg = (series < 0).sum()
                return pd.Series({'Positive Count': pos, 'Negative Count': neg})
            grouped_data = data_frame.groupby(groupby_column)[value_col].apply(sign_counts).unstack().reset_index()

        elif selected_measure == "Rank Sum":
            grouped_data = grouped.mean()
            ranked_data = grouped_data.rank(numeric_only=True, method='average')

        elif selected_measure == "Spearman Correlation":
            grouped_data = grouped.apply(lambda x: x).reset_index()
        else:
            messagebox.showerror("Error", "Invalid measure selected.")
            return None

        # Clear previous plot and recreate axes to ensure clean state
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)  # Recreate the main axes
        self.canvas_widget.draw_idle()  # Refresh the canvas
        plt.style.use('seaborn-v0_8-deep')

        # Generate the selected graph
        if graph_type == "Horizontal Bar Chart":
            grouped_data.plot(kind="barh", ax=self.ax).legend(loc='upper left', bbox_to_anchor=(1, 1))
            if selected_measure == "Standard Deviation":
                # Add a horizontal line for the standard deviation
                std_dev_value = grouped_data["Standard Deviation"].values[0]
                self.ax.axvline(x=std_dev_value, color='r', linestyle='--', label='Std Dev')
                self.ax.legend()

        elif graph_type == "Vertical Bar Chart":
            grouped_data.plot(kind="bar", ax=self.ax).legend(loc='upper left', bbox_to_anchor=(1, 1))
            if selected_measure == "Standard Deviation":
                # Add a horizontal line for the standard deviation
                std_dev_value = grouped_data["Standard Deviation"].values[0]
                self.ax.axhline(y=std_dev_value, color='r', linestyle='--', label='Std Dev')
                self.ax.legend()

        elif graph_type == "Pie Chart":
            num_cols = len(selected_columns)
            for i, col in enumerate(selected_columns, 1):
                ax = self.figure.add_subplot(1, num_cols, i)
                grouped_data[col].plot(kind="pie", ax=ax, autopct='%1.1f%%', title=col)
        elif graph_type == "Normal Distribution Curve":
            if selected_measure == "Percentiles":
                self.plot_normal_distribution_with_percentiles(grouped_data, data_frame, selected_columns)
            elif isinstance(grouped_data, pd.Series):
                sns.kdeplot(grouped_data, ax=self.ax, fill=True, label=selected_measure)
            else:
                for col in selected_columns:
                    sns.kdeplot(grouped_data[col], ax=self.ax, fill=True, label=col)
            self.ax.legend()
            self.ax.set_title(f"Probability Distribution of {groupby_column}")
        elif graph_type == "Scatter Plot":  # X-Y Graph
            if selected_measure == "Spearman Correlation":
                x = grouped_data[selected_columns[0]]
                y = grouped_data[selected_columns[1]]

                self.ax.scatter(x, y, label=groupby_column)

                self.ax.set_xlabel(selected_columns[0])
                self.ax.set_ylabel(selected_columns[1])

                coefficients = np.polyfit(x, y, 1)
                trend = np.poly1d(coefficients)
                self.ax.plot(x, trend(x), 'r--', label='Trend Line')
            if selected_measure == "Least Square Line":
                x = grouped_data[selected_columns[0]] # should be graphed on the horizontal
                y = grouped_data[selected_columns[1]] # vertical 

                # self.ax.scatter(x,y, label=groupby_column)
                # self.ax.set_xlabel(selected_columns[0])
                # self.ax.set_ylabel(selected_columns[1])

                coefficients = np.polyfit(x, y, 1)
                slope = coefficients[0]
                intercept = coefficients[1]

                # Create the line of best fit
                line = slope * x + intercept
                # Plot the original data points
                self.ax.scatter(x,y, label = 'Data Points')
                # Plot the least squares line
                self.ax.plot(x, line, color = 'red', label = 'Least Square Line')
                #plt.plot(x, line, color='red', label='Least Squares Line')


            else:
                for col in selected_columns:
                    self.ax.scatter(grouped_data.index, grouped_data[col], label=col)
            
            self.ax.legend()


        # Set labels and title
        self.ax.set_title(f"{selected_measure} by {groupby_column}")
        #self.ax.set_ylabel(selected_measure)
        #self.ax.set_xlabel(groupby_column)

        # Rotate x-axis labels for better readability (except for pie charts)
        if graph_type != "Pie Chart":
            self.ax.tick_params(axis='x', rotation=45)

        # Redraw the canvas
        self.canvas_widget.draw()

    def plot_normal_distribution_with_percentiles(self, grouped_data, data_frame, selected_columns):
        """
        Plot a KDE (normal distribution-like) curve and overlay vertical percentile lines.
        """
        from main_controller import Controller

        for col in selected_columns:
            col_series = pd.to_numeric(data_frame[col], errors='coerce').dropna()
            if not col_series.empty:
                sns.kdeplot(col_series, ax=self.ax, fill=True, label=col)

                # Overlay percentiles if available
                label, percentiles = Controller.get_last_selected_percentiles()
                if percentiles:
                    quantiles = [v / 100 for v in percentiles]
                    for q in quantiles:
                        perc_val = col_series.quantile(q)
                        self.ax.axvline(perc_val, color='red', linestyle='--', alpha=0.7)
                        x_offset = (self.ax.get_xlim()[1] - self.ax.get_xlim()[0]) * 0.01  # ~1% of axis width

                        self.ax.text(
                            perc_val + x_offset,
                            self.ax.get_ylim()[1] * 0.9,
                            f"{int(q * 100)}th",
                            rotation=90,
                            verticalalignment='center',
                            horizontalalignment='left',
                            color='red',
                            fontsize=8
                        )


class ResultsPage(BasePage):
    """
    Dashboard page of the application. Users can view their calculation results.
    """

    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        # Initialize results storage
        self.result_headers = []
        self.result_rows = {}

        # Configure grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)  # Toolbar column
        self.grid_columnconfigure(1, weight=1)  # Main content area

        # ----- Toolbar ----- #
        # Create a canvas to hold toolbar
        self.canvas = Canvas(self, bg="#FFFFFF", bd=0, highlightthickness=0, relief="ridge")
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.toolbarBackground = self.canvas.create_rectangle(0, 0, 100, self.winfo_height(), fill="#D9D9D9", outline="")
        self.canvas.bind("<Configure>", self.resize_toolbar)  # Bind the resize event

        self.data_page_button = add_button(
            self.canvas, 18, 50, 63, 63, "button_4.png", "button_hover_4.png",
            "Data page button clicked!", lambda: controller.show_page("MeasureSelectionPage")
        )
        self.data_page_button.grid(row=0, column=0, padx=10, pady=10, sticky="ns")

        self.dashboard_page_button = add_button(
            self.canvas, 18, 163, 63, 63, "button_5.png", "button_hover_5.png",
            "Dashboard page button clicked!", lambda: controller.show_page("ResultsPage")
        )
        self.dashboard_page_button.grid(row=1, column=0, padx=10, pady=10, sticky="ns")

        # ----- Main Content Area ----- #
        self.main_frame = tk.Frame(self, bg="#FFFFFF")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_rowconfigure(1, weight=1)  # Results area will expand
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Button bar at top
        self.button_frame = tk.Frame(self.main_frame, bg="#FFFFFF")
        self.button_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        self.add_graph_button = Button(
            self.button_frame, text="Create Visualization", style="TButton",
            command=lambda: controller.show_page("DashboardPage")
        )
        self.add_graph_button.pack(side="right", padx=5)

        # Results display area
        self.results_display_frame = tk.Frame(self.main_frame, bg="#D9D9D9")
        self.results_display_frame.grid(row=1, column=0, sticky="nsew")
        self.results_display_frame.grid_rowconfigure(0, weight=1)
        self.results_display_frame.grid_columnconfigure(0, weight=1)

        # Placeholder message for empty results
        self.placeholder_label = tk.Label(
            self.results_display_frame,
            text="Calculate a statistical measure to see results",
            font=("Arial", 16),
            bg="#D9D9D9"
        )
        self.placeholder_label.grid(row=0, column=0)
        # --- Initial Color Update ---
        self.update_colors()

    def update_colors(self):
        """Updates colors for non-ttk widgets and frames."""
        if not (hasattr(self.controller, 'colors') and self.controller.colors):
            print(f"Warning: Cannot update colors for {type(self).__name__}, controller or colors missing.")
            return
        if hasattr(super(), 'update_colors'):
            super().update_colors()

        background_color = self.controller.colors.get_color("background")
        text_color = self.controller.colors.get_color("text")
        toolbar_bg_color = self.controller.colors.get_color("toolbar_bg")
        results_bg_color = self.controller.colors.get_color("results_bg") # Specific results area color

        # Update Frames
        if hasattr(self, 'toolbar_frame'): self.toolbar_frame.configure(bg=toolbar_bg_color)
        if hasattr(self, 'main_frame'): self.main_frame.configure(bg=background_color)
        if hasattr(self, 'button_frame'): self.button_frame.configure(bg=background_color) # Button is ttk
        if hasattr(self, 'results_display_frame'): self.results_display_frame.configure(bg=results_bg_color)

        if hasattr(self, 'placeholder_label') and self.placeholder_label.winfo_exists():
            self.placeholder_label.configure(bg=results_bg_color, fg=text_color)


    def resize_toolbar(self, event):
        """Resize the rectangle dynamically when the window changes size."""
        self.canvas.coords(self.toolbarBackground, 0, 0, 100, event.height)  # Adjust height dynamically

    def display_headers(self, results):
        """Updates the header list if calculation requires new headers."""
        for key, value in results.items():
            if isinstance(value, dict):  # If value is a dictionary
                for subkey in value.keys():
                    if subkey not in self.result_headers:
                        self.result_headers.append(subkey)
            else:  # If value is a direct number
                if key not in self.result_headers:
                    self.result_headers.append(key)

    def display_row_data(self, results):
        """Combines all results into a single row of data."""
        row = {}
        for key, value in results.items():
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    if isinstance(subvalue, np.ndarray):
                        row[subkey] = ", ".join(map(str, subvalue.flatten()))
                    else:
                        row[subkey] = subvalue
            else:
                row[key] = value
        return row

    def display_results(self, results):
        """Updates the result table with the latest calculation."""
        # Remove placeholder if it exists
        if hasattr(self, 'placeholder_label'):
            self.placeholder_label.destroy()
            del self.placeholder_label

        # Clear existing table if it exists
        if hasattr(self, 'results_table_frame'):
            self.results_table_frame.destroy()
            del self.results_table_frame

        # Process results
        self.display_headers(results)
        result_data = self.display_row_data(results)

        # Create row data
        row_data = []
        for head in self.result_headers:
            row_data.append(result_data.get(head, ""))

        self.result_rows[len(self.result_rows) + 1] = row_data

        # Create new table frame
        self.results_table_frame = tk.Frame(self.results_display_frame)
        self.results_table_frame.grid(row=0, column=0, sticky="nsew")
        self.results_table_frame.grid_rowconfigure(0, weight=1)
        self.results_table_frame.grid_columnconfigure(0, weight=1)

        # Create and populate table
        table = TableView(self.results_table_frame, output=True)
        table.grid(row=0, column=0, sticky='nsew')
        table.controller.update_table(headers=self.result_headers, data=self.result_rows.values())


# Run the application

app = App()
app.mainloop()
