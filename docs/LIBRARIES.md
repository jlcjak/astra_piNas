# Local libraries and provenance

`lib/design.kicad_sym` is the active symbol library. Symbols were redrawn into readable functional units with explicit pin numbers; the CM5 connectors and PCIe switch use multiple units but each physical part appears once in the BOM. `lib/astra_piNas.kicad_sym` retains downloaded EasyEDA symbol sources. Active symbols point only to `astra_piNas:` footprints in the project-local `.pretty` directory.

| Part family | Geometry source and treatment |
|---|---|
| CM5 connectors, Amphenol 10164227-1004A1RLF | Pad coordinates taken from Raspberry Pi's official CM5IO revision 2 downloadable KiCad footprint. Split into two physical 100-pin connectors with local numbering. Connector separation, hole locations and module envelope retained in the carrier placement. No substituted CM4/Hirose footprint. |
| TE 1-2199230-5 M.2 | EasyEDA import checked against TE drawing C-2199230, revision B3, sheets 1–3. 0.5 mm pitch, correct M-key gap, 1.1/1.6 mm asymmetric locating holes, and 4.2 mm connector height. Locating holes corrected to NPTH. |
| Hanrun HR913180AE RJ45 | EasyEDA import, checked against Hanrun's schematic and dimensional drawing. Four independent cable center taps feed PoE. Locating holes corrected to NPTH. |
| TYPE-C-31-M-12 | EasyEDA import. Combined VBUS/GND contacts use custom pad shapes; their tiny anchor dimensions do not represent the full copper shape. Locating holes corrected to NPTH. Local pad clearance is 0.09 mm to accommodate the connector's narrow manufactured pad gaps; confirm fabrication capability. |
| AP64501 | EasyEDA package import. Four exposed-pad thermal holes corrected to pin 9/GND and removed from paste openings. Review thermal-via solder treatment with the fabricator. |
| Other semiconductors and connectors | EasyEDA imports tied to the specific LCSC ID, with explicit pin-map review against downloaded datasheets. Imported artwork is not a guarantee of assembly fit. |
| Resistors/capacitors | Vendored standard KiCad SMD footprints matching the selected package size. No 0201 parts. The 1 kΩ PD-feed and PoE-bleeder parts are 1206, 0.5 W ROHM ESR18EZPF1001. |
| YIYUAN SMTSOM225BTR and SMTSOM240BTR spacers | Custom footprints from the YIYUAN family drawing, M2 row: 6.2 mm minimum solder land and 3.73 mm finished hole. Plated holes selected (the drawing permits plating); four separate paste sectors avoid paste over the holes. Heights 2.5 and 4 mm. Verified LCSC pages C5301773 and C19626599. |
| WC-PD60B120A | **Incomplete custom candidate footprint.** The eight electrical pins use dimensions from the module drawing; support pins 9/10 are deliberately absent because their X position is not dimensioned. The body envelope is for placement only. Do not fabricate. |

Available imported WRL/STEP files are stored under `lib/astra_piNas.3dshapes`. Missing optional 3D models were not replaced with guessed geometry. A full assembled CM5/SSD/heatsink model is not provided. All existing model links resolve locally; stock-library models were removed from vendored footprints when not included.

## Primary technical sources

- [Raspberry Pi CM5 datasheet](https://datasheets.raspberrypi.com/cm5/cm5-datasheet.pdf), saved as `sources/cm5.pdf`.
- [Official CM5IO revision 2 KiCad archive](https://pip-assets.raspberrypi.com/categories/1098-design-files/documents/RP-008099-DD-1-CM5%20IO%20Board,%20revision%202,%20KiCAD%20files..zip), used as a geometry reference; the archive and extracted reference project are excluded from this repository.
- [Diodes PI7C9X2G404SL datasheet](https://www.diodes.com/assets/Datasheets/PI7C9X2G404SL.pdf), `sources/switch.pdf`.
- [Diodes AP64501 datasheet](https://www.diodes.com/assets/Datasheets/AP64501.pdf), `sources/ap64501.pdf`.
- [YIYUAN SMTSOM225BTR](https://www.lcsc.com/product-detail/C5301773.html), manufacturer family drawing saved as `sources/C5301773.pdf`; [SMTSOM240BTR](https://www.lcsc.com/product-detail/C19626599.html).
- Other manufacturer datasheets downloaded via the corresponding LCSC product pages are saved as `sources/C<number>.pdf`. LCSC product URLs, actual LCSC stock (distinct from JLC assembly stock), and UTC timestamps are in `sources/catalog.json` and the BOM. Raw retrieved product HTML is retained as evidence.

The imported libraries and manufacturer reference material retain their original ownership and licensing. These were fetched from public sources; no unrelated local project was inspected or reused.
