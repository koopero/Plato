# Plato_A2

*Please note that this design has failed testing and should not be used.*

`Plato_A2` is a regular triangle, made of light and plastic, with a dimension of about an inch. This subassembly is meant as an experiment in:

|Spec|Value|Unit|
|----|-----|----|
|LED Count| 28 | WS2812B 2020|



# Process

- Iterate design scripts from `Plato_A1` ( `Plato_A2_design.py` and `kicad_align_leds.py` )
  - Better LED orientation.
  - Export of holes and jumpers.
  - Placement of capacitors.
- Start a new project in Kicad
- Create schematic with all parts.
- Switch to PCB designer and import generated file `Plato_A2_board.dxf` into edge cut layer.
- Copy and paste the script `kicad_align_leds.py` into Kicad's scripting console to position LEDs.
- Manually place bulk capacitors and resistor.
- Draw routes to connect all components, using vias beneath LEDs.
- Create wicked silkscreen for front.
  - Create `art/Plato_A2_Art.png` in Gimp
  - Import png to Inkscape
  - *Trace Bitmap* with *Color Quantization*
  - *Path / Break Apart*
  - Delete image and background shape
  - Export to `art/Plato_A2_Art.dxf`
  - Import to kicad silkscreen layer.
  - Manually delete overlaps after DRC.
- Run DRC and fix problems.
- Use Kicad's Fabrication Toolkit plugin to aid in preparing the board for fabrication.
- Use [JLCPCB](https://jlcpcb.com/)'s online tools to order 5 copies of the board.
