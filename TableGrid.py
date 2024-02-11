import wx.grid as gridlib
import wx
import pandas


# print(df.memory_usage(deep=True).sum()) #

class TableGrid(gridlib.Grid):
    def __init__(self, parent, df: pandas.DataFrame):
        super().__init__(parent)
        self.df = df
        self.history = []  # To keep track of changes for undo
        self.redo_history = []  # To keep track of changes for redo
        self.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
        # Border Color
        self.SetGridLineColour(wx.BLACK)
        self.auto_sized_columns = set()

        self.Bind(gridlib.EVT_GRID_LABEL_LEFT_DCLICK, self.onDoubleClick)

    def onDoubleClick(self, event):
        if event.GetCol() != -1:
            if event.GetCol() not in self.auto_sized_columns:
                self.column_widths = [self.GetColSize(col) for col in range(self.GetNumberCols())]
                self.AutoSizeColumn(event.GetCol(), setAsMin=True)
                self.auto_sized_columns.add(event.GetCol())
            else:
                self.SetColSize(event.GetCol(), self.column_widths[event.GetCol()])
                self.auto_sized_columns.remove(event.GetCol())

    def onKeyDown(self, event):
        keycode = event.GetKeyCode()
        controlDown = event.CmdDown()

        if controlDown and keycode == ord('Z'):  # If Ctrl+Z is pressed...
            self.undo()
        elif controlDown and keycode == ord('Y'):  # If Ctrl+Y is pressed...
            self.redo()
        else:
            event.Skip()  # Skip other Key events

    def undo(self):
        if self.history:
            last_change = self.history.pop()
            row, col, old_val = last_change
            current_val = self.GetCellValue(row, col)
            self.redo_history.append((row, col, current_val))  # Save the current value for redo
            self.SetCellValue(row, col, old_val)  # Restore the old value

    def redo(self):
        if self.redo_history:
            last_change = self.redo_history.pop()
            row, col, old_val = last_change
            current_val = self.GetCellValue(row, col)
            self.history.append((row, col, current_val))  # Save the current value for undo
            self.SetCellValue(row, col, old_val)  # Restore the old value

    def create_grid(self):
        # Create grid with data from data
        self.CreateGrid(len(self.df.index), len(self.df.columns))
        # Fill the grid with data
        for row in range(len(self.df.index)):
            for col in range(len(self.df.columns)):
                self.SetCellValue(row, col, str(self.df.iloc[row, col]))

    def update_grid_col(self):
        # Update the grid col
        self.ClearGrid()
        self.DeleteCols(0, self.GetNumberCols())
        self.AppendCols(len(self.df.columns))
        for row in range(len(self.df.index)):
            for col in range(len(self.df.columns)):
                self.SetCellValue(row, col, str(self.df.iloc[row, col]))

    def update_grid_row(self):
        # Update the grid row
        self.ClearGrid()
        self.DeleteRows(0, self.GetNumberRows())
        self.AppendRows(len(self.df.index))
        for row in range(len(self.df.index)):
            for col in range(len(self.df.columns)):
                self.SetCellValue(row, col, str(self.df.iloc[row, col]))

    def set_col_header_names(self):
        # Set DataFrame column names as wxGrid headers
        for i, column in enumerate(self.df.columns):
            self.SetColLabelValue(i, column)

    def set_read_only(self, event):
        self.EnableEditing(False)

    def set_readable(self, event):
        self.EnableEditing(True)

    def get_grid_data(self) -> pandas.DataFrame:
        # Create an empty DataFrame
        df = pandas.DataFrame()

        # Populate the DataFrame with the grid data
        for row in range(self.GetNumberRows()):
            row_data = []
            for col in range(self.GetNumberCols()):
                cell_value = self.GetCellValue(row, col)
                row_data.append(cell_value)
            df.loc[row] = row_data

        # Set DataFrame column names as wxGrid headers
        for row in range(self.GetNumberCols()):
            df.rename(columns={row: self.GetColLabelValue(row)}, inplace=True)

    def onGetSelection(self, event):
        cells = self.GetSelectedCells()
        if not cells:
            if self.GetSelectionBlockTopLeft():
                top_left = self.GetSelectionBlockTopLeft()[0]
                bottom_right = self.GetSelectionBlockBottomRight()[0]

                self.printSelectedCells(top_left, bottom_right)
            else:
                print(self.currentlySelectedCell)
        else:
            print(cells)

    def printSelectedCells(self, top_left, bottom_right):
        cells = []
        rows_start = top_left[0]
        rows_end = bottom_right[0]
        cols_start = top_left[1]
        cols_end = bottom_right[1]
        for row in range(rows_start, rows_end + 1):
            for col in range(cols_start, cols_end + 1):
                cells.append(self.GetCellValue(row, col))
        print(cells)


'''
 def onDoubleClick(self, event):
        if event.GetCol() != -1:
            self.grid.AutoSizeColumn(event.GetCol(), setAsMin=True)
'''
