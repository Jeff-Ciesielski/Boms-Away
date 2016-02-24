# BOMs Away! - BOM/Component manager for KiCad

IMO, KiCad is one of the best EDA tools out there, with just one major
problem: Bill of Materials management is rough. If you make more than
1 board a year, you probably know how frustrating it can be to get
everything together for an order. There are multiple ways to export a
BOM (each with their own ups and downs), and the process of selecting
and entering components is excruciatingly manual.

You can of course create custom components on a per MPN basis, but
this can be time consuming and forces you to maintain a large number
of individual component libraries.

The goal of this app is to ease the bom management burden on designers
who choose to use Kicad for their layout and schematic capture needs,
allowing for faster, easier data entry, and to provide a part database
for re-use in future designs.


## Requirements

* python 2.7
* [kivy](https://kivy.org) >= 1.9.0
* kivy garden
* navigationdrawer `garden install navigationdrawer`


## Features

### Self-curated component database

Simply enter a part's manufacturer,
supplier, manufacturer PN, and supplier PN then click 'save to
datastore'.  Information is keyed off of component value and
footprint, so future uses can simply use the part lookup button to
retrieve the information.  Multiple suppliers, manufacturers, and
part numbers are supported.

### Like-Part consolidation

Everybody miskeys from time to time, this feature detects (to the best
of its ability) components that are the same, but simply have
mislabeled values. For example: (10K, 10k, 10 K) will be consolidated
into a single value selectable by the user.

`*Only components that share a footprint are consolidated.`

### CSV Bom Export

Exports PCBNew style component agregate BOMs as CSV. Suitable for
upload to digikey/mouser/octopart/etc

### KiCad Backpropegation

All changes can be saved back to KiCad Schematics


## Notes

### This tool is opinionated!

The tool has to store its information somewhere, so it uses kicad's
custom component fields. Currently, the fields SPN, MPN, SPR, and MFR
are reserved for use. If these fields do not exist, they will be
automatically added to each component as it is accessed. The tool does
not attempt to do any import or translation of other existing fields
(field remapping could be added in a future update).

### Schematic saves are not automatic!

If you would like data propegated back to your kicad schematic, please
select `Save Schematic` from the menu.


## TODO

* Semantic versioning
* Fix outstanding todo items in source
* Add Unit tests
* User Guide


## Planned Features

### Multi-supplier BOM export

Allow exporting of <supplier>_bom.csv on a per vendor basis to allow
ease of uploading/ordering

### Octopart integration

Enable part price lookups and stock amount checking

### Bom Price Breakdown View (after octopart)

View overall prices / quantity ordered


## Feature wishlist

* Part inventory accounting

## License

GPLv3, see LICENSE for details.

This project uses sch.py from
[kicad library utils](https://github.com/KiCad/kicad-library-utils)
(also GPLv3)


## Contributing

Contributions welcome (and wanted!), please send a PR.

