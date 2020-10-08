""" Module for surface profile
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

class Surface:
    def __init__(self, inner_d=0.0, outer_d=0.0):
        self.inner_d = inner_d
        self.outer_d = outer_d

    def sag(self,h):
        pass

    def deriv_1st(self, h):
        pass

    def deriv_2nd(self, h):
        pass

    def slope(self, h):
        pass

    def local_curvature(self, h):
        pass

    def local_radius(self, h):
        pass



class Sphere(Surface):
    def __init__(self, r=np.inf,inner_d=0.0, outer_d=0.0):
        super().__init__(inner_d, outer_d)
        self.type = 'SPH'
        self.r = r
        
    @property
    def c(self):
        # center radius
        if self.r == np.inf:
            _c = 0.0
        else:
            try:
                _c = 1/self.r
            except ZeroDivisionError:
                _c = np.inf
        
        return _c

    def sag(self, h):
        z = self.c* h**2 / ( 1 + np.sqrt(1 - self.c**2 * h**2) )
        return z

    def deriv_1st(self, h):
        c = self.c
        rt = np.sqrt( 1 -  c**2 * h**2 )

        z1 = 2*c*h/( rt+1 )
        z2 = c**3 * h**3 /( rt * (rt+1)**2 )

        return (z1+z2)

    def deriv_2nd(self, h):
        pass

    def slope(self,h):
        return (np.arctan(self.deriv_1st(h)))*180/np.pi

    def local_radius(self,h):
        return self.r + np.zeros_like(h)


class EvenAsphere(Surface):
    def __init__(self, r= np.inf, k=0.0, coefs=None, inner_d=0.0, outer_d=0.0):
        super().__init__(inner_d, outer_d)

        self.type = 'ASP'
        self.r = r
        self.k = k

        if coefs is None:
            self.coefs = np.zeros(9,dtype=float)
        else:
            self.coefs = coefs

    @property
    def c(self):
        try:
            _c = 1/self.r
        except ZeroDivisionError:
            _c = np.inf
        return _c

    def get_parameters(self):
        return self.r, self.k, self.coefs

    def sag(self, h):
        z_conic = self.c*np.power(h,2.0) /(1.0 + np.sqrt(1-(1+self.k)*np.power(self.c,2.0)*np.power(h,2.0)))

        z_pol = 0.0
        for i, A in enumerate(self.coefs):
            z_pol += A*h**(2*(i+1)+2)

        return (z_conic + z_pol)

    def deriv_1st(self, h):
        c = self.c
        k = self.k
        rt = np.sqrt( 1 - (1+k) * c**2 * h**2 )

        z1 = 2*c*h/( rt+1 )
        z2 = c**3 * h**3 * (k+1)/( rt * (rt+1)**2 )
        
        z_pol = 0.0
        for i, A in enumerate(self.coefs):
            z_pol += (2*(i+1)+2) * A * h**(2*(i+1)+1)
        
        return (z1 + z2 + z_pol)

    def deriv_2nd(self, h):
        c = self.c
        k = self.k
        rt = np.sqrt( 1 - (1+k) * c**2 * h**2 )

        z1 = 2*c/(rt+1)
        z2 = 5 * c**3 * h**2 * (k+1)/( rt * (rt+1)**2 )
        z3 = c**5 * h**4 * (k+1)**2 / ( rt**3 * (rt+1)**2 )
        z4 = - 2 * c**5 * h**4 * (k+1)**2 / ( (c**2 * h**2 * (k+1) -1) * (rt+1)**3 )
        
        z_pol = 0.0
        for i, A in enumerate(self.coefs):
            z_pol += (2*(i+1)+1)*(2*(i+1)+2) * A * h**(2*(i+1))
        
        return (z1+z2+z3+z4+z_pol)

    def slope(self, h):
        return (np.arctan(self.deriv_1st(h)))*180/np.pi

    def local_curvature(self, h):
        return self.deriv_2nd(h) / np.power( (1 + self.deriv_1st(h)**2), 3/2)

    def local_radius(self, h):
        try:
            lr = 1/self.local_curvature(h)
        except ZeroDivisionError:
            pass

        return lr


class OddAsphere(Surface):
    def __init__(self, r=np.inf, k=0.0, coefs=None, inner_d=0.0, outer_d=0.0):
        super().__init__(inner_d, outer_d)
        self.type = 'ODD'

        self.r = r
        self.k = k

        if coefs is None:
            self.coefs = np.zeros(9,dtype=float)
        else:
            self.coefs = coefs

    @property
    def c(self):
        try:
            _c = 1/self.r
        except ZeroDivisionError:
            _c = np.inf
        return _c
    
    def sag(self, h):
        z_conic = self.c*np.power(h,2.0) /(1.0 + np.sqrt(1-(1+self.k)*np.power(self.c,2.0)*np.power(h,2.0)))

        z_pol = 0.0
        for i, A in enumerate(self.coefs):
            z_pol += A*h**(i+3)

        return (z_conic + z_pol)

    def deriv_1st(self, h):
        c = self.c
        k = self.k
        rt = np.sqrt( 1 - (1+k) * c**2 * h**2 )

        z1 = 2*c*h/( rt+1 )
        z2 = c**3 * h**3 * (k+1)/( rt * (rt+1)**2 )
        
        z_pol = 0.0
        for i, A in enumerate(self.coefs):
            z_pol += (i+3) * A * h**(i+2)
        
        return (z1 + z2 + z_pol)

    def deriv_2nd(self, h):
        c = self.c
        k = self.k
        rt = np.sqrt( 1 - (1+k) * c**2 * h**2 )

        z1 = 2*c/(rt+1)
        z2 = 5 * c**3 * h**2 * (k+1)/( rt * (rt+1)**2 )
        z3 = c**5 * h**4 * (k+1)**2 / ( rt**3 * (rt+1)**2 )
        z4 = - 2 * c**5 * h**4 * (k+1)**2 / ( (c**2 * h**2 * (k+1) -1) * (rt+1)**3 )
        
        z_pol = 0.0
        for i,A in enumerate(self.coefs):
            z_pol += (i+2)*(i+3)*A*h**(i+1)
        
        return (z1+z2+z3+z4+z_pol)

    def slope(self, h):
        return (np.arctan(self.deriv_1st(h)))*180/np.pi
    
    def local_curvature(self, h):
        return self.deriv_2nd(h) / np.power( (1 + self.deriv_1st(h)**2), 3/2)

    def local_radius(self, h):
        try:
            lr = 1/self.local_curvature(h)
        except ZeroDivisionError:
            pass

        return lr

