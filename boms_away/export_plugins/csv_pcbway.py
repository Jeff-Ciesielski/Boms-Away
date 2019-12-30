# -*- coding: utf-8 -*-
import csv

from . import _export_base

class CsvPcbwayExport(_export_base.BomsAwayExporter):
    extension = 'csv'
    wildcard = 'PCBWay CSV Files (*.csv)|*.csv'

    def export(self, base_filename, components):
        file_path = '{}.{}'.format(base_filename, self.extension)

        with open(file_path, 'w') as csvfile:
            wrt = csv.writer(csvfile)

            wrt.writerow(['Item #', 'Ref Des', 'Qty', 'Manufacturer',
                          'Mfg Part #', 'Value', 'Description', 'Package',
                          'Supplier', 'Sup Part #', 'Sup URL'])
            item = 1
            for fp in sorted(components):
                for val in sorted(components[fp]):
                    ctcont = components[fp][val]
                    wrt.writerow([
                        item,
                        ctcont.refs,
                        len(ctcont),
                        ctcont.manufacturer,
                        ctcont.manufacturer_pn,
                        ctcont.value,
                        ctcont.description,
                        ctcont.footprint,
                        ctcont.supplier,
                        ctcont.supplier_pn,
                        ctcont.supplier_url,
                    ])
                    item = item + 1
