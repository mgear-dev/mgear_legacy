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

import mgear.maya.pyqt as gqt
QtGui, QtCore, QtWidgets, wrapInstance = gqt.qt_import()

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(259, 223)
        self.groupBox = QtWidgets.QGroupBox(Form)
        self.groupBox.setGeometry(QtCore.QRect(0, 0, 249, 211))
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.widget = QtWidgets.QWidget(self.groupBox)
        self.widget.setGeometry(QtCore.QRect(8, 10, 231, 189))
        self.widget.setObjectName("widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.softness_label = QtWidgets.QLabel(self.widget)
        self.softness_label.setObjectName("softness_label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.softness_label)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.softness_slider = QtWidgets.QSlider(self.widget)
        self.softness_slider.setMinimumSize(QtCore.QSize(0, 15))
        self.softness_slider.setMaximum(100)
        self.softness_slider.setOrientation(QtCore.Qt.Horizontal)
        self.softness_slider.setObjectName("softness_slider")
        self.horizontalLayout_3.addWidget(self.softness_slider)
        self.softness_spinBox = QtWidgets.QSpinBox(self.widget)
        self.softness_spinBox.setMaximum(100)
        self.softness_spinBox.setObjectName("softness_spinBox")
        self.horizontalLayout_3.addWidget(self.softness_spinBox)
        self.formLayout.setLayout(0, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout_3)
        self.softness_label_2 = QtWidgets.QLabel(self.widget)
        self.softness_label_2.setObjectName("softness_label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.softness_label_2)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.position_slider = QtWidgets.QSlider(self.widget)
        self.position_slider.setMinimumSize(QtCore.QSize(0, 15))
        self.position_slider.setMaximum(100)
        self.position_slider.setOrientation(QtCore.Qt.Horizontal)
        self.position_slider.setObjectName("position_slider")
        self.horizontalLayout_4.addWidget(self.position_slider)
        self.position_spinBox = QtWidgets.QSpinBox(self.widget)
        self.position_spinBox.setMaximum(100)
        self.position_spinBox.setObjectName("position_spinBox")
        self.horizontalLayout_4.addWidget(self.position_spinBox)
        self.formLayout.setLayout(1, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout_4)
        self.softness_label_3 = QtWidgets.QLabel(self.widget)
        self.softness_label_3.setObjectName("softness_label_3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.softness_label_3)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.lockOri_slider = QtWidgets.QSlider(self.widget)
        self.lockOri_slider.setMinimumSize(QtCore.QSize(0, 15))
        self.lockOri_slider.setMaximum(100)
        self.lockOri_slider.setOrientation(QtCore.Qt.Horizontal)
        self.lockOri_slider.setObjectName("lockOri_slider")
        self.horizontalLayout_5.addWidget(self.lockOri_slider)
        self.lockOri_spinBox = QtWidgets.QSpinBox(self.widget)
        self.lockOri_spinBox.setMaximum(100)
        self.lockOri_spinBox.setObjectName("lockOri_spinBox")
        self.horizontalLayout_5.addWidget(self.lockOri_spinBox)
        self.formLayout.setLayout(2, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout_5)
        self.maxStretch_label = QtWidgets.QLabel(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.maxStretch_label.sizePolicy().hasHeightForWidth())
        self.maxStretch_label.setSizePolicy(sizePolicy)
        self.maxStretch_label.setObjectName("maxStretch_label")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.maxStretch_label)
        self.maxStretch_spinBox = QtWidgets.QDoubleSpinBox(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.maxStretch_spinBox.sizePolicy().hasHeightForWidth())
        self.maxStretch_spinBox.setSizePolicy(sizePolicy)
        self.maxStretch_spinBox.setMinimum(1.0)
        self.maxStretch_spinBox.setSingleStep(0.1)
        self.maxStretch_spinBox.setProperty("value", 1.5)
        self.maxStretch_spinBox.setObjectName("maxStretch_spinBox")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.maxStretch_spinBox)
        self.maxSquash_label = QtWidgets.QLabel(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.maxSquash_label.sizePolicy().hasHeightForWidth())
        self.maxSquash_label.setSizePolicy(sizePolicy)
        self.maxSquash_label.setObjectName("maxSquash_label")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.maxSquash_label)
        self.maxSquash_spinBox = QtWidgets.QDoubleSpinBox(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.maxSquash_spinBox.sizePolicy().hasHeightForWidth())
        self.maxSquash_spinBox.setSizePolicy(sizePolicy)
        self.maxSquash_spinBox.setMinimum(0.1)
        self.maxSquash_spinBox.setMaximum(1.0)
        self.maxSquash_spinBox.setSingleStep(0.1)
        self.maxSquash_spinBox.setProperty("value", 0.5)
        self.maxSquash_spinBox.setObjectName("maxSquash_spinBox")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.maxSquash_spinBox)
        self.divisions_label = QtWidgets.QLabel(self.widget)
        self.divisions_label.setObjectName("divisions_label")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.divisions_label)
        self.division_spinBox = QtWidgets.QSpinBox(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.division_spinBox.sizePolicy().hasHeightForWidth())
        self.division_spinBox.setSizePolicy(sizePolicy)
        self.division_spinBox.setMinimum(1)
        self.division_spinBox.setProperty("value", 2)
        self.division_spinBox.setObjectName("division_spinBox")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.division_spinBox)
        self.verticalLayout.addLayout(self.formLayout)
        self.squashStretchProfile_pushButton = QtWidgets.QPushButton(self.widget)
        self.squashStretchProfile_pushButton.setObjectName("squashStretchProfile_pushButton")
        self.verticalLayout.addWidget(self.squashStretchProfile_pushButton)

        self.retranslateUi(Form)
        QtCore.QObject.connect(self.softness_slider, QtCore.SIGNAL("sliderMoved(int)"), self.softness_spinBox.setValue)
        QtCore.QObject.connect(self.softness_spinBox, QtCore.SIGNAL("valueChanged(int)"), self.softness_slider.setValue)
        QtCore.QObject.connect(self.position_slider, QtCore.SIGNAL("valueChanged(int)"), self.position_spinBox.setValue)
        QtCore.QObject.connect(self.position_spinBox, QtCore.SIGNAL("valueChanged(int)"), self.position_slider.setValue)
        QtCore.QObject.connect(self.lockOri_spinBox, QtCore.SIGNAL("valueChanged(int)"), self.lockOri_slider.setValue)
        QtCore.QObject.connect(self.lockOri_slider, QtCore.SIGNAL("valueChanged(int)"), self.lockOri_spinBox.setValue)
        QtCore.QObject.connect(self.softness_slider, QtCore.SIGNAL("valueChanged(int)"), self.softness_spinBox.setValue)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(gqt.fakeTranslate("Form", "Form", None, -1))
        self.softness_label.setText(gqt.fakeTranslate("Form", "Softness", None, -1))
        self.softness_label_2.setText(gqt.fakeTranslate("Form", "Position", None, -1))
        self.softness_label_3.setText(gqt.fakeTranslate("Form", "Lock Orient", None, -1))
        self.maxStretch_label.setText(gqt.fakeTranslate("Form", "Max Stretch", None, -1))
        self.maxSquash_label.setText(gqt.fakeTranslate("Form", "Max Squash", None, -1))
        self.divisions_label.setText(gqt.fakeTranslate("Form", "Divisions", None, -1))
        self.squashStretchProfile_pushButton.setText(gqt.fakeTranslate("Form", "Squash and Stretch Profile", None, -1))

