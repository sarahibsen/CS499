import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import ttk
from tksheet import Sheet
from tkinter import filedialog, messagebox


# TODO: 
#   Check row, column, cell selection
#   Pandas automatically changes int to float when adding columns to df
#   Call dataselection update on import csv and all edits (if just an edit return just the value or possibly just row)
#   Write test cases

class CustomTable():
    def __init__(self, parent):

        self.frame = parent

        self.data_in_table = pd.DataFrame()
        self.table = CustomSheet(self.frame, self.data_in_table)
        self.toolbar = GUIToolbar(self.frame, self.table)

    def get_table_data(self):
         return self.table.get_table_selection()
        

class CustomSheet():
    def __init__(self, parent, data_in_table=None, headers=None, data=None):
        super().__init__()
        self.parent = parent

        self.dataset = data_in_table
        if headers == None and data == None: # Startup scernario 
            self.sheet = Sheet(self.parent, data = [[f"" for c in range(26)] for r in range(50)])

        elif headers == None:
             self.sheet = Sheet(self.parent, show_header=True, data = list(data))

        else:
             self.sheet = Sheet(self.parent, headers= list(headers), data = list(data))


        self.sheet.enable_bindings("all", "edit_header", "edit_index", "ctrl_select")
        self.sheet.grid(row=0,column=0,sticky='nswe')

        self.data_test_button = tk.Button(self.parent, text="Check Table Selection (To be Removed)", command=self.get_table_selection)
        self.data_test_button.grid(row=1,column=0,sticky='sw')

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
                

    def get_table_selection(self):
        """ Creates a 2D list that matches the dimensions of the tksheet table and fills row list with None.
            Iterates over the entire table only updating the cells that are selected.
            Table selection is then matched with its header and converted to pandas df
        """
        self.currently_selected = self.sheet.get_currently_selected()
        self.column_headers = self.sheet[:].expand().options(table=False, header=True).data # Gets all headers regardless of selection or if header is default

        if self.currently_selected:
            self.TwoDList = []

            # Creates a 2D list filled with None. The idea is to just place values that are selected.
            for c in range(0, self.sheet.total_columns()): # 3
                self.column_list = []
                for r in range(0, self.sheet.total_rows()): # 1
                    self.column_list.append(np.nan)

                self.TwoDList.append(self.column_list)

            for col in range(0, self.sheet.total_columns()):
                for row in range(0, self.sheet.total_rows()):
                    if self.sheet.cell_selected(r=row,c=col,rows=True,columns=True): # Only change the cells that are selected. Leave unselected cells as None
                        self.TwoDList[col][row] = self.sheet.get_cell_data(r=row,c=col)

            print(f"Table Selection: {self.TwoDList}")

            self.table_dict = {}
            for e, col in enumerate(self.TwoDList):
                 self.table_dict[self.column_headers[e]] = col
            print(pd.DataFrame(self.table_dict))
            print(self.detect_data_type(pd.DataFrame(self.table_dict).dropna(axis=0,how='all').dropna(axis=1,how="all"))) # Dropna axis 0 drops all NaN rows, Dropna axis 1 drops all NaN columns

        else: # If the user selects nothing in the table, currently returning all of the data
            print(pd.DataFrame(self.sheet[:].expand().options(table=True, header=True).data))
            print(self.detect_data_type(pd.DataFrame(self.sheet[:].expand().options(table=True, header=True).data)))

 
    def detect_data_type(self, df): # Sarah's data validation check
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


    def merge_datasets(self, row_dataset, column_dataset, cell_dataset): # May not need
        self.dataset = {}
        self.cell_artifact = [] # Keep a record of cell locations, so even if the user selects the same cell multiple times we only include it once.
        #print(f"Row dataset: {row_dataset}")
        for key, value in row_dataset.items():
            for sub_value in value:
                if key in self.dataset.keys():
                    self.dataset[key].extend(sub_value.values())
                else:
                    print([sub_value.values()])
                    self.dataset[key] = list(sub_value.values())

                self.cell_artifact.append(sub_value.keys())

        for key, value in column_dataset.items():
            for sub_value in value:
                if sub_value.keys() not in self.cell_artifact: # Make sure cell location isn't already in dataset
                    if key in self.dataset.keys():
                        self.dataset[key].extend(sub_value.values())
                    else:
                        self.dataset[key] = list(sub_value.values())

                    self.cell_artifact.append(sub_value.keys())

        for key, value in cell_dataset.items():
            for sub_value in value:
                if sub_value.keys() not in self.cell_artifact: # Make sure cell location isn't already in dataset
                    if key in self.dataset.keys():
                        self.dataset[key].extend(sub_value.values())
                    else:
                        self.dataset[key] = list(sub_value.values())

                self.cell_artifact.append(sub_value.keys())

        return self.dataset



class GUIToolbar():
    """ Inherits from pandastable ToolBar class to only show 'import csv' button """
    def __init__(self, parent, table):
        self.parent = parent
        self.table = table

        # Image conversion: https://dafarry.github.io/tkinterbook/photoimage.htm uses base64 type
        self.img = tk.PhotoImage(format='gif',data=
                'R0lGODlhEAAQAOe1ACpgtyxity5kth57AyxltC5luS9lujBluiJ7DjBmuiN6'
                +'HTFmuyV/ADNpvDhxvzWHCjt2xDx4wTuLETqMFUJ5vz98xEB8xEOPF0V+wkKA'
                +'xUKAxkiRG0mRHUWCxUWCxkaCxEaDxkeExkaULkmFxEqUMkmIxkqIxkuIxVGX'
                +'I0uJxUuJxkyJxleYKE2LyE+Lx0+MyE+MyU+NyFubKWOeMl6fOmOfMVygPGWf'
                +'MV+hQ2SS22miNmKjRmWU22ujN2ukQWalSG+kOmilRm+lPXKoRnSrT3yvVYGz'
                +'WoCzYYK1Z1W0+Fa091S194W2ZoW2aom4a32w4X2y4o66b5C8dIS24me9/GW+'
                +'+2i//ZbBgJfCgm7C/ZjCg57FiKHGiqHHiqXIjanKkKjLkKrLka3NlLDOlrPS'
                +'8Z7X/6DY/7XU87jW9LrW9bvW9bTY9rvY9rzZ9r3a9sHb+MLc+MTd+cXf+cff'
                +'+sfg+sjg+cjg+sjg+8nh+8rh+szh+8ni+8vi+83j+83j/M7j+8/j/Mnl+s/k'
                +'/NDk+9Hk/M3m/NPl/dLm/NXl/tPm/Nfm8tTm/NTm/dPn/dXn/dbn/dbn/tfn'
                +'/tbo/tfo/tjo/t/p9Nzq9t7q9t7r9t/r9d/s9+Pt9+nv9ebw9+jx+Orx+Ory'
                +'+uvy+Ozy9+zy+Ovz+uzz+e3z+O30+O30+e30+u70+O/0+e/0+vD0+PD0+fH1'
                +'+fL2+vP3+/j7+Pj7/fj7////////////////////////////////////////'
                +'////////////////////////////////////////////////////////////'
                +'////////////////////////////////////////////////////////////'
                +'////////////////////////////////////////////////////////////'
                +'////////////////////////////////////////////////////////////'
                +'/////////////////////yH+EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEKAP8A'
                +'LAAAAAAQABAAAAj+AP/9a/Gi4IsYMFykgCCw4QhRqk6ZmjhKlCIoPBr+OwGL'
                +'Dp49d+S8QUNrzZMcDVe88vOnD586cNLMKhRoCgWBKl4BGiTIT544bSqJisUJ'
                +'A05XiRY1ItTHDhw1Z8i0+iDQxKpIjxwxOqRnDhw3bFiBEFgCFSVKkyAZIqRn'
                +'yA04qTwIDFFK0qRHWQ0N8mGEBSgNAjuEgoRXCBAdM4qEIbKhgsAMnhAZMtRj'
                +'jJgwYKR0CfJAoIVOSZQsqSEmihMmR5BoscHgX4RNWcyUkfHFC5ctTbD8UCDQ'
                +'QSYrVKqg4HBBAo0rO0QQENjgkyZMlyxZIkVqAg4SsgA0PLAggfcDBgoHIBgg'
                +'IIDAgAA7')


        self.img = tk.PhotoImage(format='gif', data=
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
        
        self.import_csv_button = ttk.Button(self.parent, text="Import CSV", image=self.img, command=self.import_csv)
        self.import_csv_button.grid(row=0,column=1,sticky='ne')

    def import_csv(self):
        """ Inherits from the Custom TKTable to pass data from csv_reader to a new table """
        file_path = filedialog.askopenfilename(
                title="Select a CSV file",
                filetypes=(("csv", "*.csv"),)
        )
        
        df = pd.read_csv(file_path)

        ask_headers = messagebox.askyesno("Headers", "Does your data have headers?")

        if ask_headers:
               CustomSheet(self.parent, headers=df.columns.tolist(), data=df.values.tolist()) # Table will include user provided headers
        else:
               CustomSheet(self.parent, data=df.values.tolist())  # Table will keep default headings

if __name__ == "__main__":
    root = tk.Tk()
    frame = tk.Frame(root)
    frame.pack()
    app = CustomTable(frame)
    root.mainloop()