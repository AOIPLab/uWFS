import numpy as np
import glob
import ciao_config as ccfg
import os,sys
try:
    from pypylon import pylon
except Exception as e:
    print(e)

try:
    from ximea import xiapi
except Exception as e:
    print(e)
   
try:
    try:
        # if on Windows, use the provided setup script to add the DLLs folder to the PATH
        from windows_setup import configure_path
        configure_path()
    except ImportError:
        configure_path = None
    
    from thorlabs_tsi_sdk.tl_camera import TLCameraSDK
    from thorlabs_tsi_sdk.tl_camera_enums import SENSOR_TYPE
except Exception as e:
        print(e)

# try:
#     from thorcam.camera import ThorCam
# except Exception as e:
#     print(e)
    

try:
    from pyvcam import pvc
    from pyvcam.camera import Camera
    from pyvcam import constants as const
except Exception as e:
    print(e)

from ctypes import *
from ctypes.util import find_library
from . import milc
from time import time

def get_camera():
    if ccfg.camera_id.lower()=='pylon':
        return PylonCamera()
    elif ccfg.camera_id.lower()=='ace':
        return AOCameraAce()
    elif ccfg.camera_id.lower()=='ximea':
        return XimeaCamera()
    elif ccfg.camera_id.lower()=='thorlabscam':
        return TLCamera()
    elif ccfg.camera_id.lower()=='pvcam':
        return PVCam()
    else:
        return SimulatedCamera()

class PVCam:
    def __init__(self,timeout=500):
        pvc.init_pvcam()
        self.cam = [cam for cam in Camera.detect_camera()][0]
        self.cam.open()
        self.cam.speed_table_index = 0
    
    def get_exposure(self):
        return self.cam.exp_time

    def set_exposure(self,exposure_us):
        self.cam.exp_time = exposure_us/1000
        
    def get_image(self):
        frame = self.cam.get_frame().reshape(self.cam.sensor_size[::-1])
        return frame
    
    def close(self):
        iself.cam.close()
        pvc.uninit_pvcam()



# class MyThorcam(ThorCam):
#     def __init__(self,timeout=500):
#         self.sdk = TLCameraSDK()
#         cameralist = self.sdk.discover_available_cameras()
#         if len(cameralist) == 0:
#             print("Error: no cameras detected!")

#         self.camera = self.sdk.open_camera(cameralist[0])
#         #  setup the camera for continuous acquisition
#         self.camera.frames_per_trigger_zero_for_unlimited = 0
#         self.camera.image_poll_timeout_ms = 2000  # 2 second timeout
#         self.camera.arm(2)
#         self.camera.exposure_time_us = ccfg.camera_exposure_us #5000

#         # save these values to place in our custom TIFF tags later
#         bit_depth = self.camera.bit_depth
#         exposure = self.camera.exposure_time_us

#         # need to save the image width and height for color processing
#         image_width = self.camera.image_width_pixels
#         image_height = self.camera.image_height_pixels
#         print(image_width)
#         print(image_height)
#         self.image = None
    
#     def get_image(self):
#         self.camera.issue_software_trigger()
#         frame = self.camera.get_pending_frame_or_null()
#         #self.image = frame.image_buffer
#         self.image = frame.image_buffer.astype(np.int16)
#         return self.image
        


#     def close(self):
#         self.camera.disarm()
#         return

#     def set_exposure(self,exposure_us):
#         self.camera.exposure_time_us = exposure_us
#         return

#     def get_exposure(self):
#         return self.camera.exposure_time_us
    
#     def received_camera_response(self, msg, value):
#         super(MyThorCam, self).received_camera_response(msg, value)
#         if msg == 'image':
#             return
#         print('Received "{}" with value "{}"'.format(msg, value))
#     def got_image(self, image, count, queued_count, t):
#         print('Received image "{}" with time "{}" and counts "{}", "{}"'
#               .format(image, t, count, queued_count))


class TLCamera:
    def __init__(self,timeout=500):
        self.sdk = TLCameraSDK()
        cameralist = self.sdk.discover_available_cameras()
        if len(cameralist) == 0:
            print("Error: no cameras detected!")

        self.camera = self.sdk.open_camera(cameralist[0])
        #  setup the camera for continuous acquisition
        self.camera.frames_per_trigger_zero_for_unlimited = 0
        self.camera.image_poll_timeout_ms = 2000  # 2 second timeout
        self.camera.arm(2)
        self.camera.exposure_time_us = ccfg.camera_exposure_us #5000

        # save these values to place in our custom TIFF tags later
        bit_depth = self.camera.bit_depth
        exposure = self.camera.exposure_time_us

        # need to save the image width and height for color processing
        image_width = self.camera.image_width_pixels
        image_height = self.camera.image_height_pixels
        print(image_width)
        print(image_height)
        self.image = None
    
    def get_image(self):
        self.camera.issue_software_trigger()
        frame = self.camera.get_pending_frame_or_null()
        #self.image = frame.image_buffer
        self.image = frame.image_buffer.astype(np.int16)
        return self.image
        


    def close(self):
        self.camera.disarm()
        return

    def set_exposure(self,exposure_us):
        self.camera.exposure_time_us = exposure_us
        return

    def get_exposure(self):
        return self.camera.exposure_time_us

class PylonCamera:

    def __init__(self,timeout=500):
        self.camera = pylon.InstantCamera(
            pylon.TlFactory.GetInstance().CreateFirstDevice())

        self.camera.Open()

        # enable all chunks
        self.camera.ChunkModeActive = True
        #self.camera.PixelFormat = "Mono12"
        
        for cf in self.camera.ChunkSelector.Symbolics:
            self.camera.ChunkSelector = cf
            self.camera.ChunkEnable = True

        self.timeout = timeout
        self.image = None

    def get_image(self):
        self.image = self.camera.GrabOne(self.timeout).Array.astype(np.int16)
        return self.image
    
    def close(self):
        return

    def set_exposure(self,exposure_us):
        return
        
    def get_exposure(self):
        return 10000
    

class XimeaCamera:

    def __init__(self,timeout=500):
        self.camera = xiapi.Camera()
        self.camera.open_device()
        try:
            self.set_exposure(ccfg.camera_exposure_us)
        except AttributeError as ae:
            print(ae)
            print("ciao_config.py is missing an entry for exposure time; please put 'camera_exposure_us = 1000' or similar into the ciao_config.py file for your session")
            sys.exit()
        self.camera.start_acquisition()
        self.img = xiapi.Image()
        self.image = None

    def get_image(self):
        self.camera.get_image(self.img)
        self.image = np.reshape(np.frombuffer(self.img.get_image_data_raw(),dtype=np.uint8),
                          (self.img.height,self.img.width)).astype(np.int16)
        return self.image
    
    def close(self):
        self.camera.stop_acquisition()
        self.camera.close_device()
        
    def set_exposure(self,exposure_us):
        print(exposure_us)
        self.camera.set_exposure(exposure_us)
        
    def get_exposure(self):
        return self.camera.get_exposure()

class SimulatedCamera:

    def __init__(self):
        self.image_list = sorted(glob.glob(os.path.join(ccfg.simulated_camera_image_directory,'*.npy')))
        self.n_images = len(self.image_list)
        self.index = 0
        #self.images = [np.load(fn) for fn in self.image_list]
        self.opacity = False
        self.sy,self.sx = np.load(self.image_list[0]).shape
        self.oy = int(round(np.random.rand()*self.sy//2+self.sy//4))
        self.ox = int(round(np.random.rand()*self.sx//2+self.sx//4))
        self.XX,self.YY = np.meshgrid(np.arange(self.sx),np.arange(self.sy))
        self.image = None

    def set_opacity(self,val):
        self.opacity = val

    def get_opacity(self):
        return self.opacity
            
    def get_image(self):
        im = np.load(self.image_list[self.index])
        #im = self.images[self.index]

        if self.opacity:
            im = self.opacify(im)
            self.oy = self.oy+np.random.randn()*.5
            self.ox = self.ox+np.random.randn()*.5

        self.index = (self.index + 1)%self.n_images
        self.image = im
        return self.image
        
    
    def opacify(self,im,sigma=50):
        xx,yy = self.XX-self.ox,self.YY-self.oy
        d = np.sqrt(xx**2+yy**2)
        #mask = np.exp((-d)/(2*sigma**2))
        #mask = mask/mask.max()
        #mask = 1-mask
        mask = np.ones(d.shape)
        mask[np.where(d<=sigma)] = 0.2
        out = np.round(im*mask).astype(np.int16)
        return out
        
    def close(self):
        return

    def set_exposure(self,exposure_us):
        return
        
    def get_exposure(self):
        return 10000
        

class AOCameraAce():

    _MilImage0 = c_longlong(0)
    _MilImage1 = c_longlong(0)
    #_InitFlag = c_longlong(milc.M_PARTIAL)
    #_InitFlagD = c_longlong(milc.M_DEFAULT)


    _MilApplication = c_longlong()
    _MilSystem = c_longlong()
    _MilDigitizer = c_longlong()
    _MilImage0 = c_longlong()
    _MilImage1 = c_longlong()

    
    def __init__(self):
    
        if sys.platform=='win32':
            self._mil = windll.LoadLibrary("mil")
        else:
            sys.exit('pyao.cameras assumes Windows DLL shared libraries')
            
        self._cameraFilename = os.path.join(ccfg.dcf_directory,'acA2040-180km-4tap-12bit_reloaded.dcf')

        # a quick fix to a deep problem; force mode 0; it slows things down a bit
        # but guards against the memory management issue
        self._mode = 2

        self._mil.MappAllocW.argtypes = [c_longlong, POINTER(c_longlong)] 
        self._mil.MsysAllocW.argtypes = [c_wchar_p, c_longlong, c_longlong, POINTER(c_longlong)]
        self._mil.MdigAllocW.argtypes = [c_longlong, c_longlong, c_wchar_p, c_longlong, POINTER(c_longlong)]
        self._mil.MbufAllocColor.argtypes = [c_longlong, c_longlong, c_longlong, c_longlong, c_longlong, c_longlong, POINTER(c_longlong)]

        self._mil.MappAllocW(self._InitFlag,byref(self._MilApplication))
        self.printMilError()
        print('MIL App Identifier: %d'%self._MilApplication.value)

        cSystemName = c_wchar_p('M_SYSTEM_SOLIOS')
        self._mil.MsysAllocW(cSystemName, milc.M_DEFAULT, 
                           self._InitFlag, byref(self._MilSystem))
        self.printMilError()
        print('MIL Sys Identifier: %d'%self._MilSystem.value)

        
        cDcfFn = c_wchar_p(self._cameraFilename)

        self._mil.MdigAllocW(self._MilSystem, milc.M_DEFAULT, cDcfFn, milc.M_DEFAULT, byref(self._MilDigitizer))
        self.printMilError()
        print('MIL Dig Identifier: %d'%self._MilDigitizer.value)

        nBands = c_longlong(1)
        bufferType = c_longlong(milc.M_SIGNED + 16)
        bufferAttribute = c_longlong(milc.M_GRAB + milc.M_IMAGE)
        
        binning = 1
        self.n_sig = 10
        self._xSizePx = 2048
        self._ySizePx = 2048
        #print binning
        #sys.exit()

        if self._mode==0: # double buffer / continuous grab
            self._mil.MbufAllocColor(self._MilSystem, nBands, self._xSizePx, self._ySizePx, bufferType, bufferAttribute, byref(self._MilImage0))
            self._mil.MbufAllocColor(self._MilSystem, nBands, self._xSizePx, self._ySizePx, bufferType, bufferAttribute, byref(self._MilImage1))
            self.printMilError()
            print('MIL Img Identifiers: %d,%d'%(self._MilImage0.value, self._MilImage1.value), self._mode)
            self._mil.MdigGrabContinuous(self._MilDigitizer,self._MilImage0)
            self.printMilError()
        elif self._mode==1: # double buffer / single grabs
            self._mil.MbufAllocColor(self._MilSystem, nBands, self._xSizePx, self._ySizePx, bufferType, bufferAttribute, byref(self._MilImage0))
            self._mil.MbufAllocColor(self._MilSystem, nBands, self._xSizePx, self._ySizePx, bufferType, bufferAttribute, byref(self._MilImage1))
            self.printMilError()
            print('MIL Img Identifiers: %d,%d'%(self._MilImage0.value, self._MilImage1.value), self._mode)
            self._mil.MdigControlInt64(self._MilDigitizer,milc.M_GRAB_MODE,milc.M_SYNCHRONOUS)
            self._mil.MdigGrab(self._MilDigitizer,self._MilImage0)
        elif self._mode==2: # single buffer / single grabs
            self._mil.MbufAllocColor(self._MilSystem, nBands, self._xSizePx, self._ySizePx, bufferType, bufferAttribute, byref(self._MilImage0))
            self.printMilError()
            print('MIL Img Identifiers: %d,%d'%(self._MilImage0.value, self._MilImage1.value), self._mode)
            # changing the GRAB_MODE from ASYNCHRONOUS to SYNCHRONOUS seemed to improve the slope responses during the poke matrix
            # acquisition
            self._mil.MdigControlInt64(self._MilDigitizer,milc.M_GRAB_MODE,milc.M_SYNCHRONOUS)
            self._mil.MdigGrab(self._MilDigitizer,self._MilImage0)
            
        self._im = np.zeros([np.int16(self._ySizePx),np.int16(self._xSizePx)]).astype(np.int16)
        self._im_ptr = self._im.ctypes.data


        

        # there must be a bug in camera initialization code above because if the camera has been
        # sitting, on, for a while, the first few frames (up to 3, anecdotally) may have serious
        # geometry problems (via, it seems, tap reordering). A quick and dirty fix: grab a few images
        # upon initialization:
        nBad = 5
        for iBad in range(nBad):
            bad = self.getImage()


    def close(self):
        print('Closing camera...')
        self._mil.MdigHalt(self._MilDigitizer)
        self.printMilError()
        self._mil.MbufFree(self._MilImage0)
        self.printMilError()
        self._mil.MbufFree(self._MilImage1)
        self.printMilError()
        self._mil.MdigFree(self._MilDigitizer)
        self.printMilError()
        self._mil.MsysFree(self._MilSystem)
        self.printMilError()
        self._mil.MappFree(self._MilApplication)

    def getSignature(self):
        N = self.n_sig
        return '_'.join(['%d'%p for p in [self._im[500,50+k] for k in range(N)]])
        
    def getImage(self):
        self.updateImage()
        return self._im
        
    def get_image(self):
        return self.getImage()
        
    def updateImage(self):
        t0 = time()
        sig = self.getSignature()
        done = False
        count = 0
        while not done:
            #print 'wait count',count,'pixels',self._im[200,200:205]
            if self._mode==0:
                # sleeping does work here (100 ms)
                #self._mil.MdigGrabWait(self._MilDigitizer, milc.M_GRAB_FRAME_END );
                # sleeping does work here (100 ms)
                self._mil.MbufCopy(self._MilImage0,self._MilImage1)
                # sleeping doesn't work here (100 ms)
                self._mil.MbufGet(self._MilImage1,self._im_ptr)
            elif self._mode==1:
                self._mil.MdigGrabWait(self._MilDigitizer, milc.M_GRAB_FRAME_END )
                self._mil.MbufCopy(self._MilImage0,self._MilImage1)
                self._mil.MdigGrab(self._MilDigitizer,self._MilImage0)
                self._mil.MbufGet(self._MilImage1,self._im_ptr)
            elif self._mode==2:
                #t1 = time()
                self._mil.MdigGrabWait(self._MilDigitizer, milc.M_GRAB_FRAME_END )
                #t2 = time()
                #print 'MdigGrabWait took %0.4f s'%(t2-t1)
                self._mil.MdigGrab(self._MilDigitizer,self._MilImage0)
                self._mil.MbufGet(self._MilImage0,self._im_ptr)
            new_sig = self.getSignature()
            done = (not sig==new_sig) or (new_sig==('0_'*self.n_sig)[:-1])
            count+=1
        t1 = time()
            
    def printMilError(self):
        err = c_longlong(0)
        self._mil.MappGetError(2,byref(err))
        print('MIL Error Code: %d'%err.value)
    
    def set_exposure(self,exposure_us):
        return
        
    def get_exposure(self):
        return 10000

