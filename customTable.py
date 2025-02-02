import tkinter as tk
from tkinter import simpledialog

from pandastable import Table, ToolBar
from pandastable.dialogs import addButton


class GUIToolbar(ToolBar):
    """ Inherits from pandastable ToolBar class to only show 'import csv' button """
    def __init__(self, parent=None, parentapp=None, **kwargs):
        super().__init__(parent=parent, parentapp=parentapp)

        # Image conversion: https://dafarry.github.io/tkinterbook/photoimage.htm
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
        
        self.func = lambda: self.parentapp.importCSV(dialog=1)
        addButton(self, 'Import', self.func, self.img, 'import csv')


class GUITable(Table):
    """ Extends the Table class within pandastable. 
        Intention would be to override the toolbar variable
        to a custom toolbar we define """
    
    def __init__(self, parent, dataframe= None, **kwargs):
        Table.__init__(self, parent, dataframe = dataframe,**kwargs)
        return
    
    def addRows(self, num=None):
        """ Add new rows
        Override Table add row number dialog to correct 'Now Many Rows' text and
        need to correct auto integer datatype conversion to float
        when adding new rows """
        if num == None:
                num = simpledialog.askinteger("How many rows?",
                                                "Number of rows:",initialvalue=1,
                                                parent=self.parentframe)
        if not num:
                return
        self.storeCurrent()
        keys = self.model.autoAddRows(num)
        self.update_rowcolors()
        self.redraw()
        self.tableChanged()
        return
        
class CustomTable(GUITable):
      """ Table class without inheritance from pandastable Table class. 
      Only 'import csv' is active, unwanted toolbar buttons are destroyed by checking button text.
      Tkinter frame only for testing, in deployment we would use the figma tkinter framework and
      only instantiate our custom table class """

      def __init__(self):
        root = tk.Tk()
        root.title("Statistical Analyzer")
        frame = tk.Frame(root)
        frame.pack(fill='both', expand=True)

        table = GUITable(frame, showtoolbar=True, showstatusbar=False)
        table.show()

        toolbar = table.toolbar
        for button in toolbar.winfo_children(): # Instead of subclassing ToolBar, we can remove buttons from the toolbar by text name
                if button.cget("text") in ["Save", "Copy", "Paste", "Plot", "Table from selection", "Clear", "Load excel", "Load table", "Transpose", "Aggregate", "Pivot", "Melt", "Merge", "Query", "Evaluate function", "Stats models"]:
                        button.destroy()

        # Run the main loop
        root.mainloop()

if __name__ == "__main__":
        CustomTable()