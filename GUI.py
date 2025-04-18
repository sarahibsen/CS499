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
        self.config(menu=menubar)  # Assign the menu to the window

        # File Menu
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.quit)  # Use self.quit
        menubar.add_cascade(label="File", menu=filemenu)  # Add the cascade to the menubar
        # Help Menu
        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=about_the_app)
        helpmenu.add_command(label="Help", command=show_help)
        menubar.add_cascade(label="Help", menu=helpmenu)
        viewmenu = Menu(menubar, tearoff=0)
        viewmenu.add_command(label="Set Theme",
                             command=lambda: set_theme(self))
        menubar.add_cascade(label="View", menu=viewmenu)
        # ----
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
                print(
                    f"Warning: Page {page_name} ({type(page).__name__}) has no update_colors method or doesn't exist.")
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
        tk.Label(self, text="STAT", bg=background_color, fg=text_color, font=("Arial", 40)).grid(column=0, row=1,
                                                                                                 sticky="nsew")
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

        # Measurement Frame
        self.measurement_frame = tk.Frame(self, bg="#FFFFFF")
        self.measurement_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nw")

        # ----- Data Table ----- #
        self.table_frame = tk.Frame(self)
        self.table_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)

        self.table = TableView(self.table_frame)
        self.table.grid(row=0, column=0, sticky='nsew')

        style = ttk.Style()
        style.configure("mystyle.Treeview", highlightthickness=0, bd=0,
                        font=('Roboto', 15), rowheight=35)  # Modify the font of the body
        style.configure("mystyle.Treeview.Heading", font=('Roboto', 18, 'bold'))  # Modify the font of the headings
        style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})])  # Remove the borders

        # Statistical Measures TreeView
        self.stat_treeview = ttk.Treeview(
            self.measurement_frame, columns=("Measure"), show="headings", selectmode="extended", style="mystyle.Treeview"
        )
        self.stat_treeview.heading("Measure", text="Statistical Measures")
        self.stat_treeview.column("Measure", anchor="w")
        self.stat_treeview.grid(row=2, column=1, padx=10, pady=10, sticky='nswe')

        # Populate TreeView immediately
        self.populate_treeview()

        # Label to show selected measures
        self.selected_stat_label = tk.Label(
            self.measurement_frame,
            text="Selected: None",
            font=("Roboto", 12),
            wraplength=300,
            justify="left",
            anchor="nw",
        )
        self.selected_stat_label.grid(row=3, column=1, padx=10, pady=10, sticky="nw")

        # Bind TreeView selection event
        self.stat_treeview.bind("<<TreeviewSelect>>", self.on_stat_measure_selected)

        # Calculate Measures Button
        self.calculate_button = Button(
            self.measurement_frame,
            text="Calculate Measures",
            style="TButton",
            command=self.calculate_statistics,
        )
        self.calculate_button.grid(row=4, column=1, padx=10, pady=10, sticky="w")

        # --- Binomial Input Fields (Initially Hidden) --- #
        self.binomial_frame = tk.Frame(self.measurement_frame, bg="#FFFFFF")

        self.label_n = tk.Label(self.binomial_frame, text="Number of Trials (n):", bg="#FFFFFF", font=("Roboto", 12))
        self.entry_n = tk.Entry(self.binomial_frame, font=("Roboto", 12), width=10)

        self.label_p = tk.Label(self.binomial_frame, text="Probability (p):", bg="#FFFFFF", font=("Roboto", 12))
        self.entry_p = tk.Entry(self.binomial_frame, font=("Roboto", 12), width=10)

        self.label_n.grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.entry_n.grid(row=0, column=1, padx=5, pady=2)

        self.label_p.grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.entry_p.grid(row=1, column=1, padx=5, pady=2)

        self.binomial_frame.grid(row=5, column=1, padx=10, pady=5, sticky="w")
        self.binomial_frame.grid_remove()  # Hide initially

        # --- Chi-Square Column Selector --- #
        self.chi_square_frame = tk.Frame(self.measurement_frame, bg="#FFFFFF")

        self.label_expected = tk.Label(self.chi_square_frame, text="Expected Column:", bg="#FFFFFF", font=("Roboto", 12))
        self.expected_dropdown = ttk.Combobox(self.chi_square_frame, state="readonly", font=("Roboto", 12))

        self.label_observed = tk.Label(self.chi_square_frame, text="Observed Column:", bg="#FFFFFF", font=("Roboto", 12))
        self.observed_dropdown = ttk.Combobox(self.chi_square_frame, state="readonly", font=("Roboto", 12))

        self.label_expected.grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.expected_dropdown.grid(row=0, column=1, padx=5, pady=2)

        self.label_observed.grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.observed_dropdown.grid(row=1, column=1, padx=5, pady=2)

        self.chi_square_frame.grid(row=6, column=1, padx=10, pady=5, sticky="w")
        self.chi_square_frame.grid_remove()  # Hidden initially


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

    def resize_toolbar(self, event):
        """Resize the rectangle dynamically when the window changes size."""
        self.canvas.coords(self.toolbarBackground, 0, 0, 100, event.height)  # Adjust height dynamically

    def populate_treeview(self):
        """Populate the treeview with statistical measures and options."""
        self.stat_treeview.delete(*self.stat_treeview.get_children())  # Clear existing items

        all_measures = statistic.registered_measures.keys()
        for measure in sorted(all_measures):
            parent_id = self.stat_treeview.insert("", tk.END, text=measure, values=(measure,))
            if measure in statistic.measure_options_map:
                for option in statistic.measure_options_map[measure]:
                    self.stat_treeview.insert(parent_id, tk.END, text=option, values=(option,))

    def on_stat_measure_selected(self, event):
        """Handles selection changes in the statistics treeview."""
        # Get the selected item IDs (iids) from the treeview
        selected_items_iids = self.stat_treeview.selection()

        
        selected_measures = [self.stat_treeview.item(iid, "values")[0] for iid in selected_items_iids]
        self.selected_stats = sorted(selected_measures)  # Store unique, sorted measure names

        # toggle the visibility of the binomial input based if the user clicks on this measure
        if "Binomial Distribution" in self.selected_stats:
            self.binomial_frame.grid()  # Show the frame
        else:
            self.binomial_frame.grid_remove()  # Hide if not selected
        if "Chi Square" in self.selected_stats:
            self.update_chi_square_dropdowns()
            self.chi_square_frame.grid()
        else:
            self.chi_square_frame.grid_remove()

        if self.selected_stats:
            display_text = "Selected: " + ", ".join(self.selected_stats)
        else:
            display_text = "Selected: None"
        self.selected_stat_label.config(text=display_text)

    def calculate_statistics(self):
        selected_measures = []
        extra_params = {}
        data_frame = self.table.controller.get_table_selection()

        if data_frame.empty:
            messagebox.showerror("Error", "No data selected.")
            return

        selected_items_iids = self.stat_treeview.selection()

        for iid in selected_items_iids:
            val = self.stat_treeview.item(iid, "values")[0]
            parent_iid = self.stat_treeview.parent(iid)

            if parent_iid:  # It's a sub-option
                main_measure = self.stat_treeview.item(parent_iid, "values")[0]

                if main_measure not in selected_measures:
                    selected_measures.append(main_measure)

                if main_measure not in extra_params:
                    extra_params[main_measure] = []
                extra_params[main_measure].append(val)

            else:  # Top-level measure
                if val not in selected_measures:
                    selected_measures.append(val)

                if val not in extra_params:
                    extra_params[val] = None  # Default will be used by logic if no sub-option

        if "Binomial Distribution" in selected_measures:
            try:
                n_input = self.entry_n.get()
                p_input = self.entry_p.get()

                n = int(n_input) if n_input.strip() != "" else 10
                p = float(p_input) if p_input.strip() != "" else 0.5

                if not (0 <= p <= 1):
                    raise ValueError("Probability must be between 0 and 1.")

                extra_params["n"] = n
                extra_params["p"] = p
            except Exception as e:
                messagebox.showerror("Input Error", f"Invalid input for Binomial Distribution: {e}")
                return
        
        if "Chi Square" in selected_measures:
            selected_expected = self.expected_dropdown.get()
            selected_observed = self.observed_dropdown.get()

            # If user didn’t change dropdowns or values are empty, fallback
            if selected_expected and selected_observed:
                extra_params["Chi Square"] = {"expected": selected_expected, "observed": selected_observed}

        results, skipped = Controller.calculate_statistics(
            data_frame, selected_measures, extra_params=extra_params
        )

        if skipped:
            explanation = self.generate_skipped_explanations(skipped, data_frame)
            messagebox.showwarning("Incompatible Measures", explanation)


        self.table.controller.log_operation(selected_measures, results, dataType="Detected")
        self.table.controller.add_log_separator()

        if results:
            result_str = "\n".join([f"{key}: {value}" for key, value in results.items()])
            messagebox.showinfo("Calculated Statistics", result_str)
            self.table.controller.log_operation(selected_measures, results, dataType="Detected")

            self.gui_controller.pages["ResultsPage"].display_results(results)
            self.gui_controller.show_page("ResultsPage")

            dashboard_page = self.gui_controller.get_page("DashboardPage")
            dashboard_page.update_dropdowns(selected_measures)


    def get_selected_measures(self):
        """Return the selected measures (list of strings)."""
        return self.selected_stats
    
    def update_chi_square_dropdowns(self):
        df = self.table.controller.get_table_selection()

        if df.empty or df.shape[1] < 2:
            self.expected_dropdown["values"] = []
            self.observed_dropdown["values"] = []
            return

        column_names = df.columns.tolist()
        self.expected_dropdown["values"] = column_names
        self.observed_dropdown["values"] = column_names

        # Optionally pre-select the first two
        self.expected_dropdown.set(column_names[0])
        self.observed_dropdown.set(column_names[1])

    def generate_skipped_explanations(self, skipped_measures, df):
        """
        We want to better explain why the measure is not working so that the user may be able to troubleshoot the problem
        themselves
        """
        explanations = []

        for measure in skipped_measures:
            if measure in ["Mean", "Median", "Mode", "Standard Deviation", "Variance", "Percentiles", "Coefficient of Variation"]:
                explanations.append(f"❌ **{measure}** requires numeric data. Try selecting columns with numbers only.")
            elif measure == "Chi Square":
                explanations.append("❌ **Chi Square** requires two columns of equal length with non-negative integer values. You can select the columns manually once Chi Square is selected.")
            elif measure in ["Least Square Line", "Correlation", "Spearman Correlation"]:
                explanations.append(f"❌ **{measure}** requires at least two numeric columns of equal length (x and y pairs).")
            elif measure == "Binomial Distribution":
                explanations.append("❌ **Binomial Distribution** needs numeric data and a number of trials and probability between 0 and 1.")
            elif measure == "Probability Distribution":
                explanations.append("❌ **Probability Distribution** requires numeric data and may fail if the standard deviation is 0.")
            else:
                explanations.append(f"❌ **{measure}** couldn't be applied due to incompatible or missing data.")

        return "Some measures could not be calculated:\n\n" + "\n".join(explanations)




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
                                                                                                      sticky="w",
                                                                                                      pady=(0, 5))
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
            command=lambda: self.get_grouped_data()  # self.plot_graph() #command=self.create_visualization
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

        # Set column dropdown - add "No Grouping" as first option
        if available_columns:
            self.column_dropdown["values"] = ["No Grouping"] + available_columns
            self.column_dropdown.set("No Grouping")  # Default to no grouping
        else:
            self.column_dropdown.set("No Grouping")
            self.column_dropdown["values"] = ["No Grouping"]

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
        plot_bg_color = background_color  # Figure background matches window

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

        # Get selected values from dropdowns
        selected_measure = self.measure_dropdown.get()
        groupby_column = self.column_dropdown.get()
        graph_type = self.graph_dropdown.get()

        # Validate selections
        if selected_measure == "Select value":
            messagebox.showerror("Error", "Please select a measure.")
            return None

        if not graph_type:
            messagebox.showerror("Error", "Please select a graph.")
            return None

        # Get all columns and selected columns
        data_frame = self.main_control.load_entire_table(table_controller)
        selected_columns = data_frame.select_dtypes(include='number').columns.tolist()

        # Variable to hold dataframe to graph
        graph_data = None

        # Check if there is a group by column
        if not groupby_column or groupby_column == 'No Grouping':
            selected_table = self.main_control.load_data_from_table(table_controller)
            if selected_table.empty:
                messagebox.showerror("Error", "No data selected for visualization.")
                return None

            raw_data = selected_table.select_dtypes(include='number')
            selected_columns = raw_data.columns.tolist()

            if selected_measure == "Mean":
                graph_data = pd.DataFrame(raw_data.mean()).T
            elif selected_measure == "Median":
                graph_data = pd.DataFrame(raw_data.median()).T
            elif selected_measure == "Mode":
                graph_data = pd.DataFrame(raw_data.mode().iloc[0]).T
            elif selected_measure == "Standard Deviation":
                graph_data = pd.DataFrame(raw_data.std()).T
            elif selected_measure == "Variance":
                graph_data = pd.DataFrame(raw_data.var()).T
            elif selected_measure == "Coefficient Of Variation":
                graph_data = pd.DataFrame((raw_data.std() / raw_data.mean())).T
            elif selected_measure == "Percentiles":
                label, values = Controller.get_last_selected_percentiles()
                values = [v / 100 for v in values]
                percentiles_df = raw_data.quantile(values)
                percentiles_df.index = [f"{int(v * 100)}th" for v in values]
                graph_data = percentiles_df
            elif selected_measure == "Probability Distribution":
                freq = raw_data.apply(lambda col: col.value_counts(normalize=True))
                graph_data = freq.fillna(0).T
            elif selected_measure == "Binomial Distribution":
                n_trials, prob = Controller.get_last_binomial_params()
                if n_trials is None or prob is None:
                    messagebox.showerror("Error",
                                         "No binomial parameters found. Please run Binomial Distribution measure first.")
                    return None
                try:
                    k = np.arange(0, n_trials + 1)
                    pmf_values = stats.binom.pmf(k, n_trials, prob)
                    graph_data = pd.Series(pmf_values, index=k, name="Probability")
                    graph_data = graph_data.to_frame()  # Convert to DataFrame for consistent downstream handling
                    graph_data.index.name = "Number of Successes"
                except Exception as e:
                    messagebox.showerror("Error", f"Error calculating Binomial Distribution: {e}")
                    return None
            else:
                messagebox.showerror("Error", f"{selected_measure} is not supported without grouping.\n"
                                              f"Please select a Group By Column")
                return None

        else:
            # Original groupby logic
            data_frame = self.main_control.load_entire_table(table_controller)
            grouped_data = None
            if data_frame.empty:
                messagebox.showerror("Error", "Table is empty.")
                return None

            selected_table = self.main_control.load_data_from_table(table_controller)
            selected_rows = table_controller.get_table_selection()
            if not selected_rows.empty:
                data_frame = data_frame.loc[selected_rows.index]

            if selected_table.empty:
                print("Error: Data frame is empty, cannot populate dropdown.")
                return

            selected_columns = list(selected_table.columns)

            # Filter the dataframe to only include rows with indices from selected_rows
            if not selected_rows.empty:
                selected_indices = selected_rows.index
                data_frame = data_frame.loc[selected_indices]

            # Group the data
            grouped = data_frame.groupby([groupby_column])[selected_columns]

            # Perform statistical measure on grouped data and create dataframe
            if selected_measure == "Mean":
                grouped_data = grouped.mean()
            elif selected_measure == "Median":
                grouped_data = grouped.median()
            elif selected_measure == "Mode":
                grouped_data = grouped.agg(lambda x: x.mode().iloc[0] if not x.mode().empty else None)
            elif selected_measure == "Standard Deviation":
                messagebox.showerror("Error", f"{selected_measure} is not supported with grouping.\n"
                                              f"Please select No Grouping for Group By Column.")
                return None
            elif selected_measure == "Variance":
                messagebox.showerror("Error", f"{selected_measure} is not supported with grouping.\n"
                                              f"Please select No Grouping for Group By Column.")
                return None
            elif selected_measure == "Coefficient Of Variation":
                messagebox.showerror("Error", f"{selected_measure} is not supported with grouping.\n"
                                              f"Please select No Grouping for Group By Column.")
                return None
            elif selected_measure == "Percentiles":
                messagebox.showerror("Error", f"{selected_measure} is not supported with grouping.\n"
                                              f"Please select No Grouping for Group By Column.")
                return None
            elif selected_measure == "Probability Distribution":
                # calculating the frequency of each group
                group_counts = grouped.size()  # Get counts for each group
                total_count = group_counts.sum()  # Total number of rows
                grouped_data = group_counts / total_count
            elif selected_measure == "Binomial Distribution":
                messagebox.showerror("Error", f"{selected_measure} is not supported with grouping.\n"
                                              f"Please select No Grouping for Group By Column.")
                return None
            elif selected_measure == "Least Square Line":
                # slope, y_int = np.polyfit(x, y, 1)
                grouped_data = grouped.mean()
                # x values is on the horizontal and y-vlaues on the vertical. the slope and y int will be used as the regression line
            elif selected_measure == "Chi Square":
                grouped_data = grouped.apply(lambda x: x)
                grouped_data.iloc[:, 0] = pd.to_numeric(grouped_data.iloc[:, 0], errors='coerce').dropna().astype(
                    int).values
                grouped_data.iloc[:, 1] = pd.to_numeric(grouped_data.iloc[:, 1], errors='coerce').dropna().astype(
                    int).values
            elif selected_measure == "Correlation":
                grouped_data = grouped.apply(lambda x: x).reset_index()
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

            graph_data = grouped_data

        # Fully clear the figure and remove all subplots
        self.figure.clf()
        self.ax = self.figure.add_subplot(111)
        plt.style.use('seaborn-v0_8-deep')

        # Generate the selected graph
        if graph_type == "Horizontal Bar Chart":
            graph_data.plot(kind="barh", ax=self.ax).legend(loc='upper left', bbox_to_anchor=(1, 1))
            self.ax.set_ylabel(f'{selected_measure} Value')

        elif graph_type == "Vertical Bar Chart":
            graph_data.plot(kind="bar", ax=self.ax).legend(loc='upper left', bbox_to_anchor=(1, 1))
            self.ax.set_ylabel(f'{selected_measure} Value')

        elif graph_type == "Pie Chart":
            self.figure.clf()  # Make sure to fully clear everything again here too
            num_cols = len(selected_columns)
            for i, col in enumerate(selected_columns, 1):
                ax = self.figure.add_subplot(1, num_cols, i)
                graph_data[col].plot(kind="pie", ax=ax, autopct='%1.1f%%', title=col)
                ax.set_ylabel('')  # Remove Y-axis label
            self.canvas_widget.draw()

        elif graph_type == "Normal Distribution Curve":
            if selected_measure == "Binomial Distribution":
                n_trails, prob = Controller.get_last_binomial_params()
                if n_trails is None or prob is None:
                    messagebox.showerror("Error",
                                         "No binomial parameters found. Please run Binomial Distribution measure first.")
                    return
                mean = n_trails * prob
                std_dev = np.sqrt(n_trails * prob * (1 - prob))
                if n_trails * prob < 5 or n_trails * (1 - prob) < 5:
                    messagebox.showwarning(
                        "Warning",
                        "Normal approximation may not be accurate for small n or extreme probabilities. "
                        "Please consider using Vertical Bar Chart instead."
                    )

                # Generate values for the x-axis
                x_vals = np.linspace(0, n_trails, 1000)
                normal_approx = stats.norm.pdf(x_vals, mean, std_dev)

                # Plot the normal approximation curve
                self.ax.plot(x_vals, normal_approx, color='green',
                             label=f"Normal Approximation (μ={mean:.2f}, σ={std_dev:.2f})")
                self.ax.set_xlabel("Number of Successes (k)")
                self.ax.set_ylabel("Probability Density")
                self.ax.legend()

            elif selected_measure == "Percentiles":
                # Plot the percentiles for the selected measure
                self.plot_normal_distribution_with_percentiles(graph_data, data_frame, selected_columns)

            elif selected_measure == "Standard Deviation":
                try:
                    # Clear previous plot
                    self.figure.clf()
                    self.ax = self.figure.add_subplot(111)

                    # Get the original data
                    table_controller = self.get_table_controller()

                    if not table_controller:
                        messagebox.showerror("Error", "Could not access table data")
                        return

                    data_frame = self.main_control.load_data_from_table(table_controller)

                    if data_frame.empty:
                        messagebox.showerror("Error", "No data available for plotting")
                        return

                    # Select only numeric columns
                    numeric_cols = data_frame.select_dtypes(include=['number']).columns

                    if len(numeric_cols) == 0:
                        messagebox.showerror("Error", "No numeric columns found for calculation")
                        return

                    # Calculate standard deviation for each column
                    std_values = {}
                    for col in numeric_cols:
                        col_data = data_frame[col].dropna()
                        if len(col_data) > 1:  # Need at least 2 points for std dev
                            std = col_data.std()
                            std_values[col] = std

                    if not std_values:
                        messagebox.showerror("Error", "Could not calculate standard deviation")
                        return

                    # Plot normal distribution of the actual data with std dev in legend
                    for col, std in std_values.items():
                        col_data = data_frame[col].dropna()

                        # Plot KDE of actual data
                        sns.kdeplot(col_data, ax=self.ax, fill=True,
                                    label=f"{col} (σ={std:.2f})")

                        # Calculate reference values
                        mean_val = col_data.mean()

                        # Add vertical lines with labels
                        mean_line = self.ax.axvline(mean_val, color='r', linestyle='--', alpha=0.7,
                                                    label=f'{col} Mean ({mean_val:.2f})')
                        upper_line = self.ax.axvline(mean_val + std, color='g', linestyle=':', alpha=0.7,
                                                     label=f'{col} Mean+σ ({mean_val + std:.2f})')
                        lower_line = self.ax.axvline(mean_val - std, color='g', linestyle=':', alpha=0.7,
                                                     label=f'{col} Mean-σ ({mean_val - std:.2f})')

                        # Add text labels near the lines
                        y_max = self.ax.get_ylim()[1]
                        offset = y_max * 0.05  # Small offset from lines
                        self.ax.text(mean_val, y_max - offset, 'Mean',

                                     color='red', ha='center', va='bottom',
                                     bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))

                        self.ax.text(mean_val + std, y_max - offset * 2, '+σ',
                                     color='green', ha='center', va='bottom',
                                     bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))

                        self.ax.text(mean_val - std, y_max - offset * 2, '-σ',
                                     color='green', ha='center', va='bottom',
                                     bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))

                        # Shade the ±1σ region
                        self.ax.axvspan(mean_val - std, mean_val + std,
                                        color='green', alpha=0.1,
                                        label=f'{col} ±1σ range')

                    # Add plot decorations
                    self.ax.set_title("Data Distribution with Standard Deviation")
                    self.ax.set_xlabel("Values")
                    self.ax.set_ylabel("Density")

                    # Create legend with all elements
                    handles, labels = self.ax.get_legend_handles_labels()

                    # Remove duplicate labels while preserving order
                    unique = [(h, l) for i, (h, l) in enumerate(zip(handles, labels)) if l not in labels[:i]]
                    self.ax.legend(*zip(*unique), loc='upper right')
                    self.canvas_widget.draw()

                except Exception as e:
                    messagebox.showerror("Error", f"Failed to plot Standard Deviation: {str(e)}")
                    print(f"Error plotting Std Dev: {e}")

            elif selected_measure == "Variance":
                try:
                    # Clear previous plot
                    self.figure.clf()
                    self.ax = self.figure.add_subplot(111)

                    # Get the original data, not just the variance values
                    table_controller = self.get_table_controller()

                    if not table_controller:
                        messagebox.showerror("Error", "Could not access table data")
                        return

                    data_frame = self.main_control.load_data_from_table(table_controller)

                    if data_frame.empty:
                        messagebox.showerror("Error", "No data available for plotting")
                        return

                    # Select only numeric columns
                    numeric_cols = data_frame.select_dtypes(include=['number']).columns
                    if len(numeric_cols) == 0:
                        messagebox.showerror("Error", "No numeric columns found for variance calculation")
                        return

                    # Calculate and display variance for each column
                    variance_values = data_frame[numeric_cols].var()

                    # Plot normal distribution of the actual data
                    for col in numeric_cols:
                        col_data = data_frame[col].dropna()
                        if len(col_data) > 1:  # Need at least 2 points for variance
                            # Plot KDE of actual data
                            sns.kdeplot(col_data, ax=self.ax, fill=True, label=f"{col} (σ²={variance_values[col]:.2f})")
                            # Add vertical line at mean
                            mean_val = col_data.mean()
                            self.ax.axvline(mean_val, color='r', linestyle='--', alpha=0.5)

                    if len(numeric_cols) > 0:
                        self.ax.set_title("Data Distribution with Variance")
                        self.ax.set_xlabel("Values")
                        self.ax.set_ylabel("Density")
                        self.ax.legend()
                        self.canvas_widget.draw()
                    else:
                        messagebox.showwarning("Warning", "No plottable data found")


                except Exception as e:
                    messagebox.showerror("Error", f"Failed to plot variance: {str(e)}")
                    print(f"Error plotting variance: {e}")

            elif selected_measure == "Coefficient Of Variation":
                try:
                    # Clear previous plot
                    self.figure.clf()
                    self.ax = self.figure.add_subplot(111)

                    # Get the original data
                    table_controller = self.get_table_controller()
                    if not table_controller:
                        messagebox.showerror("Error", "Could not access table data")
                        return

                    data_frame = self.main_control.load_data_from_table(table_controller)
                    if data_frame.empty:
                        messagebox.showerror("Error", "No data available for plotting")
                        return

                    # Select only numeric columns
                    numeric_cols = data_frame.select_dtypes(include=['number']).columns

                    if len(numeric_cols) == 0:
                        messagebox.showerror("Error", "No numeric columns found for calculation")
                        return

                    # Calculate coefficient of variation for each column
                    cv_values = {}
                    for col in numeric_cols:
                        col_data = data_frame[col].dropna()
                        if len(col_data) > 1 and col_data.mean() != 0:  # Need at least 2 points and non-zero mean
                            cv = col_data.std() / col_data.mean()
                            cv_values[col] = cv

                    if not cv_values:
                        messagebox.showerror("Error", "Could not calculate CV (possibly zero mean values)")
                        return

                    # Plot normal distribution of the actual data with CV in legend
                    for col, cv in cv_values.items():
                        col_data = data_frame[col].dropna()
                        # Plot KDE of actual data
                        sns.kdeplot(col_data, ax=self.ax, fill=True,
                                    label=f"{col} (CV={cv:.2f})")

                        # Calculate reference values
                        mean_val = col_data.mean()
                        std_val = col_data.std()

                        # Add vertical lines with labels
                        mean_line = self.ax.axvline(mean_val, color='r', linestyle='--', alpha=0.7,
                                                    label=f'{col} Mean ({mean_val:.2f})')

                        upper_line = self.ax.axvline(mean_val + std_val, color='g', linestyle=':', alpha=0.7,
                                                     label=f'{col} Mean+1σ ({mean_val + std_val:.2f})')

                        lower_line = self.ax.axvline(mean_val - std_val, color='g', linestyle=':', alpha=0.7,
                                                     label=f'{col} Mean-1σ ({mean_val - std_val:.2f})')

                        # Add text labels near the lines
                        y_max = self.ax.get_ylim()[1]
                        offset = y_max * 0.05  # Small offset from lines

                        self.ax.text(mean_val, y_max - offset, 'Mean',
                                     color='red', ha='center', va='bottom',
                                     bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))

                        self.ax.text(mean_val + std_val, y_max - offset * 2, '+1σ',
                                     color='green', ha='center', va='bottom',
                                     bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))

                        self.ax.text(mean_val - std_val, y_max - offset * 2, '-1σ',
                                     color='green', ha='center', va='bottom',
                                     bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))

                    # Add plot decorations
                    self.ax.set_title("Data Distribution with Coefficient of Variation")
                    self.ax.set_xlabel("Values")
                    self.ax.set_ylabel("Density")

                    # Create legend with all elements
                    handles, labels = self.ax.get_legend_handles_labels()
                    # Remove duplicate labels while preserving order
                    unique = [(h, l) for i, (h, l) in enumerate(zip(handles, labels)) if l not in labels[:i]]
                    self.ax.legend(*zip(*unique), loc='upper right')

                    self.canvas_widget.draw()

                except Exception as e:
                    messagebox.showerror("Error", f"Failed to plot Coefficient of Variation: {str(e)}")
                    print(f"Error plotting CV: {e}")

            elif isinstance(graph_data, pd.Series):
                sns.kdeplot(graph_data, ax=self.ax, fill=True, label=selected_measure)

            else:
                for col in selected_columns:
                    if col in data_frame.columns:
                        col_data = pd.to_numeric(data_frame[col], errors='coerce').dropna()
                        if not col_data.empty:
                            sns.kdeplot(col_data, ax=self.ax, fill=True, label=col)
                            self.ax.legend([f"{col}"])

        elif graph_type == "Scatter Plot":  # X-Y Graph
            if selected_measure == "Correlation":
                x = graph_data[selected_columns[0]]
                y = graph_data[selected_columns[1]]

                self.ax.scatter(x, y, label=groupby_column)
                self.ax.set_xlabel(selected_columns[0])
                self.ax.set_ylabel(selected_columns[1])

                coefficients = np.polyfit(x, y, 1)
                trend = np.poly1d(coefficients)
                self.ax.plot(x, trend(x), 'r--', label='Trend Line')
            if selected_measure == "Spearman Correlation":
                x = graph_data[selected_columns[0]]
                y = graph_data[selected_columns[1]]

                self.ax.scatter(x, y, label=groupby_column)
                self.ax.set_xlabel(selected_columns[0])
                self.ax.set_ylabel(selected_columns[1])

                coefficients = np.polyfit(x, y, 1)
                trend = np.poly1d(coefficients)
                self.ax.plot(x, trend(x), 'r--', label='Trend Line')
            if selected_measure == "Least Square Line":
                x = graph_data[selected_columns[0]]  # should be graphed on the horizontal
                y = graph_data[selected_columns[1]]  # vertical

                coefficients = np.polyfit(x, y, 1)
                slope = coefficients[0]
                intercept = coefficients[1]

                # Create the line of best fit
                line = slope * x + intercept
                # Plot the original data points
                self.ax.scatter(x, y, label='Data Points')
                # Plot the least squares line
                self.ax.plot(x, line, color='red', label='Least Square Line')

            else:
                for col in selected_columns:
                    self.ax.scatter(graph_data.index, graph_data[col], label=col)

            self.ax.legend()

        # Set labels and title
        column_names = ", ".join(selected_columns)
        if groupby_column == "No Grouping":
            self.ax.set_title(f"{selected_measure} of {column_names}")
        else:
            self.ax.set_title(f"{selected_measure} of {column_names} by {groupby_column}")

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

        self.toolbarBackground = self.canvas.create_rectangle(0, 0, 100, self.winfo_height(), fill="#D9D9D9",
                                                              outline="")
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
        results_bg_color = self.controller.colors.get_color("results_bg")  # Specific results area color

        # Update Frames
        if hasattr(self, 'toolbar_frame'): self.toolbar_frame.configure(bg=toolbar_bg_color)
        if hasattr(self, 'main_frame'): self.main_frame.configure(bg=background_color)
        if hasattr(self, 'button_frame'): self.button_frame.configure(bg=background_color)  # Button is ttk
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
