import sys,os
#sys.path.append(os.path.split(__file__)[0])
sys.path.append(os.path.join(os.getcwd(), "..",".."))
import ciaoPy3
from matplotlib import pyplot as plt
import numpy as np
import sys
from PyQt5.QtWidgets import QApplication

mirror = ciaoPy3.mirrors.Mirror()
app = QApplication(sys.argv)
ui = ciaoPy3.ui.MirrorUI(mirror)
sys.exit(app.exec_())


