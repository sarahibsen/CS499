import tkinter as tk
from tkinter import Canvas, Button, PhotoImage, filedialog
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
        self.geometry("900x700")
        self.configure(bg="#FFFFFF")
        #self.resizable(False, False)
        self.title("Statistical Analyzer")

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
    # TODO: Change this path
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
            self, bg="#FFFFFF", height=700, width=900, bd=0,
            highlightthickness=0, relief="ridge"
        )
        canvas.pack(fill="both", expand=True)

        # ----- Background ----- #
        canvas.create_rectangle(0, 0, 900, 700, fill="#FFFFFF", outline="")

        # ----- Text ----- #
        canvas.create_text(80, 118, anchor="nw", text="TEXT", fill="#000000", font=("Roboto Light", -96))
        canvas.create_text(110, 234, anchor="nw", text="Lorem ipsum dolor", fill="#000000", font=("Roboto Regular", -24))
        canvas.create_text(151, 256, anchor="nw", text="sit amet", fill="#000000", font=("Roboto SemiBold", -24))

        # ----- Buttons ----- #
        self.continue_button = add_button(
            canvas, 70, 584, 300, 60, "button_3.png", "button_hover_3.png",
            "Button 3 clicked!", lambda: controller.show_page("MeasureSelectionPage")
        )
        self.continue_button.place_forget()  # Hide continue button initially

        upload_data_button = add_button(
            canvas, 70, 355, 300, 60, "upload_data_button.png",
            "upload_data_button_hover.png", "Upload data button clicked!", self.upload_data
        )
        upload_data_button.place()

        enter_data_button = add_button(
            canvas, 70, 432, 300, 60, "enter_data_button.png",
            "enter_data_button_hover.png", "Enter data button clicked!", self.enter_data
        )
        enter_data_button.place()

        # ----- Images ----- #
        # TODO: This is serving as a placeholder
        image_image_1 = PhotoImage(file=relative_to_assets("image_1.png"))
        canvas.create_image(662, 350, image=image_image_1)
        self.image_image_1 = image_image_1  # Keep a reference to avoid garbage collection

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

        # Create a canvas
        canvas = Canvas(
            self, bg="#FFFFFF", height=700, width=900, bd=0,
            highlightthickness=0, relief="ridge"
        )
        canvas.pack(fill="both", expand=True)

        canvas.create_text(27, 0, anchor="nw", text="Select a statistic to calculate:",
                           fill="#000000", font=("Roboto Light", 24))
# TODO: create a drop down menu for the user to select the statistic 

        # ----- Background ----- #
        canvas.create_rectangle(0, 0, 900, 700, fill="#FFFFFF", outline="")

        # ----- Text ----- #
        canvas.create_text(27.0, 0.0, anchor="nw", text="TEXT", fill="#000000", font=("Roboto Light", 48 * -1))

        # ----- Buttons ----- #
        button_1 = add_button(
            canvas, 562, 607, 300, 60, "button_1.png", "button_hover_1.png",
            "Button 1 clicked!", self.button_1_placeholder
        )
        button_1.place()

        # ----- Other Elements ----- #
        # TODO: These rectangles are placeholders for measure and graph selection
        canvas.create_rectangle(57.0, 124.0, 419.0, 577.0, fill="#D9D9D9", outline="")
        canvas.create_rectangle(500.0, 124.0, 862.0, 577.0, fill="#D9D9D9", outline="")

    def button_1_placeholder(self):
        """
        Display continue button when either the enter data or upload data button is clicked.
        """
        print("button 1 called")

        # TODO: Use input validation to determine whether continue button should display after user
        #   selects the measures and graphs
        self.controller.show_page("LaunchPage")


# Run the application
app = App()
app.mainloop()
