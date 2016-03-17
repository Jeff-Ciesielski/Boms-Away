#!/usr/bin/env pythonw
import os
import csv

import wx
from boms_away import sch, datastore
from boms_away import kicad_helpers as kch

class ComponentTypeView(wx.Panel):
    def __init__(self, parent, id):
        super(ComponentTypeView, self).__init__(parent, id, wx.DefaultPosition)
        vbox = wx.BoxSizer(wx.VERTICAL)
        grid = wx.GridSizer(0, 2, 3, 3)

        grid.AddMany([
            (wx.StaticText(self, -1, 'Quantity'), 0, wx.EXPAND),
            (wx.TextCtrl(self, 301, ''), 0, wx.EXPAND),
            (wx.StaticText(self, -1, 'Refs'), 0, wx.EXPAND),
            (wx.TextCtrl(self, 302, ''), 0, wx.EXPAND),
            (wx.StaticText(self, -1, 'Footprint'), 0, wx.EXPAND),
            (wx.TextCtrl(self, 303, ''), 0, wx.EXPAND),
            (wx.StaticText(self, -1, 'Value'), 0, wx.EXPAND),
            (wx.TextCtrl(self, 304, ''), 0, wx.EXPAND),
            (wx.StaticText(self, -1, 'Datasheet'), 0, wx.EXPAND),
            (wx.TextCtrl(self, 305, ''), 0, wx.EXPAND),
            (wx.StaticText(self, -1, 'Manufacturer'), 0, wx.EXPAND),
            (wx.TextCtrl(self, 306, ''), 0, wx.EXPAND),
            (wx.StaticText(self, -1, 'manufacturer PN'), 0, wx.EXPAND),
            (wx.TextCtrl(self, 307, ''), 0, wx.EXPAND),
            (wx.StaticText(self, -1, 'Supplier'), 0, wx.EXPAND),
            (wx.TextCtrl(self, 308, ''), 0, wx.EXPAND),
            (wx.StaticText(self, -1, 'Supplier PN'), 0, wx.EXPAND),
            (wx.TextCtrl(self, 309, ''), 0, wx.EXPAND),
        ])

        vbox.Add(grid, 1, wx.EXPAND | wx.ALL, 3)
        self.SetSizer(vbox)

class MainFrame(wx.Frame):
    def __init__(self, parent, id, title):
        super(MainFrame, self).__init__(parent, id, title, wx.DefaultPosition, wx.Size(800, 600))
        self._create_menu()
        self._do_layout()
        self.Centre()

    def _do_layout(self):
        vbox = wx.BoxSizer(wx.VERTICAL)
        pnl1 = ComponentTypeView(self, -1)
        pnl2 = wx.Panel(self, -1, style=wx.SIMPLE_BORDER)

        vbox.Add(pnl1, 1, wx.EXPAND | wx.ALL, 3)
        vbox.Add(pnl2, 1, wx.EXPAND | wx.ALL, 3)

        self.SetSizer(vbox)

    def _create_menu(self):
        menubar = wx.MenuBar()
        file = wx.Menu()
        edit = wx.Menu()
        help = wx.Menu()
        file.Append(101, '&Open', 'Open a schematic')
        file.Append(102, '&Save', 'Save the schematic')
        file.AppendSeparator()
        file.Append(103, '&Export BOM as CSV', 'Export the BOM as CSV')
        file.AppendSeparator()
        quit = wx.MenuItem(file, 105, '&Quit\tCtrl+Q', 'Quit the Application')
        file.AppendItem(quit)
        edit.Append(201, 'Consolidate Components', 'Consolidate duplicated components')
        menubar.Append(file, '&File')
        menubar.Append(edit, '&Edit')
        menubar.Append(help, '&Help')
        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.on_quit, id=105)
        self.Bind(wx.EVT_MENU, self.on_open, id=101)

    def on_open(self, event):
        """
        Recursively loads a KiCad schematic and all subsheets
        """
        #self.save_component_type_changes()
        openFileDialog = wx.FileDialog(self, "Open KiCad Schematic", "", "",
                                       "Kicad Schematics (*.sch)|*.sch", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            return

        # Load Chosen Schematic
        print "opening File:", openFileDialog.GetPath()

    def on_quit(self, event):
        """
        Quits the application
        """
        #self.save_component_type_changes()
        exit(0)

class BomsAwayApp(wx.App):
    def OnInit(self):
        frame = MainFrame(None, -1, 'Boms-Away!')
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

if __name__ == '__main__':
    BomsAwayApp(0).MainLoop()
