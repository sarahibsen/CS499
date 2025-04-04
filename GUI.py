import tkinter as tk
from tkinter import Canvas, Button, PhotoImage, filedialog, ttk, messagebox, Label, simpledialog
from tkinter.ttk import Button, Style
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
        self.title("STATS")

        # Bind Escape key to close the application
        self.bind("<Escape>", lambda event: self.quit())

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


class BasePage(tk.Frame):
    """Base class for all pages."""

    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller


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
        image = Image.open("assets/features.png")
        photo = ImageTk.PhotoImage(image)
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
            text="Selected Measures: None",
            font=("Roboto", 14),
            bg="#FFFFFF",
            wraplength=350,
            justify="left",
            anchor="w"
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

    def import_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                data = pd.read_csv(file_path)
                # Show data in the table
                self.display_table(data)

            except Exception as e:
                print(f"Error importing CSV: {e}")

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
        print(f"Final Data Before Validation:\n{data_frame}")  # Final confirmation

        if data_frame.empty:
            messagebox.showerror("Error", "No data to analyze.")
            return

        if not self.controller.validate_data(data_frame):
            messagebox.showerror("Error", "Data validation failed.")
            return

        results = self.controller.perform_statistics(data_frame, selected_measures, selected_data_type)

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

    def update_dropdowns(self, selected_measures, selected_data_type):
        """Update the measure and column dropdowns with available options while excluding selected columns."""

        # Ensure the table controller is available
        table_controller = self.get_table_controller()
        if not table_controller:
            print("Error: Table controller not found.")
            return

        # Load data from the table
        data_frame = self.main_control.load_entire_table(table_controller)

        # Load table selection
        selected_table = self.main_control.load_data_from_table(table_controller)

        # Check if data is retrieved
        if data_frame.empty:
            messagebox.showerror("Error", "Data frame is empty, cannot populate dropdown.")
            return

        # Retrieve column names
        all_columns = list(data_frame.columns)
        selected_columns = list(selected_table.columns)

        # Exclude selected columns from all_columns
        available_columns = [col for col in all_columns if col not in selected_columns]

        # Reset dropdowns before updating
        self.column_dropdown.set("")
        self.measure_dropdown.set("")
        self.graph_dropdown.set("")

        # Update column dropdown
        self.column_dropdown["values"] = available_columns
        if available_columns:
            self.column_dropdown.set(available_columns[0] if available_columns else "")

        # Update measure dropdown
        self.measure_dropdown["values"] = selected_measures
        if selected_measures:
            self.measure_dropdown.set(selected_measures[0] if selected_measures else "")

        # Update graph dropdown
        graph_types = Controller.plots_for_data_type(selected_data_type)
        self.graph_dropdown["values"] = graph_types
        if graph_types:
            self.graph_dropdown.set(graph_types[0] if graph_types else "")

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

        # TODO: Get selected rows
        selected_rows = table_controller.get_selected_rows()
        print("Retrieved Selected Rows:", selected_rows)

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
        if not selected_measure or not groupby_column:
            messagebox.showerror("Error", "Please select both a measure and a column.")
            return None

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
            grouped_data = grouped.std()

        elif selected_measure == "Coefficient of Variation":
            grouped_std = grouped.std()
            grouped_mean = grouped.mean()
            grouped_data = grouped_std / grouped_mean

        elif selected_measure == "Percentiles":
            #TODO: Pull percentile that user enters
            grouped_data = grouped.quantile(0.25)

        elif selected_measure == "Probability Distribution":
            grouped_data = None

        elif selected_measure == "Binomial Distribution":
            grouped_data = None

        elif selected_measure == "Least Square Line":
            grouped_data = None

        elif selected_measure == "Chi Square":
            grouped_data = None

        elif selected_measure == "Correlation":
            grouped_data = grouped.corr()

        elif selected_measure == "Sign Test":
            grouped_data = None

        elif selected_measure == "Rank Sum":
            grouped_data = None

        elif selected_measure == "Spearman Correlation":
            grouped_data = None
        else:
            messagebox.showerror("Error", "Invalid measure selected.")
            return None

        # Clear previous plot
        self.ax.clear()

        # Generate the selected graph
        if graph_type == "Horizontal Bar Chart":
            grouped_data.plot(kind="barh", ax=self.ax, legend=False)
        elif graph_type == "Vertical Bar Chart":
            grouped_data.plot(kind="bar", ax=self.ax, legend=False)
        elif graph_type == "Pie Chart":
            pie_data = grouped_data[selected_columns[0]]  # Choose the first column for pie chart plotting
            pie_data.plot(kind="pie", ax=self.ax, legend=False, autopct='%1.1f%%')
        elif graph_type == "Normal Distribution Curve":
            # Plot a KDE (Kernel Density Estimation) curve to approximate normal distribution
            for col in selected_columns:
                sns.kdeplot(data_frame[col], ax=self.ax, fill=True, label=col)
            self.ax.legend()
        elif graph_type == "Scatter Plot":
            # Scatter plot (X-Y graph)
            for col in selected_columns:
                self.ax.scatter(data_frame[groupby_column], data_frame[col], label=col)
            self.ax.legend()
        else:
            messagebox.showerror("Error", "Invalid graph type selected.")
            return None

        # Set labels and title
        self.ax.set_title(f"{selected_measure} by {groupby_column}")
        self.ax.set_ylabel(selected_measure)
        self.ax.set_xlabel(groupby_column)

        # Rotate x-axis labels for better readability (except for pie charts)
        if graph_type != "Pie Chart":
            self.ax.tick_params(axis='x', rotation=45)

        # Redraw the canvas
        self.canvas_widget.draw()


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
        table = TableView(self.results_table_frame)
        table.grid(row=0, column=0, sticky='nsew')
        table.controller.update_table(headers=self.result_headers, data=self.result_rows.values())


# Run the application
app = App()
app.mainloop()
