import numpy as np
cimport numpy as np
from matplotlib import pyplot as plt
import cython
from cython.parallel import prange
ctypedef np.uint16_t uint16_t

# this function takes the following arguments:
# 1. spots_image (int array): the spots image
# 2. sb_x_vec (float array): the x coordinates of search box centers
# 3. sb_y_vec (float array): the y coordinates of search box centers
# 4. sb_width (integer): the width of the search box (inclusive),
#    which should be an odd integer
# 5. iterations (integer): the number of centroid iterations, in
#    which the search boxes are recentered about the
#    previous center of mass measurement
# 6. iteration_step_px (integer): the number of pixels by which
#    to reduce the search box half-width on each iteration
# 7. x_out (float array): an array in which to store the
#    resulting x coordinates of centers of mass
# 8. y_out (float array): an array in which to store the
#    resulting y coordinates of centers of mass
# 9. mean_intensity (float array): an array in which to store each
#    search box's mean intensity
# 10. maximum_intensity (float array): (ditto)
# 11. minimum_intensity (float array): (ditto)
# 12. background_intensity (float array): (ditto)
# 13. estimate_background (boolean): should the algorithm try to
#     estimate the background intensity by looking at the edges of
#     each box; this is an implementation of so-called "adaptive"
#     thresholding
# 14. additional_background_correction (float): added to spots image
#     before computing centers of mass; should be negative to do
#     extra background subtraction.
# 15. modify_spots_image (boolean): should the spots image be modified
#     in place (so, e.g., the the background subtraction step is visible
#     in the UI. Use caution--if you want to save raw spots images in
#     the loop, it must be done before computing centroids, otherwise
#     the artifacts of background subtraction (dark search boxes with
#     a bright grid between them) will be visible.



@cython.boundscheck(False)
@cython.wraparound(False)
cpdef compute_centroids(np.ndarray[np.int16_t,ndim=2] spots_image,
                        np.ndarray[np.int16_t,ndim=1] sb_x1_vec,
                        np.ndarray[np.int16_t,ndim=1] sb_x2_vec,
                        np.ndarray[np.int16_t,ndim=1] sb_y1_vec,
                        np.ndarray[np.int16_t,ndim=1] sb_y2_vec,
                        np.ndarray[np.float_t,ndim=1] x_out,
                        np.ndarray[np.float_t,ndim=1] y_out,
                        np.ndarray[np.float_t,ndim=1] mean_intensity,
                        np.ndarray[np.float_t,ndim=1] maximum_intensity,
                        np.ndarray[np.float_t,ndim=1] minimum_intensity,
                        np.ndarray[np.float_t,ndim=1] background_intensity,
                        estimate_background = True,
                        additional_background_correction = 0.0,
                        num_threads = 4,
                        modify_spots_image = False):

    cdef np.int_t n_spots = len(sb_x1_vec)
    cdef np.int_t k
    cdef np.int_t num_threads_t = int(num_threads)
    cdef np.float_t intensity
    cdef np.float_t background
    cdef np.float_t xprod
    cdef np.float_t yprod
    cdef np.int_t x
    cdef np.int_t y
    cdef np.float_t imax
    cdef np.float_t imin
    cdef np.float_t pixel
    cdef np.float_t edge_counter
    cdef np.int_t estimate_background_t
    cdef np.int_t modify_spots_image_t
    cdef np.float_t additional_background_correction_t
    cdef np.float_t counter

    # if modify_spots_image:
    #     modify_spots_image_t = 1
    # else:
    #     modify_spots_image_t = 0
    
    # if estimate_background:
    #     estimate_background_t = 1
    # else:
    #     estimate_background_t = 0

    modify_spots_image_t = int(modify_spots_image)
    estimate_background_t = int(estimate_background)

    additional_background_correction_t = float(additional_background_correction)
    num_threads_t = int(num_threads)
    
    #for k in prange(n_spots,nogil=True,num_threads=num_threads_t):
    for k in range(n_spots):
        if estimate_background_t:
            edge_counter = 0.0
            background = 0.0
            for x in range(sb_x1_vec[k],sb_x2_vec[k]+1):
                pixel = float(spots_image[sb_y1_vec[k],x])
                background = background + pixel
                edge_counter = edge_counter + 1
                pixel = float(spots_image[sb_y2_vec[k],x])
                background = background + pixel
                edge_counter = edge_counter + 1
            for y in range(sb_y1_vec[k]+1,sb_y2_vec[k]):
                pixel = float(spots_image[y,sb_x1_vec[k]])
                background = background + pixel
                edge_counter = edge_counter + 1
                pixel = float(spots_image[y,sb_x1_vec[k]])
                background = background + pixel
                edge_counter = edge_counter + 1
            background = background/edge_counter
        else:
            background = 0.0
        intensity = 0.0
        xprod = 0.0
        yprod = 0.0
        imin = 2**15
        imax = -2**15
        for x in range(sb_x1_vec[k],sb_x2_vec[k]+1):
            for y in range(sb_y1_vec[k],sb_y2_vec[k]+1):
                pixel = float(spots_image[y,x])-(background+additional_background_correction_t)
                if pixel<0.0:
                    pixel = 0.0
                if modify_spots_image_t:
                    spots_image[y,x] = <np.int_t>pixel
                xprod = xprod + pixel*x
                yprod = yprod + pixel*y
                intensity = intensity + pixel
                if pixel<imin:
                    imin=pixel
                if pixel>imax:
                    imax=pixel
                counter = counter + 1.0

        if xprod==0 or yprod==0:
            print 'Warning: search box intensity low; skipping. Check additional_background_correction.'
            continue
        mean_intensity[k] = intensity/counter
        background_intensity[k] = background
        maximum_intensity[k] = imax
        minimum_intensity[k] = imin
        if intensity==0.0:
            intensity = 1.0
        x_out[k] = xprod/intensity
        y_out[k] = yprod/intensity
    return x_out,y_out
