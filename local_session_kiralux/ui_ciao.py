import sys,os
#sys.path.append(os.path.split(__file__)[0])
sys.path.append(os.path.join(os.getcwd(), "..",".."))
import uWFS
import ciao_config as ccfg
from matplotlib import pyplot as plt
import numpy as np
from PyQt5.QtWidgets import QApplication




if ccfg.simulate:
    sim = uWFS.simulator.Simulator()
    sensor = uWFS.sensors.Sensor(sim)
    mirror = sim
else:
    cam = uWFS.cameras.get_camera()
    mirror = uWFS.mirrors.Mirror()
    sensor = uWFS.sensors.Sensor(cam)
    
app = QApplication(sys.argv)
loop = uWFS.loops.Loop(sensor,mirror)
ui = uWFS.ui.UI(loop)
loop.start()
sys.exit(app.exec_())


