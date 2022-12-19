import numpy as np

class Surface:
    def __init__(self, r, cd, ed = None):
        self.radius = r
        self.clear_diameter = cd
        
        if ed is None:
            self.edge_diameter = cd
        else:
            self.edge_diameter = ed

    def __repr__(self) -> str:
        return str({"R": self.radius, "clear_diameter":self.clear_diameter, "edge_diameter":self.edge_diameter})

    def sag(self, h) -> float:
        r = self.radius
        adj = np.sqrt(r*r - h*h)
        return r*(1-np.abs(adj/r))

    @property
    def curvature(self) -> float:
        if self.radius == 0.0:
            return 0.0
        else:
            return 1/self.radius

class Singlet:
    def __init__(self, r1, cd1, ed1, r2, cd2, ed2, m, t):
        self.left_surface  = Surface(r1, cd1, ed1)
        self.right_surface = Surface(r2, cd2, ed2)
        self.material = "N-BK7"
        self.thickness = t

    @property
    def mech_diameter(self) -> float:
        return max(self.left_surface.edge_diameter, self.right_surface.edge_diameter)

    def power(self) -> float:
        n = 1.5
        t = self.thickness
        cv1 = self.left_surface.curvature
        cv2 = self.right_surface.curvature
        return (n-1)*(cv1-cv2 + t*(n-1)*cv1*cv2/n)
    
    def focal_length(self) -> float:
        return 1/self.power()
