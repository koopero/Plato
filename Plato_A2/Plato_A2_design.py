import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from shapely.geometry import Point, Polygon
import pandas as pd
from math import cos, sin, pi, atan2, sqrt
import ezdxf
from time import sleep

Face_centre = (100,100)
Face_radius = 27
Face_roundness = 1
Face_thickness = 1.6
Face_triangle_rows = 7
Face_hole_radius = 0.55
Face_jumper_radius = 0.38
Face_led_pitch = 6
Face_led_count = 28
Face_cap_offset = (0,2)
Face_cap_orientation = 0
Face_led_size = 2
Face_cap_size = (1.82,0.98)
row_orientation = [
    0,
    180,
    0,
    180,
    0,
    180,
    0,
]
led_names = [f"D{i}" for i in range(1, Face_led_count + 1)]
hole_names = [
    "J1",
    "J2",
    "J3",
    "H1",
    "H2",
    "H3",
    "H4",
    "H5",
    "H6",
    "H7",
    "J4",
    "H8",
    "H9",
    "H10",
    "J5",
    "J6",
    "J7",
    "H11",
    "H12",
    "J8",
    "H13",

]



def ensure_directory_for_path(path):
    """ Ensure the directory for a given file path exists. """
    import os
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

def rotate_degrees( point, angle ):
    """Rotate a point by a given angle in degrees."""
    x, y = point
    angle = angle * pi / 180
    new_x = x * cos(angle) - y * sin(angle)
    new_y = x * sin(angle) + y * cos(angle)
    return (new_x, new_y)

class Circle:
    def __init__(self, centre, radius, circle_type):
        self.centre = Point(centre)
        self.radius = radius
        self.type = circle_type
        self.orientation = 0
    
    def intersects(self, other_circle):
        """Check if this circle intersects with another circle."""
        distance = self.centre.distance(other_circle.centre)
        return distance < (self.radius + other_circle.radius)
    
    def to_shapely_path(self):
        """Convert this circle to a Shapely circular path."""
        return self.centre.buffer(self.radius)
    
def triangle_points( radius, rotation ) :
    points = []
    for i in range(3):
        angle = 2 * pi / 3 * i + rotation * pi / 180
        y = radius * cos(angle)
        x = radius * sin(angle)
        points.append((x, y))
    return points

class Plan:
    def __init__(self):
        self.clip_geometry = None
        self.circles = []
        self.leds = []
        self.holes = []
        self.caps = []
        self.parts = []

    
    def base_triangle(self, radius, roundness, inset=0 ):
        """Create a rounded triangle as the base geometry."""
        points = triangle_points(radius, 0)
        triangle = Polygon(points)
        self.clip_geometry = triangle
        self.board_geometry = triangle.buffer(-roundness).buffer(roundness)
        # self.clip_geometry = triangle.buffer(roundness) - triangle.buffer(-roundness)
        # self.clip_geometry = orient(self.clip_geometry, sign=1.0)  # Ensure consistent orientation
    
    def check_circles(self, given_circle):
        """Check if the given circle intersects with any in the circles list."""
        return any(given_circle.intersects(circle) for circle in self.circles)
    
    def within_base(self, given_circle):
        """Check if the given circle is completely within the base geometry."""
        circle_path = given_circle.to_shapely_path()
        return self.clip_geometry.contains( circle_path)
        return True
        return self.clip_geometry.contains(circle_path)

    def display(self, output = None, block=True):
        """Display the base geometry and all circles using matplotlib."""

        plt.clf()
        fig, ax = plt.subplots()
        
        # Display base geometry
        x, y = self.board_geometry.exterior.xy
        ax.fill(x, y, alpha=0.5, fc='lightblue', ec='blue')

        plt.title('Plato_A2 Design')
        
        # Display leds

        for circle in self.leds:
          centre = circle.centre
          x, y = centre.x, centre.y
          rect = Rectangle((x-Face_led_size/2, y-Face_led_size/2), Face_led_size, Face_led_size, edgecolor='black', facecolor='white')
          ax.add_patch(rect)


        for circle in self.caps:
          centre = circle.centre
          x, y = centre.x, centre.y
          sx, sy = Face_cap_size
          rect = Rectangle((x-sx/2, y-sy/2), sx, sy, edgecolor='black', facecolor='cyan')
          ax.add_patch(rect)


        for circle in self.holes:
            circle_path = circle.to_shapely_path()
            x, y = circle_path.exterior.xy

            colour = 'green'
            if circle.name.startswith("J"): colour = 'red'
            ax.fill(x, y, alpha=0.5, fc=colour, ec='black')
        
        # Set plot limits
        xmin, ymin, xmax, ymax = self.clip_geometry.bounds
        ax.set_xlim(xmin - 10, xmax + 10)
        ax.set_ylim(ymin - 10, ymax + 10)
        ax.set_aspect('equal')

        if output:
            ensure_directory_for_path(output)
            fig.savefig(output)

        plt.show( block=block  )

    def leds_to_parts( self ) :
        """Convert LEDs to parts."""
        parts = self.leds + self.holes + self.caps
        sorted_leds = sorted(parts, key=lambda led: led.name )
        for led in sorted_leds:
            row = ( led.name, led.centre.x, led.centre.y, led.orientation )
            self.parts.append(row)
    
    def export_parts_to_csv( self, filename ):
        """Export parts to a CSV file."""
        self.leds_to_parts()
        # Convert to DataFrame
        df = pd.DataFrame(self.parts, columns=["Name", "X", "Y","Orientation"])

        # Save to CSV
        df.to_csv(filename, index=False)

    def orient_leds_to_origin( self ):
        """Orient LEDs to the origin."""
        for led in self.leds:
            x, y = led.centre.x, led.centre.y
            angle = int(180 * atan2(x, y) / pi /5 ) * 5
            angle = angle % 360
            if angle < 0:
                angle += 360
            led.orientation = angle

    def export_clip_geometry_to_dxf( self, filename ):
        """Export the clip geometry to a DXF file."""
        doc = ezdxf.new('R2010', setup=True)
        
        # Set units to millimeters (1 = inches, 4 = millimeters)
        doc.header['$MEASUREMENT'] = 1
        doc.header['$INSUNITS'] = 4

        # Add modelspace, which is where you add your entities
        msp = doc.modelspace()

        # Add the base shape (rounded triangle)
        coordinates = list(self.board_geometry.exterior.coords)
        scale_factor = 1
        scaled_coordinates = [(x * scale_factor, y * scale_factor) for x, y in coordinates]

        msp.add_lwpolyline(list(scaled_coordinates))

        # for circle in self.holes:
            # msp.add_circle(center=(circle.centre.x, circle.centre.y), radius=circle.radius)
        doc.saveas(filename)

    def output_board_scad( self, board_filename, layout_filename=None ):
        """Output the board geometry to an OpenSCAD file."""
        with open(board_filename,"w") as f:
            f.write("use <../library.scad>;\n")
            f.write("difference() {\n")
            f.write(f"   triangle_board( {Face_radius}, {Face_roundness}, {Face_thickness});\n")
            for circle in self.holes:
                f.write(f"   hole({circle.centre.x}, {circle.centre.y}, {circle.radius});\n")
            f.write("}\n")
            f.close()

        with open(layout_filename,"w") as f:
            f.write("include <./Plato_A2_Board.scad>;\n")
            for circle in self.leds:
                f.write(f"   led({circle.centre.x}, {circle.centre.y}, {circle.radius});\n")
            f.close()

    def add_capacitors( self ) :
        """Add capacitors to the board."""
        for led in self.leds :
          lx, ly = led.centre.x, led.centre.y
          ox, oy = rotate_degrees(Face_cap_offset, 0)
          cx, cy = lx + ox, ly + oy
          cap = Circle((cx, cy), Face_hole_radius, "cap")
          cap.name = f"C{led.name[1:]}"
          cap.orientation = Face_cap_orientation
          self.caps.append(cap)



    def board_to_stl( self, in_file, out_file ):
        """Convert the board geometry to an STL file."""
        import subprocess
        subprocess.run(["openscad", "-o", out_file, in_file])

# Example usage:
plan = Plan()
plan.base_triangle(radius=Face_radius, roundness=Face_roundness)



def place_in_triangle_pattern( triangle_rows, spacing, offset, names, type ):
    for index, name in enumerate(names):
        rowsize = 1
        rowindex = index
        for row in range(triangle_rows):
            if rowindex < rowsize:
                orientation = row_orientation[row]
                if row % 2 == 0:
                    rowindex = rowsize - rowindex - 1

                x = (rowindex - rowsize / 2 + 0.5) * 2 * spacing
                y = (((triangle_rows) / 2 - row + 0.5 ) * sqrt(3)) * spacing + offset
                break
            
            rowindex -= rowsize
            rowsize += 1
            
        if type == "led":
          radius = Face_led_size/2
        elif type == "hole":
          radius = name.startswith("J") and Face_jumper_radius or Face_hole_radius

        led = Circle((x, y), radius, "led")
        led.name = name
        led.type = type
        led.orientation = orientation
        plan.circles.append(led)
        
        if type == "hole" :
          plan.holes.append(led)

        if type == "led":
          plan.leds.append(led)
          



place_in_triangle_pattern(Face_triangle_rows, Face_led_pitch/2, 0, led_names, "led")
place_in_triangle_pattern(Face_triangle_rows, Face_led_pitch/2, -Face_led_pitch/sqrt(3), hole_names, "hole")



plan.add_capacitors()

plan.export_parts_to_csv("output/Plato_A2_LEDs.csv")
plan.export_clip_geometry_to_dxf("output/Plato_A2_Board.dxf")
plan.output_board_scad("output/Plato_A2_Board.scad","output/Plato_A2.scad")
# plan.board_to_stl("output/Plato_A2_Board.scad", "output/Plato_A2_Board.stl")
plan.display( output="output/Plato_A2_design.svg", block = True )
