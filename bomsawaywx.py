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

        self._current_type = None
        self.grid = wx.GridSizer(0, 2, 3, 3)

        self.lookup_button = wx.Button(self, 310, 'Part Lookup')
        self.save_button = wx.Button(self, 311, 'Save Part to Datastore')

        self.qty_text = wx.TextCtrl(self, 301, '', style=wx.TE_READONLY)
        self.refs_text = wx.TextCtrl(self, 302, '', style=wx.TE_READONLY)
        self.fp_text = wx.TextCtrl(self, 303, '', style=wx.TE_READONLY)
        self.value_text = wx.TextCtrl(self, 304, '')
        self.ds_text = wx.TextCtrl(self, 305, '')
        self.mfr_text = wx.TextCtrl(self, 306, '')
        self.mpn_text = wx.TextCtrl(self, 307, '')
        self.spr_text = wx.TextCtrl(self, 308, '')
        self.spn_text = wx.TextCtrl(self, 309, '')

        # Set the background color of the read only controls to
        # slightly darker to differentiate them
        for ctrl in (self.qty_text, self.refs_text, self.fp_text):
            ctrl.SetBackgroundColour(wx.ColourDatabase().Find('Light Grey'))

        self._populate_grid()

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
        vbox.Add(self.grid, 1, wx.EXPAND | wx.ALL, 3)
        vbox.Add(selbox, 3, wx.EXPAND | wx.ALL, 3)

        self.SetSizer(vbox)

    def _populate_grid(self):
        # Create text objects to be stored in grid

        # Create the component detail grid
        self.grid.AddMany([
            (wx.StaticText(self, -1, 'Quantity'), 0, wx.EXPAND),
            (self.qty_text, 0, wx.EXPAND),
            (wx.StaticText(self, -1, 'Refs'), 0, wx.EXPAND),
            (self.refs_text, 0, wx.EXPAND),
            (wx.StaticText(self, -1, 'Footprint'), 0, wx.EXPAND),
            (self.fp_text, 0, wx.EXPAND),
            (wx.StaticText(self, -1, 'Value'), 0, wx.EXPAND),
            (self.value_text, 0, wx.EXPAND),
            (wx.StaticText(self, -1, 'Datasheet'), 0, wx.EXPAND),
            (self.ds_text, 0, wx.EXPAND),
            (wx.StaticText(self, -1, 'Manufacturer'), 0, wx.EXPAND),
            (self.mfr_text, 0, wx.EXPAND),
            (wx.StaticText(self, -1, 'Manufacturer PN'), 0, wx.EXPAND),
            (self.mpn_text, 0, wx.EXPAND),
            (wx.StaticText(self, -1, 'Supplier'), 0, wx.EXPAND),
            (self.spr_text, 0, wx.EXPAND),
            (wx.StaticText(self, -1, 'Supplier PN'), 0, wx.EXPAND),
            (self.spn_text, 0, wx.EXPAND),
            (self.lookup_button, 0, wx.EXPAND),
            (self.save_button, 0, wx.EXPAND),
        ])

    def save_component_type_changes(self):
        comp = self._current_type

        if not comp:
            return

        comp.value = self.value_text.GetValue()
        comp.datasheet = self.ds_text.GetValue()
        comp.manufacturer = self.mfr_text.GetValue()
        comp.manufacturer_pn = self.mpn_text.GetValue()
        comp.supplier = self.spr_text.GetValue()
        comp.supplier_pn = self.spn_text.GetValue()

    def on_fp_list(self, event):
        self.save_component_type_changes()
        self.comp_list.Clear()
        self._current_type = None

        map(self.comp_list.Append,
            [x for x in sorted(set(self.type_data[self.fp_list.GetStringSelection()].keys()))])

    def on_comp_list(self, event):
        self.save_component_type_changes()
        fp = self.fp_list.GetStringSelection()
        ct = self.comp_list.GetStringSelection()

        comp = self.type_data[fp][ct]

        self.qty_text.SetValue(str(len(comp)))
        self.refs_text.SetValue(comp.refs)
        self.fp_text.SetValue(comp.footprint)
        self.value_text.SetValue(comp.value)
        self.ds_text.SetValue(comp.datasheet)
        self.mfr_text.SetValue(comp.manufacturer)
        self.mpn_text.SetValue(comp.manufacturer_pn)
        self.spr_text.SetValue(comp.supplier)
        self.spn_text.SetValue(comp.supplier_pn)

        self._current_type = comp

    def _reset(self):
        self.comp_list.Clear()
        self.fp_list.Clear()
        self._current_type = None

    def attach_data(self, type_data):
        self.type_data = type_data

        self._reset()

        map(self.fp_list.Append,
            [x for x in sorted(set(type_data.keys()))])

class UniquePartSelectorDialog(wx.Dialog):
    def __init__(self, parent, id, title):
        wx.Dialog.__init__(self, parent, id, title)
        self.selection_idx = None
        self.selection_text = None

        vbox = wx.BoxSizer(wx.VERTICAL)
        stline = wx.StaticText(self, 11, 'Duplicate Component values found!\n\nPlease select which format to follow:')
        vbox.Add(stline, 1, wx.ALIGN_CENTER|wx.TOP, 45)
        self.comp_list = wx.ListBox(self, 331, style=wx.LB_SINGLE)

        vbox.Add(self.comp_list, 0, wx.ALIGN_CENTER)
        self.SetSizer(vbox)
        self.comp_list.Bind(wx.EVT_LISTBOX, self.on_selection, id=wx.ID_ANY)

    def on_selection(self, event):
        self.selection_text = self.comp_list.GetStringSelection()
        self.selection_idx = self.comp_list.GetSelection()
        self.Close()

    def attach_data(self, data):
        map(self.comp_list.Append, data)

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
        self.Bind(wx.EVT_MENU, self.on_consolidate, id=201)

    def _reset(self):
        self.schematics = {}
        self.component_type_map = {}

    def _consolidate(self):
        """
        Performs consolidation
        """
        uniq = {}
        dups = {}

        # Find all duplicated components and put them into a dups map
        for fp in self.component_type_map:
            for ct in self.component_type_map[fp]:
                cthsh = ct.upper().replace(' ', '')

                if cthsh in uniq:
                    if cthsh not in dups:
                        dups[cthsh] = [uniq[cthsh]]

                    dups[cthsh].append(self.component_type_map[fp][ct])
                else:
                    uniq[cthsh] = self.component_type_map[fp][ct]

        for d, cl in dups.items():

            _popup = UniquePartSelectorDialog(self,
                                              wx.ID_ANY,
                                              'Duplicate part value')

            _popup.attach_data([x.value for x in cl])
            _popup.ShowModal()

            # If the user didn't select anything, just move on
            if not _popup.selection_idx:
                continue

            sel = cl.pop(_popup.selection_idx)

            for rem in cl:
                old_fp = rem.footprint
                old_val = rem.value

                # Set all relevant fields
                rem.value = sel.value
                rem.manufacturer = sel.manufacturer
                rem.manufacturer_pn = sel.manufacturer_pn
                rem.supplier_pn = sel.supplier_pn
                rem.supplier = sel.supplier

                sel.extract_components(rem)
                del self.component_type_map[old_fp][old_val]

            self.ctv.attach_data(self.component_type_map)

            _popup.Destroy()


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
        # TODO: re-work this to return values instead of passing them byref
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

                if c.footprint not in self.component_type_map:
                    self.component_type_map[c.footprint] = {}

                if c.value not in self.component_type_map[c.footprint]:
                    self.component_type_map[c.footprint][c.value] = kch.ComponentTypeContainer()

                self.component_type_map[c.footprint][c.value].add(c)

        self.ctv.attach_data(self.component_type_map)
        self._current_type = None
        self.ctv.lookup_button.disabled = True
        self.ctv.save_button.disabled = True

    def on_consolidate(self, event):
        self._consolidate()

    def on_open(self, event):
        """
        Recursively loads a KiCad schematic and all subsheets
        """
        #self.save_component_type_changes()
        openFileDialog = wx.FileDialog(self, "Open KiCad Schematic", "", "",
                                       "Kicad Schematics (*.sch)|*.sch",
                                       wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

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

    def on_save(self, event):
        self.ctv.save_component_type_changes()
        for name, schematic in self.schematics.items():
            schematic.save()


class BomsAwayApp(wx.App):
    def OnInit(self):
        frame = MainFrame(None, -1, 'Boms-Away!')
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

if __name__ == '__main__':
    BomsAwayApp(0).MainLoop()
