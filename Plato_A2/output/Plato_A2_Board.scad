use <../library.scad>;
difference() {
   triangle_board( 27, 1, 1.6);
   hole(0.0, 17.320508075688775, 0.38);
   hole(-3.0, 12.12435565298214, 0.38);
   hole(3.0, 12.12435565298214, 0.38);
   hole(6.0, 6.928203230275509, 0.55);
   hole(0.0, 6.928203230275509, 0.55);
   hole(-6.0, 6.928203230275509, 0.55);
   hole(-9.0, 1.7320508075688772, 0.55);
   hole(-3.0, 1.7320508075688772, 0.55);
   hole(3.0, 1.7320508075688772, 0.55);
   hole(9.0, 1.7320508075688772, 0.55);
   hole(12.0, -3.464101615137755, 0.38);
   hole(6.0, -3.464101615137755, 0.55);
   hole(0.0, -3.464101615137755, 0.55);
   hole(-6.0, -3.464101615137755, 0.55);
   hole(-12.0, -3.464101615137755, 0.38);
   hole(-15.0, -8.660254037844387, 0.38);
   hole(-9.0, -8.660254037844387, 0.38);
   hole(-3.0, -8.660254037844387, 0.55);
   hole(3.0, -8.660254037844387, 0.55);
   hole(9.0, -8.660254037844387, 0.38);
   hole(15.0, -8.660254037844387, 0.55);
}