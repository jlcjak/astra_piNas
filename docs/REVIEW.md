# Release status: routed review; fabrication hold

This is a new KiCad 10 project created in this directory. The schematics and board are linked, with project-local symbols, footprints and available 3D models. The 100 × 120 mm, six-layer board is routed and geometrically length-matched. No Gerbers have been released.

## Open design decisions

1. **PoE does not yet meet the sourcing/mechanical requirement.** WC-PD60B120A (LCSC C2848082) has only **15** units available in the captured LCSC evidence. It is a candidate, not an approved production selection. Its supplied drawing does not locate support pins 9/10 horizontally. Its local footprint therefore intentionally includes only the eight dimensioned electrical pins and a body envelope. Do not manufacture that footprint. A manufacturer-confirmed drawing and adequate supply, or a different PoE implementation, are required. The low stock was not silently accepted as “well stocked.”
2. **PoE power budget needs a decision.** The module advertises 12 V / 5 A and mentions class 5/6 operation. That does not establish delivery of 60 W to this carrier from a class-6 PSE. Classification, conversion loss and temperature derating must be resolved. A fully loaded CM5 and two unrestricted SSDs cannot be promised to operate on an ordinary PoE+ port. There is no software-controlled load shedding or negotiated-power telemetry in this draft.
3. **Power validation remains required.** Check AP64501 compensation with effective, voltage-biased output capacitance (including the SSD input capacitance), USB-PD inrush and source handover, 9 V maximum-load operation, and temperatures of the OR diodes and converters. Check the 1 V/3.3 V switch power-down sequence and reset timing on actual hardware. ERC does not validate these behaviors.
4. **Connector/mechanical fit must be checked with purchased samples.** CM5 connector pads and relative positioning use the official CM5IO reference. M.2 pads match the TE drawing. The SSD insertion datum and spacer height were derived from TE's drawing; confirm with the actual sockets and SSDs before release. The PoE support-hole problem is a known incompleteness, not a sample-validation formality.
5. **Assembly hardware:** the soldered spacers are in the LCSC BOM; removable M2 screws, the CM5 Lite, SSDs, heatsinks and enclosure are not included in the carrier BOM. Screw engagement and head diameter must be selected for the actual assembly. M2 screws are used through the CM5's 2.7 mm mounting holes.

## Implemented architecture

- CM5 **Lite** carrier; native microSD wiring. An eMMC-equipped CM5 cannot use this socket as its native SD boot interface.
- Two TE 1-2199230-5 M-key sockets, each connected at PCIe x1, supporting 2280 **NVMe** modules. SATA SSDs are not supported.
- Diodes PI7C9X2G404SLBFDEX PCIe switch: upstream port 0, SSDs on ports 1 and 2, port 3 unused. All SSD traffic shares the CM5 PCIe Gen 2 x1 link; this is not two independent x4 links.
- Integrated switch clock buffer. CM5 CLKREQ# is grounded for continuous clocking. Switch TX lines have external AC coupling; the CM5 TX coupling is already on the module. HCSL outputs use 49.9-ohm shunts and 33.2-ohm series resistors; the switch's own REFCLK input is AC coupled.
- Separate AP64501 converters for CM5 5 V and each SSD 3.3 V rail. SSD enables follow PCIE_PWR_EN. A TLV62569 generates the switch's 1 V rail, enabled from CM5 3.3 V.
- Gigabit PoE-capable Hanrun HR913180AE magjack, with the four cable-side center taps routed to the candidate PoE module. PHY-side center taps have local bypassing.
- Center-positive 9–25 V barrel input, 5 A fuse, TVS and Schottky reverse-current blocking. Input current and temperature, especially at 9 V, limit total usable power.
- Power-only USB-C uses a CH224K requesting **20 V** (CFG1=0, CFG2=1, CFG3=0; the CH224Q/A strap table is different). Use a supply offering 20 V at 3 A. Its status signal controls a level-shifted PMOS gate, with a 10 V gate clamp. The VDD feed resistor is rated 0.5 W. A gate capacitor slows switching, but compliant inrush has not been demonstrated.
- The second USB-C connects only to CH343P USB-UART. USB VBUS powers the bridge; CM5 3.3 V powers its independent VIO. GPIO14 is CM5 TX; GPIO15 is CM5 RX. This is **not** the separate on-module boot-debug UART. Configure the OS UART/pin mux accordingly. USB enumeration and a compatible driver are required on the host.
- All selected resistors and capacitors are 0402 or larger. Every populated carrier component has `MANUFACTURER PART NUMBER`, manufacturer and LCSC fields. Positive stock is recorded in the BOM, but stock is a snapshot, not a reservation.

## Verification meaning

`erc.rpt` is KiCad's electrical-rules report. `audit.json` checks the generated netlist against the explicit pin-to-net manifest and verifies MPN/stock metadata; it is a consistency check, not an independent circuit proof. `drc.rpt` records the final PCB geometry and connectivity checks. `pair_lengths.csv` records the pad-to-pad differential-path measurements. Known limitations must not be hidden by quoting a clean ERC result.

The imported EasyEDA footprints were corrected where locating holes were erroneously plated and where buck-converter thermal vias were unnamed. The terminal numbers of all connected schematic pins are checked against board pads. YIYUAN spacer footprints use the manufacturer's 6.2 mm solder land and 3.73 mm finished hole. Plated holes are selected and the paste aperture is split into four sectors. The rejected Würth candidates were not retained in the active BOM because their LCSC pages were unavailable.

## Final automated checks

See `routing_validation.json`, `erc.rpt`, `drc.rpt`, `schematic_parity.rpt`, `audit.json` and `board_audit.json` for the actual final results. Routing DRC and schematic parity are reported separately: the two omitted PoE support pads, U7.9 and U7.10, remain a known footprint incompleteness. The consistency audit checks 685 connected schematic pin assignments across 176 physical components. These checks do not resolve the PoE hold or replace prototype validation.
