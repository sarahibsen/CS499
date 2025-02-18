import tkinter as tk
from tkinter import Canvas, Button, PhotoImage, filedialog, ttk
import pandas as pd
import numpy as np
from pathlib import Path

from customTable import *
from statisticsLogic import *
from main import *

class App(tk.Tk):
    """
    Main application class to handle multiple pages.
    """
    def __init__(self):
        super().__init__()
        # set window to be responsive to the device it's running on
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.geometry("1280x832")  # Default size

        self.configure(bg="#FFFFFF")
        self.title("Statistical Analyzer")

        # Enable full screen mode
        # self.attributes("-fullscreen", True)  # Enable full screen mode

        # Bind the Escape key to exit full screen mode
        # self.bind("<Escape>", self.toggle_fullscreen)

        # Container to hold all pages
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

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
        canvas.create_image(227, 343, image=image_image_2)
        self.image_image_2 = image_image_2  # Keep a reference to avoid garbage collection

        # TODO: This is serving as a placeholder
        image_image_3 = PhotoImage(file=relative_to_assets("0_image_3.png"))
        canvas.create_image(902.77783203125, 415.125, image=image_image_3)
        self.image_image_3 = image_image_3  # Keep a reference to avoid garbage collection



class MeasureSelectionPage(BasePage):
    """
    Measure selection page of the application. Users will select what statistical measures
    they want to perform on the dataset.

    """
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.controller = controller

        # Create a canvas
        self.canvas = Canvas(self, bg="#FFFFFF", bd=0, highlightthickness=0, relief="ridge")
        self.canvas.pack(fill="both", expand=True)

        # Data Table Frame
        self.table_frame = tk.Frame(self)
        self.table_frame.place(x=550, y=35, width=700, height=750)
        self.table = CustomTable()
        self.toolbar =GUIToolbar(self.table_frame)

        # Add Calculate Button
        self.calculate_button = ttk.Button(self, text="Calculate Measures", command=self.calculate_statistics)
        self.calculate_button.place(x=151, y=200, width=200, height=40)


        # ComboBox for Data Types
        self.data_type_options = ["Nominal", "Ordinal", "Discrete", "Continuous"]
        self.data_type_dropdown = ttk.Combobox(self, values=self.data_type_options, font=("Roboto", 14), state="readonly")

        self.data_type_dropdown.place(x=151, y=300, width=351, height=57)

        self.data_type_dropdown.set("Select Data Type")
        self.data_type_dropdown.bind("<<ComboboxSelected>>", self.on_data_type_selected)

        # Statistical Measures Listbox
        self.stat_measures_listbox = tk.Listbox(self, font=("Roboto", 14), selectmode="multiple", exportselection=False)

        self.stat_measures_listbox.place(x=151, y=380, width=351, height=100)


        # Label to show selected measures
        self.selected_stat_label = tk.Label(
            self,
            text="Selected Measures: None",
            font=("Roboto", 14),
            bg="#FFFFFF",
            wraplength=350,
            justify="left",
            anchor="w"
        )

        self.selected_stat_label.place(x=151, y=500, width=351, height=50)


        # Bind listbox selection
        self.stat_measures_listbox.bind("<<ListboxSelect>>", self.on_stat_measure_selected)


        # ----- Toolbar ----- #
        self.canvas.create_rectangle(0, 0, 100, 832, fill="#D9D9D9", outline="")
        self.data_page_button = add_button(
            self.canvas, 18, 50, 63, 63, "button_4.png", "button_hover_4.png",
            "Data page button clicked!"
        )
        self.data_page_button.place()
        self.dashboard_page_button = add_button(
            self.canvas, 18, 163, 63, 63, "button_5.png", "button_hover_5.png",
            "Dashboard page button clicked!", lambda: controller.show_page("DashboardPage")
        )
        self.dashboard_page_button.place()

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
            measures = ["Median", "Mode", "Frequency"]
        elif selected_data_type == "Discrete":
            measures = ["Mean", "Median", "Mode", "Standard Deviation", "Variance"]
        elif selected_data_type == "Continuous":
            measures = ["Mean", "Median", "Mode", "Standard Deviation", "Variance"]

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
        selected_data_type = self.data_type_dropdown.get()
        selected_measures = [self.stat_measures_listbox.get(i) for i in self.stat_measures_listbox.curselection()]
        
        if selected_data_type == "Nominal":
            logic = nominalStatistics(self.get_table_data())
        elif selected_data_type == "Ordinal":
            logic = ordinalStatistics(self.get_table_data())
        elif selected_data_type == "Discrete":
            logic = discreteStatistics(self.get_table_data())
        elif selected_data_type == "Continuous":
            logic = continuousStatistics(self.get_table_data())
        else:
            print("Please select a data type.")
            return

        # Compute statistics based on selection
        result = []
        for measure in selected_measures:
            if measure == "Mean":
                result.append(f"Mean: {logic.mean()}")
            elif measure == "Median":
                result.append(f"Median: {logic.median()}")
            elif measure == "Mode":
                result.append(f"Mode: {logic.mode()}")
            elif measure == "Standard Deviation":
                result.append(f"Standard Deviation: {logic.standard_deviation()}")
            elif measure == "Variance":
                result.append(f"Variance: {logic.variance()}")

        # Display results in a pop-up
        messagebox.showinfo("Calculated Statistics", "\n".join(result))

    def get_table_data(self):
        # Fetch table data from the CustomTable widget
        return TkTable.celldType()



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