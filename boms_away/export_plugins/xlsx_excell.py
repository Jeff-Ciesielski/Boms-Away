# -*- coding: utf-8 -*-
import xlsxwriter

from . import _export_base

class XlsxExport(_export_base.BomsAwayExporter):
    extension = 'xlsx'
    wildcard = 'Excel XLSX Files (*.xlsx)|*.xlsx'

    def export(self, base_filename, components):
        file_path = '{}.{}'.format(base_filename, self.extension)
        workbook = xlsxwriter.Workbook(file_path)
        worksheet = workbook.add_worksheet()
        worksheet.write_row(0, 0,
                            ['Refs', 'Value', 'Footprint', 'Quantity', 'DESC',
                             'MFR', 'MPN', 'SPR', 'SPN', 'SPURL']),
        row = 1
        for fp in sorted(components):
            for val in sorted(components[fp]):
                ctcont = components[fp][val]
                worksheet.write_row(row, 0,
                                    [
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
                row = row + 1
        workbook.close()
