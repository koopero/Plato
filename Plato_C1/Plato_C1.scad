// Define vertices of the regular tetrahedron
vertices = [
    [ 0,  0,  2],  // Vertex 0
    [-cos(60)*1,  -sin(60)*1, 0],  // Vertex 1
    [-cos(60)*1,  sin(60)*1, 0],  // Vertex 2
    [ 1,  0, 0]   // Vertex 3
];

// Define faces using the vertices
faces = [
    [0, 1, 2], // Face 1
    [0, 3, 1], // Face 2
    [0, 2, 3], // Face 3
    [1, 3, 2]  // Face 4
];



// Create the regular tetrahedron
polyhedron(points = vertices, faces = faces);