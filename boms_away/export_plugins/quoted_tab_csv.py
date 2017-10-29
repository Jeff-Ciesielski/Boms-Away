import csv

from . import _export_base

class QuotedTabExport(_export_base.BomsAwayExporter):
    extension = 'csv'
    wildcard = 'Quoted, tab delimited CSV (*.csv)|*.csv'

    def export(self, base_filename, components):
        file_path = '{}.{}'.format(base_filename, self.extension)

        with open(file_path, 'w') as csvfile:
            wrt = csv.writer(csvfile, dialect='excel-tab')

            wrt.writerow(['Refs', 'Value', 'Footprint',
                          'Quantity', 'MFR', 'MPN', 'SPR', 'SPN'])

            for fp in sorted(components):
                for val in sorted(components[fp]):
                    ctcont = components[fp][val]
                    commarefs = ctcont.refs.replace(';', ',')
                    wrt.writerow([
                        '"{}"'.format(commarefs),
                        '"{}"'.format(ctcont.value),
                        '"{}"'.format(ctcont.footprint),
                        '"{}"'.format(len(ctcont)),
                        '"{}"'.format(ctcont.manufacturer),
                        '"{}"'.format(ctcont.manufacturer_pn),
                        '"{}"'.format(ctcont.supplier),
                        '"{}"'.format(ctcont.supplier_pn),
                    ])
