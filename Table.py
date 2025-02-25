import pandas as pd
from tkinter import filedialog, messagebox
from tksheet import Sheet
from tkinter import ttk, PhotoImage
import tkinter as tk

class TableModel:
    def __init__(self):
         self.data = [[f"" for c in range(26)] for r in range(50)] # Default table on startup

    def get_data(self):
        return self.data
    
    def detect_data_type(self, df): # Sarah's data validation check
        data_types = {}
        for column in df.columns:
            #print(f"df column: {df[column]}")
            if pd.api.types.is_numeric_dtype(df[column]):
                unique_values = df[column].nunique()
                #print(unique_values)
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
        elif str(value).strip().isnumeric(): # If csv has any leading/trailing whitespace, float datatype won't be found
                return int(value)

        elif is_float(str(value).strip()):
                return float(value)
        else:
                return value 
    

class TableController:
    def __init__(self, parent):
        self.model = TableModel()
        self.parent = parent

    def get_table_data(self):
        return self.model.get_data()         

    def update_table(self, table, headers=None, data=None):
        table.destroy() # Destroys the current table since we are overwriting it with data from CSV

        if headers == None: # If headers are not provided, default headers will be used
             self.table = Sheet(self.parent, show_header=True, data = list(data), width=1000, height=500)
             self.win_width = self.table.winfo_reqwidth()
             self.win_height = self.table.winfo_reqheight()
             #self.table = Sheet(root, show_header=True, self.model.data = list(data))

        else: # Used headers and data provided
             self.table = Sheet(self.parent, headers= list(headers), data = list(data), width=1000, height=500)
             self.table.config(width=self.table.winfo_reqwidth(), height=self.table.winfo_reqheight())
             self.table.update_idletasks()

        self.table.grid(row=0,column=0,sticky='nswe')
        self.table.enable_bindings("all", "edit_header", "edit_index", "ctrl_select")

    def get_table_selection(self):
        """ Creates a 2D list that matches the dimensions of the tksheet table and fills row list with None.
            Iterates over the entire table only updating the cells that are selected.
            Table selection is then matched with its header and converted to pandas df
        """
        self.table = self.table
        self.currently_selected = self.table.get_currently_selected()
        self.column_headers = self.table[:].expand().options(table=False, header=True).data # Gets all headers regardless of selection or if header is default

        # if self.currently_selected:
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
                    if self.table.cell_selected(r=row,c=col,rows=True,columns=True): # Only change the cells that are selected. Leave unselected cells as None
                        self.TwoDList[col][row] = self.table.get_cell_data(r=row,c=col)
                else:
                        self.TwoDList[col][row] = self.table.get_cell_data(r=row,c=col)

        print(f"Table Selection: {self.TwoDList}")

        self.table_dict = {}
        for e, col in enumerate(self.TwoDList):
                self.table_dict[self.column_headers[e]] = col # Adds in the headers

        df = pd.DataFrame(self.table_dict)
        df.dropna(axis=0,how='all', inplace=True) # Dropna axis 0 drops all NaN rows
        df.dropna(axis=1,how="all", inplace=True) # Dropna axis 1 drops all NaN columns
        print(df)
        print(self.model.detect_data_type(df)) # Dropna axis 0 drops all NaN rows, Dropna axis 1 drops all NaN columns


    def import_csv(self, table):
        """ Inherits from the Custom TKTable to pass data from csv_reader to a new table """
        file_path = filedialog.askopenfilename(
                title="Select a CSV file",
                filetypes=(("csv", "*.csv"),)
        )
        
        df = pd.read_csv(file_path)

        ask_headers = messagebox.askyesno("Headers", "Does your data have headers?")

        if ask_headers:
            self.update_table(table, headers=df.columns.tolist(), data=df.values.tolist()) # Table will include user provided headers
        else:
            self.update_table(table, data=df.values.tolist())  # Table will keep default headings


class TableView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        """ Table on Startup"""
        self.controller = TableController(parent)
        #if headers == None and data == None: # Startup scernario (No data nor headers) 
        self.sheet = Sheet(parent, data = self.controller.get_table_data(), width=1000, height=500)
        self.sheet.grid(row=0,column=0,sticky='nswe')
        self.sheet.config(width=self.sheet.winfo_reqwidth(), height=self.sheet.winfo_reqheight())
        self.sheet.update_idletasks()

        self.data_test_button = ttk.Button(parent, text="Get Data (To be Removed)", command=self.controller.get_table_selection)
        self.data_test_button.grid(row=1,column=0,sticky='sw')

        self.sheet.enable_bindings("all", "edit_header", "edit_index", "ctrl_select")

        self.toolbar = GUIToolbar(parent, self.controller, self.sheet)
        #self.toolbar.grid(row=0,column=1,sticky='ne')


class GUIToolbar():
    """ Inherits from pandastable ToolBar class to only show 'import csv' button """
    def __init__(self, parent, controller, table):
        self.parent = parent
        self.controller = controller
        self.table = table

        # Image conversion: https://dafarry.github.io/tkinterbook/photoimage.htm uses base64 type
        self.img = PhotoImage(format='gif', data=
                'R0lGODlhGQAZAIe1ACpgtyxity5kth57AyxltC5luS9lujBluiJ7DjBmuiN6HTFmuyV'
                +'/ADNpvDhxvzWHCjt2xDx4wTuLETqMFUJ5vz98xEB8xEOPF0V+wkKAxUKAxkiRG0mRHU'
                +'WCxUWCxkaCxEaDxkeExkaULkmFxEqUMkmIxkqIxkuIxVGXI0uJxUuJxkyJxleYKE2LyE'
                +'+Lx0+MyE+MyU+NyFubKWOeMl6fOmOfMVygPGWfMV+hQ2SS22miNmKjRmWU22ujN2ukQW'
                +'alSG+kOmilRm+lPXKoRnSrT3yvVYGzWoCzYYK1Z1W0+Fa091S194W2ZoW2aom4a32w4X'
                +'2y4o66b5C8dIS24me9/GW++2i//ZbBgJfCgm7C/ZjCg57FiKHGiqHHiqXIjanKkKjLkK'
                +'rLka3NlLDOlrPS8Z7X/6DY/7XU87jW9LrW9bvW9bTY9rvY9rzZ9r3a9sHb+MLc+MTd+c'
                +'Xf+cff+sfg+sjg+cjg+sjg+8nh+8rh+szh+8ni+8vi+83j+83j/M7j+8/j/Mnl+s/k/N'
                +'Dk+9Hk/M3m/NPl/dLm/NXl/tPm/Nfm8tTm/NTm/dPn/dXn/dbn/dbn/tfn/tbo/tfo/t'
                +'jo/t/p9Nzq9t7q9t7r9t/r9d/s9+Pt9+nv9ebw9+jx+Orx+Ory+uvy+Ozy9+zy+Ovz+u'
                +'zz+e3z+O30+O30+e30+u70+O/0+e/0+vD0+PD0+fH1+fL2+vP3+/j7+Pj7/fj7/////w'
                +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
                +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
                +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
                +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
                +'AAAAAAAAAAAAAAAAAAAAAAACH+EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEKALUALAAAAA'
                +'AZABkAQAj/AGsJbNHihcGDMWLAcOEiBQQIAiNGVOHKVaJFixoRItSnjx04cNScOUOmVa'
                +'sPEjN48oTIkMsePcaMERMmDBgpUroECfJAYq0DBxYkGDoUqIECBRAMGCAgQACfJ2DBoo'
                +'MHz547d+TIeYMGDa01a57kyOGzBCpUlNJOggTJJSE9eobcuAEnVSoPEh1kymSFCpUqKF'
                +'Bw4HBBggQaV67sECGCgMQRokSpOnXKlGXLoyIrggKFh0+BKl69AjRokCA/fvLkidOmTa'
                +'XIsThxwiDRxKpVkR49csSI0aFDeubMgePGDRtWrEBI7BAqFCTdj4QIAQJEx4wZRWoS2b'
                +'ChgkQLnTol+lGiZEmNGmLERHHihMmRI0i0aLHBgIHABp8+acKE6ZKl/5aQIuAEOOBAgi'
                +'yyAOATQQchpBBDDkH0WS1RTVXVVVlt1dVXYY3l0wqi+fHHH33wwUcddcCRRhqzFFJIIF'
                +'NMQYFEoY1W2mmprdbaa6LENlttt+W2W2+/BTdcccclJ5FZaKnFlltwyUWXXXhFFEIppU'
                +'gyySTQOeKIIaX5YIQRLIACigbLNfecbtJRZx122nHnXUTgiUeeeeipx5578MlHn321RL'
                +'DJJlmYYUYZMsjwxRdecMHFFk00gcUPPyiQ1159/RXYYIUdlthijfkElFBEJWAUUkox5VREAQEAOw==')
        
        self.import_csv_button = ttk.Button(self.parent, text="Import CSV", image=self.img, command= lambda: self.controller.import_csv(self.table))
        self.import_csv_button.grid(row=0,column=1,sticky='ne')


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Table View")
    app = TableView(root)
    root.mainloop()