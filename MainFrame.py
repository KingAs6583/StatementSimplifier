import wx
import sys
import os
import pkg_resources
from SimpliferPanels import (DisplaySidePanel, LeftSidePanel, RightSidePanel)


class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="Bank Statement Simplifier", size=(800, 600))
        # positioning to center
        self.Centre()
        # Create a parent panel
        self.parentPanel = wx.Panel(self)

        # Create a vertical box sizer for the panels
        self.left_panel_sizer = wx.BoxSizer(wx.VERTICAL)
        self.right_panel_sizer = wx.BoxSizer(wx.VERTICAL)

        # Create another panel on the Display 
        self.display_panel = DisplaySidePanel(self.parentPanel)
        self.display_panel.SetBackgroundColour('#FFFFED')  # To distinguish display panel

        # Create a left panel on the left side
        self.left_panel = LeftSidePanel(self.parentPanel, size=(200, -1), left_panel_sizer=self.left_panel_sizer,
                                        display_panel=self.display_panel)
        self.left_panel.SetBackgroundColour('#ADD8E6')  # To distinguish left panel

        # Create a right side panel
        self.right_panel = RightSidePanel(self.parentPanel, (200, -1), self.right_panel_sizer, self.display_panel, self)
        self.right_panel.SetBackgroundColour('green')  # To distinguish right panel

        # Create a box sizer
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Add left panel, display panel and right panel to the sizer
        self.sizer.Add(self.left_panel, 0, wx.EXPAND)
        self.sizer.Add(self.display_panel, 1, wx.EXPAND)
        self.sizer.Add(self.right_panel, 0, wx.EXPAND)
        # Hide the right panel
        self.right_panel.Hide()

        # Set the sizer for the left panel
        self.left_panel.SetSizer(self.left_panel_sizer)

        # Set the sizer for the parent panel
        self.parentPanel.SetSizer(self.sizer)

        self.Show()

    def navigate_right_panel(self, event) -> None:
        """_summary_
        navigate from left to right panel and hide left panel
        and set table to panel and show it on display panel
        Args:
            event (_type_): _description_
        """
        if self.display_panel.stmt is not None:
            self.left_panel.Hide()
            self.right_panel.set_stmt(self.display_panel.stmt)
            self.right_panel.set_table_grid(self.display_panel.table_grid)
            # onclick back btn
            self.right_panel.back_btn.Bind(wx.EVT_BUTTON, self.navigate_left_panel)
            # self.sizer.Replace(self.left_panel,self.right_panel)
            self.right_panel.Show()
            self.right_panel.SetSizer(self.right_panel_sizer)
            self.parentPanel.Layout()

    def navigate_left_panel(self, event) -> None:
        """_summary_
        navigate from left to right panel and hide right panel
        Args:
            event (_type_): _description_
        """
        # Hide the right panel and show the left panel
        self.right_panel.Hide()
        # self.sizer.Replace(self.right_panel,self.left_panel)
        self.left_panel.Show()
        # Update the layout
        self.parentPanel.Layout()

    def on_navigate_right(self, event) -> None:
        """_summary_
        read the Excel or csv file and create table and navigate to right panel
        Args:
            event (_type_): _description_
        """
        self.left_panel.on_read_stmt(event)
        self.navigate_right_panel(event)

    def is_object_ref_same(self) -> None:
        """
        check if the pandas reference is same or not
        """
        if self.right_panel.stmt is self.right_panel.table_grid.df and self.right_panel.stmt is self.display_panel.stmt:
            print("\033[91m {}\033[00m".format('same reference rp_s = rt_df'))
        else:
            print("\033[91m {}\033[00m".format('different reference'))

        if self.display_panel.stmt is self.display_panel.table_grid.df:
            print("\033[91m {}\033[00m".format('same reference dp_s = dt_df'))
        else:
            print("\033[91m {}\033[00m".format('different reference'))


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


if __name__ == "__main__":
    app = wx.App(False)
    # Set the icon for the frame
    frame = MainFrame()
    try:
        icon_path = resource_path("Icons/icon.png")
        print(icon_path)
        image = wx.Image(icon_path, wx.BITMAP_TYPE_ANY)
        scaled_image = image.Scale(48, 48, wx.IMAGE_QUALITY_HIGH)
        icon = wx.Icon(wx.Bitmap(scaled_image))
        frame.SetIcon(icon)
    except:
        pass
    app.MainLoop()
