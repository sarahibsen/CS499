import csv
import tkinter as tk
from tkinter import ttk
from tkinter.font import Font
from tkinter import simpledialog, filedialog, messagebox

DEFAULT_HEADINGS = ['A', 'B', 'C', 'D']
     
class CustomTable(tk.Tk):
      def __init__(self):
        super().__init__()
        self.title("Statistical Analyzer")
        self.geometry('900x400')
        self.toolbar = GUIToolbar(self)
        
        self.mainloop()


class TkTable(ttk.Frame):
        """ Builds a Custom Table by extending the ttk.Frame Class from Tkinter. 
            Table structure uses the ttk.Treeview Class
        """
        def __init__(self, parent, headings=DEFAULT_HEADINGS, data=None):
                super().__init__(parent)
                self.table = ttk.Treeview(self, columns=headings, show='headings')
                self.setup_table(headings, data)
                
                #self.table.config(yscrollcommand=self.scroll.set)
                self.pack(side="left", fill='both', expand=True)
                
        def setup_table(self, headings, data):
                """ Sets up a blank table when the TkTable Class is initialized OR imports data from CSV.
                    If data already exists in table before calling CSV import from GUIToolBar Class, wipe the
                    existing table instance and build a new one.
                """
                for row in self.table.get_children():
                        self.table.delete(row) # Cleanup any old table for when a CSV is imported
                        
                
                for txt in DEFAULT_HEADINGS:   # Headings will either be defaulted to 'A', 'B', 'C', ... OR users will need to be able to supply manually or from CSV.
                        self.table.heading(txt, text=txt)

                self.table.pack(side="left",fill='both', expand=True)

                if data is None:
                        for e, _ in enumerate(headings):
                                self.table.insert("", "end", text=f"Item {e}", values=(["","","",""]))
                else:
                        for e, row in enumerate(data):
                                self.table.insert("", "end", text=f"Item {e}", values=(row))

                
                self.table.bind("<Double-Button-1>", self.edit_cell) # Bind double-click to edit cell

                self.menu = tk.Menu(self.table, tearoff=0)
                self.menu.add_command(label="Add Row(s)", command=self.add_row)
                self.table.bind("<Button-3>",self.popup_menu) # Bind right-click to show Add/Delete Rows & Columns

                self.pack(fill='both', expand=True)

        def row_menu(self, event):
                """ Row menu popup for right-click.
                    Needs to include Add Row(s) & Delete Row 
                """
                self.menu = tk.Menu(self.table, tearoff=0)
                self.menu.add_command(label="Add Row(s)", command=self.add_row)

        def add_row(self):
                input = simpledialog.askinteger("Add Row(s)", "How many Rows?")
                for i in range(input):
                       self.table.insert("","end", values=())

        def column_menu(self, event):
                """ Column menu popup for right-click.
                    Needs to include Add Column(s) & Delete Column
                """
                pass

        def add_column(self):
                pass

        def popup_menu(self, event):
                try:
                    self.menu.tk_popup(event.x_root, event.y_root,0)
                finally:
                       self.menu.grab_release()

        def edit_cell(self, event):
                """ Allows users to edit existing rows by double-clicking at the desired cell location.
                    This could also be used to track if the user has unsaved changes:
                        1) When a users imports CSV and makes an edit (flag) OR if a user enters data manually (flag)
                        2) Only unflag with a save method
                """
                item = self.table.identify_row(event.y)
                column = self.table.identify_column(event.x)
                if item and column:
                        value = self.table.item(item, 'values')[int(column[1:]) - 1] # Get the value from the treeview cell
                        row_value = list(self.table.item(item, 'values'))
                        print(row_value)
                        
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

        # Image conversion: https://dafarry.github.io/tkinterbook/photoimage.htm uses based64 type
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
        
        ttk.Button(self, text="Import CSV", image=self.img, command=self.import_csv).pack(fill='y', expand=False)
        super(TkTable, self).pack(side="right", fill="y", expand=True) # Places on ttk.Frame

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
               self.setup_table(data[0], data[1:])      # Need to add the ability for users to provide their own headings
        else:
               self.setup_table(DEFAULT_HEADINGS, data) # Need to change to populate based on the number of commas, this will represent A-Z default headings

    
if __name__ == "__main__":
        CustomTable()

# https://www.youtube.com/watch?v=zhheiV3eQXI