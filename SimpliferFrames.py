import wx
from TableGrid import TableGrid


class DataFramePreview(wx.Frame):
    def __init__(self, parent, df):
        wx.Frame.__init__(self, parent, -1, "Ledger Preview", size=(600, 300))
        self.Centre()
        self.df = df.fillna('')
        self.grid = TableGrid(self, df)
        self.grid.CreateGrid(df.shape[0], df.shape[1])

        for r in range(df.shape[0]):
            for c in range(df.shape[1]):
                self.grid.SetCellValue(r, c, str(df.iat[r, c]))
        self.grid.set_col_header_names()

        self.saveButton = wx.Button(self, label="Save")
        self.saveButton.Bind(wx.EVT_BUTTON, self.on_save)
        self.cancelButton = wx.Button(self, label="Cancel")
        self.cancelButton.Bind(wx.EVT_BUTTON, self.on_cancel)

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(self.saveButton, 1, wx.ALL | wx.CENTER, 5)
        button_sizer.Add(self.cancelButton, 1, wx.ALL | wx.CENTER, 5)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.grid, 1, wx.EXPAND)
        sizer.Add(button_sizer, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer)

    def on_save(self, event):
        with wx.FileDialog(self, "Save as Excel or CSV", wildcard="Excel files (*.xlsx)|*.xlsx|CSV files (*.csv)|*.csv",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind

            # save the current contents in the file
            pathname = fileDialog.GetPath()
            try:
                #  df is  DataFrame
                if pathname.endswith('.xlsx'):
                    self.df.to_excel('Ledger_' + pathname, index=False)
                elif pathname.endswith('.csv'):
                    self.df.to_csv('Ledger_' + pathname, index=False)
                del self.df
                self.Destroy()
            except IOError:
                wx.LogError("Cannot save current data in file '%s'." % pathname)

    def on_cancel(self, event):
        self.Destroy()
