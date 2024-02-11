import wx


class RemoveColumnsDialog(wx.Dialog):
    """
    This is custom Dialog which pop up to take a column which has to be removed
    """

    def __init__(self, parent, column_names: list):
        """
        :param parent = frame
        :param column_names = list
        """
        wx.Dialog.__init__(self, parent, title="Select Columns to Remove")

        self.checkboxes: list[wx.CheckBox] = []
        sizer = wx.BoxSizer(wx.VERTICAL)

        for name in column_names:
            checkbox = wx.CheckBox(self, label=name)
            self.checkboxes.append(checkbox)
            sizer.Add(checkbox, 0, wx.ALL, 5)

        self.removeButton = wx.Button(self, label="Remove")
        self.removeButton.Bind(wx.EVT_BUTTON, self.OnRemove)
        sizer.Add(self.removeButton, 0, wx.ALL, 5)

        self.SetSizer(sizer)

    def GetCheckedItems(self):
        return [checkbox.GetLabel() for checkbox in self.checkboxes if checkbox.IsChecked()]

    def OnRemove(self, event):
        self.EndModal(wx.ID_OK)


class MainColumnsSelectorDialog(wx.Dialog):
    """
    Select the Main columns for simplifying statement
    """

    def __init__(self, parent, column_names: list, type_of_stmt: str):
        wx.Dialog.__init__(self, parent, title="Select Main Columns")

        self.static_text: list[wx.StaticText] = []
        self.combo_boxes: list[wx.ComboBox] = []
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.column_names = column_names

        if type_of_stmt == "dr_cr_col":
            self.create_gui_components(self.get_main_dr_cr_type_col())
        elif type_of_stmt == "amt_dr_cr_col":
            self.create_gui_components(self.get_main_amt_dr_cr_type_col())
        else:
            self.create_gui_components(self.get_main_cols())

        self.removeButton = wx.Button(self, label="Simplify")
        self.removeButton.Bind(wx.EVT_BUTTON, self.OnRemove)
        self.sizer.Add(self.removeButton, 0, wx.ALL, 5)

        self.SetSizer(self.sizer)

    @staticmethod
    def get_main_cols() -> tuple:
        return (
            "Description or Remarks Column", "Debit or Withdrawal Column", "Credit or Deposit Column", "Balance Column")

    @staticmethod
    def get_main_dr_cr_type_col() -> tuple:
        return (
            "Description or Remarks Column", "Dr/Cr Indicator Column", "Transaction Amount Column", "Balance Column")

    @staticmethod
    def get_main_amt_dr_cr_type_col() -> tuple:
        return ("Description or Remarks Column", "Amount With Dr/Cr Column Example 12(cr)", "Balance Column")

    def create_gui_components(self, labels):
        for label in labels:
            textCtrl = wx.StaticText(self, label=label, pos=(25, 25))
            self.static_text.append(textCtrl)
            self.sizer.Add(textCtrl, 0, wx.ALL, 5)

            combobox = wx.ComboBox(self, choices=self.column_names)
            self.combo_boxes.append(combobox)
            self.sizer.Add(combobox, 0, wx.ALL, 5)

    def GetCheckedItems(self):
        return [combobox.GetValue() for combobox in self.combo_boxes]

    def OnRemove(self, event):
        """
        close the dialog
        """
        self.EndModal(wx.ID_OK)


class SelectColumnsDialog(wx.Dialog):
    """
    This is custom Dialog which pop up to take a column which has to be removed
    """

    def __init__(self, parent, column_names: list):
        """
        :param parent = frame
        :param column_names = list
        """
        wx.Dialog.__init__(self, parent, title="Select Columns for Creation of Ledger")

        self.static_text: list[wx.StaticText] = []
        self.combo_boxes: list[wx.ComboBox] = []
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.column_names = column_names

        labels = ("Select Date Column", "Select Description or Remarks Column", "Select Debit or Withdrawal Column",
                  "Select Credit or Deposit Column")
        self.create_gui_components(labels)
        self.removeButton = wx.Button(self, label="Create Ledger")
        self.removeButton.Bind(wx.EVT_BUTTON, self.OnRemove)
        self.sizer.Add(self.removeButton, 0, wx.ALL, 5)

        self.SetSizer(self.sizer)

    def create_gui_components(self, labels):
        for label in labels:
            textCtrl = wx.StaticText(self, label=label, pos=(25, 25))
            self.static_text.append(textCtrl)
            self.sizer.Add(textCtrl, 0, wx.ALL, 5)

            combobox = wx.ComboBox(self, choices=self.column_names)
            self.combo_boxes.append(combobox)
            self.sizer.Add(combobox, 0, wx.ALL, 5)

    def GetCheckedItems(self):
        return [combobox.GetValue() for combobox in self.combo_boxes]

    def OnRemove(self, event):
        self.EndModal(wx.ID_OK)
