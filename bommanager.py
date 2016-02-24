#!/usr/bin/env python

import os
import csv

import sch
import datastore

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
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
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.scrollview import ScrollView

import kicad_helpers as kch

# TODO: Normalize all input schematic components to follow field
# guidelines

SidePanel_AppMenu = {
    'Load Schematic': ['on_load', None],
    'Save Schematic': ['on_save', None],
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


class ComponentTypeAccordionMember(BoxLayout):
    pass


class ComponentTypeView(BoxLayout):
    top_box = ObjectProperty(None)
    scrollbox = ObjectProperty(None)
    comp_type_list = ObjectProperty(None)
    data = ListProperty([])

    component_type_map = DictProperty({})
    schematics = DictProperty({})

    def __init__(self, **kwargs):
        super(ComponentTypeView, self).__init__(**kwargs)

    def attach_data(self, data):
        self.comp_type_list.component_view.adapter.data = data

    def attach_selection_callback(self, cb):
        self.comp_type_list.component_view.adapter.bind(on_selection_change=cb)


class BomManagerApp(App):
    top_box = ObjectProperty(None)
    scrollbox = ObjectProperty(None)
    comp_list = ObjectProperty(None)
    component_type_data = ListProperty([])

    component_type_map = DictProperty({})
    schematics = DictProperty({})

    # I really hate global state, but this seems like the fastest path
    # forward...
    _current_type = None

    def _update_component_type_selection(self, adapter, *args):
        long_key = adapter.selection.pop().text
        val, fp = [x.strip() for x in long_key.split('|')]
        type_key = '{}|{}'.format(val, fp)

        # Save any changes
        self.save_component_type_changes()

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

        # Enable the part lookup button
        self.type_view.lookup_button.disabled = False
        self.type_view.save_button.disabled = False

    def save_component_type_changes(self, *args):

        if self._current_type is None:
            return

        ct = self._current_type

        ct.value = self.type_view.val_text.text
        ct.datasheet = self.type_view.ds_text.text
        ct.manufacturer = self.type_view.mfr_text.text
        ct.manufacturer_pn = self.type_view.mfr_pn_text.text
        ct.supplier = self.type_view.sup_text.text
        ct.supplier_pn = self.type_view.sup_pn_text.text

    def dismiss_popup(self, *args):
        self._popup.dismiss()

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)

        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def show_export(self):
        content = ExportDialog(export=self.export_csv,
                               cancel=self.dismiss_popup)
        self._popup = Popup(title="Export BOM CSV", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def export_csv(self, path, filename):

        # TODO: Check if file exists and ask about overwrite
        with open(os.path.join(path, filename), 'w') as csvfile:
            wrt = csv.writer(csvfile)

            wrt.writerow(['Refs', 'Value', 'Footprint',
                          'QTY', 'MFR', 'MPN', 'SPR', 'SPN'])

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

    def _reset(self):
        self.schematics = {}
        self.component_type_map = {}

    def _update_data(self):

        type_data = []

        for ctname, ct in self.component_type_map.items():
            type_data.append('{} | {}'.format(
                ct.value,
                ct.footprint,
            ))

        # Sort and attach data
        self.type_view.attach_data(sorted(type_data))

    def load(self, path, filename):
        self.dismiss_popup()

        if len(path) == 0 or len(filename) == 0:
            return

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

                if c.typeid not in self.component_type_map:
                    self.component_type_map[c.typeid] = (
                        kch.ComponentTypeContainer()
                    )
                self.component_type_map[c.typeid].add(c)

        self._update_data()
        self._current_type = None
        self.type_view.lookup_button.disabled = True
        self.type_view.save_button.disabled = True

    def _consolidate(self):
        """
        Performs consolidation
        """

        def consolidation_closure(index, clo_cl, clo_popup):
            def fn(*args):
                sel = clo_cl.pop(index)

                for rem in clo_cl:

                    old_typeid = rem.typeid
                    # Set all relevant fields
                    rem.value = sel.value
                    rem.manufacturer = sel.manufacturer
                    rem.manufacturer_pn = sel.manufacturer_pn
                    rem.supplier_pn = sel.supplier_pn
                    rem.supplier = sel.supplier

                    sel.extract_components(rem)
                    self.component_type_map.pop(old_typeid, None)

                self._update_data()
                clo_popup.dismiss()
            return fn

        uniq = {}
        dups = {}

        ctmap_keys = self.component_type_map.keys()

        # Find all duplicated components and put them into a dups map
        for ct in ctmap_keys:
            cthsh = ct.upper().replace(' ', '')

            if cthsh in uniq:
                if cthsh not in dups:
                    dups[cthsh] = [uniq[cthsh]]

                dups[cthsh].append(self.component_type_map[ct])
            else:
                uniq[cthsh] = self.component_type_map[ct]

        for d, cl in dups.items():

            _popup = Popup(title='Duplicate part value',
                           auto_dismiss=False,
                           size_hint=(0.9, 0.9))
            content = UniquePartSelectorDialog()
            for idx, c in enumerate(cl):
                content.top_box.add_widget(
                    Button(text=c.value,
                           on_release=consolidation_closure(idx,
                                                            cl,
                                                            _popup))
                )

            _popup.content = content
            _popup.open()

    def _init_config_dir(self):
        config_dir = os.path.join(
            os.path.expanduser("~"),
            '.kicadbommgr.d'
        )

        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

    def attempt_part_lookup(self, *args):
        ct = self._current_type

        if ct is None:
            raise Exception("No component selected, this should not happen\n")

        if not ct.has_valid_key_fields:
            raise Exception("Missing key fields (value / footprint)!")

        # TODO: Wrap these guys up. Think about perhaps having a
        # component manager class that encompases the datastore and
        # component type wrappers?

        up = self.ds.lookup(ct)

        if up is None:
            content = BoxLayout(orientation='vertical')
            content.add_widget(Label(text="Component does not exist in Datastore"))
            content.add_widget(Button(text='OK',
                                      size_hint_y=0.1,
                                      on_release=self.dismiss_popup))
            self._popup = Popup(title='No results found',
                                auto_dismiss=True,
                                content=content,
                                size_hint=(0.9, 0.9))
            self._popup.open()
            return

        if not up.manufacturer_pns.count():
            content = BoxLayout(orientation='vertical')
            content.add_widget(Label(text="No suitable parts found in Datastore"))
            content.add_widget(Button(text='OK',
                                      size_hint_y=0.1,
                                      on_release=self.dismiss_popup))
            
            self._popup = Popup(title='No results found',
                                auto_dismiss=True,
                                content=content,
                                size_hint=(0.9, 0.9))
            self._popup.open()
            return

        def lookup_closure(clo_mpn, clo_spn, clo_popup, *args):
            def fn (*args):
                if clo_mpn:
                    self.type_view.mfr_text.text = clo_mpn.manufacturer.name
                    self.type_view.mfr_pn_text.text = clo_mpn.pn
                if clo_spn:
                    self.type_view.sup_text.text = clo_spn.supplier.name
                    self.type_view.sup_pn_text.text = clo_spn.pn

                if clo_popup:
                    clo_popup.dismiss()

            return fn

        cb_map = {}
        for pn in up.manufacturer_pns:
            if not len(pn.supplier_parts):
                btn_text = '{} (No Known Suppliers)'.format(
                    pn.pn
                )
                cb_map[btn_text] = (pn, None)
            else:
                for s_pn in pn.supplier_parts:
                    btn_text = '{} {} @ {}[{}]'.format(
                        pn.manufacturer.name,
                        pn.pn,
                        s_pn.supplier.name,
                        s_pn.pn
                    )
                    cb_map[btn_text] = (pn, s_pn)

        if len(cb_map) == 1:
            pn, s_pn = cb_map.values().pop()
            lookup_closure(pn, s_pn, None)()
        else:
            content = BoxLayout(orientation='vertical')
            _popup = Popup(title='No results found',
                           auto_dismiss=True,
                           size_hint=(0.9, 0.9))

            for btn_txt, pns in cb_map.items():
                cb = lookup_closure(pns[0], pns[1], _popup)
                content.add_widget(Button(text=btn_txt,
                                          size_hint_y=0.1,
                                          on_release=cb))
            _popup.content = content
            _popup.open()

    def do_datastore_update(self, *args):
        self.save_component_type_changes()
        self.ds.update(self._current_type)

    def build(self):
        global AppRoot
        AppRoot = self

        self._init_config_dir()

        self.ds = datastore.Datastore()

        self.navdrawer = NavDrawer()

        self.side_panel = SidePanel()
        self.navdrawer.add_widget(self.side_panel)

        self.type_view = ComponentTypeView()

        self.type_view.attach_selection_callback(
            self._update_component_type_selection
        )

        self.main_panel = self.type_view

        self.navdrawer.anim_type = 'slide_above_anim'
        self.navdrawer.add_widget(self.main_panel)
        Window.bind(mouse_pos=self.on_motion)

        self.type_view.lookup_button.bind(on_release=self.attempt_part_lookup)
        self.type_view.save_button.bind(on_release=self.do_datastore_update)
        return self.navdrawer

    def on_motion(self, etype, motionevent):
        if self.navdrawer.state == 'closed':
            if motionevent[0] < 50:
                self.navdrawer.toggle_state()
        else:
            if motionevent[0] > self.navdrawer.side_panel_width:
                self.navdrawer.close_sidepanel()

    def on_load(self):
        """
        Recursively loads a KiCad schematic and all subsheets
        """
        self.save_component_type_changes()
        self.navdrawer.close_sidepanel()
        self.show_load()

    def on_save(self):
        """
        Saves all schematics
        """
        self.save_component_type_changes()
        for name, schematic in self.schematics.items():
            schematic.save()

    def on_type(self):
        """
        Switches to component type (grouped) view
        """
        self.save_component_type_changes()
        self._switch_main_page(self.type_view)

    def on_quit(self):
        """
        Quits the application
        """
        self.save_component_type_changes()
        exit(0)

    def on_export_csv(self):
        """
        Exports Bill of Materials as a CSV File
        """
        self.save_component_type_changes()
        self.show_export()

    def on_consolidate(self):
        """
        Consolidates components (i.e. 1K 0603 and 1k 0603 become same
        component group -> 1K 0603 x 2)
        """
        self.save_component_type_changes()
        self._consolidate()

    def _switch_main_page(self, panel):
        self.navdrawer.close_sidepanel()
        self.navdrawer.remove_widget(self.main_panel)
        self.navdrawer.add_widget(panel)
        self.main_panel = panel


if __name__ == '__main__':
    BomManagerApp().run()
