import tkinter as tk
from tkinter import Canvas, Button, PhotoImage, filedialog, ttk, messagebox, Label
from tkinter.ttk import Button, Style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd
import numpy as np
from pathlib import Path
from Table import TableView
from statisticsLogic import *
from main import *
from main_controller import Controller # using the controller class to handle the communication between all components 

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


# ----- GUI Page Classes ----- #
class App(tk.Tk):
    """
    Main application class to handle multiple pages.
    """

    def __init__(self):
        super().__init__()

        # Configure window
        self.configure(bg="white")
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
            ("DashboardPage", DashboardPage)
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


class BasePage(tk.Frame):
    """Base class for all pages."""

    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller


class LaunchPage(BasePage):
    """Start page of the application."""

    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        # Configure row weights
        for i in range(7):
            self.rowconfigure(i, weight=1)

        # Configure column weights
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Button style
        style = Style()
        style.configure(
            "TButton", font=("Arial", 20), background="white", height=50,
            width=20, pady=20, ipadx=20, ipady=10, relief="groove",
        )

        # ----- Image Area (Placeholder for now) ----- #
        self.canvas = Canvas(self, bg="lightblue", bd=0, highlightthickness=0, relief="ridge")
        self.canvas.grid(column=1, rowspan=7, sticky="nsew", padx=20, pady=20)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)

        # ----- Text Area ----- #
        tk.Label(self, text="STATS", bg="white", font=("Arial", 40)).grid(column=0, row=1, sticky="nsew")
        tk.Label(self, text="Lorem ipsum dolor \n sit amet", bg="white", font=("Arial", 25)).grid(column=0, row=2,
                                                                                                  sticky="nsew")
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
        self.controller = controller    

        self.grid_rowconfigure(0, weight = 1)
        self.grid_columnconfigure(2, weight = 2)

        # Create a canvas
        self.canvas = Canvas(self, bg="#FFFFFF", bd=0, highlightthickness=0, relief="ridge")
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.measurement_frame = tk.Frame(self)
        self.measurement_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nw")
        
        # ----- Data Table ----- #
        self.table_frame = tk.Frame(self)

        self.table_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)

        self.table = TableView(self.table_frame)
        self.table.grid(row=0, column=0, sticky='nsew')

        # ----- Measure Selection Area ----- #
        # Add Calculate Button
        self.calculate_button = ttk.Button(self.measurement_frame, text="Calculate Measures",
                                           command=self.calculate_statistics)
        self.calculate_button.grid(row=0, column=1, padx=10, pady=10, sticky='w')


## TODO: change this to grab data types from main.py
        # ComboBox for Data Types
        self.data_type_options = ["Nominal", "Ordinal", "Discrete", "Continuous"]
        self.data_type_dropdown = ttk.Combobox(self.measurement_frame, values=self.data_type_options,
                                               font=("Roboto", 14), state="readonly")

        #self.data_type_dropdown.place(x=151, y=300, width=351, height=57)
        self.data_type_dropdown.grid(row=1, column=1, padx=10, pady=10, sticky='nw')

        self.data_type_dropdown.set("Select Data Type")
        self.data_type_dropdown.bind("<<ComboboxSelected>>", self.on_data_type_selected)

        # Statistical Measures Listbox
        self.stat_measures_listbox = tk.Listbox(self.measurement_frame, font=("Roboto", 14), selectmode="multiple",
                                                exportselection=False)

        #self.stat_measures_listbox.place(x=151, y=380, width=351, height=100)
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

        #self.selected_stat_label.place(x=151, y=500, width=351, height=50)
        self.selected_stat_label.grid(row=3, column=1, padx=10, pady=10, sticky='nw')

        # Bind listbox selection
        self.stat_measures_listbox.bind("<<ListboxSelect>>", self.on_stat_measure_selected)

        # ----- Toolbar ----- #
        self.toolbarBackground = self.canvas.create_rectangle(0, 0, 100, self.winfo_height(), fill="#D9D9D9",
                                                              outline="")
        self.canvas.bind("<Configure>", self.resize_rectangle)  # Bind the resize event

        self.data_page_button = add_button(
            self.canvas, 18, 50, 63, 63, "button_4.png", "button_hover_4.png",
            "Data page button clicked!"
        )
        self.data_page_button.grid(row=0, column=0, padx=10, pady=10, sticky="ns")

        self.dashboard_page_button = add_button(
            self.canvas, 18, 163, 63, 63, "button_5.png", "button_hover_5.png",
            "Dashboard page button clicked!", lambda: controller.show_page("DashboardPage")
        )
        self.dashboard_page_button.grid(row=1, column=0, padx=10, pady=10, sticky="ns")

    def resize_rectangle(self, event):
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
        measures = []
        if selected_data_type == "Nominal":
            measures = ["Mode", "Frequency"]
        elif selected_data_type == "Ordinal":
            measures = ["Median", "Mode", "Frequency", "Percentiles", "Rank Sum", "Spearman Coefficient"]
        elif selected_data_type == "Discrete":
            measures = ["Mean", "Median", "Mode", "Standard Deviation", "Variance", "Percentiles", "Probability Distribution", "Binomial Distribution"]
        elif selected_data_type == "Continuous":
            measures = ["Mean", "Median", "Mode", "Standard Deviation", "Variance", "Percentiles", "Probability Distribution", "Binomial Distribution", 
                        "Least Square Line", "Chi-Square Test", "Correlation Coefficient", "Significance Test"]

        for measure in measures:
            self.stat_measures_listbox.insert(tk.END, measure)


    def on_stat_measure_selected(self, event):
        # Get selected items from the listbox
        selected_indices = self.stat_measures_listbox.curselection()
        selected_stats = [self.stat_measures_listbox.get(i) for i in selected_indices]

        # Limit selection to 3 measures
        if len(selected_stats) > 3:
            self.stat_measures_listbox.selection_clear(selected_indices[0])  # Remove the first selected item

        # Update the label with selected measures
        self.selected_stat_label.config(
            text=f"Selected Measures: {', '.join(selected_stats)}" if selected_stats else "Selected Measures: None"
        )

    def calculate_statistics(self):
        if not hasattr(self.table.controller, 'get_table_selection'):
            messagebox.showerror("Error", "Table not initialized.")
            return
        
        self.controller = Controller()

        selected_data_type = self.data_type_dropdown.get()
        selected_measures = [self.stat_measures_listbox.get(i) for i in self.stat_measures_listbox.curselection()]
        
        variance_type = None # default to none unless variance is selected
        if "Variance" in selected_measures:
            variance_type = simpledialog.askstring(
                "Variance Type",
                "Enter the type of variance (Population or Sample):",
                initialvalue="Population"
            )
            if variance_type not in ["Population", "Sample"]:
                messagebox.showerror("Error", "Invalid variance type.")
                return
        data_frame = self.controller.load_data_from_table(self.table.controller)
        print(f"Final Data Before Validation:\n{data_frame}")  # Final confirmation
        
        if data_frame.empty:
            messagebox.showerror("Error", "No data to analyze.")
            return
        
        if not self.controller.validate_data(data_frame):
            messagebox.showerror("Error", "Data validation failed.")
            return

        results = self.controller.perform_statistics(data_frame, selected_measures, selected_data_type, variance_type)

        if results:
            result_str = "\n".join([f"{key}: {value}" for key, value in results.items()])
            messagebox.showinfo("Calculated Statistics", result_str)
           # self.controller.export_results(results)

    def get_table_data(self):
        # Fetch table data from the CustomTable widget

        return self.table.celldType()


class DashboardPage(BasePage):
    """
    Dashboard page of the application. Users can select what graphs they would like to display.
    """

    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        # Configure rows and columns
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Create a canvas
        self.canvas = Canvas(self, bg="#FFFFFF", bd=0, highlightthickness=0, relief="ridge")
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # ----- Toolbar ----- #
        self.toolbarBackground = self.canvas.create_rectangle(0, 0, 100, self.winfo_height(), fill="#D9D9D9", outline="")
        self.canvas.bind("<Configure>", self.resize_rectangle)  # Bind the resize event

        self.data_page_button = add_button(
            self.canvas, 18, 50, 63, 63, "button_4.png", "button_hover_4.png",
            "Data page button clicked!", lambda: controller.show_page("MeasureSelectionPage")
        )
        self.data_page_button.grid(row=0, column=0, padx=10, pady=10, sticky="ns")

        self.dashboard_page_button = add_button(
            self.canvas, 18, 163, 63, 63, "button_5.png", "button_hover_5.png",
            "Dashboard page button clicked!", lambda: controller.show_page("DashboardPage")
        )
        self.dashboard_page_button.grid(row=1, column=0, padx=10, pady=10, sticky="ns")

        # ----- Dashboard Area ----- #
        self.dashboard_frame = tk.Frame(self, bg="#FFFFFF")
        self.dashboard_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.dashboard_frame.grid_rowconfigure(0, weight=1)
        self.dashboard_frame.grid_columnconfigure(0, weight=1)

        # Create a figure for the graph
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.figure.add_subplot(111)

        # Add some example data to plot
        x = [1, 2, 3, 4, 5]
        y = [1, 4, 9, 16, 25]
        self.ax.plot(x, y, label="Example Line Plot")

        # Set plot labels and title
        self.ax.set_title("Example Graph")
        self.ax.set_xlabel("X Axis")
        self.ax.set_ylabel("Y Axis")
        self.ax.legend()

        # Create a canvas widget to embed the matplotlib plot
        self.canvas_widget = FigureCanvasTkAgg(self.figure, master=self.dashboard_frame)
        self.canvas_widget.draw()

        # Place the matplotlib canvas in the dashboard area
        self.canvas_widget.get_tk_widget().grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # ----- Buttons ----- #
        self.add_graph_button = Button(
            self.dashboard_frame, text="Add Graph", style="TButton",
            command=lambda: print("Add Graph button clicked!")
        )
        self.add_graph_button.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.save_results_button = Button(
            self.dashboard_frame, text="Save Results", style="TButton",
            command=lambda: print("Save Results button clicked!")
        )
        self.save_results_button.grid(row=1, column=0, padx=10, pady=10, sticky="e")

        self.export_data_button = Button(
            self.dashboard_frame, text="Export Data", style="TButton",
            command=lambda: print("Export Data button clicked!")
        )
        self.export_data_button.grid(row=1, column=0, padx=10, pady=10, sticky="e")

    def resize_rectangle(self, event):
        """Resize the rectangle dynamically when the window changes size."""
        self.canvas.coords(self.toolbarBackground, 0, 0, 100, event.height)  # Adjust height dynamically


# Run the application
app = App()
app.mainloop()