import tkinter as tk
from pandastable import Table, ToolBar
from pandastable.dialogs import addButton


class CustomTable():
      """ Table class without inheritance from pandastable Table class. 
      Only 'import csv' is active, unwanted toolbar buttons are destroyed by checking button text.
      Tkinter frame only for testing, in deployment we would use the figma tkinter framework and
      only instantiate our custom table class """

      def __init__(self):
        root = tk.Tk()
        root.title("Statistical Analyzer")
        frame = tk.Frame(root)
        frame.pack(fill='both', expand=True)

        table = Table(frame, showtoolbar=True, showstatusbar=False)
        table.show()

        toolbar = table.toolbar
        for button in toolbar.winfo_children(): # Instead of subclassing ToolBar, we can remove buttons from the toolbar by text name
                if button.cget("text") in ["Save", "Copy", "Paste", "Plot", "Table from selection", "Clear", "Load excel", "Load table", "Transpose", "Aggregate", "Pivot", "Melt", "Merge", "Query", "Evaluate function", "Stats models"]:
                        button.destroy()

        # Run the main loop
        root.mainloop()

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
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        def show(self, callback=None):
                """Adds column header and scrollbars and combines them with
                the current table adding all to the master frame provided in constructor.
                Table is then redrawn."""
                
                #Add the table and header to the frame
                self.rowheader = super().RowHeader(self.parentframe, self)
                self.colheader = super().ColumnHeader(self.parentframe, self, bg='gray25')
                self.rowindexheader = super().IndexHeader(self.parentframe, self, bg='gray75')
                self.Yscrollbar = super().AutoScrollbar(self.parentframe,orient=super().VERTICAL,command=self.set_yviews)
                self.Yscrollbar.grid(row=1,column=2,rowspan=1,sticky='news',pady=0,ipady=0)
                self.Xscrollbar = super().AutoScrollbar(self.parentframe,orient=super().HORIZONTAL,command=self.set_xviews)
                self.Xscrollbar.grid(row=2,column=1,columnspan=1,sticky='news')
                self['xscrollcommand'] = self.Xscrollbar.set
                self['yscrollcommand'] = self.Yscrollbar.set
                self.colheader['xscrollcommand'] = self.Xscrollbar.set
                self.rowheader['yscrollcommand'] = self.Yscrollbar.set
                self.parentframe.rowconfigure(1,weight=1)
                self.parentframe.columnconfigure(1,weight=1)

                self.rowindexheader.grid(row=0,column=0,rowspan=1,sticky='news')
                self.colheader.grid(row=0,column=1,rowspan=1,sticky='news')
                self.rowheader.grid(row=1,column=0,rowspan=1,sticky='news')
                self.grid(row=1,column=1,rowspan=1,sticky='news',pady=0,ipady=0)

                self.adjustColumnWidths()
                #bind redraw to resize, may trigger redraws when widgets added
                self.parentframe.bind("<Configure>", self.resized) #self.redrawVisible)
                self.colheader.xview("moveto", 0)
                self.xview("moveto", 0)
                if self.showtoolbar == True:
                        self.toolbar = GUIToolbar(self.parentframe, self)
                        self.toolbar.grid(row=0,column=3,rowspan=2,sticky='news')
                if self.showstatusbar == True:
                        self.statusbar = super().statusBar(self.parentframe, self)
                        self.statusbar.grid(row=3,column=0,columnspan=2,sticky='ew')
                #self.redraw(callback=callback)
                self.currwidth = self.parentframe.winfo_width()
                self.currheight = self.parentframe.winfo_height()
                if hasattr(self, 'pf'):
                        self.pf.updateData()
                return
                #Table.toolbar = guiToolbar(parent, self)


if __name__ == "__main__":
        CustomTable()