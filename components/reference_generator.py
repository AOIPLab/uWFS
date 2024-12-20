import numpy as np
import ciao_config as ccfg
import os,sys
from .tools import now_string

class ReferenceGenerator:
    def __init__(self,camera,mask,x_offset=0.0,y_offset=0.0,spot_half_width=5,window_spots=False):
        self.cam = camera
        sensor_x = ccfg.image_width_px
        sensor_y = ccfg.image_height_px
        lenslet_pitch = ccfg.lenslet_pitch_m
        pixel_size = ccfg.pixel_size_m
        stride = lenslet_pitch/pixel_size
        my,mx = mask.shape
        xvec = np.arange(stride/2.0,mx*stride,stride)+x_offset
        yvec = np.arange(stride/2.0,my*stride,stride)+y_offset
        ref_xy = []
        for y in range(my):
            for x in range(mx):
                if mask[y,x]:
                    ref_xy.append((xvec[x],yvec[y]))
        self.xy = np.array(ref_xy)
        self.x_ref = self.xy[:,0]
        self.y_ref = self.xy[:,1]
        
        sim = np.zeros((ccfg.image_height_px,ccfg.image_width_px))
        for x,y in zip(self.x_ref,self.y_ref):
            ry,rx = int(round(y)),int(round(x))
            sim[ry-spot_half_width:ry+spot_half_width+1,
                rx-spot_half_width:rx+spot_half_width+1] = 1.0

        N = 10
        spots = self.cam.get_image().astype(np.float)
        for k in range(N-1):
            spots = spots + self.cam.get_image()
        spots = spots/np.float(N)
        
        if window_spots:
            sy,sx = sim.shape
            XX,YY = np.meshgrid(np.arange(sx),np.arange(sy))
            xcom = np.sum(spots*XX)/np.sum(spots)
            ycom = np.sum(spots*YY)/np.sum(spots)
            XX = XX-xcom
            YY = YY-ycom
            d = np.sqrt(XX**2+YY**2)
            sigma = ccfg.image_width_px//2
            g = np.exp((-d**2)/(2*sigma**2))
            spots = spots*g
        
        # cross-correlate it with a spots image to find the most likely offset
        nxc = np.abs(np.fft.ifft2(np.fft.fft2(spots)*np.conj(np.fft.fft2(sim))))

        sy,sx = nxc.shape
        ymax,xmax = np.unravel_index(np.argmax(nxc),nxc.shape)
        if ymax>sy//2:
            ymax = ymax-sy
        if xmax>sx//2:
            xmax = xmax-sx
        
        new_x_ref = self.x_ref+xmax
        new_y_ref = self.y_ref+ymax

        self.xy = np.vstack((new_x_ref,new_y_ref)).T
        
    def make_coords(self):
        outfn = os.path.join(ccfg.reference_directory,'%s_coords.txt'%now_string())
        print('Reference coordinates saved in %s'%outfn)
        print('Please add the following line to config.py:')
        print("reference_coordinates_filename = '%s'"%outfn)
        np.savetxt(outfn,self.xy)
        
