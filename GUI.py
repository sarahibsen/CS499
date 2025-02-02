import tkinter as tk
from tkinter import Canvas, Button, PhotoImage, filedialog, ttk
import pandas as pd
import numpy as np
from pathlib import Path

from customTable import *
from statisticsLogic import *

class App(tk.Tk):
    """
    Main application class to handle multiple pages.
    """
    def __init__(self):
        super().__init__()
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
        r"new_assets"
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

    # TODO: Add functionality to this upload data button by finishing this function
    def upload_data(self):
        """
        Display continue button when either the enter data or upload data button is clicked.
        """
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])  
        if file_path:
            try:
                # Load the CSV data using pandas
                data = pd.read_csv(file_path)
                # Embed the custom table within this GUI
                self.display_table(data)
                
                # Store numeric data and initialize statistics logic
                numeric_data = data.select_dtypes(include=[np.number]).values.flatten()
                self.stat_logic = statistic(numeric_data)

                # Optionally show computed statistics (just to test)
                print(f"Mean: {self.stat_logic.mean()}")
                print(f"Standard Deviation: {self.stat_logic.standardDeviation()}")
            
            except Exception as e:
                print(f"Error loading CSV: {e}")
        # TODO: Use input validation to determine whether continue button should display after user enters data
        #   this function can be appended to whatever function is created to add functionality to the enter data buttons
        self.continue_button.place(x=70, y=584, width=300, height=60)

    def display_table(self, data):
        """
        embeds the custom table within the gui displaying the loaded data
        """
        # Create a Toplevel window for the popup
        popup = tk.Toplevel(self)
        popup.title("Data Table")
        popup.geometry("800x600")  # Adjust the size as needed

        # Create a frame inside the popup to host the table
        table_frame = tk.Frame(popup)
        table_frame.pack(fill='both', expand=True)

        # Create and display the table using custom GUITable
        table = GUITable(table_frame, dataframe=data, showtoolbar=True, showstatusbar=False)
        table.show()
        
        # Store shared data for statistics logic
        self.shared_data = {"numeric_data": data.select_dtypes(include=[np.number]).values.flatten()}
        
    # TODO: Decide if this button is necessary. If yes, add functionality to this button by finishing this function
    def enter_data(self):
        """
        Display continue button when either the enter data or upload data button is clicked.
        """
        user_input = simpledialog.askstring("Enter Data", "Enter numeric calues separated by commas: ")
        if user_input:
            try:
                data = np.array([float(x) for x in user_input.split(",")])
                self.stat_logic = statistic(data)
                print("Data entered successfully.")
                
                # show continue button
                self.continue_button.place(x=70, y=584, width=300, height=60)
            except ValueError:
                print("Invalid data entered. Please enter numeric values separated by commas.")

        # TODO: Use input validation to determine whether continue button should display after user enters data
        #   this function can be appended to whatever function is created to add functionality to the enter data buttons
        self.continue_button.place(x=70, y=584, width=300, height=60)


class MeasureSelectionPage(BasePage):
    """
    Measure selection page of the application. Users will select what statistical measures
    they want to use as well as what graphs they would like to display.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.controller = controller

        # Create a canvas
        self.canvas = Canvas(self, bg="#FFFFFF", bd=0, highlightthickness=0, relief="ridge")
        self.canvas.pack(fill="both", expand=True)

        # ----- Images ----- #
        # Select data type text
        image_image_3 = PhotoImage(file=relative_to_assets("1_image_3.png"))
        self.canvas.create_image(258, 153, image=image_image_3)
        self.image_image_1 = image_image_3  # Keep a reference to avoid garbage collection

        # Logo placeholder text
        image_image_2 = PhotoImage(file=relative_to_assets("1_image_2.png"))
        self.canvas.create_image(106, 51, image=image_image_2)
        self.image_image_2 = image_image_2  # Keep a reference to avoid garbage collection

        # Select statistical measures text
        image_image_4 = PhotoImage(file=relative_to_assets("1_image_4.png"))
        self.canvas.create_image(258, 335, image=image_image_4)
        self.image_image_4 = image_image_4  # Keep a reference to avoid garbage collection

        # ----- Buttons ----- #
        self.continue_button = add_button(
            self.canvas, 83, 685, 350.619873046875, 64.11334991455078, "1_button_1.png", "1_button_hover_1.png",
            "Button 1 clicked!", lambda: controller.show_page("MeasureSelectionPage")
        )
        self.continue_button.place()

        # ----- Pandas Table ----- #
        self.table_frame = tk.Frame(self)
        self.table_frame.place(x=600, y=150, width=600, height=500)
        self.table = GUITable(self.table_frame, showtoolbar=True, showstatusbar=False)
        self.table.show()

        # ----- Data Type Combobox ----- #
        self.data_type_options = ["Nominal", "Ordinal", "Discrete", "Continuous"]
        self.data_type_dropdown = ttk.Combobox(self, values=self.data_type_options, font=("Roboto", 14), state="readonly")
        self.data_type_dropdown.place(x=83, y=183, width=351, height=57)
        self.data_type_dropdown.set("Select Data Type")
        self.data_type_dropdown.bind("<<ComboboxSelected>>", self.on_data_type_selected)

        # ----- Statistical Measure Listbox (Allows Multiple Selections) ----- #
        self.stat_measures_listbox = tk.Listbox(self, font=("Roboto", 14), selectmode="multiple", exportselection=False)
        self.stat_measures_listbox.place(x=83, y=364, width=351, height=100)

        # ----- Selected Measures Label ----- #
        self.selected_stat_label = tk.Label(
            self,
            text="Selected Measures: None",
            font=("Roboto", 14),
            bg="#FFFFFF",
            wraplength=350,  # Wrap text at 350 pixels width
            justify="left",  # Align text to the left
            anchor="w"  # Start text from the left side
        )
        self.selected_stat_label.place(x=83, y=480, width=351, height=164)

        # Bind selection event
        self.stat_measures_listbox.bind("<<ListboxSelect>>", self.on_stat_measure_selected)

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
        selected_stats = [self.stat_measures_listbox.get(i) for i in self.stat_measures_listbox.curselection()]
        self.selected_stat_label.config(
            text=f"Selected Measures: {', '.join(selected_stats)}" if selected_stats else "Selected Measures: None")


# Run the application
app = App()
app.mainloop()
