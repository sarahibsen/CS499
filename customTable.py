""" 
    File: customTable.py
    Date: February 9th, 2025
    Author(s): Team 6b
               Sarah Ibsen,
               Jarrett Miller,
               Natalia MIller,
               Matthew Sims
"""

import csv
import tkinter as tk
from tkinter import ttk
from tkinter.font import Font
from tkinter import simpledialog, filedialog, messagebox

# TO DO (Potential Future Improvements):
#       - Prompt user when exiting without saving. Turn edit flag to True everytime an edit it made. It close detected with edit flag == True, prompt user.
#       - Add Row/Column at location, rather than at the end of table.
#       - Doubleclick header to change heading title
#       - Add row numbers in column #0
#       - Make a mapping system for default headings so we don't have a static list

DEFAULT_HEADINGS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
     
class CustomTable(tk.Tk):
      def __init__(self):
        super().__init__()
        self.title("Statistical Analyzer")

        self.geometry("%dx%d" % (self.winfo_screenwidth(), self.winfo_screenheight()))
        self.toolbar = GUIToolbar(self) # Toolbar initializes parent table
        
        self.mainloop()


class TkTable(ttk.Frame):
        """ Builds a Custom Table by extending the ttk.Frame Class from Tkinter. 
            Table structure uses the ttk.Treeview Class
        """
        def __init__(self, parent, headings=DEFAULT_HEADINGS):
                super().__init__(parent)
                self.table = ttk.Treeview(self, columns=headings, show='headings', selectmode='extended')
                self.setup_table(data=None, headings=DEFAULT_HEADINGS)
                
                self.pack(fill='both', expand=True)

                self.scrollbarx = tk.Scrollbar(self.table, orient='horizontal')
                self.scrollbarx.pack(side='bottom', fill='x')
                self.table.configure(xscrollcommand=self.scrollbarx.set)
                self.scrollbarx.configure(command=self.table.xview)

                self.scrollbary = tk.Scrollbar(self.table, orient='vertical')
                self.scrollbary.pack(side="right", fill='y')
                self.table.configure(yscrollcommand=self.scrollbary.set)
                self.scrollbary.configure(command=self.table.yview)

                
        def setup_table(self, data, headings):
                """ Sets up a blank table when the TkTable Class is initialized OR imports data from CSV.
                    If data already exists in table before calling CSV import from GUIToolBar Class, wipe the
                    existing table instance and build a new one.
                """
                for row in self.table.get_children():
                        self.table.delete(row) # Cleanup any old table if a CSV is imported

                self.table["columns"] = headings
                self.add_column(headings, True)

                if data is None:
                        self.add_row(prompt=False)
                else:
                        self.add_row(prompt=False, data=data)

                
                self.table.bind("<Double-Button-1>", self.edit_cell) # Bind double-click to edit cell
                self.table.bind("<Button-3>",self.popup_menu)        # Bind right-click to show Add/Delete Rows & Columns

                self.table.pack(side="left", fill="both", expand=True)


        def add_row(self, prompt=True, data=None):
                """ """
                if prompt == True:                                   # If user initates a row add - need to know how many rows
                        input = simpledialog.askinteger("Add Row(s)", "How many Rows?")
                else:                                                # This will just be on startup or when user imports a CSV
                        input = len(DEFAULT_HEADINGS)

                if data == None:
                        for _ in range(input):
                                self.table.insert(parent="", index="end", text='', values=(['']*len(self.table['columns'])))
                else:
                        for row in data:
                                self.table.insert(parent="", index="end", text='', values= tuple(row))


        def delete_row(self):
                """ Deletes the row(s) selected """
                selected_row = self.table.selection()
                if selected_row:
                        self.table.delete(selected_row)


        def add_column(self, headings=None, startup=False):
                """ Adds a new column at the end of table.
                    If at table initialization, column headings will reflect the default heading list.
                    If at CSV import, will either use headings in file or keep default heading if none supplied in file.
                    If at user request, then user will be prompted to provide heading name
                """
                if startup:
                        for i, heading in enumerate(headings):
                                self.table.heading(f'#{i+1}', text= heading.strip())
                else:
                        input = simpledialog.askstring("Add Column", "Enter new column header:")

                        current_columns = list(self.table['columns'])
                        current_columns = {key:self.table.heading(key) for key in current_columns}

                        self.table['columns'] = list(current_columns.keys()) + [input]

                        for i, key in enumerate(self.table['columns']):
                                self.table.heading(f'#{i+1}', text=key.strip())

                        for i in self.table.get_children():
                                updated_row = self.table.item(i,'values') + ('',)
                                self.table.item(i, values=updated_row)

        def delete_column(self, event):
                """ Deletes column at the right-click event location """
                column_id = self.table.identify_column(event.x)
                column_name = self.table['columns'][int(column_id[1:]) - 1]

                new_columns = list(self.table['columns'])
                new_columns.remove(column_name)
                self.table['columns'] = tuple(new_columns)
                for i, col in enumerate(self.table['columns']):
                        self.table.heading(f'#{i+1}', text=col.strip())

                for item in self.table.get_children():
                        values = list(self.table.item(item, 'values'))
                        values.pop(int(column_id[1:]) - 1)
                        self.table.item(item, values=values)


        def popup_menu(self, event):
                """ Custom right-click menu based on the region location within the table widget.
                    If right-click was made on an existing row, menu option include only 'Delete Row'.
                    If right-click was made on an existing heading, menu option includes only 'Delete Column'.
                    If right-click was made elsewhere, menu options include both 'Add Row(s)' & 'Add Column'"""
                self.menu = tk.Menu(self.table, tearoff=0)
                try:
                        region = self.table.identify("region", event.x, event.y)
                        if region == "heading" or region == "separator": # Check if right-click was on header or row
                                self.menu.add_command(label="Delete Column", command=lambda: self.delete_column(event))
                        elif region == "cell":
                                self.menu.add_command(label="Delete Row", command=self.delete_row)
                        else:
                                self.menu.add_command(label="Add Row(s)", command=self.add_row)
                                self.menu.add_command(label="Add Column", command=self.add_column)

                        self.menu.tk_popup(event.x_root, event.y_root,0)
                finally:
                        self.menu.grab_release()

        def edit_cell(self, event):
                """ Allows users to edit existing rows by double-clicking at the desired cell location.
                    FUTURE IMPROVEMENT: This could also be used to track if the user has unsaved changes:
                        1) When a users imports CSV and makes an edit (flag) OR if a user enters data manually (flag)
                        2) Only unflag with a save method
                """
                
                item = self.table.identify_row(event.y)
                column = self.table.identify_column(event.x)

                if item and column:
                        value = self.table.item(item, 'values')[int(column[1:]) - 1] # Get the value from the treeview cell
                        row_value = list(self.table.item(item, 'values'))
                        
                        entry = tk.Entry(self) # Create an entry widget
                        entry.insert(0, value)
                        entry.place(x=event.x, y=event.y)

                        def update_value(event=None):
                                row_value[int(column[1:]) - 1] = entry.get()      # Replaces just the value in the specified column
                                self.celldType(row_value)
                                self.table.item(item, values=(tuple(row_value)))  # Update the cell value
                                entry.destroy() # Cleanup entry box when done

                        entry.bind("<FocusOut>", update_value)  # Update when clicking off of widget
                        entry.bind("<Return>", update_value)    # Update when cell with Enter key
                        entry.focus_set()

        def celldType(self, row):
                """ Infers datatype (String, Float, Int, None) of each value in table.
                    This method should be called whenever we need to retrieve data from the table.
                """
                data = []

                def is_float(s):
                        """ Python doesn't have an implict float type check, need to make our own
                            by trying to cast cell value within a try/catch block.
                        """
                        try:
                                float(s)
                                return True
                        except ValueError:
                                return False

                for value in row:
                        if value == "":
                               data.append(None)
                        elif value.strip().isnumeric(): # If csv has any leading/trailing whitespace, float datatype won't be found
                                data.append(int(value))
 
                        elif is_float(value.strip()):
                                data.append(float(value))
                        else:
                                data.append(value) 

                print([type(cell) for cell in data])
                        
class GUIToolbar(TkTable):
    """ Inherits from pandastable ToolBar class to only show 'import csv' button """
    def __init__(self, parent):
        super().__init__(parent)

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
        
        import_csv_button = ttk.Button(self, text="Import CSV", image=self.img, command=self.import_csv)
        import_csv_button.pack(fill='y', padx=5, expand=False)

    def import_csv(self):
        """ Inherits from the Custom TKTable to pass data from csv_reader to a new table """
        file_path = filedialog.askopenfilename(
                title="Select a CSV file",
                filetypes=(("csv", "*.csv"),)
        )

        data = []
        with open(file_path, 'r') as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                        data.append(row)

        ask_headers = messagebox.askyesno("Headers", "Does your data have headers?")

        if ask_headers:
               self.setup_table(data[1:], data[0])      # Need to add the ability for users to provide their own headings
        else:
               self.setup_table(data, DEFAULT_HEADINGS) # Need to change to populate based on the number of commas, this will represent A-Z default headings

    
if __name__ == "__main__":
        CustomTable()