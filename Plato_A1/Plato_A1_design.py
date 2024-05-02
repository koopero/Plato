import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon
import pandas as pd
from math import cos, sin, pi, atan2, sqrt
import ezdxf
from time import sleep

Face_radius = 25
Face_roundness = 1
Face_triangle_rows = 6
Face_led_radius = 3.6
Face_led_count = 21


def ensure_directory_for_path(path):
    """ Ensure the directory for a given file path exists. """
    import os
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

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
        x = radius * cos(angle)
        y = radius * sin(angle)
        points.append((x, y))
    return points

class Plan:
    def __init__(self):
        self.clip_geometry = None
        self.circles = []
        self.leds = []
        self.holes = []
        self.parts = []

    
    def base_triangle(self, radius, roundness, inset=0 ):
        """Create a rounded triangle as the base geometry."""
        points = triangle_points(radius, 0)
        triangle = Polygon(points)
        self.clip_geometry = triangle
        self.board_geometry = triangle.buffer(roundness) - triangle.buffer(-roundness)
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

        plt.title('Plato_A1 Design')
        
        # Display circles
        for circle in self.circles:
            circle_path = circle.to_shapely_path()
            x, y = circle_path.exterior.xy

            colour = 'green' if circle.type == "bad" else 'red'
            if circle.type == "eye": colour = 'cyan'
            if circle.type == "mount": colour = 'yellow'
            if circle.type == "cap": colour = 'purple'
            if circle.type == "vent": colour = 'cyan'
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

    def connect_leds(self):
        """Connect LEDs to the base geometry."""
        unconnected_leds = self.leds.copy()
        connected_leds = []
        connections = []

        leds_by_x = sorted(unconnected_leds, key=lambda led: led.centre.x )
        rightmost_led = leds_by_x.pop()

        rightmost_led.name = "LED1"
        unconnected_leds.remove(rightmost_led)
        connected_leds.append(rightmost_led)

        led_index = 2
        while unconnected_leds:
            last_led = connected_leds[-1]
            closest_led = min(unconnected_leds, key=lambda led: led.centre.distance(last_led.centre) - led.centre.x * 1.2 )
            
            closest_led.name = f"LED{led_index}"
            led_index += 1
            unconnected_leds.remove(closest_led)
            connected_leds.append(closest_led)
            connections.append((last_led.centre, closest_led.centre ) )



        self.connections = connections

    def leds_to_parts( self ) :
        """Convert LEDs to parts."""
        sorted_leds = sorted(self.leds, key=lambda led: led.name )
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

        # Add circles
        for circle in self.holes:
            msp.add_circle(center=(circle.centre.x, circle.centre.y), radius=circle.radius)

        doc.saveas(filename)

# Example usage:
plan = Plan()
plan.base_triangle(radius=Face_radius, roundness=Face_roundness)



def place_in_triangle_pattern( triangle_rows, spacing, radius, offset, names, type ):
    for index, name in enumerate(names):
        rowsize = 1
        rowindex = index
        for row in range(triangle_rows):
            if rowindex < rowsize:
                if row % 2 == 0:
                    rowindex = rowsize - rowindex - 1
                y = (rowindex - rowsize / 2 + 0.5) * 2 * spacing
                x = (((triangle_rows) / 2 - row + 0.5 ) * sqrt(3)) * spacing + offset
                break
            
            rowindex -= rowsize
            rowsize += 1
            

        led = Circle((x, y), radius, "led")
        led.name = name
        led.type = type
        plan.leds.append(led)
        plan.circles.append(led)

led_names = [f"D{i}" for i in range(1, Face_led_count + 1)]
place_in_triangle_pattern(Face_triangle_rows, Face_led_radius, Face_led_radius, -1, led_names, "led")

hole_names = [
    "J1",
    "J2",
    "J3",
    "H1",
    "H2",
    "H3",
    "J4",
    "H4",
    "H5",
    "J5",
    "J8",
    "J7",
    "H6",
    "J6",
    "H7",
]

place_in_triangle_pattern(Face_triangle_rows, Face_led_radius, 1.6, -Face_led_radius-1.5, hole_names, "hole")
plan.orient_leds_to_origin()
plan.export_parts_to_csv("output/Plato_A1_LEDs.csv")
plan.export_clip_geometry_to_dxf("output/Plato_A1_Board.dxf")
plan.display( output="output/Plato_A1_design.svg", block = True )
