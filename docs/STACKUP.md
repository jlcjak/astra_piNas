# Six-layer stackup

Selected fabrication reference: **JLCPCB JLC06161H-3313**, nominal finished thickness **1.6 mm**, outer copper 1 oz and inner copper 0.5 oz. Dimensions below follow [JLCPCB's published impedance stackup](https://jlcpcb.com/impedance), checked 5 September 2026. Finished thickness includes manufacturing tolerances; do not substitute another six-layer construction without recalculating impedance.

| Layer / dielectric | Thickness, mm | Relative permittivity | Use |
|---|---:|---:|---|
| F.Cu | 0.0350 | — | Components, high-speed pairs, local power loops |
| 3313 prepreg | 0.0994 | 4.10 | |
| In1.Cu | 0.0152 | — | Ground reference; no signal routing |
| Core | 0.5500 | 4.60 | |
| In2.Cu | 0.0152 | — | Power distribution and slow signals |
| 2116 prepreg | 0.1088 | 4.16 | |
| In3.Cu | 0.0152 | — | Power distribution and slow signals |
| Core | 0.5500 | 4.60 | |
| In4.Cu | 0.0152 | — | Ground reference; no signal routing |
| 3313 prepreg | 0.0994 | 4.10 | |
| B.Cu | 0.0350 | — | SSD sockets, high-speed pairs and local bridges |

Outer microstrip starting dimensions are **0.127 mm width / 0.150 mm gap** for 90 Ω PCIe and USB, and **0.100 mm width / 0.150 mm gap** for 100 Ω Ethernet. These are nominal design dimensions, not measured impedance. The fabricator must confirm its controlled-impedance construction and coupon results; solder-mask thickness, etched conductor shape and actual dielectric properties affect the result. The exploratory quasi-static estimates in `routing/impedance_estimates.json` are not a fabrication field-solver sign-off.

The reference planes are continuous in the secondary power domain. Cable-side PoE conductors and the module primary connections are excluded from secondary copper regions. Power bridges use the two interior signal layers or the outer layers, retaining both ground reference layers.

Minimum ordinary clearance is 0.127 mm; existing fine-pitch connector land patterns retain their documented local clearances. Small through vias are 0.45 / 0.20 mm diameter/drill; power arrays use 0.60 / 0.30 mm. Copper is kept at least 0.5 mm from the routed board edge. Some exposed-pad and power-pad connections use vias in pads: confirm a filled/capped process and the corresponding stencil with the assembler before fabrication.

Raspberry Pi specifies 90 Ω differential PCIe routing with an ideal 0.1 mm intra-pair length match, and 100 Ω Ethernet with an ideal 0.15 mm intra-pair match. See the [CM5 datasheet](https://pip-assets.raspberrypi.com/categories/944-raspberry-pi-compute-module-5/documents/RP-008180-DS-4-cm5-datasheet.pdf). The two CM5 receiver coupling capacitors are 220 nF; the other data coupling positions are 100 nF.

This stackup selection does not clear the outstanding PoE mechanical fabrication hold in `REVIEW.md`.
