#!/usr/bin/env python

import os
import sch
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty,\
    ObjectProperty, ListProperty, DictProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.factory import Factory
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.adapters.listadapter import ListAdapter
from kivy.garden.NavigationDrawer import NavigationDrawer
from kivy.core.window import Window
import csv

# TODO: Normalize all input schematic components to follow field
# guidelines

SidePanel_AppMenu = {'Load Schematic': ['on_load', None],
                     'Save Schematic': ['on_save', None],
                     'Components': ['on_component', None],
                     'Component Types': ['on_type', None],
                     'Export BOM as CSV': ['on_export_csv', None],
                     'Quit': ['on_quit', None],
                     'Consolidate Like Components': ['on_consolidate', None],
                     }
id_AppMenu_METHOD = 0
id_AppMenu_PANEL = 1


class SidePanel(BoxLayout):
    pass


class NavDrawer(NavigationDrawer):
    def __init__(self, **kwargs):
        super(NavDrawer, self).__init__(**kwargs)

    def close_sidepanel(self, animate=True):
        if self.state == 'open':
            if animate:
                self.anim_to_state('closed')
            else:
                self.state = 'closed'


class MenuItem(Button):
    def __init__(self, **kwargs):
        super(MenuItem, self).__init__(**kwargs)
        self.bind(on_press=self.menuitem_selected)

    def menuitem_selected(self, *args):
        print ("{} {} {}".format(
            self.text,
            SidePanel_AppMenu[self.text],
            SidePanel_AppMenu[self.text][id_AppMenu_METHOD]
        ))
        try:
            function_to_call = SidePanel_AppMenu[self.text][id_AppMenu_METHOD]
        except:
            print 'Error configuring menu'
            return
        getattr(AppRoot, function_to_call)()


class UniquePartSelectorDialog(BoxLayout):
    selection = NumericProperty(None)
    dismiss = ObjectProperty(None)

class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


class ExportDialog(FloatLayout):
    export = ObjectProperty(None)
    cancel = ObjectProperty(None)

# TODO: Attempt to fold selectablelist/componentview/componenttypeview
# into one base class, then subclass for the editor views
class SelectableList(BoxLayout):
    component_view = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(SelectableList, self).__init__(**kwargs)


# TODO: Enumerate field values
class ComponentWrapper(object):
    def __init__(self, base_component):
        self._cmp = base_component

    def _get_field(self, field_no):
        return (
            [x for x in self._cmp.fields if x['id'] == str(field_no)][0]
        )

    def _set_field_value(self, field_no, value):
        f = self._get_field(field_no)
        f['ref'] = '"{}"'.format(value)

    def _get_field_value(self, field_no):
        try:
            return self._get_field(field_no)['ref'].strip('"')
        except:
            return ''

    @property
    def reference(self):
        return self._get_field_value(0)

    @property
    def value(self):
        return self._get_field_value(1)

    @value.setter
    def value(self, val):
        self._set_field_value(1, val)

    @property
    def footprint(self):
        return self._get_field_value(2)

    @property
    def datasheet(self):
        return self._get_field_value(3)

    @datasheet.setter
    def datasheet(self, val):
        self._set_field_value(3, val)

    @property
    def is_virtual(self):
        if self._cmp.labels['ref'][0] == '#':
            return True
        return False

    @property
    def manufacturer(self):
        return self._get_field_value(7)

    @manufacturer.setter
    def manufacturer(self, mfr):
        self._set_field_value(7, mfr)

    @property
    def supplier(self):
        return self._get_field_value(6)

    @supplier.setter
    def supplier(self, sup):
        self._set_field_value(6, sup)

    @property
    def manufacturer_pn(self):
        return self._get_field_value(5)

    @manufacturer_pn.setter
    def manufacturer_pn(self, pn):
        self._set_field_value(5, pn)

    @property
    def supplier_pn(self):
        return self._get_field_value(4)

    @supplier_pn.setter
    def supplier_pn(self, pn):
        self._set_field_value(4, pn)

    def __str__(self):
        return '\n'.join([
            '\nComponent: {}'.format(self.reference),
            '-' * 20,
            'Value: {}'.format(self.value),
            'Footprint: {}'.format(self.footprint),
        ])

class ComponentTypeContainer(object):
    def __init__(self):
        self._components = []

    def add(self, component):
        # Only allow insertion of like components
        if len(self._components):
            if ((component.value != self._components[0].value) or
                (component.footprint != self._components[0].footprint)):
                raise Exception("Attempted to insert unlike component into ComponentTypeContainer")

        self._components.append(component)

    def __len__(self):
        return len(self._components)

    # TODO: Add validation function and enforce!

    def extract_components(self, other):
        for c in other._components:
            self.add(c)

    @property
    def refs(self):
        return ';'.join([x.reference for x in self._components])

    @property
    def value(self):
        return self._components[0].value

    @value.setter
    def value(self, val):
        for c in self._components:
            c.value = val

    @property
    def footprint(self):
        return self._components[0].footprint

    @property
    def datasheet(self):
        return self._components[0].datasheet

    @datasheet.setter
    def datasheet(self, ds):
        for c in self._components:
            c.datasheet = ds

    @property
    def manufacturer(self):
        return self._components[0].manufacturer

    @manufacturer.setter
    def manufacturer(self, mfgr):
        for c in self._components:
            c.manufacturer = mfgr

    @property
    def manufacturer_pn(self):
        return self._components[0].manufacturer_pn

    @manufacturer_pn.setter
    def manufacturer_pn(self, pn):
        for c in self._components:
            c.manufacturer_pn = pn

    @property
    def supplier(self):
        return self._components[0].supplier

    @supplier.setter
    def supplier(self, sup):
        for c in self._components:
            c.supplier = sup

    @property
    def supplier_pn(self):
        return self._components[0].supplier_pn

    @supplier_pn.setter
    def supplier_pn(self, pn):
        for c in self._components:
            c.supplier_pn = pn


    def __str__(self):
        return '\n'.join([
            '\nComponent Type Container',
            '-' * 20,
            'Value: {}'.format(self.value),
            'Footprint: {}'.format(self.footprint),
            'Quantity: {}'.format(len(self))
        ])

class ComponentView(BoxLayout):
    top_box = ObjectProperty(None)
    scrollbox = ObjectProperty(None)
    comp_list = ObjectProperty(None)
    update_cb = ObjectProperty(None)
    data = ListProperty([])

    component_map = DictProperty({})
    component_type_map = DictProperty({})
    schematics = DictProperty({})

    def __init__(self, **kwargs):
        super(ComponentView, self).__init__(**kwargs)

    def attach_data(self, data):
        self.comp_list.component_view.adapter.data = data

    def attach_selection_callback(self, cb):
        self.comp_list.component_view.adapter.bind(on_selection_change=cb)

    def attach_update_callback(self, cb):
        self.update_cb = cb



class ComponentTypeView(BoxLayout):
    top_box = ObjectProperty(None)
    scrollbox = ObjectProperty(None)
    comp_type_list = ObjectProperty(None)
    update_cb = ObjectProperty(None)
    data = ListProperty([])

    component_map = DictProperty({})
    component_type_map = DictProperty({})
    schematics = DictProperty({})

    def __init__(self, **kwargs):
        super(ComponentTypeView, self).__init__(**kwargs)

    def attach_data(self, data):
        self.comp_type_list.component_view.adapter.data = data

    def attach_selection_callback(self, cb):
        self.comp_type_list.component_view.adapter.bind(on_selection_change=cb)

    def attach_update_callback(self, cb):
        self.update_cb = cb

class BomManagerApp(App):
    top_box = ObjectProperty(None)
    scrollbox = ObjectProperty(None)
    comp_list = ObjectProperty(None)
    component_data = ListProperty([])
    component_type_data = ListProperty([])

    component_map = DictProperty({})
    component_type_map = DictProperty({})
    schematics = DictProperty({})

    # I really hate global state, but this seems like the fastest path forward...
    _current_component = None
    _current_type = None

    def _update_component_selection(self, adapter, *args):

        long_key = adapter.selection.pop().text

        ref, val, fp = [x.strip() for x in long_key.split('|')]
        type_key = '{}|{}'.format(val, fp)

        # Save any changes
        self.update_component()

        self._current_component = self.component_map[ref]
        self.load_component()

    def _update_component_type_selection(self, adapter, *args):
        long_key = adapter.selection.pop().text
        val, fp = [x.strip() for x in long_key.split('|')]
        type_key = '{}|{}'.format(val, fp)

        # Save any changes
        self.update_component_type()

        self._current_type = self.component_type_map[type_key]
        self.load_component_type()

    def load_component_type(self):


        ct = self._current_type

        self.type_view.qty_text.text = str(len(ct))
        self.type_view.refs_text.text = ct.refs
        self.type_view.val_text.text = ct.value
        self.type_view.fp_text.text = ct.footprint
        self.type_view.ds_text.text = ct.datasheet
        self.type_view.mfr_text.text = ct.manufacturer
        self.type_view.mfr_pn_text.text = ct.manufacturer_pn
        self.type_view.sup_text.text = ct.supplier
        self.type_view.sup_pn_text.text = ct.supplier_pn

    def load_component(self):

        c = self._current_component

        self.comp_view.ref_text.text = c.reference
        self.comp_view.val_text.text = c.value
        self.comp_view.fp_text.text = c.footprint
        self.comp_view.ds_text.text = c.datasheet
        self.comp_view.mfr_text.text = c.manufacturer
        self.comp_view.mfr_pn_text.text = c.manufacturer_pn
        self.comp_view.sup_text.text = c.supplier
        self.comp_view.sup_pn_text.text = c.supplier_pn

    def update_component(self, *args):

        if self._current_component is None:
            return

        c = self._current_component

        c.value = self.comp_view.val_text.text
        c.datasheet = self.comp_view.ds_text.text
        c.manufacturer = self.comp_view.mfr_text.text
        c.manufacturer_pn = self.comp_view.mfr_pn_text.text
        c.supplier = self.comp_view.sup_text.text
        c.supplier_pn = self.comp_view.sup_pn_text.text

    def update_component_type(self, *args):

        if self._current_type is None:
            return

        ct = self._current_type

        ct.value = self.type_view.val_text.text
        ct.datasheet = self.type_view.ds_text.text
        ct.manufacturer = self.type_view.mfr_text.text
        ct.manufacturer_pn = self.type_view.mfr_pn_text.text
        ct.supplier = self.type_view.sup_text.text
        ct.supplier_pn = self.type_view.sup_pn_text.text

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)

        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def show_export(self):
        content = ExportDialog(export=self.export_csv, cancel=self.dismiss_popup)
        self._popup = Popup(title="Export BOM CSV", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def export_csv(self, path, filename):

        # TODO: Check if file exists and ask about overwrite
        with open(os.path.join(path, filename), 'w') as csvfile:
            wrt = csv.writer(csvfile)

            wrt.writerow(['Refs', 'Value', 'Footprint', 'QTY', 'MFR', 'MPN', 'SPR', 'SPN'])

            for ctype in sorted(self.component_type_map):
                ctcont = self.component_type_map[ctype]
                wrt.writerow([
                    ctcont.refs,
                    ctcont.value,
                    ctcont.footprint,
                    len(ctcont),
                    ctcont.manufacturer,
                    ctcont.manufacturer_pn,
                    ctcont.supplier,
                    ctcont.supplier_pn,
                ])

        self.dismiss_popup()

    def _walk_sheets(self, base_dir, sheets):
        for sheet in sheets:
            sheet_name = sheet.fields[0]['value'].strip('"')
            sheet_sch = sheet.fields[1]['value'].strip('"')
            schematic = sch.Schematic(os.path.join(base_dir, sheet_sch))
            self.schematics[sheet_name] = (
                sch.Schematic(os.path.join(base_dir, sheet_sch))
            )
            self._walk_sheets(base_dir, schematic.sheets)

    def _reset(self):
        self.schematics = {}
        self.component_map = {}
        self.component_type_map = {}

    def _update_data(self):

        type_data = []
        component_data = []

        for ctname, ct in self.component_type_map.items():
            type_data.append('{} | {}'.format(ct.value, ct.footprint))

        for cname, c in self.component_map.items():
            component_data.append('{} | {} | {}'.format(c.reference,
                                                        c.value,
                                                        c.footprint))

        # Sort and attach data
        self.comp_view.attach_data(sorted(component_data))
        self.type_view.attach_data(sorted(type_data))

    def load(self, path, filename):
        self.dismiss_popup()

        # Enable buttons if we have a live schematic
        self.side_panel.save_button.disabled = False
        self.side_panel.export_button.disabled = False
        self.side_panel.consolidate_button.disabled = False

        # remove old schematic information
        self._reset()

        base_dir = path
        top_sch = os.path.split(filename[0])[-1]
        top_name = os.path.splitext(top_sch)[0]

        compmap = {}

        self.schematics[top_name] = (
            sch.Schematic(os.path.join(base_dir, top_sch))
        )

        # Recursively walks sheets to locate nested subschematics
        self._walk_sheets(base_dir, self.schematics[top_name].sheets)

        for name, schematic in self.schematics.items():
            for _cbase in schematic.components:
                c = ComponentWrapper(_cbase)

                # Skip virtual components (power, gnd, etc)
                if c.is_virtual:
                    continue

                comp_type_key = '{}|{}'.format(c.value, c.footprint)
                comp_key = c.reference

                self.component_map[comp_key] = c

                if comp_type_key not in self.component_type_map:
                    self.component_type_map[comp_type_key] = ComponentTypeContainer()
                self.component_type_map[comp_type_key].add(c)

        self._update_data()

    def _consolidate(self):
        """
        Performs consolidation
        """

        def consolidation_closure(index, clo_cl, clo_popup):
            def fn(*args):
                sel = clo_cl.pop(index)

                for rem in clo_cl:

                    ct_key = '{}|{}'.format(rem.value,
                                            rem.footprint)

                    # Set all relevant fields
                    rem.value = sel.value
                    rem.manufacturer = sel.manufacturer
                    rem.manufacturer_pn = sel.manufacturer_pn
                    rem.supplier_pn = sel.supplier_pn
                    rem.supplier = sel.supplier

                    sel.extract_components(rem)
                    self.component_type_map.pop(ct_key, None)


                self._update_data()
                clo_popup.dismiss()
            return fn

        uniq = {}
        dups = {}

        ctmap_keys = self.component_type_map.keys()

        # Find all duplicated components and put them into a dups map
        for ct in ctmap_keys:
            cthsh = ct.upper().replace(' ','')

            if cthsh in uniq:
                if not cthsh in dups:
                    dups[cthsh] = [uniq[cthsh]]

                dups[cthsh].append(self.component_type_map[ct])
            else:
                uniq[cthsh] = self.component_type_map[ct]

        for d, cl in dups.items():

            _popup = Popup(title='Duplicate part value',
                           auto_dismiss=False,
                           size_hint = (0.9, 0.9))
            content = UniquePartSelectorDialog()
            for idx, c in enumerate(cl):
                content.top_box.add_widget(
                    Button(text=c.value,
                           on_release=consolidation_closure(idx,
                                                            cl,
                                                            _popup))
                )

            _popup.content=content
            _popup.open()

    def _bind_focus_callbacks(self):
        comp_textboxes = [
            self.comp_view.val_text,
            self.comp_view.ds_text,
            self.comp_view.mfr_text,
            self.comp_view.mfr_pn_text,
            self.comp_view.sup_text,
            self.comp_view.sup_pn_text,
        ]

        type_textboxes = [
            self.type_view.val_text,
            self.type_view.ds_text,
            self.type_view.mfr_text,
            self.type_view.mfr_pn_text,
            self.type_view.sup_text,
            self.type_view.sup_pn_text,

        ]

        for tb in comp_textboxes:
            tb.bind(focus=self.update_component)

        for tb in type_textboxes:
            tb.bind(focus=self.update_component_type)

    def build(self):
        global AppRoot
        AppRoot = self

        self.navdrawer = NavDrawer()

        self.side_panel = SidePanel()
        self.navdrawer.add_widget(self.side_panel)

        self.comp_view = ComponentView()
        self.type_view = ComponentTypeView()

        self.comp_view.attach_selection_callback(self._update_component_selection)
        self.comp_view.attach_update_callback(self.update_component)
        self.type_view.attach_selection_callback(self._update_component_type_selection)
        self.type_view.attach_update_callback(self.update_component_type)

        # Bind all textbox focus changes to save component changes
        self._bind_focus_callbacks()

        self.main_panel = self.type_view

        self.navdrawer.anim_type = 'slide_above_anim'
        self.navdrawer.add_widget(self.main_panel)
        Window.bind(mouse_pos=self.on_motion)

        return self.navdrawer

    def on_motion(self, etype, motionevent):
        if self.navdrawer.state == 'closed':
            if motionevent[0] < 50:
                self.navdrawer.toggle_state()
        else:
            # TODO: Fix this calculation, it isn't correct
            if motionevent[0] > self.navdrawer.side_panel_width / 2:
                self.navdrawer.close_sidepanel()

    def on_load(self):
        """
        Recursively loads a KiCad schematic and all subsheets
        """
        self.navdrawer.close_sidepanel()
        self.show_load()

    def on_component(self):
        """
        Switches to component (individual) view
        """
        self._switch_main_page(self.comp_view)

    def on_save(self):
        """
        Saves all schematics
        """
        for name, schematic in self.schematics.items():
            schematic.save()

    def on_type(self):
        """
        Switches to component type (grouped) view
        """
        self._switch_main_page(self.type_view)

    def on_quit(self):
        """
        Quits the application
        """
        exit(0)

    def on_export_csv(self):
        """
        Exports Bill of Materials as a CSV File
        """
        self.show_export()

    def on_consolidate(self):
        """
        Consolidates components (i.e. 1K 0603 and 1k 0603 become same component group -> 1K 0603 x 2)
        """
        self._consolidate()

    def _switch_main_page(self, panel):
        self.navdrawer.close_sidepanel()
        self.navdrawer.remove_widget(self.main_panel)
        self.navdrawer.add_widget(panel)
        self.main_panel = panel


if __name__ == '__main__':

    BomManagerApp().run()
