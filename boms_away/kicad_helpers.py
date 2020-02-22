from . import sch
import os


def sanitized(f):
    """
    Removes newlines/tabs/carriage/returns to prevent breakages in schematics

    Returns: Sanitized string
    """

    for v in ['\n', '\r', '\t']:
        f = f.replace(v, '')

    return f


# TODO: Enumerate field values
class ComponentWrapper(object):

    _builtin_field_map = {
        'reference': '0',
        'value': '1',
        'footprint': '2',
        'datasheet': '3',
    }

    def __init__(self, base_component):
        self._cmp = base_component

    def _get_field(self, field_name):
        if field_name in self._builtin_field_map:
            field = [
                x for x in self._cmp.fields
                if
                x['id'] == self._builtin_field_map[field_name]
            ][0]
        else:
            field = [
                x for x in self._cmp.fields
                if
                x['name'].strip('"') == field_name
            ][0]

        return field

    def _set_field_value(self, field, value):
        f = self._get_field(field)

        f['ref'] = '"{}"'.format(sanitized(value))

    def _get_field_value(self, field):
        return self._get_field(field)['ref'].strip('"')

    def _has_field(self, field):
        try:
            self._get_field(field)
            return True
        except:
            return False

    def add_bom_fields(self):

        _fields = [
            "MFR",
            "MPN",
            "SPR",
            "SPN",
            "SPURL",
        ]

        for f in _fields:

            if self._has_field(f):
                continue

            f_data = {
                'name': '"{}"'.format(f),
                'ref': '"-"'
            }

            self._cmp.addField(f_data)

    def set_field_visibility(self, field, visible=True):
        f = self._get_field(field)
        if visible:
            vis = '0000'
        else:
            vis = '0001'

        f['attributs'] = vis

    @property
    def has_valid_key_fields(self):
        if not len(self.footprint.strip()) or not len(self.value.strip()):
            return False

        return True
        
    @property
    def typeid(self):
        return '{}|{}'.format(self.value,
                              self.footprint)

    @property
    def num_fields(self):
        return len(self._cmp.fields)

    @property
    def reference(self):
        return self._get_field_value('reference')

    @property
    def value(self):
        return self._get_field_value('value')

    @value.setter
    def value(self, val):
        self._set_field_value('value', val)

    @property
    def footprint(self):
        return self._get_field_value('footprint')

    @property
    def datasheet(self):
        return self._get_field_value('datasheet')

    @datasheet.setter
    def datasheet(self, val):
        self._set_field_value('datasheet', val)
        self.set_field_visibility('datasheet', False)

    @property
    def is_virtual(self):
        if self._cmp.labels['ref'][0] == '#':
            return True
        return False

    @property
    def manufacturer(self):
        return self._get_field_value('MFR')

    @manufacturer.setter
    def manufacturer(self, mfr):
        self._set_field_value('MFR', mfr)

    @property
    def supplier(self):
        return self._get_field_value('SPR')

    @supplier.setter
    def supplier(self, sup):
        self._set_field_value('SPR', sup)

    @property
    def manufacturer_pn(self):
        return self._get_field_value('MPN')

    @manufacturer_pn.setter
    def manufacturer_pn(self, pn):
        self._set_field_value('MPN', pn)

    @property
    def supplier_pn(self):
        return self._get_field_value('SPN')

    @supplier_pn.setter
    def supplier_pn(self, pn):
        self._set_field_value('SPN', pn)

    @property
    def supplier_url(self):
        return self._get_field_value('SPURL')

    @supplier_url.setter
    def supplier_url(self, url):
        self._set_field_value('SPURL', url)

    @property
    def unit(self):
        return int(self._cmp.unit['unit'])

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
                raise Exception("Attempted to insert unlike "
                                "component into ComponentTypeContainer")

        self._components.append(component)

    def __len__(self):
        return len(self._unique_components)

    @property
    def _unique_components(self):
        """Returns a list of the unique components. This will group multi-part
        components together (i.e. individual units, such as a 4
        channel op-amp in a single package, will show as a single unified component)

        """
        return [x for x in self._components if x.unit == 1]

    @property
    def has_valid_key_fields(self):
        if not len(self.footprint.strip()) or not len(self.value.strip()):
            return False

        return True

    def extract_components(self, other):
        for c in other._components:
            self.add(c)

    @property
    def typeid(self):
        return '{}|{}'.format(self.value,
                              self.footprint)

    @property
    def refs(self):
        return ';'.join([x.reference for x in self._unique_components])

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

    @property
    def supplier_url(self):
        return self._components[0].supplier_url

    @supplier_url.setter
    def supplier_url(self, url):
        for c in self._components:
            c.supplier_url = url

    def __str__(self):
        return '\n'.join([
            '\nComponent Type Container',
            '-' * 20,
            'Value: {}'.format(self.value),
            'Footprint: {}'.format(self.footprint),
            'Quantity: {}'.format(len(self))
        ])


def walk_sheets(base_dir, sheets, sch_dict):
    for sheet in sheets:
        sheet_name = sheet.fields[0]['value'].strip('"')
        sheet_sch = sheet.fields[1]['value'].strip('"')
        schematic = sch.Schematic(os.path.join(base_dir, sheet_sch))
        sch_dict[sheet_name] = (
            sch.Schematic(os.path.join(base_dir, sheet_sch))
        )
        base_dir = os.path.join(base_dir, os.path.split(sheet_sch)[0])

        walk_sheets(base_dir, schematic.sheets, sch_dict)
            
