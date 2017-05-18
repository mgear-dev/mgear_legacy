# MGEAR is under the terms of the MIT License

# Copyright (c) 2016 Jeremie Passerin, Miquel Campos

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Author:     Jeremie Passerin      geerem@hotmail.com  www.jeremiepasserin.com
# Author:     Miquel Campos         hello@miquel-campos.com  www.miquel-campos.com
# Date:       2016 / 10 / 10

#############################################
# GLOBAL
#############################################
from functools import partial
# pyMel
import pymel.core as pm

# mgear
from mgear.maya.shifter.component.guide import ComponentGuide
import mgear.maya.transform as tra

#Pyside
from mgear.maya.shifter.component.guide import componentMainSettings
import mgear.maya.pyqt as gqt
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from maya.app.general.mayaMixin import MayaQDockWidget
import maya.OpenMayaUI as omui
QtGui, QtCore, QtWidgets, wrapInstance = gqt.qt_import()
import settingsUI as sui

# guide info
AUTHOR = "Jeremie Passerin, Miquel Campos"
URL = "www.jeremiepasserin.com, www.miquel-campos.com"
EMAIL = "geerem@hotmail.com, hello@miquel-campos.com"
VERSION = [1,0,0]
TYPE = "foot_bk_01"
NAME = "foot"
DESCRIPTION = "Foot with reversed controllers to control foot roll."

##########################################################
# CLASS
##########################################################
class Guide(ComponentGuide):

    compType = TYPE
    compName = NAME
    description = DESCRIPTION

    author = AUTHOR
    url = URL
    email = EMAIL
    version = VERSION

    connectors = ["leg_2jnt_01", "leg_ms_2jnt_01", "leg_3jnt_01"]

    # =====================================================
    ##
    # @param self
    def postInit(self):
        self.save_transform = ["root", "#_loc", "heel", "outpivot", "inpivot"]
        self.addMinMax("#_loc", 1, -1)

    # =====================================================
    ## Add more object to the object definition list.
    # @param self
    def addObjects(self):

        self.root = self.addRoot()
        self.locs = self.addLocMulti("#_loc", self.root)

        centers = [self.root]
        centers.extend(self.locs)
        self.dispcrv = self.addDispCurve("crv", centers)

        # Heel and pivots
        vTemp = tra.getOffsetPosition( self.root, [0,-1,-1])
        self.heel = self.addLoc("heel", self.root, vTemp)
        vTemp = tra.getOffsetPosition( self.root, [1,-1,-1])
        self.outpivot = self.addLoc("outpivot", self.root, vTemp)
        vTemp = tra.getOffsetPosition( self.root, [-1,-1,-1])
        self.inpivot = self.addLoc("inpivot", self.root, vTemp)

        self.dispcrv = self.addDispCurve("1", [self.root, self.heel, self.outpivot, self.heel, self.inpivot])

    # =====================================================
    ## Add more parameter to the parameter definition list.
    # @param self
    def addParameters(self):

        # self.pRoll = self.addParam("roll", "long", 0, 0, 1)
        self.pRoll       = self.addParam("useRollCtl", "bool", True)
        self.pUseIndex       = self.addParam("useIndex", "bool", False)
        self.pParentJointIndex = self.addParam("parentJointIndex", "long", -1, None, None)


##########################################################
# Setting Page
##########################################################

class settingsTab(QtWidgets.QDialog, sui.Ui_Form):

    def __init__(self, parent=None):
        super(settingsTab, self).__init__(parent)
        self.setupUi(self)


class componentSettings(MayaQWidgetDockableMixin, componentMainSettings):

    def __init__(self, parent = None):
        self.toolName = TYPE
        # Delete old instances of the componet settings window.
        gqt.deleteInstances(self, MayaQDockWidget)

        super(self.__class__, self).__init__(parent = parent)
        self.settingsTab = settingsTab()


        self.setup_componentSettingWindow()
        self.create_componentControls()
        self.populate_componentControls()
        self.create_componentLayout()
        self.create_componentConnections()

    def setup_componentSettingWindow(self):
        self.mayaMainWindow = gqt.maya_main_window()

        self.setObjectName(self.toolName)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle(TYPE)
        self.resize(280, 350)

    def create_componentControls(self):
        return
        

    def populate_componentControls(self):
        """
        Populate the controls values from the custom attributes of the component.

        """
        #populate tab
        self.tabs.insertTab(1, self.settingsTab, "Component Settings")

        #populate component settings
        self.populateCheck(self.settingsTab.useRollCtl_checkBox, "useRollCtl")

        #populate connections in main settings
        for cnx in Guide.connectors:
            self.mainSettingsTab.connector_comboBox.addItem(cnx)
        self.connector_items = [ self.mainSettingsTab.connector_comboBox.itemText(i) for i in range( self.mainSettingsTab.connector_comboBox.count())]
        currentConnector = self.root.attr("connector").get()
        if currentConnector not in self.connector_items:
            self.mainSettingsTab.connector_comboBox.addItem(currentConnector)
            self.connector_items.append(currentConnector)
            pm.displayWarning("The current connector: %s, is not a valid connector for this component. Build will Fail!!")
        comboIndex = self.connector_items.index(currentConnector)
        self.mainSettingsTab.connector_comboBox.setCurrentIndex(comboIndex)


    def create_componentLayout(self):

        self.settings_layout = QtWidgets.QVBoxLayout()
        self.settings_layout.addWidget(self.tabs)
        self.settings_layout.addWidget(self.close_button)

        self.setLayout(self.settings_layout)

    def create_componentConnections(self):

        self.settingsTab.useRollCtl_checkBox.stateChanged.connect(partial(self.updateCheck, self.settingsTab.useRollCtl_checkBox, "neutralpose"))
        self.mainSettingsTab.connector_comboBox.currentIndexChanged.connect(partial(self.updateConnector, self.mainSettingsTab.connector_comboBox, self.connector_items) )


    def dockCloseEventTriggered(self):
        gqt.deleteInstances(self, MayaQDockWidget)