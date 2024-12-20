"""This module contains functions for Zernike calculations. Mainly the private
function _zgen, a generator function for Zernike polynomials. The public
functions make use of _zgen to create height or slope maps in a unit
pupil, corresponding to individual Zernike terms.

Author: Ravi S. Jonnal / Werner Lab, UC Davis

Revision: 3.0 / 14 March 2019

"""

import numpy as np
from matplotlib import pyplot as plt
import sys,os
import ciao_config as ccfg

def fact(num):
    """Implementation of factorial function.
    """
    # Check that the number is an integer.
    assert(num%1==0)
    # Check that $num\geq 0$.
    assert(num>=0)
    
    # Compute $num!$ recursively.
    if num==0 or num==1:
        return 1
    else:
        return num * fact(num-1)

def choose(a,b):
    """Binomial coefficient, implemented using
    this module's factorial function.
    See [here](http://www.encyclopediaofmath.org/index.php/Newton_binomial) for detail.
    """
    assert(a>=b)
    return fact(a)/(fact(b)*fact(a-b))

class Zernike:

    def j2nm(self,j):
        n = np.ceil((-3+np.sqrt(9+8*j))/2)
        m = 2*j-n*(n+2)
        return int(n),int(m)

    def nm2j(self,n,m):
        return int(n*(n+1)/2.0+(n+m)/2.0)

    def zeqn(self,n,m,kind='h',forceRecompute=False):
        """Return parameters sufficient for specifying a Zernike term
        of desired order and azimuthal frequency.

        Given an order (or degree) n and azimuthal frequency f, and x-
        and y- rectangular (Cartesian) coordinates, produce parameters
        necessary for constructing the appropriate Zernike
        representation.

        An individual polynomial has the format:

        $$ Z_n^m = \sqrt{c} \Sigma^j\Sigma^k [a_{jk}X^jY^k] $$

        This function returns a tuple ($c$,cdict). $c$ is the square
        of the normalizing coefficient $\sqrt{c}$, and cdict contains
        key-value pairs (($j$,$k$),$a$), mapping the $X$ and $Y$
        exponents ($j$ and $k$, respectively) onto polynomial term
        coefficients ($a$). The resulting structure can be used to
        compute the wavefront height or slope for arbitrary pupil
        coordinates, or to generate string representations of the
        polynomials.

        Zernike terms are only defined when n and m have the same
        parity (both odd or both even).

        Please see Schwiegerling lecture notes in
        /doc/supporting_docs/ for eqn. references.

        Args:

          n (int): The Zernike order or degree.

          m (int): The azimuthal frequency.

          kind (str): 'h', 'dx', or 'dy', for height, partial x
              derivative (slope) or partial y derivative,
              respectively.

        Returns:

          params (tuple): (c,cdict), with c being the normalizing
              coefficient c and cdict being the map of exponent pairs
              onto inner coefficients.

        """
        absm = np.abs(m)

        # check that n and m are both even or both odd
        if (float(n-absm))%2.0:
            errString = 'zernike._zgen error: ' + \
                'parity of n and m are different; n = %d, m = %d'%(n,m)
            sys.exit(errString)

        # check that n is non-negative:
        if n<0:
            errString = 'zernike._zgen error: ' + \
                'n must be non-negative; n = %d'%n
            sys.exit(errString)

        # $|m|$ must be less than or equal to $n$.
        if abs(m)>n:
            errString = 'zernike._zgen error: ' + \
                '|m| must be less than or equal to n, but n=%d and m=%d.'%(n,m)
            sys.exit(errString)

        # These are the squares of the outer coefficients. It's useful
        # to keep them this way for _convertToString, since we'd
        # prefer to print the $\sqrt{}$ rather than a truncated irrational
        # number.
        if m==0:
            outerCoef = n+1
        else:
            outerCoef = 2*(n+1)
        
        srange = range(int((n-absm)/2+1))

        cdict = {}

        for s in srange:
            jrange = range(int(((n-absm)/2)-s+1))
            for j in jrange:

                # Subtract 1 from absm to determine range,
                # only when m<0.
                if m<0:
                    krange = range(int((absm-1)/2+1))
                else:
                    krange = range(int(absm/2+1))

                for k in krange:
                    # If m==0, k must also be 0;
                    # see eqn. 13c, 19c, and 20c, each of which
                    # only sum over s and j, not k.
                    if m==0:
                        assert(k==0)
                    # For m==0 cases, n/2 is used in coef denominator. Make
                    # sure that n is even, or else n/2 is not well-defined
                    # because n is an integer.
                    if m==0:
                        assert n%2==0
                        
                    # The coefficient for each term in this
                    # polynomial has the format: $$\frac{t1n}{t1d1
                    # t1d2 t1d3} t2 t3$$. These six terms are
                    # computed here.
                    t1n = ((-1)**(s+k))*fact(n-s)
                    t1d1 = fact(s)
                    t1d2 = fact((n + absm)/2-s)
                    t1d3 = fact((n - absm)/2-s)
                    t1 = t1n/(t1d1*t1d2*t1d3)

                    t2 = choose((n - absm)/2 - s, j)
                    t3 = choose(absm, 2*k + (m<0))


                    if kind.lower()=='h':
                        # The (implied) coefficient of the $X^a Y^b$
                        # term at the end of eqns. 13a-c.
                        c = 1 
                        tXexp = n - 2*(s+j+k) - (m<0)
                        tYexp = 2*(j+k) + (m<0)
                        
                    elif kind.lower()=='dx':
                        # The coefficient of the $X^a Y^b$ term at
                        # the end of eqns. 19a-c.
                        c = (n - 2*(s+j+k) - (m<0)) 

                        # Could cacluate explicitly:
                        # $tXexp = X^{(n - 2*(s+j+k)- 1 - (m<0))}$
                        # 
                        # However, piggy-backing on previous
                        # calculation of c speeds things up.
                        tXexp = c - 1
                        tYexp = 2*(j+k) + (m<0)

                    elif kind.lower()=='dy':
                        # The coefficient of the $X^a Y^b$ term at
                        # the end of eqns. 20a-c.
                        c = 2*(j+k) + (m<0)
                        tXexp = n - 2*(s+j+k) - (m<0)
                        tYexp = c - 1

                    ct123 = c*t1*t2*t3
                    # The key for the polynomial dictionary is the pair of X,Y
                    # coefficients.
                    termKey = (tXexp,tYexp)

                    # Leave this term out of the dictionary if its coefficient
                    # is 0.
                    if ct123:
                        # If we already have this term, add to its coefficient.
                        if termKey in cdict:
                            cdict[termKey] = cdict[termKey] + ct123
                        # If not, add it to the dictionary.
                        else:
                            cdict[termKey] = ct123

        # Remove zeros to speed up computations later.
        cdict = {key: value for key, value in cdict.items() if value}

        return (outerCoef,cdict)

    def convert_to_surface(self,params,X,Y,mask=None):
        """Return a phase map specified by a Zernike polynomial.

        This function takes a tuple, consisting of a squared
        normalizing coefficient and dictionary of inner coefficients
        and exponents, provided by zeqn, and x- and y- rectangular
        (Cartesian) coordinates, and produces a phase map.

        This function works by evaluating the polynomial expressed by
        params at each coordinate specified by X and Y.


        Args:

          params (tuple): A pair consisting of an outer coefficient
            $c$ and a dictionary mapping tuples (xexp,yexp) of
            exponents onto the corresponding term coefficients.

          X (float): A scalar, vector, or matrix of X coordinates in unit pupil.

          Y (float): A scalar, vector, or matrix of Y coordinates in unit pupil.

          kind (str): 'h', 'dx', or 'dy', for height, partial x derivative (slope)
              or partial y derivative, respectively.

        Returns:

          float: height, dx, or dy; returned structure same size as X and Y.
        """

        # Check that shapes of X and Y are equal (not necessarily square).
        if not (X.shape[0]==Y.shape[0] and \
                    X.shape[1]==Y.shape[1]):
            errString = 'zernike.getSurface error: ' + \
                'X and Y must have the same shape, but X is %d x %d'%(X.shape[0],X.shape[1]) + \
                'and Y is %d x %d'%(Y.shape[0],Y.shape[1])
            sys.exit(errString)

        if mask is None:
            mask = np.ones(X.shape)

        params = self.zeqn(n,m,kind)
        normalizer = np.sqrt(params[0])

        matrix_out = np.zeros(X.shape)
        

        for item in params[1].items():
            matrix_out = matrix_out + item[1] * X**(item[0][0]) * Y**(item[0][1])

        matrix_out = matrix_out * np.sqrt(normalizer)
        matrix_out = matrix_out * mask

        return matrix_out

    def get_j_surface(self,j,X,Y,kind='h',mask=None):
        n,m = self.j2nm(j)
        return self.get_surface(n,m,X,Y,kind,mask)
    
    def get_surface(self,n,m,X,Y,kind='h',mask=None):
        """Return a phase map specified by a Zernike order and azimuthal frequency.

        Given an order (or degree) n and azimuthal frequency f, and x- and y-
        rectangular (Cartesian) coordinates, produce a phase map of either height,
        partial x derivative, or partial y derivative.

        Zernike terms are only defined when n and m have the same parity (both odd
        or both even).

        The input X and Y values should be located inside a unit pupil, such that
        $$\sqrt{X^2 + Y^2}\leq 1$$

        Please see Schwiegerling lecture notes in /doc/supporting_docs/ for eqn.
        references.

        This function works by calling Zernike.zeqn to calculate the coefficients
        and exponents of the polynomial, and then using the supplied X and Y
        coordinates to produce the height map (or partial derivative).

        Args:

          n (int): The Zernike order or degree.

          m (int): The azimuthal frequency.

          X (float): A scalar, vector, or matrix of X coordinates in unit pupil.

          Y (float): A scalar, vector, or matrix of Y coordinates in unit pupil.

          kind (str): 'h', 'dx', or 'dy', for height, partial x derivative (slope)
              or partial y derivative, respectively.

        Returns:

          float: height, dx, or dy; returned structure same size as X and Y.
        """

        # Check that shapes of X and Y are equal (not necessarily square).
        if not np.all(X.shape==Y.shape):
            errString = 'zernike.getSurface error: ' + \
                'X and Y must have the same shape, but X is %d x %d'%(X.shape[0],X.shape[1]) + \
                'and Y is %d x %d'%(Y.shape[0],Y.shape[1])
            sys.exit(errString)
        

        if mask is None:
            mask = np.ones(X.shape)

        params = self.zeqn(n,m,kind)
        normalizer = np.sqrt(params[0])
        matrix_out = np.zeros(X.shape)
        
        for item in params[1].items():
            matrix_out = matrix_out + item[1] * X**(item[0][0]) * Y**(item[0][1])

        matrix_out = matrix_out * normalizer
        matrix_out = matrix_out * mask

        return matrix_out


class Reconstructor:

    def __init__(self,x,y,mask,regularize=False):
        self.pixel_size = ccfg.pixel_size_m
        self.pupil_size = ccfg.beam_diameter_m
        self.N = ccfg.n_zernike_terms
        
        self.regularize = regularize
        self.mask = mask
        Z = Zernike()
        self.Z = Z

        self.N_orders = self.Z.j2nm(self.N)[0]
        refx = x
        refy = y
        
        # convert refx and refy from pixels to unit pupil
        refx = refx*self.pixel_size/(self.pupil_size/2.0)
        refx = refx-refx.mean()
        refy = refy*self.pixel_size/(self.pupil_size/2.0)
        refy = refy-refy.mean()

        # compute dx and dh for some n,m pairs for first n_terms terms:
        # build these up into matrices for inversion
        dxmat = []
        dymat = []
        hmat = []
        
        for j in range(self.N):
            n,m = Z.j2nm(j)
            h = Z.get_surface(n,m,refx,refy,kind='h')
            dx = Z.get_surface(n,m,refx,refy,kind='dx')
            dy = Z.get_surface(n,m,refx,refy,kind='dy')
            hmat.append(h)
            dxmat.append(dx)
            dymat.append(dy)
            
            if j==4:
                self.defocus_h = h
                self.defocus_dx = dx
                self.defocus_dy = dy
            if j==3:
                self.astig0_h = h
                self.astig0_dx = dx
                self.astig0_dy = dy
            if j==5:
                self.astig1_h = h
                self.astig1_dx = dx
                self.astig1_dy = dy
        
    
        dxmat = np.array(dxmat)
        dymat = np.array(dymat)
        hmat = np.array(hmat)

        if self.regularize:
            A = np.vstack((dxmat.T,dymat.T,np.ones(self.N)))
        else:
            A = np.vstack((dxmat.T,dymat.T))
        
        #why did I originally write it this way?
        #self.matrix = np.dot(np.linalg.pinv(np.dot(A.T,A)),A.T)

        # a matrix for converting slopes into zernike coefficients:
        self.zernike_matrix = np.linalg.pinv(A)

        # it's inverse, a matrix for converting zernikes into slopes:
        self.slope_matrix = A
        
        self.wavefront_matrix = np.array(hmat).T
        self.wavefront = np.zeros(self.mask.shape)
        
    def get_wavefront(self,xslopes,yslopes):
        
        if self.regularize:
            newSlopeRow = np.zeros([1])
            slopes = np.hstack((xslopes,yslopes,newSlopeRow))
        else:
            slopes = np.hstack((xslopes,yslopes))

        coefs = np.dot(self.zernike_matrix,slopes)
        wavefront_vec = np.dot(self.wavefront_matrix,coefs)*(self.pupil_size/2.0)
        error = wavefront_vec.std()
        self.wavefront[np.where(self.mask)] = wavefront_vec
        return coefs,self.wavefront,error


if __name__=='__main__':
    refxy = np.loadtxt('./etc/ref/coords.txt')
    x = refxy[:,0]
    y = refxy[:,1]

    r = Reconstructor(x,y)
