import pandas as pd
from tkinter import filedialog, messagebox
from tksheet import Sheet
from tkinter import ttk, PhotoImage
import tkinter as tk
from PIL import Image, ImageTk


class TableModel:
    def __init__(self):
        self.data = [[f"" for c in range(26)] for r in range(50)]  # Default table on startup

    def get_data(self):
        return self.data

    def detect_data_type(self, df):  # Sarah's data validation check
        data_types = {}
        for column in df.columns:
            if pd.api.types.is_numeric_dtype(df[column]):
                unique_values = df[column].nunique()
                if unique_values < 10:  # Threshold to differentiate discrete vs continuous
                    data_types[column] = "Discrete"
                else:
                    data_types[column] = "Continuous"
            else:
                unique_values = df[column].nunique()
                if unique_values / len(df) < 0.05:  # If few unique values relative to data size
                    data_types[column] = "Nominal"
                else:
                    data_types[column] = "Ordinal"

        return data_types

    def celldType(self, value):
        """ Infers datatype (String, Float, Int, None) of each value in table.
            This method should be called whenever we need to retrieve data from the table.
        """

        def is_float(s):
            """ Python doesn't have an implict float type check, need to make our own
                by trying to cast cell value within a try/catch block.
            """
            try:
                float(s)
                return True
            except ValueError:
                return False

        if value == "":
            return None
        elif str(
                value).strip().isnumeric():  # If csv has any leading/trailing whitespace, float datatype won't be found
            return int(value)

        elif is_float(str(value).strip()):
            return float(value)
        else:
            return value


class TableController:
    """
    TableController class is used to reference the current table to provide the current table selection of an
    existing table or import a CSV that will overwrite the current table.
    """

    operations_log = []  # Store all operations performed

    def __init__(self, parent, table):
        self.model = TableModel()
        self.parent = parent
        self.table = table

    def get_table_data(self):
        return self.model.get_data()

    # TODO: Get selected rows
    def get_selected_rows(self):
        selected_rows = self.table.get_selected_rows()
        print("Selected Rows:", selected_rows)  # Debugging statement
        return selected_rows

    def get_entire_table(self):
        """ Retrieves the entire table data from the tksheet widget and converts it into a pandas DataFrame. """

        # Get the full table data including headers
        table_data = self.table.get_sheet_data(
            get_displayed=False,
            get_header=True,  # Retrieve column headers
            get_index=False,  # Ignore row indices
            get_index_displayed=True,
            get_header_displayed=True
        )

        # Extract headers from the first row
        column_headers = table_data[0] if table_data else []

        # Extract data (excluding the first row which contains headers)
        data_rows = table_data[1:] if len(table_data) > 1 else []

        # Convert to pandas DataFrame
        df = pd.DataFrame(data_rows, columns=column_headers)

        # Drop fully empty rows and columns
        df.dropna(axis=0, how='all', inplace=True)
        df.dropna(axis=1, how='all', inplace=True)

        return df

    def update_table(self, headers=None, data=None):
        """
        Destroys the current table and creates a new table from CSV file.

        Args:
            table   (Sheet) : Existing table will be destroyed and replaced.
            headers (List)  : List of headers provided by user through CSV file if available.
            data    (List)  : List of values from CSV file if available.
        """

        if hasattr(self.table, 'destroy'):
            self.table.destroy()

        if headers is None:  # If headers are not provided, default headers will be used
            self.table = Sheet(self.parent, show_header=True, data=list(data))

        else:
            self.table = Sheet(self.parent, headers=list(headers), data=list(data))

        self.table.grid(row=0, column=0, sticky='nswe')
        self.table.enable_bindings("all", "edit_header", "edit_index", "ctrl_select")

    def get_table_selection(self):
        """ Creates a 2D list that matches the dimensions of the tksheet table and fills row list with None.
            Iterates over the entire table only updating the cells that are selected.
            Table selection is then matched with its header and converted to pandas df
        """
        self.currently_selected = self.table.get_currently_selected()

        # Gets all headers regardless of selection or if header is default
        self.column_headers = self.table[:].expand().options(table=False, header=True).data

        self.TwoDList = []

        # Creates a 2D list filled with None. The idea is to just place values that are selected.
        for c in range(0, self.table.total_columns()):
            self.column_list = []
            for r in range(0, self.table.total_rows()):
                self.column_list.append(pd.NA)

            self.TwoDList.append(self.column_list)

        for col in range(0, self.table.total_columns()):
            for row in range(0, self.table.total_rows()):
                if self.currently_selected:
                    if self.table.cell_selected(r=row, c=col, rows=True,
                                                columns=True):  # Only change the cells that are selected. Leave unselected cells as None
                        self.TwoDList[col][row] = self.table.get_cell_data(r=row, c=col)
                else:
                    self.TwoDList[col][row] = self.table.get_cell_data(r=row, c=col)

        self.table_dict = {}
        for e, col in enumerate(self.TwoDList):
            self.table_dict[self.column_headers[e]] = col  # Adds in the headers

        df = pd.DataFrame(self.table_dict)
        df.dropna(axis=0, how='all', inplace=True)  # Dropna axis 0 drops all NaN rows
        df.dropna(axis=1, how="all", inplace=True)  # Dropna axis 1 drops all NaN columns

        return df

    def import_csv(self):
        """
        Reads in a csv file to a new table instance. Prompts user for headers.
        If no headers, default headers will be kept.
        """

        file_path = filedialog.askopenfilename(
            title="Select a CSV file",
            filetypes=(("csv", "*.csv"),)
        )

        if file_path:
            df = pd.read_csv(file_path)

            ask_headers = messagebox.askyesno("Headers", "Does your data have headers?")

            if ask_headers:
                self.update_table(headers=df.columns.tolist(),
                                  data=df.values.tolist())  # Table will include user provided headers
            else:
                self.update_table(data=df.values.tolist())  # Table will keep default headings

        self.log_operation(f"Imported file: {file_path}")

    def export_table(self):
        """ Export table to .csv (Comma delimited) or .tsv (Tab delimited) file """

        file_types = [('CSV (Comma delimited)', '.csv'), ('Tab (Tab delimited)', '.tsv'), ('Text', '.txt')]
        file = filedialog.asksaveasfile(
            filetypes=file_types,
            defaultextension=file_types)

        df = self.get_table_selection(self.table)

        if file and not df.empty:  # Make sure filename was entered and table has data
            if file.name.endswith('.csv'):
                df.to_csv(file, index=False, lineterminator='\n')
            if file.name.endswith('.tsv'):
                df.to_csv(file, index=False, sep='\t', lineterminator='\n')

    def log_operation(self, operation):
        """ Log the operation performed. """
        self.operations_log.append(operation)
        print(f"Operation logged: {operation}")

    def export_txt_file(self):
        file_path = filedialog.asksaveasfilename(
            title="Select a location to save the text file",
            filetypes=[("Text files", "*.txt")]
        )

        if file_path:
            with open(file_path, 'w') as file:
                for operation in self.operations_log:
                    file.write(operation + "\n")


class TableView(tk.Frame):
    """
    TableView class to be displayed on application startup. Table will be empty until user imports a CSV or inputs data manually.
    All bindings must be enabled to allow for row/column selections and manual header changes.
    """
    def __init__(self, parent, output=False):
        super().__init__(parent)

        """ Table on Startup"""
        self.sheet = Sheet(parent, data = [[f"" for c in range(26)] for r in range(50)])
        self.sheet.grid(row=0,column=0,sticky='nswe')
        self.sheet.enable_bindings("all", "edit_header", "edit_index", "ctrl_select")

        self.controller = TableController(parent, self.sheet)

        self.toolbar = GUIToolbar(parent, self.controller, self.sheet, output)


class GUIToolbar:
    """
    Creates a toolbar for the table.
    Toolbar should include actions directly associated with table:
        - Import CSV
        - Export .CSV (Comma Separated Values) & .TSV (Tab Separated Values)
    """

    def __init__(self, parent, controller, table, output):
        self.toolbar_frame = tk.Frame(parent)
        self.toolbar_frame.grid(row=0, column=1, sticky='ne')
        self.controller = controller
        self.table = table

        if not output:
            # Image conversion: https://dafarry.github.io/tkinterbook/photoimage.htm uses base64 type
            self.save_img = PhotoImage(format='gif', data=
            'R0lGODlhGQAZAIe1ACpgtyxity5kth57AyxltC5luS9lujBluiJ7DjBmuiN6HTFmuyV'
            + '/ADNpvDhxvzWHCjt2xDx4wTuLETqMFUJ5vz98xEB8xEOPF0V+wkKAxUKAxkiRG0mRHU'
            + 'WCxUWCxkaCxEaDxkeExkaULkmFxEqUMkmIxkqIxkuIxVGXI0uJxUuJxkyJxleYKE2LyE'
            + '+Lx0+MyE+MyU+NyFubKWOeMl6fOmOfMVygPGWfMV+hQ2SS22miNmKjRmWU22ujN2ukQW'
            + 'alSG+kOmilRm+lPXKoRnSrT3yvVYGzWoCzYYK1Z1W0+Fa091S194W2ZoW2aom4a32w4X'
            + '2y4o66b5C8dIS24me9/GW++2i//ZbBgJfCgm7C/ZjCg57FiKHGiqHHiqXIjanKkKjLkK'
            + 'rLka3NlLDOlrPS8Z7X/6DY/7XU87jW9LrW9bvW9bTY9rvY9rzZ9r3a9sHb+MLc+MTd+c'
            + 'Xf+cff+sfg+sjg+cjg+sjg+8nh+8rh+szh+8ni+8vi+83j+83j/M7j+8/j/Mnl+s/k/N'
            + 'Dk+9Hk/M3m/NPl/dLm/NXl/tPm/Nfm8tTm/NTm/dPn/dXn/dbn/dbn/tfn/tbo/tfo/t'
            + 'jo/t/p9Nzq9t7q9t7r9t/r9d/s9+Pt9+nv9ebw9+jx+Orx+Ory+uvy+Ozy9+zy+Ovz+u'
            + 'zz+e3z+O30+O30+e30+u70+O/0+e/0+vD0+PD0+fH1+fL2+vP3+/j7+Pj7/fj7/////w'
            + 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            + 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            + 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            + 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            + 'AAAAAAAAAAAAAAAAAAAAAAACH+EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEKALUALAAAAA'
            + 'AZABkAQAj/AGsJbNHihcGDMWLAcOEiBQQIAiNGVOHKVaJFixoRItSnjx04cNScOUOmVa'
            + 'sPEjN48oTIkMsePcaMERMmDBgpUroECfJAYq0DBxYkGDoUqIECBRAMGCAgQACfJ2DBoo'
            + 'MHz547d+TIeYMGDa01a57kyOGzBCpUlNJOggTJJSE9eobcuAEnVSoPEh1kymSFCpUqKF'
            + 'Bw4HBBggQaV67sECGCgMQRokSpOnXKlGXLoyIrggKFh0+BKl69AjRokCA/fvLkidOmTa'
            + 'XIsThxwiDRxKpVkR49csSI0aFDeubMgePGDRtWrEBI7BAqFCTdj4QIAQJEx4wZRWoS2b'
            + 'ChgkQLnTol+lGiZEmNGmLERHHihMmRI0i0aLHBgIHABp8+acKE6ZKl/5aQIuAEOOBAgi'
            + 'yyAOATQQchpBBDDkH0WS1RTVXVVVlt1dVXYY3l0wqi+fHHH33wwUcddcCRRhqzFFJIIF'
            + 'NMQYFEoY1W2mmprdbaa6LENlttt+W2W2+/BTdcccclJ5FZaKnFlltwyUWXXXhFFEIppU'
            + 'gyySTQOeKIIaX5YIQRLIACigbLNfecbtJRZx122nHnXUTgiUeeeeipx5578MlHn321RL'
            + 'DJJlmYYUYZMsjwxRdecMHFFk00gcUPPyiQ1159/RXYYIUdlthijfkElFBEJWAUUkox5VREAQEAOw==')

            self.import_csv_button = ttk.Button(self.toolbar_frame, text="Import CSV", image=self.save_img,
                                                command=lambda: self.controller.import_csv())
            self.import_csv_button.grid(row=0, column=0, sticky='ne')

            self.export_img = tk.PhotoImage(format='gif', data=
            'R0lGODlhGQAZAIcAAIjAYjFgpjFgpzFgqDFhqDJhqDJhqTJhqjJiqjJiqzJjrDNjrTNkrj'
            + 'NkrzNlsDRlsTRmsjRmszRntDVotTVotjVotzVptzVpuDVpuTVqujZqujdrujZquzZruzZ'
            + 'rvDhruzhsuzptuzlsvDtuvT5wu16JyWSMyGWMyGWNyWaNyWeOyWWNymmQymySy22Sy2iQ'
            + 'zWqTz3mYx3yayHybyW2W03CZ1nGZ2HKb2XOb2XOb2nKc23Sc2nSd3HSe3Xaf3XWe3naf3'
            + 'nef3neg3neg33ih4Hii4Hmi4Xqi4Hqi4Xqj4Xuj4Xqi4nqj4nuj4nqj43uk4nqk43uk43'
            + '2m5n2n536o536o6MLcv4GezISjzoqn0o6r1ZWw2pq13YCq6Z+64aS+5KnC563F6q3G67P'
            + 'K7bbM7rjO77rQ7rvQ773Q7L7S8MPV78LV8sXY8sfZ9Mnc9Mzd9dDf9tHf9tHg9tHg99jl'
            + '9tnl99vm99vn99vn+N3o+N/p+N/p+eHs+eLs+ePt+eXt+ujw+unw+unx+urw+urx++vx+'
            + '+3y++7z++70++70/O/0/PD1/PH2/PL2/PP3/fP4/fb5/fb6/ff6/fb6/vf6/vf7/vj6/v'
            + 'j7/gAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            + 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            + 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            + 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            + 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            + 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            + 'AAAAACH5BAEAAJgALAAAAAAZABkAQAj/ADFh8kCwYIeDHBKKEDEiRIgPJEgIxHTQzZQpf'
            + 'DL6SZRIkiRHf/7cqVOHjhAhXyRI0KDhzJIll2LKnEmTBo0sCRKwxHDhQoUJEyRAgODAAQ'
            + 'MFChAYMDBAgIAABAgQjNOly6RIkUwcOkSIUKOYjPr0wWPGDJqICdlEieIECpQnTZooUWJ'
            + 'kyBAgPXro4MGDy4MHGzaMOXKEEoDDiBMjhrRixQynBOXMmXOpUiVIixYNGmQIEiRJhQrp'
            + 'QYOmhECCb6hQAcQ6RaBAjx5ZUqRoz52RRYqAoUDhYBspUkygQKGiRQsXLlicOGGiuYkdO'
            + '7xEiJAwDZPrSZLIVUKESBAfPnjc7rhho0YNLQsWfPhQxogRw4rjA4AEAwaWAwcyZBATJg'
            + 'zN/zPJIEMMTp1WEEEHdZAQBws19FBEE01V1VVZbdXVV5eENVZZZ5FAEBxVVMHIiCYIIgg'
            + 'iiEjiGSB55GFHdmpYYAFqqrEGiGuwyUabbbjpxptvwAlHnHHIKcecc9BJRx0HarHlFlzb'
            + '1XVXXnv19VdCazihZVxNPPGEe0Sc9ANfOeCAwxYNNFDddUxkt11334U3Xnnnpbdee+/JF'
            + 'x999uEHAghkIIEEJVYUauihhkLywgtXFFBAYIMVpqdijDnm1E49/RTUUEUdldRSTT0VVUAAOw==')

            self.export_button = ttk.Button(self.toolbar_frame, text="Export", image=self.export_img,
                                            command=lambda: self.controller.export_table())
            self.export_button.grid(row=1, column=0, sticky='ne')

        else:
            self.export_img = tk.PhotoImage(format='gif', data=
            'R0lGODlhGQAZAIcAAIjAYjFgpjFgpzFgqDFhqDJhqDJhqTJhqjJiqjJiqzJjrDNjrTNkrj'
            + 'NkrzNlsDRlsTRmsjRmszRntDVotTVotjVotzVptzVpuDVpuTVqujZqujdrujZquzZruzZ'
            + 'rvDhruzhsuzptuzlsvDtuvT5wu16JyWSMyGWMyGWNyWaNyWeOyWWNymmQymySy22Sy2iQ'
            + 'zWqTz3mYx3yayHybyW2W03CZ1nGZ2HKb2XOb2XOb2nKc23Sc2nSd3HSe3Xaf3XWe3naf3'
            + 'nef3neg3neg33ih4Hii4Hmi4Xqi4Hqi4Xqj4Xuj4Xqi4nqj4nuj4nqj43uk4nqk43uk43'
            + '2m5n2n536o536o6MLcv4GezISjzoqn0o6r1ZWw2pq13YCq6Z+64aS+5KnC563F6q3G67P'
            + 'K7bbM7rjO77rQ7rvQ773Q7L7S8MPV78LV8sXY8sfZ9Mnc9Mzd9dDf9tHf9tHg9tHg99jl'
            + '9tnl99vm99vn99vn+N3o+N/p+N/p+eHs+eLs+ePt+eXt+ujw+unw+unx+urw+urx++vx+'
            + '+3y++7z++70++70/O/0/PD1/PH2/PL2/PP3/fP4/fb5/fb6/ff6/fb6/vf6/vf7/vj6/v'
            + 'j7/gAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            + 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            + 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            + 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            + 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            + 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            + 'AAAAACH5BAEAAJgALAAAAAAZABkAQAj/ADFh8kCwYIeDHBKKEDEiRIgPJEgIxHTQzZQpf'
            + 'DL6SZRIkiRHf/7cqVOHjhAhXyRI0KDhzJIll2LKnEmTBo0sCRKwxHDhQoUJEyRAgODAAQ'
            + 'MFChAYMDBAgIAABAgQjNOly6RIkUwcOkSIUKOYjPr0wWPGDJqICdlEieIECpQnTZooUWJ'
            + 'kyBAgPXro4MGDy4MHGzaMOXKEEoDDiBMjhrRixQynBOXMmXOpUiVIixYNGmQIEiRJhQrp'
            + 'QYOmhECCb6hQAcQ6RaBAjx5ZUqRoz52RRYqAoUDhYBspUkygQKGiRQsXLlicOGGiuYkdO'
            + '7xEiJAwDZPrSZLIVUKESBAfPnjc7rhho0YNLQsWfPhQxogRw4rjA4AEAwaWAwcyZBATJg'
            + 'zN/zPJIEMMTp1WEEEHdZAQBws19FBEE01V1VVZbdXVV5eENVZZZ5FAEBxVVMHIiCYIIgg'
            + 'iiEjiGSB55GFHdmpYYAFqqrEGiGuwyUabbbjpxptvwAlHnHHIKcecc9BJRx0HarHlFlzb'
            + '1XVXXnv19VdCazihZVxNPPGEe0Sc9ANfOeCAwxYNNFDddUxkt11334U3Xnnnpbdee+/JF'
            + 'x999uEHAghkIIEEJVYUauihhkLywgtXFFBAYIMVpqdijDnm1E49/RTUUEUdldRSTT0VVUAAOw==')

            self.export_button = ttk.Button(self.toolbar_frame, text="Export", image=self.export_img,
                                            command=lambda: self.export_txt_file())
            self.export_button.grid(row=1, column=0, sticky='ne')

            # Add Export Operations Log Button with an Icon this will be the output
            self.export_log_img = Image.open("assets/txticon.png")
            self.export_log_img = self.export_log_img.resize((28, 28))  # Resize to 32x32 (adjust the size as necessary)
            self.export_log_img = ImageTk.PhotoImage(self.export_log_img)  # Convert to a Tkinter-compatible format

            self.export_log_button = ttk.Button(self.toolbar_frame, text="Export Log", image=self.export_log_img,
                                                command=self.controller.export_txt_file)
            self.export_log_button.grid(row=2, column=0, sticky='ne')


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Table View")
    app = TableView(root)
    root.mainloop()
