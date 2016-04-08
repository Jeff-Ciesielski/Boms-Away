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

        self.lookup_button = wx.Button(self, 310, 'Part Lookup')
        self.save_button = wx.Button(self, 311, 'Save Part to Datastore')

        # Create the component detail grid
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
            (wx.StaticText(self, -1, 'Manufacturer PN'), 0, wx.EXPAND),
            (wx.TextCtrl(self, 307, ''), 0, wx.EXPAND),
            (wx.StaticText(self, -1, 'Supplier'), 0, wx.EXPAND),
            (wx.TextCtrl(self, 308, ''), 0, wx.EXPAND),
            (wx.StaticText(self, -1, 'Supplier PN'), 0, wx.EXPAND),
            (wx.TextCtrl(self, 309, ''), 0, wx.EXPAND),
            (self.lookup_button, 0, wx.EXPAND),
            (self.save_button, 0, wx.EXPAND),
        ])

        # Create fooprint selector box
        fpbox = wx.BoxSizer(wx.VERTICAL)

        fp_label = wx.StaticText(self, -1, 'Footprints', style=wx.ALIGN_CENTER_HORIZONTAL)
        self.fp_list = wx.ListBox(self, 330, style=wx.LB_SINGLE)

        fpbox.Add(fp_label, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND)
        fpbox.Add(self.fp_list, 1, wx.EXPAND)

        self.fp_list.Bind(wx.EVT_LISTBOX, self.on_fp_list, id=wx.ID_ANY)
 
        # Create Component selector box
        compbox = wx.BoxSizer(wx.VERTICAL)

        comp_label = wx.StaticText(self, -1, 'Componenents', style=wx.ALIGN_CENTER_HORIZONTAL)
        self.comp_list = wx.ListBox(self, 331, style=wx.LB_SINGLE)

        compbox.Add(comp_label,  0, wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND)
        compbox.Add(self.comp_list, 1, wx.EXPAND)
        self.comp_list.Bind(wx.EVT_LISTBOX, self.on_comp_list, id=wx.ID_ANY)
 
        # Lay out the fpbox and compbox side by side
        selbox = wx.BoxSizer(wx.HORIZONTAL)

        selbox.Add(fpbox, 1, wx.EXPAND)
        selbox.Add(compbox, 1, wx.EXPAND)

        # Perform final layout
        vbox.Add(grid, 1, wx.EXPAND | wx.ALL, 3)
        vbox.Add(selbox, 3, wx.EXPAND | wx.ALL, 3)

        self.SetSizer(vbox)

    def on_fp_list(self, event):
        self.comp_list.Clear()
        map(self.comp_list.Append,
            [x for x in sorted(set(self.type_data[self.fp_list.GetStringSelection()].keys()))])

    def on_comp_list(self, event):
        pass

    def _reset(self):
        self.comp_list.Clear()
        self.fp_list.Clear()

    def attach_data(self, type_data):
        self.type_data = type_data

        map(self.fp_list.Append,
            [x for x in sorted(set(type_data.keys()))])


class MainFrame(wx.Frame):
    def __init__(self, parent, id, title):
        super(MainFrame, self).__init__(parent, id, title, wx.DefaultPosition, wx.Size(800, 600))
        self._create_menu()
        self._do_layout()
        self.Centre()

        self._reset()

    def _do_layout(self):
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.ctv = ComponentTypeView(self, -1)

        vbox.Add(self.ctv, 1, wx.EXPAND | wx.ALL, 3)

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

    def _reset(self):
        self.schematics = {}
        self.component_type_map = {}

    def load(self, path):
        if len(path) == 0:
            return

        # remove old schematic information
        self._reset()

        base_dir = os.path.split(path)[0]
        top_sch = os.path.split(path)[-1]
        top_name = os.path.splitext(top_sch)[0]

        compmap = {}

        self.schematics[top_name] = (
            sch.Schematic(os.path.join(base_dir, top_sch))
        )

        # Recursively walks sheets to locate nested subschematics
        kch.walk_sheets(base_dir, self.schematics[top_name].sheets, self.schematics)

        for name, schematic in self.schematics.items():
            for _cbase in schematic.components:
                c = kch.ComponentWrapper(_cbase)

                # Skip virtual components (power, gnd, etc)
                if c.is_virtual:
                    continue

                # Skip anything that is missing either a value or a
                # footprint
                if not c.has_valid_key_fields:
                    continue

                c.add_bom_fields()

                # TODO: Remove typeid, just map by footprint:>component
                if c.footprint not in self.component_type_map:
                    self.component_type_map[c.footprint] = {}

                if c.value not in self.component_type_map[c.footprint]:
                    self.component_type_map[c.footprint][c.value] = []

                self.component_type_map[c.footprint][c.value].append(c)

        self.ctv.attach_data(self.component_type_map)
        self._current_type = None
        self.ctv.lookup_button.disabled = True
        self.ctv.save_button.disabled = True


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

        self.load(openFileDialog.GetPath())

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
