import tkinter as tk
from tkinter import Canvas, Button, PhotoImage, filedialog, ttk, messagebox
import pandas as pd
import numpy as np
from pathlib import Path

from Table import TableView
from tkinter import simpledialog # for input dialog in the statistic


from main_controller import Controller # using the controller class to handle the communication between all components 
class App(tk.Tk):
    """
    Main application class to handle multiple pages.
    """
    def __init__(self):
        super().__init__()
        # initialize the controller
        
        # set window to be responsive to the device it's running on
        width = self.winfo_screenwidth()
        height = self.winfo_screenheight()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.geometry("%dx%d" % (width, height))  # Default size
        self.state("zoomed")

        self.configure(bg="#FFFFFF")
        self.title("Statistical Analyzer")

        # Enable full screen mode
        # self.attributes("-fullscreen", True)  # Enable full screen mode

        # Bind the Escape key to exit full screen mode
        # self.bind("<Escape>", self.toggle_fullscreen)

        # Container to hold all pages
        self.container = tk.Frame(self)
        self.container.grid(row=0, column=0, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Dictionary to store pages
        self.pages = {}

        # Initialize pages
        self.add_page("LaunchPage", LaunchPage)
        self.add_page("MeasureSelectionPage", MeasureSelectionPage)
        self.add_page("DashboardPage", DashboardPage)

        # Add CustomTable which includes the GUI toolbar

        # Show the initial page
        self.show_page("LaunchPage")

    def toggle_fullscreen(self, event=None):
        """
        Toggle full screen mode on/off when the Escape key is pressed.
        """
        self.attributes("-fullscreen", not self.attributes("-fullscreen"))

    def add_page(self, page_name, page_class):
        """
        Add a new page to the application.

        Args:
            page_name (str): Unique name for the page.
            page_class (class): Class implementing the page.
        """
        #self.container.grid(row=0, column=0, sticky="nsew")
        page = page_class(self.container, self)
        self.pages[page_name] = page
        page.grid(row=0, column=0, sticky="nsew")
        

    def show_page(self, page_name):
        """
        Display the specified page.

        Args:
            page_name (str): Name of the page to display.
        """
        page = self.pages[page_name]
        page.tkraise()

def relative_to_assets(path: str) -> Path:
    """
    Get the full path to a resource file located in the assets directory.
    """
    assets_path = Path(__file__).parent / Path(
        r"assets"

    )
    return assets_path / Path(path)


class BasePage(tk.Frame):
    """
    Base class for all pages.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller


def add_button(canvas, x, y, w, h, normal_image, hover_image, message, callback=None):
    """
    Add a button with hover effects to the canvas.

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

    # Command to handle button click and callback execution
    def button_command():
        print(message)
        if callback:  # Check if callback is not None
            callback()

    button = Button(
        canvas,
        image=normal_image_file,
        borderwidth=0,
        highlightthickness=0,
        command=button_command,  # Use the defined command
        relief="flat"
    )
    button.place(x=x, y=y, width=w, height=h)
    button.image = normal_image_file  # Keep reference to avoid garbage collection

    # Define hover behavior
    def on_hover(event):
        button.config(image=hover_image_file)

    def on_leave(event):
        button.config(image=normal_image_file)

    button.bind('<Enter>', on_hover)
    button.bind('<Leave>', on_leave)

    return button


class LaunchPage(BasePage):
    """
    Start page of the application.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        # Create a canvas
        canvas = Canvas(
            self, bg="#FFFFFF", height=832, width=1280, bd=0,
            highlightthickness=0, relief="ridge"
        )
        canvas.pack(fill="both", expand=True)

        # ----- Background ----- #
        canvas.create_rectangle(0, 0, 1280, 832, fill="#FFFFFF", outline="")

        # ----- Buttons ----- #
        self.continue_button = add_button(
            canvas, 85, 589, 383.1111145019531, 64.03428649902344, "0_button_1.png", "0_button_hover_1.png",
            "Button 1 clicked!", lambda: controller.show_page("MeasureSelectionPage")
        )
        self.continue_button.place()

        # ----- Images ----- #
        image_image_1 = PhotoImage(file=relative_to_assets("0_image_1.png"))
        canvas.create_image(227, 186, image=image_image_1)
        self.image_image_1 = image_image_1  # Keep a reference to avoid garbage collection

        image_image_2 = PhotoImage(file=relative_to_assets("0_image_2.png"))
        canvas.create_image(250, 343, image=image_image_2)
        self.image_image_2 = image_image_2  # Keep a reference to avoid garbage collection

        # TODO: This is serving as a placeholder
        image_image_3 = PhotoImage(file=relative_to_assets("0_image_3.png"))
        canvas.create_image(1000, 415.125, image=image_image_3)
        self.image_image_3 = image_image_3  # Keep a reference to avoid garbage collection



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
        
        # Data Table Frame
        self.table_frame = tk.Frame(self)

        self.table_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)

        self.table = TableView(self.table_frame)
        self.table.grid(row=0, column=0, sticky='nsew')
              

        # Add Calculate Button
        self.calculate_button = ttk.Button(self.measurement_frame, text="Calculate Measures", command=self.calculate_statistics)
        self.calculate_button.grid(row=0, column=1, padx=10, pady=10, sticky='w')


## TODO: change this to grab data types from main.py
        # ComboBox for Data Types
        #self.data_type_options = ["Nominal", "Ordinal", "Discrete", "Continuous"]
        self.data_type_options = list(Controller.get_data_type_classes().keys())
        self.data_type_dropdown = ttk.Combobox(self.measurement_frame, values=self.data_type_options, font=("Roboto", 14), state="readonly")

        #self.data_type_dropdown.place(x=151, y=300, width=351, height=57)
        self.data_type_dropdown.grid(row=1, column=1, padx=10, pady=10, sticky='nw')

        self.data_type_dropdown.set("Select Data Type")
        self.data_type_dropdown.bind("<<ComboboxSelected>>", self.on_data_type_selected)

        # Statistical Measures Listbox

        self.stat_measures_listbox = tk.Listbox(self.measurement_frame, font=("Roboto", 14), selectmode="multiple", exportselection=False)

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
        self.canvas.create_rectangle(0, 0, 100, 832, fill="#D9D9D9", outline="")
        self.data_page_button = add_button(
            self.canvas, 18, 50, 63, 63, "button_4.png", "button_hover_4.png",
            "Data page button clicked!"
        )

        #self.data_page_button.place()
        self.data_page_button.grid(row=0, column=0, padx=10, pady=10, sticky="ns")

        self.dashboard_page_button = add_button(
            self.canvas, 18, 163, 63, 63, "button_5.png", "button_hover_5.png",
            "Dashboard page button clicked!", lambda: controller.show_page("DashboardPage")
        )

        # self.dashboard_page_button.place()
        self.dashboard_page_button.grid(row=1, column=0, padx=10, pady=10, sticky="ns")

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
        # make the names appear better
       
        # measures = []
        # if selected_data_type == "Nominal":
        #     measures = ["Mode", "Frequency"]
        # elif selected_data_type == "Ordinal":
        #     measures = ["Median", "Mode", "Frequency", "Percentiles", "Rank Sum", "Spearman Coefficient"]
        # elif selected_data_type == "Discrete":
        #     measures = ["Mean", "Median", "Mode", "Standard Deviation", "Variance", "Percentiles", "Probability Distribution", "Binomial Distribution"]
        # elif selected_data_type == "Continuous":
        #     measures = ["Mean", "Median", "Mode", "Standard Deviation", "Variance", "Percentiles", "Probability Distribution", "Binomial Distribution", 
        #                 "Least Square Line", "Chi-Square Test", "Correlation Coefficient", "Sign Test"]

        # for measure in measures:
        #     self.stat_measures_listbox.insert(tk.END, measure)


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
    Dashboard page of the application. Users what graphs they would like to display.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        # Create a canvas
        self.canvas = Canvas(self, bg="#FFFFFF", bd=0, highlightthickness=0, relief="ridge")
        self.canvas.pack(fill="both", expand=True)

        # ----- Background ----- #
        self.canvas.create_rectangle(0, 0, 1280, 832, fill="#FFFFFF", outline="")

        # ----- Buttons ----- #
        # TODO: Add functionality to buttons
        self.add_graph_button = add_button(
            self.canvas, 566, 33, 200, 72.0187759399414, "add_graph_button.png", "add_graph_button_hover.png",
            "Add graph page button clicked!"
        )
        self.add_graph_button.place()
        self.save_results_button = add_button(
            self.canvas, 795, 33, 215, 72.0187759399414, "button_2.png", "button_hover_2.png",
            "Save Results button clicked!"
        )
        self.save_results_button.place()
        self.export_data_button = add_button(
            self.canvas, 1039, 33, 215, 72.0187759399414, "export_data_button.png", "export_data_button_hover.png",
            "Add graph page button clicked!"
        )
        self.export_data_button.place()

        # ----- Dashboard Area ----- #
        # TODO: Placeholder, add matplotlib widget
        self.canvas.create_rectangle(129, 153, 1252, 807, fill="#D9D9D9", outline="")

        # ----- Toolbar ----- #
        self.canvas.create_rectangle(0, 0, 100, 832, fill="#D9D9D9", outline="")
        self.data_page_button = add_button(
            self.canvas, 18, 50, 63, 63, "button_4.png", "button_hover_4.png",
            "Data page button clicked!", lambda: controller.show_page("MeasureSelectionPage")
        )
        self.data_page_button.place()
        self.dashboard_page_button = add_button(
            self.canvas, 18, 163, 63, 63, "button_5.png", "button_hover_5.png",
            "Dashboard page button clicked!"
        )
        self.dashboard_page_button.place()

# Run the application
app = App()
app.mainloop()