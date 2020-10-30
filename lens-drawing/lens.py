""" Module for lens data container
"""

"""
    Copyright (C) 2020 Hiiragi <heterophyllus.work@gmail.com>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
"""

import numpy as np
import surface as s

class Lens:
    def __init__(self, left_surf=None, right_surf=None, name= "", thickness=0.0, material=""):
        
        self.name = name
        self.description = ""

        if left_surf is None:
            self.left = s.Sphere()
        else:
            self.left = left_surf

        if right_surf is None:
            self.right = s.Sphere()
        else:
            self.right = right_surf
        
        self.thickness = thickness
        self.material = material
        

    @property
    def volume(self):
        pass

    @property
    def weight(self):
        pass

    def edge_thickness(self, h):
        pass

    def to_dict(self):
        dct = {}
        dct['name'] = self.name
        dct['material'] = self.material
        dct['thickness'] = self.thickness
        dct['description'] = self.description

        dct['left'] = {}
        dct['left']['type'] = self.left.type
        dct['left']['inner_d'] = self.left.inner_d
        dct['left']['outer_d'] = self.left.outer_d
        dct['left']['radius'] = self.left.r
        if self.left.type != 'SPH':
            dct['left']['k'] = self.left.k
            if isinstance(self.left.coefs, np.ndarray):
                dct['left']['coefs'] = self.left.coefs.tolist()
            else:
                dct['left']['coefs'] = self.left.coefs
        
        dct['right'] = {}
        dct['right']['type'] = self.right.type
        dct['right']['inner_d'] = self.right.inner_d
        dct['right']['outer_d'] = self.right.outer_d
        dct['right']['radius'] = self.right.r
        if self.right.type != 'SPH':
            dct['right']['k'] = self.right.k
            if isinstance(self.right.coefs, np.ndarray):
                dct['right']['coefs'] = self.right.coefs.tolist()
            else:
                dct['right']['coefs'] = self.right.coefs

        return dct

    def from_dict(self, dct=None):
        if dct is None:
            return

        self.name = dct['name']
        self.material = dct['material']
        self.thickness = float(dct['thickness'])
        self.description = dct['description']
        
        # left
        if dct['left']['type'] == 'SPH':
            self.left = s.Sphere()
            try:
                self.left.r = float(dct['left']['radius'])
            except ValueError:
                self.left.r = np.inf
        else:
            self.left = s.EvenAsphere()
            try:
                self.left.r = float(dct['left']['radius'])
            except ValueError:
                self.left.r = np.inf
            self.left.k = float(dct['left']['k'])
            self.left.coefs = np.array(dct['left']['coefs'], dtype=float)

        self.left.inner_d = float(dct['left']['inner_d'])
        self.left.outer_d = float(dct['left']['outer_d'])

        # right
        if dct['right']['type'] == 'SPH':
            self.right = s.Sphere()
            try:
                self.right.r = float(dct['right']['radius'])
            except ValueError:
                self.right.r = np.inf
        else:
            self.right = s.EvenAsphere()
            try:
                self.right.r = dct['right']['radius']
            except ValueError:
                self.right.r = np.inf
            self.right.k = float(dct['right']['k'])
            self.right.coefs = np.array(dct['right']['coefs'], dtype=float)

        self.right.inner_d = float(dct['right']['inner_d'])
        self.right.outer_d = float(dct['right']['outer_d'])



