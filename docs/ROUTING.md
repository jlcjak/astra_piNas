# Routed board

The outline remains **100 × 120 mm**. The board uses **six copper layers**, with the JLCPCB JLC06161H-3313 construction recorded in the KiCad stackup. See [STACKUP.md](STACKUP.md) for dielectric thicknesses, copper weights and impedance assumptions.

| Layer | Assignment |
|---|---|
| F.Cu | Components, differential pairs, local power loops and signal escapes |
| In1.Cu | Ground reference |
| In2.Cu | Power distribution and slow signals |
| In3.Cu | Power distribution and slow signals |
| In4.Cu | Ground reference |
| B.Cu | M.2 sockets, differential pairs and local connections |

There are no signal traces on In1.Cu or In4.Cu. Secondary ground is excluded from the cable-side PoE region. PCIe, reference-clock, Ethernet and USB data traces use the outer layers.

## Pair routing and verification

PCIe and USB nominal dimensions are 0.127 mm width / 0.150 mm coupled gap; Ethernet uses 0.100 mm / 0.150 mm. Local escapes, AC-coupling parts and tuning sections separate the pair members. Fabricator confirmation of controlled impedance remains necessary.

The pad-to-pad length audit follows each signal through its coupling capacitors and clock resistors, excludes unused branches, and checks both USB-C plug orientations. Pair members have equal traversed-via counts and equal calculated barrel lengths. Targets are 0.10 mm intra-pair skew for PCIe/clock/USB and 0.15 mm for Ethernet. See [pair_lengths.csv](pair_lengths.csv) for the final measurements and [routing_validation.json](routing_validation.json) for check results. This geometric audit is not an electromagnetic simulation or a hardware eye-diagram test.

Three supported PCIe polarity reversals are explicit in the schematics: the CM5 receive pair, the switch's upstream receive pair, and SSD2's receive pair at J4. These do not swap transmit and receive functions. The switch's RXPOLINV_DIS pin remains unconnected, using its internal pull-down.

Ground return vias accompany layer transitions. Long auxiliary supply bridges are stitched into the broad supply planes; local via arrays serve the regulators, OR diodes and load connections. Power-loop copper and regulator switch nodes were routed before the remaining signals. Some power, exposed-pad and small-component connections use vias in pads: specify an appropriate filled/capped process and review the stencil with the assembler.

## Mechanical placement

- CM5 body envelope: X=1.5–41.5, Y=43.5–98.5 mm. J1=(4.5,73.5), J2=(38.5,73.5), preserving the official 34 mm connector separation. CM5 spacer centers are (5,47), (38,47), (5,95), (38,95), a 33 × 48 mm mounting pattern with 4 mm spacers.
- Both 2280 SSDs are on the underside. Sockets are centered at (20,35) and (52,35), with insertion toward increasing Y. Their 2.5 mm retention spacers are at Y=113.75 mm. Card envelopes are drawn on Dwgs.User; bottom-side components are kept out of them.
- The PCIe switch and its small passives occupy the center. Three main power stages occupy the right side. RJ45 is at the upper-right edge, barrel power at the right edge, the two USB-C ports at the bottom, and microSD at the lower-left edge.
- Keep adequate airflow and CM5/SSD cooling. The project does not contain a complete enclosure or heatsink clearance model.

## Fabrication hold

Routing completion does not clear the PoE module's missing support-pin dimensions or its limited stock. See [REVIEW.md](REVIEW.md). No fabrication package is released. Prototype validation must cover supply regulation and temperature under load, source handover, USB-PD inrush, PoE classification/budget, reset sequencing, and operation of both SSDs.
