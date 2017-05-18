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

##################################################
# GLOBAL
##################################################
import mgear.maya.pyqt as gqt
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from maya.app.general.mayaMixin import MayaQDockWidget
QtGui, QtCore, QtWidgets, wrapInstance = gqt.qt_import()

import mgear.maya.synoptic.utils as syn_uti


##################################################
# PROMOTED WIDGETS
##################################################
# They must be declared first because they are used in the widget.ui

class toggleCombo(QtWidgets.QComboBox):

    def __init__(self, parent=None):
        super(toggleCombo, self).__init__(parent)
        self.firstUpdate = False

        self.currentIndexChanged['QString'].connect(self.handleChanged)

        
    def wheelEvent (self, event):
        event.ignore()


    # def focusInEvent(self, event):
    def enterEvent(self, event):
        self.model = syn_uti.getModel(self)
        self.uihost_name = str(self.property("Object"))
        self.combo_attr = str(self.property("Attr"))
        self.ctl_name = str(self.property("ik_ctl"))
        if not self.currentText():
            list1 = syn_uti.getComboKeys( self.model, self.uihost_name, self.combo_attr)
            self.addItems(list1)

        self.setCurrentIndex(syn_uti.getComboIndex( self.model, self.uihost_name, self.combo_attr))
        self.firstUpdate = True 

    def handleChanged(self):
        if self.firstUpdate:
            if self.currentIndex() == self.count() -1:
                print "Space Transfer"
                self.setCurrentIndex(syn_uti.getComboIndex( self.model, self.uihost_name, self.combo_attr))
                # self.setCurrentIndex(0)
                syn_uti.ParentSpaceTransfer.showUI(self, self.model, self.uihost_name, self.combo_attr, self.ctl_name)

            else:
                syn_uti.changeSpace(self.model, self.uihost_name, self.combo_attr, self.currentIndex(), self.ctl_name)

class bakeMocap(QtWidgets.QPushButton):

    def mousePressEvent(self, event):

        model = syn_uti.getModel(self)
        syn_uti.bakeMocap(model)


class ikfkMatchButton(QtWidgets.QPushButton):

    MAXIMUM_TRY_FOR_SEARCHING_FK = 1000

    def __init__(self, *args, **kwargs):
        # type: (*str, **str) -> None
        super(ikfkMatchButton, self).__init__(*args, **kwargs)
        self.numFkControllers = None

    def searchNumberOfFkControllers(self):
        # type: () -> None

        for i in range(self.MAXIMUM_TRY_FOR_SEARCHING_FK):
            prop = self.property("fk{0}".format(str(i)))
            if not prop:
                self.numFkControllers = i
                break

    def mousePressEvent(self, event):
        # type: (QtCore.QEvent) -> None

        mouse_button = event.button()

        model = syn_uti.getModel(self)
        ikfk_attr = str(self.property("ikfk_attr"))
        uiHost_name = str(self.property("uiHost_name"))

        if not self.numFkControllers:
            self.searchNumberOfFkControllers()

        fks = []
        for i in range(self.numFkControllers):
            label = "fk{0}".format(str(i))
            prop = str(self.property(label))
            fks.append(prop)

        ik = str(self.property("ik"))
        upv = str(self.property("upv"))

        if mouse_button == QtCore.Qt.RightButton:
            syn_uti.IkFkTransfer.showUI(model, ikfk_attr, uiHost_name, fks, ik, upv)
            return

        else:
            syn_uti.ikFkMatch(model, ikfk_attr, uiHost_name, fks, ik, upv)
            return


class toggleAttrButton(QtWidgets.QPushButton):

    def mousePressEvent(self, event):

        model = syn_uti.getModel(self)
        object_name = str(self.property("Object"))
        attr_name = str(self.property("Attr"))
        mouse_button = event.button()

        syn_uti.toggleAttr(model, object_name, attr_name)


class resetTransform(QtWidgets.QPushButton):

    def mousePressEvent(self, event):
        mouse_button = event.button()
        syn_uti.resetSelTrans()


class resetBindPose(QtWidgets.QPushButton):

    def mousePressEvent(self, event):

        model = syn_uti.getModel(self)
        mouse_button = event.button()

        syn_uti.bindPose(model)

class MirrorPoseButton(QtWidgets.QPushButton):

    def mousePressEvent(self, event):

        mouse_button = event.button()
        syn_uti.mirrorPose()

class FlipPoseButton(QtWidgets.QPushButton):

    def mousePressEvent(self, event):

        mouse_button = event.button()
        syn_uti.mirrorPose(True)

class QuickSelButton(QtWidgets.QPushButton):

    def mousePressEvent(self, event):

        model = syn_uti.getModel(self)
        channel = str(self.property("channel"))
        mouse_button = event.button()

        syn_uti.quickSel(model, channel, mouse_button)

class SelectButton(QtWidgets.QWidget):
    over = False
    color_over = QtGui.QColor(255, 255, 255, 255)

    def __init__(self, parent=None):
        super(SelectButton, self).__init__(parent)
        self.defaultBGColor = QtGui.QPalette().color(self.backgroundRole())
        self.setBorderColor(self.defaultBGColor)
        p = self.palette()
        p.setColor(self.foregroundRole(), QtGui.QColor(000, 000, 000, 000))
        p.setColor(self.backgroundRole(), QtGui.QColor(000, 000, 000, 000))
        self.setPalette(p)


    def enterEvent(self, event):
        self.over = True
        self.repaint()
        self.update()

    def leaveEvent(self, event):
        self.over = False
        self.repaint()
        self.update()

    def rectangleSelection(self,event, firstLoop):
        if firstLoop:
            key_modifier = event.modifiers()
        else:
            key_modifier = QtCore.Qt.ShiftModifier
        model = syn_uti.getModel(self)
        object = str(self.property("object")).split(",")

        mouse_button = event.button()
        syn_uti.selectObj(model, object, mouse_button, key_modifier)

    def mousePressEvent(self, event):

        model = syn_uti.getModel(self)
        object = str(self.property("object")).split(",")
        mouse_button = event.button()
        key_modifier = event.modifiers()

        syn_uti.selectObj(model, object, mouse_button, key_modifier)

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        if self.over:
            painter.setBrush(self.color_over)
        else:
            painter.setBrush(self.color)
        self.drawShape(painter)
        painter.end()

    def paintSelected(self, paint=False):
        if paint:
            p = self.palette()
            p.setColor(self.foregroundRole(),QtGui.QColor(255, 255, 255, 255))
            self.setPalette(p)
            self.setBorderColor(QtGui.QColor(255, 255, 255, 255))
        else:
            p = self.palette()
            p.setColor(self.foregroundRole(),QtGui.QColor(000, 000, 000, 010))
            self.setPalette(p)
            self.setBorderColor(self.defaultBGColor)

    def setBorderColor(self, color):
        self.borderColor = color

    def drawPathWithBorder(self, painter, path, borderWidth):
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        pen = QtGui.QPen(self.borderColor, borderWidth)
        painter.setPen(pen)
        painter.fillPath(path, QtCore.Qt.red)
        painter.drawPath(path)


##############################################################################
# Classes for Mixin Color
##############################################################################
class SelectBtn_RFk(SelectButton):
    color = QtGui.QColor(0, 0, 192, 255)

class SelectBtn_RIk(SelectButton):
    color = QtGui.QColor(0, 128, 192, 255)

class SelectBtn_CFk(SelectButton):
    color = QtGui.QColor(128, 0, 128, 255)

class SelectBtn_CIk(SelectButton):
    color = QtGui.QColor(192, 64, 192, 255)

class SelectBtn_LFk(SelectButton):
    color = QtGui.QColor(192, 0, 0, 255)

class SelectBtn_LIk(SelectButton):
    color = QtGui.QColor(192, 128, 0, 255)

class SelectBtn_yellow(SelectButton):
    color = QtGui.QColor(255, 192, 0, 255)

class SelectBtn_green(SelectButton):
    color = QtGui.QColor(0, 192, 0, 255)

class SelectBtn_darkGreen(SelectButton):
    color = QtGui.QColor(0, 100, 0, 255)


##############################################################################
# Classes for Mixin Drawing Shape
##############################################################################
class SelectBtn_Box(SelectButton):

    def drawShape(self, painter):
        borderWidth = 1
        x = borderWidth / 2.0
        y = borderWidth / 2.0
        w = self.width() - borderWidth
        h = self.height() - borderWidth

        # round radius
        if self.height() < self.width():
            rr = self.height() * 0.20
        else:
            rr = self.width() * 0.20

        path = QtGui.QPainterPath()
        path.addRoundedRect(QtCore.QRectF(x, y, w, h), rr, rr)
        self.drawPathWithBorder(painter, path, borderWidth)


class SelectBtn_OutlineBox(SelectButton):

    def drawShape(self, painter):
        borderWidth = 1
        x = borderWidth / 2.0
        y = borderWidth / 2.0
        w = self.width() - borderWidth
        h = self.height() - borderWidth

        # round radius and outline width
        if self.height() < self.width():
            rr = self.height() * 0.20
            ow = self.height() * 0.33
        else:
            rr = self.width() * 0.20
            ow = self.width() * 0.33

        pathOuter = QtGui.QPainterPath()
        pathOuter.addRoundedRect(QtCore.QRectF(x, y, w, h), rr, rr)

        innX = x + ow
        innY = y + ow
        innW = w - (ow * 2)
        innH = h - (ow * 2)
        innR = rr * 0.2
        pathInner = QtGui.QPainterPath()
        pathInner.addRoundedRect(QtCore.QRectF(innX, innY, innW, innH), innR, innR)

        self.drawPathWithBorder(painter,  pathOuter - pathInner, borderWidth)


class SelectBtn_Circle(SelectButton):

    def drawShape(self, painter):
        borderWidth = 1
        x = borderWidth / 2.0
        y = borderWidth / 2.0
        w = self.width() - borderWidth
        h = self.height() - borderWidth

        path = QtGui.QPainterPath()
        path.addEllipse(QtCore.QRectF(x, y, w, h))
        self.drawPathWithBorder(painter, path, borderWidth)


class SelectBtn_OutlineCircle(SelectButton):

    def drawShape(self, painter):
        borderWidth = 1
        x = borderWidth / 2.0
        y = borderWidth / 2.0
        w = self.width() - borderWidth
        h = self.height() - borderWidth

        path = QtGui.QPainterPath()
        path.addEllipse(QtCore.QRectF(x, y, w, h))

        if self.height() < self.width():
            ow = self.height() * 0.25
        else:
            ow = self.width() * 0.25

        innX = x + ow
        innY = y + ow
        innW = w - (ow * 2)
        innH = h - (ow * 2)
        pathInner = QtGui.QPainterPath()
        pathInner.addEllipse(QtCore.QRectF(innX, innY, innW, innH))
        self.drawPathWithBorder(painter, path - pathInner, borderWidth)


class SelectBtn_TriangleLeft(SelectButton):

    def drawShape(self, painter):
        borderWidth = 1
        w = self.width() - borderWidth
        h = self.height() - borderWidth

        triangle = QtGui.QPolygon([QtCore.QPoint(1, h/2), QtCore.QPoint( w-1, 0), QtCore.QPoint( w-1,h-1)])
        path = QtGui.QPainterPath()
        path.addPolygon(triangle)
        self.drawPathWithBorder(painter, path, borderWidth)
        painter.setClipRegion(triangle, QtCore.Qt.ReplaceClip)


class SelectBtn_OutlineTriangleLeft(SelectButton):

    def drawShape(self, painter):
        borderWidth = 1
        w = self.width() - borderWidth
        h = self.height() - borderWidth

        triangle = QtGui.QPolygon([QtCore.QPoint(1, h/2), QtCore.QPoint( w-1, 0), QtCore.QPoint( w-1,h-1)])
        path = QtGui.QPainterPath()
        path.addPolygon(triangle)
        self.drawPathWithBorder(painter, path, borderWidth)
        painter.setClipRegion(triangle, QtCore.Qt.ReplaceClip)


class SelectBtn_TriangleRight(SelectButton):

    def drawShape(self, painter):
        borderWidth = 1
        w = self.width() - borderWidth
        h = self.height() - borderWidth

        triangle = QtGui.QPolygon([ QtCore.QPoint(-1, 0), QtCore.QPoint( -1, h-1), QtCore.QPoint(w-1, h/2)])
        path = QtGui.QPainterPath()
        path.addPolygon(triangle)
        self.drawPathWithBorder(painter, path, borderWidth)
        painter.setClipRegion(triangle, QtCore.Qt.ReplaceClip)


class SelectBtn_OutlineTriangleRight(SelectButton):

    def drawShape(self, painter):
        borderWidth = 1
        w = self.width() - borderWidth
        h = self.height() - borderWidth

        triangle = QtGui.QPolygon([ QtCore.QPoint(-1, 0), QtCore.QPoint( -1, h-1), QtCore.QPoint(w-1, h/2)])
        path = QtGui.QPainterPath()
        path.addPolygon(triangle)
        self.drawPathWithBorder(painter, path, borderWidth)
        painter.setClipRegion(triangle, QtCore.Qt.ReplaceClip)


# ------------------------------------------
def _boilSelector(selectorName, color, shape):
    class SelectorClass(color, shape):
        pass

    SelectorClass.__name__ = selectorName
    return SelectorClass


SELECTORS = {
    # "selector button name":       [ColorClass,          DrawingClass],
    "SelectBtn_RFkBox":              [SelectBtn_RFk,       SelectBtn_Box],
    "SelectBtn_RIkBox":              [SelectBtn_RIk,       SelectBtn_Box],
    "SelectBtn_CFkBox":              [SelectBtn_CFk,       SelectBtn_Box],
    "SelectBtn_CIkBox":              [SelectBtn_CIk,       SelectBtn_Box],
    "SelectBtn_LFkBox":              [SelectBtn_LFk,       SelectBtn_Box],
    "SelectBtn_LIkBox":              [SelectBtn_LIk,       SelectBtn_Box],
    "SelectBtn_yellowBox":           [SelectBtn_yellow,    SelectBtn_Box],
    "SelectBtn_greenBox":            [SelectBtn_green,     SelectBtn_Box],
    "SelectBtn_darkGreenBox":        [SelectBtn_darkGreen, SelectBtn_Box],
    "SelectBtn_blueBox":             [SelectBtn_RFk,       SelectBtn_Box],
    "SelectBtn_redBox":              [SelectBtn_LFk,       SelectBtn_Box],

    "SelectBtn_RFkCircle":           [SelectBtn_RFk,       SelectBtn_Circle],
    "SelectBtn_RIkCircle":           [SelectBtn_RIk,       SelectBtn_Circle],
    "SelectBtn_CFkCircle":           [SelectBtn_CFk,       SelectBtn_Circle],
    "SelectBtn_CIkCircle":           [SelectBtn_CIk,       SelectBtn_Circle],
    "SelectBtn_LFkCircle":           [SelectBtn_LFk,       SelectBtn_Circle],
    "SelectBtn_LIkCircle":           [SelectBtn_LIk,       SelectBtn_Circle],
    "SelectBtn_greenCircle":         [SelectBtn_green,     SelectBtn_Circle],
    "SelectBtn_redCircle":           [SelectBtn_LFk,       SelectBtn_Circle],
    "SelectBtn_yellowCircle":        [SelectBtn_yellow,    SelectBtn_Circle],
    "SelectBtn_blueCircle":          [SelectBtn_RFk,       SelectBtn_Circle],

    "SelectBtn_RFkOutlineBox":       [SelectBtn_RFk,       SelectBtn_OutlineBox],
    "SelectBtn_RIkOutlineBox":       [SelectBtn_RIk,       SelectBtn_OutlineBox],
    "SelectBtn_CFkOutlineBox":       [SelectBtn_CFk,       SelectBtn_OutlineBox],
    "SelectBtn_CIkOutlineBox":       [SelectBtn_CIk,       SelectBtn_OutlineBox],
    "SelectBtn_LFkOutlineBox":       [SelectBtn_LFk,       SelectBtn_OutlineBox],
    "SelectBtn_LIkOutlineBox":       [SelectBtn_LIk,       SelectBtn_OutlineBox],
    "SelectBtn_yellowOutlineBox":    [SelectBtn_yellow,    SelectBtn_OutlineBox],
    "SelectBtn_greenOutlineBox":     [SelectBtn_green,     SelectBtn_OutlineBox],
    "SelectBtn_darkGreenOutlineBox": [SelectBtn_darkGreen, SelectBtn_OutlineBox],

    "SelectBtn_RFkOutlineCircle":    [SelectBtn_RFk,       SelectBtn_OutlineCircle],
    "SelectBtn_RIkOutlineCircle":    [SelectBtn_RIk,       SelectBtn_OutlineCircle],
    "SelectBtn_CFkOutlineCircle":    [SelectBtn_CFk,       SelectBtn_OutlineCircle],
    "SelectBtn_CIkOutlineCircle":    [SelectBtn_CIk,       SelectBtn_OutlineCircle],
    "SelectBtn_LFkOutlineCircle":    [SelectBtn_LFk,       SelectBtn_OutlineCircle],
    "SelectBtn_LIkOutlineCircle":    [SelectBtn_LIk,       SelectBtn_OutlineCircle],
    "SelectBtn_greenOutlineCircle":  [SelectBtn_green,     SelectBtn_OutlineCircle],
    "SelectBtn_redOutlineCircle":    [SelectBtn_LFk,       SelectBtn_OutlineCircle],
    "SelectBtn_yellowOutlineCircle": [SelectBtn_yellow,    SelectBtn_OutlineCircle],
    "SelectBtn_blueOutlineCircle":   [SelectBtn_RFk,       SelectBtn_OutlineCircle],

    "SelectBtn_RFkTriangleRight":  [SelectBtn_RFk,         SelectBtn_TriangleRight],
    "SelectBtn_RIkTriangleRight":  [SelectBtn_RIk,         SelectBtn_TriangleRight],
    "SelectBtn_LFkTriangleLeft":   [SelectBtn_LFk,         SelectBtn_TriangleLeft],
    "SelectBtn_LIkTriangleLeft":   [SelectBtn_LIk,         SelectBtn_TriangleLeft],

    "SelectBtn_greenTriangleRight":  [SelectBtn_green,     SelectBtn_TriangleRight],
    "SelectBtn_greenTriangleLeft":   [SelectBtn_green,     SelectBtn_TriangleLeft]
}


for name, mixins in SELECTORS.items():
    klass = _boilSelector(name, mixins[0], mixins[1])
    globals()[klass.__name__] = klass
