$fs = 0.1;
$fa = 0.1;

module triangle_board( point_radius = 24, roundness = 1, extrusion = 1.6 ) {
    color([0.3,0.3,0.3])
    linear_extrude(height = extrusion, center = false)
    offset(r = roundness, chamfer = false) 
    offset(r = -roundness, chamfer = false) 
    polygon(points=[
        [-sin(60)*point_radius, -cos(60)* point_radius], // First vertex at origin
        [sin(60)*point_radius, -cos(60)* point_radius], // First vertex at origin
        [0, point_radius] // Third vertex at top center
    ]);
}

module hole(x, y, radius) {
    translate([x, y, 0])  // Move the cylinder to the (x, y) position
    cylinder(h = 100, r = radius, center = true);
}

module led(x, y, orientation, z = 1.6) {
    color("white", 1)
    translate([x, y, z+0.5])
    rotate([0, 0, orientation])
    cube([2, 2, 1], center = true);
}