import numpy as np

class Surface:
    def __init__(self, radius:float, clear_diameter:float):
        self.radius:float = radius
        self.clear_diameter:float = clear_diameter
        
    def sag(self, h:float) -> float:
        r = self.radius
        adj = np.sqrt(r*r - h*h)
        return r*(1-np.abs(adj/r))

    @property
    def curvature(self) -> float:
        if abs(self.radius) < 1e-6:
            return 0.0
        else:
            return 1.0/self.radius


class Singlet:
    def __init__(self, radius1:float, clear_diameter1:float, radius2:float, clear_diameter2:float, mech_diameter:float, material:str, thickness:float):
        self.left_surface  = Surface(radius1, clear_diameter1)
        self.right_surface = Surface(radius2, clear_diameter2)
        self.mech_diameter = mech_diameter
        self.material      = material
        self.thickness     = thickness

        self.tolerances = {
            "thickness":(-0.05, 0.05),
            "koba":(-0.05, 0.05),
            "mech_diameter":(-0.08, -0.03),
        }

    def set_tolerance(self, tolerance_name, tolerance_range):
        if tolerance_name in self.tolerances.keys:
            self.tolerances[tolerance_name] = tolerance_range

