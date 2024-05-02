import os 
from lxml import etree

output_dir = os.getcwd()+"/output/"
density = "-density 800"
crop = "2700x2400-1200-1000"
project = "Plato_A2"

blur = "\\( -clone 0 -channel R -gaussian-blur 1x1 +channel \\) \\( -clone 0 -channel G -gaussian-blur 3x3 +channel \\) \\( -clone 0 -channel B -gaussian-blur 9x9 +channel \\) -delete 0 -combine"

pairs = [
  "Silkscreen",
  "Mask",
  "Cu",
  "Paste",
]

svgs = sum([ [f"{project}-F_{pair}", f"{project}-B_{pair}"] for pair in pairs ],[]) + [ f"{project}-Edge_Cuts" ]

def remove_text_from_svg(overwrite_file):
    # Parse the SVG file using lxml
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(overwrite_file, parser)
    root = tree.getroot()

    # Define the namespaces if there are any. SVG files usually use namespaces.
    namespaces = {'svg': 'http://www.w3.org/2000/svg'}

    # Find all text elements and remove them
    for text in root.findall('.//svg:text', namespaces):
        parent = text.getparent()
        if parent is not None:
            parent.remove(text)

    # Save the modified SVG
    tree.write(overwrite_file, pretty_print=True, xml_declaration=True, encoding='UTF-8')





def run_command( command ):
  print(command+"\n")
  os.system(command )


def combine_pair ( file1, file2, output_file ) :
  run_command( f"magick convert {output_dir}/{file1}.png {output_dir}/{file2}.png +append {output_dir}/{output_file}.png" )


run_command( f"openscad -o {output_dir}/{project}_Board.stl {output_dir}/{project}_Board.scad" )
run_command( f"openscad -o {output_dir}/{project}.stl {output_dir}/{project}.scad" )

for svg in svgs:
  remove_text_from_svg( f"{output_dir}/{svg}.svg")
  run_command( f"magick convert {density} {output_dir}/{svg}.svg -crop {crop} -channel RGB -negate {blur} {output_dir}/{svg}.png" )


combine_pair(f"{project}-Edge_Cuts", f"{project}-Edge_Cuts", f"{project}-Edge")

for pair in pairs:
  combine_pair(f"{project}-F_{pair}", f"{project}-B_{pair}", f"{project}-Pair-{pair}")