import wx
from SimplifierDialogs import RemoveColumnsDialog, MainColumnsSelectorDialog, SelectColumnsDialog
from BankStatementSimplifier import StatementSimplifier, read_stmt, pandas
from TableGrid import TableGrid
import wx.lib.printout as printout
from SimpliferFrames import DataFramePreview


class LeftSidePanel(wx.Panel):
    """
    Panel class with 5 buttons as a children
    """

    def __init__(self, parent: wx.Panel, size: tuple, left_panel_sizer: wx.BoxSizer, display_panel: wx.Panel):
        """
        :param parent: parent window
        :param size: size of panel as a tuple
        :param left_panel_sizer: box sizer of self
        :param display_panel: reference of display panel class
        """
        super().__init__(parent, size=size)

        # set a box sizer for the left panel
        self.exit_frame = None
        self.close_stmt = None
        self.amt_dr_cr_col = None
        self.dr_cr_col = None
        self.stmt_with_dr_cr = None
        self.left_panel_sizer = left_panel_sizer
        # set display panel reference for class level
        self.display_panel: DisplaySidePanel  = display_panel
        # Add a static text
        self.side_title_text = wx.StaticText(self, label="Simplify your\n Statements", pos=(25, 25),
                                             style=wx.ALIGN_CENTER)
        self.side_title_text.BackgroundColour = "white"
        self.side_title_text.ForegroundColour = "#333333"
        # Set font to bold and size to 10
        font = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.side_title_text.SetFont(font)
        # add title text and expand it to content and window
        self.left_panel_sizer.Add(self.side_title_text, 0, wx.EXPAND | wx.ALL, 5)
        self.type_of_stmt = None

        self.create_buttons()
        self.bind_buttons()
        self.set_hint_on_buttons()

    def create_buttons(self):
        self.line()
        self.stmt_with_dr_cr = wx.Button(self, label="Deposit Withdrawal Columns")
        self.left_panel_sizer.Add(self.stmt_with_dr_cr, 0, wx.EXPAND | wx.ALL, 5)
        self.dr_cr_col = wx.Button(self, label="Dr/Cr Column")
        self.left_panel_sizer.Add(self.dr_cr_col, 0, wx.EXPAND | wx.ALL, 5)
        self.amt_dr_cr_col = wx.Button(self, label="Dr/Cr in Amount Column")
        self.left_panel_sizer.Add(self.amt_dr_cr_col, 0, wx.EXPAND | wx.ALL, 5)
        self.line()
        self.close_stmt = wx.Button(self, label="Close Stmt")
        self.left_panel_sizer.Add(self.close_stmt, 0, wx.EXPAND | wx.ALL, 5)
        self.exit_frame = wx.Button(self, label="Exit")
        self.left_panel_sizer.Add(self.exit_frame, 0, wx.EXPAND | wx.ALL, 5)

    def bind_buttons(self):
        self.stmt_with_dr_cr.Bind(wx.EVT_BUTTON, lambda event: self.set_stmt_type(event, "normal"))
        self.dr_cr_col.Bind(wx.EVT_BUTTON, lambda event: self.set_stmt_type(event, "dr_cr_col"))
        self.amt_dr_cr_col.Bind(wx.EVT_BUTTON, lambda event: self.set_stmt_type(event, "amt_dr_cr_col"))
        self.exit_frame.Bind(wx.EVT_BUTTON, self.on_exit)
        self.close_stmt.Bind(wx.EVT_BUTTON, self.on_close_stmt)

    def on_close_stmt(self, event):
        self.display_panel.remove_sizer()

    def on_exit(self, event):
        self.GetParent().GetParent().Destroy()

    def set_stmt_type(self, event, stmt_type: str) -> None:
        self.type_of_stmt = stmt_type
        self.GrandParent.on_navigate_right(event)
        print("\033[91m {}\033[00m".format(f'{self.type_of_stmt}'))

    def style_buttons(self) -> None:
        pass

    def set_hint_on_buttons(self) -> None:
        self.stmt_with_dr_cr.SetToolTip("Statement with Deposit and Withdraw columns")
        self.dr_cr_col.SetToolTip("Statement which has dr/cr indicator column")
        self.amt_dr_cr_col.SetToolTip("Statement which has Amount column \nwhich contain dr/cr indicator in itself")
        self.close_stmt.SetToolTip("Close Right Side Statement")
        self.exit_frame.SetToolTip("Exit")

    def line(self) -> None:
        # Add a horizontal line
        hr_line = wx.StaticLine(self)
        self.left_panel_sizer.Add(hr_line, 0, wx.ALL | wx.EXPAND, 5)

    def get_file_path(self) -> str :
        # Create a file dialog
        with wx.FileDialog(self, "Open Excel file",
                           wildcard="Excel files (*.xlsx)|*.xlsx|CSV files (*.csv)|*.csv") as file_dialog:
            file_dialog: wx.FileDialog = file_dialog

            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind

            # Proceed loading the file chosen by the user
            return file_dialog.GetPath()

    def on_read_stmt(self, event):
        pathname = self.get_file_path()
        self.display_panel.remove_sizer()
        try:
            # Read data from an Excel file
            df = read_stmt(pathname)
            self.display_panel.stmt = df
            if df is not None:
                self.display_panel.setup_grid_df(df, None)
                # Create a grid and set it to fill the right panel
                self.display_panel.table_grid.CreateGrid(len(df.index), len(df.columns))
                self.display_panel.table_grid.update_grid_col()
                self.display_panel.display_sizer = wx.BoxSizer(wx.VERTICAL)
                self.display_panel.display_sizer.Add(self.display_panel.table_grid, 1, wx.EXPAND)
                self.display_panel.SetSizer(self.display_panel.display_sizer)
                self.display_panel.Layout()
        except IOError:
            wx.LogError("Cannot open file '%s'." % pathname)
        except AttributeError:
            AttributeError().with_traceback(None)


class DisplaySidePanel(wx.Panel):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        # Create a grid table
        self.table_grid: TableGrid  = None
        self.stmt: pandas.DataFrame  = None
        self.display_sizer = None

    def new_grid(self) -> None:
        if self.table_grid is not None:
            self.RemoveChild(self.table_grid)

    def setup_grid_df(self, df: pandas.DataFrame, sizer) -> None:
        self.table_grid = TableGrid(self, df)
        self.stmt = df
        self.display_sizer = sizer

    def remove_sizer(self):
        sizer = self.GetSizer()
        if sizer is not None:
            for child in sizer.GetChildren():
                self.RemoveChild(child.GetWindow())
                child.GetWindow().Destroy()
            self.SetSizer(None)


class RightSidePanel(wx.Panel):
    def __init__(self, parent: wx.Panel, size: tuple, sizer: wx.BoxSizer, display_panel: DisplaySidePanel, frame):
        super().__init__(parent, size=size)
        self.display_panel: DisplaySidePanel = display_panel
        self.table_grid = display_panel.table_grid
        self.stmt: pandas.DataFrame = display_panel.stmt
        self.sizer = sizer
        self.stmt_simplifier: StatementSimplifier  = None
        self.create_buttons()
        self.bind_buttons()
        self.set_hint_on_buttons()
        self.frame = frame

    def set_stmt(self, df):
        self.stmt = df

    def set_table_grid(self, grid):
        self.table_grid = grid

    def create_buttons(self) -> None:
        self.static_txt = wx.StaticText()

        self.simplify_btn = wx.Button(self, label="Simplify Stmt")
        self.sizer.Add(self.simplify_btn, 0, wx.EXPAND | wx.ALL, 5)

        self.remove_col_btn = wx.Button(self, label="Remove Columns")
        self.sizer.Add(self.remove_col_btn, 0, wx.EXPAND | wx.ALL, 5)

        self.bank_ledger_btn = wx.Button(self, label="Generate Ledger")
        self.sizer.Add(self.bank_ledger_btn, 0, wx.EXPAND | wx.ALL, 5)

        self.edit_btn = wx.Button(self, label="Edit Stmt")
        self.sizer.Add(self.edit_btn, 0, wx.EXPAND | wx.ALL, 5)

        self.save_stmt_btn = wx.Button(self, label="Save Stmt")
        self.sizer.Add(self.save_stmt_btn, 0, wx.EXPAND | wx.ALL, 5)

        self.back_btn = wx.Button(self, label="Back")
        self.sizer.Add(self.back_btn, 0, wx.EXPAND | wx.ALL, 5)

    def bind_buttons(self) -> None:
        self.simplify_btn.Bind(wx.EVT_BUTTON, self.on_simplify_stmt)
        self.remove_col_btn.Bind(wx.EVT_BUTTON, self.on_remove_col)
        self.bank_ledger_btn.Bind(wx.EVT_BUTTON, self.on_bank_ledger)
        self.edit_btn.Bind(wx.EVT_BUTTON, self.set_grid_readable)
        self.save_stmt_btn.Bind(wx.EVT_BUTTON, self.on_save_stmt)
        # self.back_btn.Bind(wx.EVT_BUTTON,self.on_Back)

    def set_grid_readable(self, event) -> None:
        self.table_grid.EnableEditing(True)
        self.table_grid.set_col_header_names()
        self.table_grid.update_grid_col()

    def on_simplify_stmt(self, event) -> None:
        # Remove rows from the dataframe if more than three columns contain NaN values
        self.stmt.dropna(thresh=len(self.stmt.columns) - 2, inplace=True)
        # Remove columns from the dataframe if they only contain NaN values
        self.stmt.dropna(axis=1, how='all', inplace=True)
        self.stmt.fillna(0, inplace=True)
        self.set_col_name()
        self.table_grid.set_col_header_names()
        self.table_grid.EnableEditing(False)
        self.table_grid.update_grid_row()
        self.select_main_col()

    def set_col_name(self):
        # Assuming df is your DataFrame
        if self.stmt.columns.str.contains('Unnamed').sum() > 3:
            self.stmt.columns = self.stmt.iloc[0]
            self.stmt.drop(self.stmt.index[0], inplace=True)

    def on_remove_col(self, event) -> None:
        with RemoveColumnsDialog(self, self.stmt.columns) as columnDialog:
            if columnDialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind

            # Get the column names checked by the user
            column_names = columnDialog.GetCheckedItems()

            # Remove the specified columns from the dataframe
            self.stmt.drop(column_names, axis=1, inplace=True)
            self.table_grid.set_col_header_names()
            self.table_grid.update_grid_col()

    def get_file_path(self) -> str :
        # Create a file dialog
        with wx.FileDialog(self, "Open Excel file", wildcard="Excel files (*.xlsx)|*.xlsx") as file_dialog:
            file_dialog: wx.FileDialog = file_dialog

            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind

            # Proceed loading the file chosen by the user
            return file_dialog.GetPath()

    def on_bank_ledger(self, event) -> None:
        self.select_col_for_ledger()

    def on_save_stmt(self, event) -> None:
        with wx.FileDialog(self, "Save as Excel or CSV", wildcard="Excel files (*.xlsx)|*.xlsx|CSV files (*.csv)|*.csv",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind

            # save the current contents in the file
            pathname = fileDialog.GetPath()
            try:
                # Assuming df is your DataFrame
                if pathname.endswith('.xlsx'):
                    self.stmt.to_excel(pathname, index=False)
                elif pathname.endswith('.csv'):
                    self.stmt.to_csv(pathname, index=False)
            except IOError:
                wx.LogError("Cannot save current data in file '%s'." % pathname)

    def style_buttons(self) -> None:
        pass

    def set_hint_on_buttons(self) -> None:
        self.back_btn.SetToolTip("Navigate Home Window")
        self.edit_btn.SetToolTip("Enable Edit for left side table")
        self.bank_ledger_btn.SetToolTip("Generate a New Ledger Table")

    def select_main_col(self) -> None:
        # Create a custom dialog
        type_of_stmt = self.GrandParent.left_panel.type_of_stmt
        with MainColumnsSelectorDialog(self, self.stmt.columns, type_of_stmt) as main_col_dialog:

            if main_col_dialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind

            # Get the column names checked by the user
            column_names = main_col_dialog.GetCheckedItems()
            self.stmt_simplifier = StatementSimplifier(self.stmt)

            if type_of_stmt == "dr_cr_col":
                self.stmt_simplifier.dr_cr(column_names[2], column_names[1], column_names[0], column_names[3])
                column_names.remove(column_names[-1])
                self.stmt.drop(column_names[1:], axis=1, errors='ignore', inplace=True)
                self.stmt.fillna(0, inplace=True)
            elif type_of_stmt == "amt_dr_cr_col":
                self.stmt_simplifier.clean(column_names[1], column_names[0], column_names[2])
                column_names.remove(column_names[-1])
                self.stmt.drop(column_names[1:], axis=1, errors='ignore', inplace=True)
                self.stmt.fillna(0, inplace=True)
            else:
                self.stmt_simplifier.clean_data(column_names[2], column_names[1], column_names[3], column_names[0])

            # Keep only the specified columns in the dataframe
            # self.df = self.df[column_names]
            self.table_grid.update_grid_col()
            self.table_grid.set_col_header_names()
            self.frame.is_object_ref_same()

    def onPrint(self, event):
        printout.PrintGrid(self.GrandParent, self.table_grid).Print()

    def onPreview(self, event) -> None:
        """
        preview and print the table grid
        :param event:
        :return:
        """
        printout.PrintGrid(self.GrandParent, self.table_grid).Preview()

    def select_col_for_ledger(self) -> None:
        # Create a custom dialog
        with SelectColumnsDialog(self, self.stmt.columns) as select_col_dialog:
            if select_col_dialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind
            # Get the column names checked by the user
            column_names = select_col_dialog.GetCheckedItems()
            if column_names[-1] != column_names[-2]:
                ledger = self.stmt_simplifier.bankAc(column_names[0], column_names[1], column_names[2], column_names[3])
                ledger.columns = [
                    "Date", "Particulars (Deposit)", "Amount", "Date", "Particulars (Withdraw)", "Amount"]
                preview = DataFramePreview(self.GrandParent, ledger)
                preview.Show()

    def check_data_type(self):
        for column in self.stmt.columns:
            print(f"Data type of {column} is {self.stmt[column].dtype}")
