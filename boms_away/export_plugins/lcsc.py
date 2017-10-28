import csv

from . import _export_base

class LCSCExport(_export_base.BomsAwayExporter):
    extension = 'csv'
    wildcard = 'lcsc.com CSV (*.csv)|*.csv'

    def export(self, base_filename, components):
        file_path = '{}.{}'.format(base_filename, self.extension)

        with open(file_path, 'w') as csvfile:
            wrt = csv.writer(csvfile)

            wrt.writerow(['Quantity','Value', 'Refs', 'Footprint',
                        'Manufacturer','Manufacture Part Number',
                        'LCSC Part Number'])

            for fp in sorted(components):
                for val in sorted(components[fp]):
                    ctcont = components[fp][val]
                    wrt.writerow([
                        len(ctcont),
                        ctcont.value,
                        ctcont.refs,
                        ctcont.footprint,
                        ctcont.manufacturer,
                        ctcont.manufacturer_pn,
                        ctcont.supplier_pn,
                    ])
