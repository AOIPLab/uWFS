import ciao
from matplotlib import pyplot as plt
import numpy as np
import sys
from PyQt5.QtWidgets import QApplication

#cam = ciao.cameras.SimulatedCamera()
#cam = ciao.cameras.PylonCamera()
cam = ciao.cameras.AOCameraAce()
sensor = ciao.sensors.Sensor(cam)

mirror = ciao.mirrors.Mirror()

app = QApplication(sys.argv)
loop = ciao.loops.Loop(sensor,mirror)
ui = ciao.ui.UI(loop)
loop.start()
sys.exit(app.exec_())


