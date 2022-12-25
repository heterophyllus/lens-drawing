import ezdxf
from ezdxf.enums import TextEntityAlignment
from ezdxf.math import ConstructionArc
import numpy as np
from lens import *

class LensDrawing:
    def __init__(self, templatefile:str):
        self.doc = ezdxf.readfile(templatefile)
        self.msp = self.doc.modelspace()
        layers = ["structure", "dimension", "text", "frame"] #構造物 寸法 文字列 図枠
        for layer in layers:
            self.doc.layers.add(name=layer)#特に属性は指定しない 
        
        self.with_dimension = True
        self.lineweight = 25
        self.structure_layer = 'structure'
        self.dimension_layer = 'dimension'

    def saveas(self, filename:str):
        self.doc.saveas(filename)
        
    def draw_lens(self, lens, pos:tuple):
        cd1 = lens.left_surface.clear_diameter
        cd2 = lens.right_surface.clear_diameter
        mech_d = lens.mech_diameter
    
        r1 = lens.left_surface.radius
        r2 = lens.right_surface.radius
        t  = lens.thickness
        
        # draw curved surface
        left_pos = pos
        left_arc = self.add_arc(left_pos, r1, cd1)
        right_pos = (pos[0]+t, pos[1] )
        right_arc = self.add_arc(right_pos, r2, cd2)
    
        # draw flat surface
        left_x = left_pos[0]+lens.left_surface.sag(cd1/2)
        pt1 = (left_x, left_pos[1]+cd1/2)
        pt2 = (left_x, left_pos[1]+mech_d/2)
        self.add_line(pt1, pt2)
        
        pt1 = (left_x, left_pos[1]-cd1/2)
        pt2 = (left_x, left_pos[1]-mech_d/2)
        self.add_line(pt1, pt2)
        
        right_x = right_pos[0]+lens.right_surface.sag(cd2/2)
        pt1 = (right_x, left_pos[1]+cd2/2)
        pt2 = (right_x, left_pos[1]+mech_d/2)
        self.add_line(pt1, pt2)
        
        pt1 = (right_x, left_pos[1]-cd2/2)
        pt2 = (right_x, left_pos[1]-mech_d/2)
        self.add_line(pt1, pt2)
    
        # draw koba
        upper_koba_pt1 = (left_pos[0]+lens.left_surface.sag(cd1/2), left_pos[1]+mech_d/2)
        upper_koba_pt2 = (right_pos[0]+lens.right_surface.sag(cd2/2), right_pos[1]+mech_d/2)
        self.add_line(upper_koba_pt1, upper_koba_pt2)
        
        lower_koba_pt1 = (left_pos[0]+lens.left_surface.sag(cd1/2), left_pos[1]-mech_d/2)
        lower_koba_pt2 = (right_pos[0]+lens.right_surface.sag(cd2/2), right_pos[1]-mech_d/2)
        self.add_line(lower_koba_pt1, lower_koba_pt2)
        
        # draw dimensions
        if self.with_dimension:

            # radius
            #self.add_radius_dim(left_arc, lens.left_surface.radius, direction=-1)
            #self.add_radius_dim(right_arc, lens.right_surface.radius, direction= 1)

            # koba
            self.add_dim(p1= upper_koba_pt1, p2= upper_koba_pt2, distance= 10)

            # center thickness
            self.add_dim(p1=left_pos, p2=right_pos, distance=-(mech_d/2)*1.5, tolerance=lens.tolerances["thickness"])
            
            thresh = 0.01
            # inner diameter left
            if abs(mech_d - cd1) > thresh:
                self.add_dim(p1= left_arc.end_point, p2=left_arc.start_point, distance= -10)

            # inner diameter right
            if abs(mech_d - cd2) > thresh:
                self.add_dim(p1= right_arc.start_point, p2=right_arc.end_point, distance= 10)

            # outer diameter
            self.add_dim(p1=upper_koba_pt1, p2=lower_koba_pt1, distance=20, tolerance=lens.tolerances["mech_diameter"])

    def add_text(self, pt, text):
        self.msp.add_text(
            text,
            height= 0.35
        ).set_placement(pt,align=TextEntityAlignment.MIDDLE_LEFT)

    def add_line(self, p1, p2):
        new_line = self.msp.add_line(
            start=p1, 
            end=p2, 
            dxfattribs={
                'layer':'structure',
                'lineweight':self.lineweight
            })
        return new_line

    def add_arc(self, vertex_pt, radius, diameter):
        center_pt = (vertex_pt[0]+radius, vertex_pt[1])
        h = diameter/2
        start_ang = 0
        end_ang   = 0
        if radius > 0:
            start_ang = 180 - np.degrees( np.arcsin(h/radius) )
            end_ang   = 180 + np.degrees( np.arcsin(h/radius) )
        else:
            start_ang = np.degrees( np.arcsin(h/radius) )
            end_ang   = -start_ang
            
        new_arc = self.msp.add_arc(
            center= center_pt, 
            radius= abs(radius), 
            start_angle= start_ang, 
            end_angle= end_ang, 
            dxfattribs={'layer':'structure','lineweight':self.lineweight})

        return new_arc

    def add_dim(self, p1, p2, distance, tolerance:tuple= None):
        dim = self.msp.add_aligned_dim(
            p1=p1, 
            p2=p2, 
            distance=distance, 
            dimstyle="Standard", 
            override={
                "dimjust": 1, 
                "dimtad":3,
                "dimblk":"OPEN30",
                "dimdsep":ord(".")
            },
            dxfattribs={'layer':'structure'})

        if tolerance is not None:
            upper = tolerance[1]
            lower = tolerance[0]
            if tolerance[0] < 0.0: # a bug in ezdxf?
                lower = -tolerance[0]

            dim.set_tolerance(
                upper= upper,
                lower= lower, 
                hfactor= 0.4, 
                dec=2)

        dim.render()
        
        return dim

    def add_radius_dim(self, arc, actual_radius, direction):
        cons_arc = arc.construction_tool()

        if actual_radius > 0:
            if direction > 0:
                loc = (cons_arc.center[0]-cons_arc.radius, cons_arc.center[1])
                dim = self.msp.add_radius_dim(
                    center=cons_arc.center,
                    radius=cons_arc.radius,
                    location=loc,
                    dimstyle="EZ_RADIUS",
                    override={
                        "dimtad": 1,
                        "dimtoh":1}
                    )
                return dim
            else:
                loc = (cons_arc.center[0]+cons_arc.radius, cons_arc.center[1])
                dim = self.msp.add_radius_dim(
                    center=cons_arc.center,
                    radius=cons_arc.radius,
                    location=loc,
                    dimstyle="EZ_RADIUS",
                    override={
                        "dimtad": 1,
                        "dimtih":1}
                    )

                return dim

        else: # actual_radius < 0
            if direction > 0:
                loc = (cons_arc.center[0]+cons_arc.radius, cons_arc.center[1])
                dim = self.msp.add_radius_dim(
                    center=cons_arc.center,
                    radius=cons_arc.radius,
                    location=loc,
                    dimstyle="EZ_RADIUS",
                    override={
                        "dimtad": 1,
                        "dimtoh":1}
                    )

                return dim
            else:
                loc = (cons_arc.center[0]-cons_arc.radius, cons_arc.center[1])
                dim = self.msp.add_radius_dim(
                    center=cons_arc.center,
                    radius=cons_arc.radius,
                    location=loc,
                    dimstyle="EZ_RADIUS",
                    override={
                        "dimtad": 1,
                        "dimtih":1}
                    )

                return dim

    