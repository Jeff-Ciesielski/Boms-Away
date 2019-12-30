# -*- coding: utf-8 -*-
import csv

from . import _export_base

class CsvExport(_export_base.BomsAwayExporter):
    extension = 'csv'
    wildcard = 'CSV Files (*.csv)|*.csv'

    def export(self, base_filename, components):
        file_path = '{}.{}'.format(base_filename, self.extension)

        with open(file_path, 'w') as csvfile:
            wrt = csv.writer(csvfile)

            wrt.writerow(['Refs', 'Value', 'Footprint',
                          'Quantity', 'DESC', 'MFR', 'MPN', 'SPR', 'SPN',
                          'SPURL'])

            for fp in sorted(components):
                for val in sorted(components[fp]):
                    ctcont = components[fp][val]
                    wrt.writerow([
                        ctcont.refs,
                        ctcont.value,
                        ctcont.footprint,
                        len(ctcont),
                        ctcont.description,
                        ctcont.manufacturer,
                        ctcont.manufacturer_pn,
                        ctcont.supplier,
                        ctcont.supplier_pn,
                        ctcont.supplier_url,
                    ])
