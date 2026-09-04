# Astra piNas — CM5 dual NVMe carrier

Open **[astra_piNas.kicad_pro](astra_piNas.kicad_pro)** in **KiCad 10**. The project contains nine schematic sheets and a fully routed **100 × 120 mm, six-layer** board. Both 2280 NVMe sockets are on the underside. Use a **CM5 Lite** for the native microSD interface.

- [Routing and placement notes](docs/ROUTING.md), [selected stackup](docs/STACKUP.md)
- [Schematic PDF](docs/schematics.pdf)
- [Top copper view](docs/routing_top.svg), [bottom copper view](docs/routing_bottom.svg)
- [Top assembly view](docs/placement_top.svg), [bottom assembly view](docs/placement_bottom.svg)
- [BOM with MPNs and LCSC stock snapshots](docs/BOM.csv), [library provenance](docs/LIBRARIES.md)
- [Final validation summary](docs/routing_validation.json), [pair measurements](docs/pair_lengths.csv)
- [ERC](docs/erc.rpt), [PCB DRC](docs/drc.rpt), [schematic parity](docs/schematic_parity.rpt)

All symbols and footprints resolve through the project-local library tables to `lib/`. Available 3D models use project-relative paths. No unrelated local project was searched or reused; the Raspberry Pi reference files were downloaded from the official archive linked in [library provenance](docs/LIBRARIES.md).

The main project files above are the current design. Local routing experiments, tool caches and the downloaded CM5IO reference archive are excluded from this repository. Final routing measurements and validation reports are included under `docs/`. Regeneration scripts can overwrite manual edits. No fabrication package is released while the PoE hold remains unresolved.
