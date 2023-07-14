# -*- coding: utf-8 -*-

u"""=================================================
ツール名：
    CTRL LIBRARY

今後の課題：
    - 設定画面の追加
        ＞命名規則の変更
        ＞回転値とスケール値の変更
        ＞ジョイントシェイプに入れるか

================================================="""

# Standard Modules
import os
from functools import partial
import shutil
import json

# Maya Modules
import pymel.core as pm
import maya.OpenMaya as OpenMaya

# Local Modules
from maglev.lib import widget
from maglev.lib import rename
from maglev.lib import rigging
from maglev.lib import position
from maglev.lib import controller
from maglev.util import optionvar

import maglev.icons as icon

ui = partial(widget.uiName, __name__.replace('.', '_'))
callback = partial(widget.callback, __name__)


def main():
    win = Window()
    win.exist()
    win.create()
    win.show()


class Window(object):

    def __init__(self):
        self.win = 'mainWindow'
        self.win_name = "CTRL LIBRARY"
        self.frame_bgc = [0.2, 0.2, 0.2]
        self.frame_layout_bgc = [0.3, 0.3, 0.3]
        self.button_bgc = [0.8, 0.8, 0.8]

        self.builder = ControlBuilder()
        self.element = ElementUI()
        self.edit = EditControlShape()

    def exist(self):
        if pm.window(self.win, q=True, ex=True):
            pm.deleteUI(self.win)

    def create(self):
        pm.window(self.win,
                  title=self.win_name,
                  w=260,
                  h=510,
                  mb=1,
                  nm=1,
                  s=1)

        self.create_contents()
        return True

    def show(self):
        pm.showWindow(self.win)

    def create_contents(self):
        self.create_menu()
        self.create_preference_frame()
        self.create_control_frame()
        self.create_change_frame()
        self.create_color_frame()

    def create_menu(self):
        menu = pm.menu(label='Edit', tearOff=False)
        pm.menuItem(label='Combine Shapes',
                    c=callback('rigging.combineShapes'))
        pm.menuItem(label='Parent Joint Shapes',
                    c=callback('rigging.jointParentShape'))
        pm.menuItem(divider=True, p=menu)
        pm.menuItem(label='Continual Parent',
                    c='maglev.lib.rigging.parent_chain(pm.ls(sl=True))')
        pm.menuItem(label='Continual Space Parent',
                    c='maglev.lib.rigging.parent_space_chain(pm.ls(sl=True))')
        pm.menu(label='Option', tearOff=False)
        pm.menuItem(label='CenterPivot',
                    c=callback('rigging.centerPivot'))
        pm.menuItem(label='FreezeTransform',
                    c=callback('rigging.freezeTrans'))
        pm.menuItem(label='DeleteHistory',
                    c=callback('rigging.deleteHistory'))
        pm.menu(label='Name', tearOff=False)
        pm.radioMenuItemCollection(ui('nameRadioItem'))
        pm.menuItem(ui('menuRadioA'), l='ReelFX',
                    cl=ui('nameRadioItem'), rb=True)
        pm.menuItem(ui('menuRadioB'), l='Original',
                    cl=ui('nameRadioItem'), rb=False)

        return menu

    def create_preference_frame(self):
        pm.columnLayout('ctrlMasterCL', w=265)
        pm.separator(height=3, style='none')
        pm.frameLayout(label="Preference",
                       bgc=self.frame_bgc,
                       cl=True,
                       w=262,
                       mh=2,
                       mw=2,
                       p='ctrlMasterCL')

        pm.columnLayout('SetMasterCL',
                        bgc=self.frame_layout_bgc,
                        w=130,
                        h=70)

        pm.radioButtonGrp(ui('methodTypeRC'),
                          nrb=2,
                          l='Method:',
                          cw3=[80, 65, 60],
                          columnAttach=[(1, 'left', 20),
                                        (2, 'left', -10)],
                          labelArray2=['Create', 'Replace'],
                          sl=1)

        pm.radioButtonGrp(ui('selectionTypeRC'),
                          nrb=2,
                          l='Type:',
                          cw3=[80, 65, 60],
                          columnAttach=[(1, 'left', 20),
                                        (2, 'left', -10)],
                          labelArray2=['Selected', 'Hierarchy'],
                          sl=1)
        pm.columnLayout(w=350)
        pm.separator(w=250, style='in')
        pm.setParent('..')

        pm.floatFieldGrp(numberOfFields=1,
                         label='Controller Scale:',
                         cw2=[150, 70],
                         value1=1,
                         columnAttach=[(1, 'left', 60),
                                       (2, 'right', 10)]
                         )

    def create_control_frame(self):
        pm.separator(height=3, style='none')
        pm.frameLayout(label="Make Controls",
                       bgc=self.frame_bgc,
                       cl=True,
                       w=262,
                       h=200,
                       mh=2,
                       mw=2,
                       p='ctrlMasterCL')
        pm.columnLayout('MakeMasterCL',
                        bgc=self.frame_layout_bgc,
                        w=152)
        
        # iconLayout = IconLayoutIO()
        # iconLayout.generateTab()

        tab = pm.tabLayout(imw=5,
                           imh=5,
                           p='MakeMasterCL')
        child1 = pm.rowColumnLayout(w=250, nc=7)

        self.element.create_icon_button('circleNormal', 'make_circle_normal')
        self.element.create_icon_button('circleCross', 'make_cross_circle')
        self.element.create_icon_button('circleWave', 'make_circle_wave')
        self.element.create_icon_button('circleHalf', 'make_circle_half')
        self.element.create_icon_button('circleQuarter', 'make_circle_quarter')
        self.element.create_icon_button('circleDoubleHalf', 'make_circle_double_half')
        self.element.create_icon_button('circleDoubleQuarter', 'make_circle_double_quarter')
        self.element.create_icon_button('makeSquare01', 'make_square_01')
        self.element.create_icon_button('makeSquareX01', 'make_square_x_01')
        self.element.create_icon_button('makeSquare02', 'make_square_02')
        self.element.create_icon_button('makeTriangle02', 'make_triangle_02')
        self.element.create_icon_button('makeTriangle01', 'make_triangle_01')
        self.element.create_icon_button('crossA', 'make_crossA')
        self.element.create_icon_button('crossB', 'make_crossB')
        self.element.create_icon_button('hexagonA', 'make_hexagonA')
        self.element.create_icon_button('starA', 'make_star01')
        self.element.create_icon_button('makeNail01', 'make_nail_01')
        self.element.create_icon_button('makeFace01', 'make_face_01')
        self.element.create_icon_button('makeFoot01', 'make_foot')
        self.element.create_icon_button('makeEyes01', 'make_eyes_01')
        pm.setParent('..')

        child2 = pm.rowColumnLayout(w=250, nc=7)
        self.element.create_icon_button('makeBall01', 'make_ball_01')
        self.element.create_icon_button('makeSphereArrow02', 'make_sphere_arrow_02')
        self.element.create_icon_button('halfBall', 'make_half_ball')
        self.element.create_icon_button('makeCircleDir', 'make_circle_dir')
        self.element.create_icon_button('makeCube01', 'make_cube_01')
        self.element.create_icon_button('makeCylinder01', 'make_cylinder_01')
        self.element.create_icon_button('makeCylinder02', 'make_cylinder_02')
        self.element.create_icon_button('makeCylinder03', 'make_cylinder_03')
        self.element.create_icon_button('makePyramid01', 'make_pyramid_01')
        self.element.create_icon_button('makeHalfPyramid01', 'make_half_pyramid_01')
        self.element.create_icon_button('makeRumbus01', 'make_rumbus_01')
        self.element.create_icon_button('makePyramid01', 'make_pyramid_01')
        self.element.create_icon_button('makeCone01', 'make_cone_01')
        self.element.create_icon_button('makeSphereArrow01', 'make_sphere_arrow_01')
        self.element.create_icon_button('makeBigArrow01', 'make_big_arrow_01')
        self.element.create_icon_button('makeCapsule01', 'make_capsule_01')
        self.element.create_icon_button('chestBox', 'make_chest_box')
        pm.setParent('..')

        child3 = pm.rowColumnLayout(w=250, nc=7)
        self.element.create_icon_button('makeArrow01', 'make_arrow_01')
        self.element.create_icon_button('makeArrow02', 'make_arrow_02')
        self.element.create_icon_button('makeArrow06', 'make_arrow_06')
        self.element.create_icon_button('makeArrow07', 'make_arrow_07')
        self.element.create_icon_button('makeArrow08', 'make_arrow_08')
        self.element.create_icon_button('makeArrow09', 'make_arrow_09')
        self.element.create_icon_button('makeArrow10', 'make_arrow_10')
        self.element.create_icon_button('makeArrow11', 'make_arrow_11')
        self.element.create_icon_button('makeArrow13', 'make_arrow_13')
        self.element.create_icon_button('makeArrow14', 'make_arrow_14')
        self.element.create_icon_button('makeArrow15', 'make_arrow_15')
        self.element.create_icon_button('makeArrow16', 'make_arrow_16')
        self.element.create_icon_button('circleArrow', 'make_circle_arrow')
        self.element.create_icon_button('circleAllDir', 'make_circle_all_dir')
        self.element.create_icon_button('circleArrowTwoA', 'make_circle_arrow_twoA')
        self.element.create_icon_button('circleArrowTwoB', 'make_circle_arrow_twoB')
        self.element.create_icon_button('arrowSquere01', 'make_world_arrow')

        pm.setParent('..')
        pm.tabLayout(tab,
                     edit=True,
                     tabLabel=((child1, ' 2Dshape  '),
                               (child2, ' 3Dshape  '),
                               (child3, '  Direction   ')))

        pm.rowColumnLayout('otherRCL',
                           nc=2,
                           cw=[(1, 127), (2, 127)],
                           p="MakeMasterCL")
        register = RegisterWindow()
        pm.button(ui('registerShapeBT'),
                  label='Register Shape',
                  bgc=[0.22, 0.22, 0.22],
                  h=21,
                  c=lambda *args: (register.show()))
        pm.button(ui('editIconBT'),
                  label='Save Icon Layout',
                  bgc=[0.22, 0.22, 0.22],
                  h=21,
                  c="")

    def create_change_frame(self):
        pm.frameLayout(label="Edit Controls",
                       bgc=self.frame_bgc,
                       cl=True,
                       w=262,
                       mh=2,
                       mw=2,
                       p='ctrlMasterCL')
        pm.columnLayout('TransformsMasterCL',
                        bgc=self.frame_layout_bgc,
                        w=152)
        pm.rowColumnLayout('rotateRCL',
                           nc=1,
                           cw=[(1, 255)],
                           p="TransformsMasterCL")
        pm.separator(height=2, style='none')
        pm.radioButtonGrp(ui('axisTypeRBG'),
                          nrb=2,
                          l='Axis:',
                          cw3=[80, 65, 60],
                          columnAttach=[(1, 'left', 20),
                                        (2, 'left', -10)],
                          labelArray2=['Object', 'Pivot'],
                          sl=1)
        pm.separator(height=2, style='none')

        pm.rowColumnLayout(nc=3,
                           cw=[(1, 85), (2, 85), (3, 85)],
                           p='rotateRCL')
        pm.button(label='X',
                  bgc=self.button_bgc,
                  h=25,
                  c=lambda *args: (self.edit.rotate_ctrl_shape('X')))
        pm.button(label='Y',
                  bgc=self.button_bgc,
                  h=25,
                  c=lambda *args: (self.edit.rotate_ctrl_shape('Y')))
        pm.button(label='Z',
                  bgc=self.button_bgc,
                  h=25,
                  c=lambda *args: (self.edit.rotate_ctrl_shape('Z')))
        pm.rowColumnLayout('scaleRCL',
                           nc=1,
                           cw=[(1, 255)],
                           p="TransformsMasterCL")
        pm.rowColumnLayout(nc=2,
                           cw=[(1, 127), (2, 127)],
                           p='scaleRCL')
        pm.button(label='+',
                  bgc=self.button_bgc,
                  h=35,
                  c=lambda *args: (self.edit.scale_ctrl_shape('up')))
        pm.button(label='-',
                  bgc=self.button_bgc,
                  h=35,
                  c=lambda *args: (self.edit.scale_ctrl_shape('down')))
        pm.separator(height=1, style='none')
        pm.rowColumnLayout('otherRCL',
                           nc=2,
                           cw=[(1, 127), (2, 127)],
                           p="TransformsMasterCL")
        pm.button(label='Select All CV',
                  bgc=self.button_bgc, h=25,
                  c=lambda *args: (self.edit.select_shape_mode()))
        pm.button(ui('curveModeBT'),
                  label='Curve Selection',
                  bgc=self.button_bgc,
                  h=25,
                  c=lambda *args: (self.edit.set_curve_mode()))
        pm.separator(height=6, style='none')

    def create_color_frame(self):
        pm.frameLayout('colorFL', label="Color Palette", bgc=self.frame_bgc,
                       cl=True, w=262, mh=2, mw=2, p='ctrlMasterCL')
        pm.columnLayout('colorMasterCL',
                        bgc=self.frame_layout_bgc, w=280, h=120)
        pm.radioButtonGrp(ui('colorPlaceAtRBG'),
                          nrb=2,
                          l='Color At:',
                          cw3=[80, 65, 60],
                          columnAttach=[(1, 'left', 20),
                                        (2, 'left', -10)],
                          labelArray2=['Transform', 'Shape'],
                          sl=0)
        pm.separator(height=1, style='none')
        pm.gridLayout('colorGL', nr=4, nc=8, cwh=[32, 20])

        pm.iconTextButton(nbg=True, l="x", style='iconAndTextCentered', flat=True,
                          c=lambda *args: (self.element.change_color_button_name()), p='colorGL')
        pm.iconTextButton(bgc=[0.467, 0.467, 0.467],
                          c=lambda *args: (self.element.set_slider_value(0)), p='colorGL')
        pm.iconTextButton(bgc=[0.000, 0.000, 0.000],
                          c=lambda *args: (self.element.set_slider_value(1)), p='colorGL')
        pm.iconTextButton(bgc=[0.247, 0.247, 0.247],
                          c=lambda *args: (self.element.set_slider_value(2)), p='colorGL')
        pm.iconTextButton(bgc=[0.498, 0.498, 0.498],
                          c=lambda *args: (self.element.set_slider_value(3)), p='colorGL')
        pm.iconTextButton(bgc=[0.608, 0.000, 0.157],
                          c=lambda *args: (self.element.set_slider_value(4)), p='colorGL')
        pm.iconTextButton(bgc=[0.000, 0.016, 0.373],
                          c=lambda *args: (self.element.set_slider_value(5)), p='colorGL')
        pm.iconTextButton(bgc=[0.000, 0.000, 1.000],
                          c=lambda *args: (self.element.set_slider_value(6)), p='colorGL')
        pm.iconTextButton(bgc=[0.000, 0.275, 0.094],
                          c=lambda *args: (self.element.set_slider_value(7)), p='colorGL')
        pm.iconTextButton(bgc=[0.145, 0.000, 0.263],
                          c=lambda *args: (self.element.set_slider_value(8)), p='colorGL')
        pm.iconTextButton(bgc=[0.780, 0.000, 0.780],
                          c=lambda *args: (self.element.set_slider_value(9)), p='colorGL')
        pm.iconTextButton(bgc=[0.537, 0.278, 0.200],
                          c=lambda *args: (self.element.set_slider_value(10)), p='colorGL')
        pm.iconTextButton(bgc=[0.243, 0.133, 0.122],
                          c=lambda *args: (self.element.set_slider_value(11)), p='colorGL')
        pm.iconTextButton(bgc=[0.600, 0.145, 0.001],
                          c=lambda *args: (self.element.set_slider_value(12)), p='colorGL')
        pm.iconTextButton(bgc=[1.000, 0.000, 0.000],
                          c=lambda *args: (self.element.set_slider_value(13)), p='colorGL')
        pm.iconTextButton(bgc=[0.000, 1.000, 0.000],
                          c=lambda *args: (self.element.set_slider_value(14)), p='colorGL')
        pm.iconTextButton(bgc=[0.000, 0.255, 0.600],
                          c=lambda *args: (self.element.set_slider_value(15)), p='colorGL')
        pm.iconTextButton(bgc=[1.000, 1.000, 1.000],
                          c=lambda *args: (self.element.set_slider_value(16)), p='colorGL')
        pm.iconTextButton(bgc=[1.000, 1.000, 0.000],
                          c=lambda *args: (self.element.set_slider_value(17)), p='colorGL')
        pm.iconTextButton(bgc=[0.388, 0.863, 1.000],
                          c=lambda *args: (self.element.set_slider_value(18)), p='colorGL')
        pm.iconTextButton(bgc=[0.263, 1.000, 0.635],
                          c=lambda *args: (self.element.set_slider_value(19)), p='colorGL')
        pm.iconTextButton(bgc=[1.000, 0.686, 0.686],
                          c=lambda *args: (self.element.set_slider_value(20)), p='colorGL')
        pm.iconTextButton(bgc=[0.890, 0.675, 0.475],
                          c=lambda *args: (self.element.set_slider_value(21)), p='colorGL')
        pm.iconTextButton(bgc=[1.000, 1.000, 0.384],
                          c=lambda *args: (self.element.set_slider_value(22)), p='colorGL')
        pm.iconTextButton(bgc=[0.000, 0.600, 0.325],
                          c=lambda *args: (self.element.set_slider_value(23)), p='colorGL')
        pm.iconTextButton(bgc=[0.627, 0.412, 0.188],
                          c=lambda *args: (self.element.set_slider_value(24)), p='colorGL')
        pm.iconTextButton(bgc=[0.620, 0.627, 0.188],
                          c=lambda *args: (self.element.set_slider_value(25)), p='colorGL')
        pm.iconTextButton(bgc=[0.408, 0.627, 0.188],
                          c=lambda *args: (self.element.set_slider_value(26)), p='colorGL')
        pm.iconTextButton(bgc=[0.188, 0.627, 0.365],
                          c=lambda *args: (self.element.set_slider_value(27)), p='colorGL')
        pm.iconTextButton(bgc=[0.188, 0.627, 0.627],
                          c=lambda *args: (self.element.set_slider_value(28)), p='colorGL')
        pm.iconTextButton(bgc=[0.188, 0.404, 0.627],
                          c=lambda *args: (self.element.set_slider_value(29)), p='colorGL')
        pm.iconTextButton(bgc=[0.435, 0.188, 0.627],
                          c=lambda *args: (self.element.set_slider_value(30)), p='colorGL')
        pm.rowColumnLayout('colorPartsRCL',
                           nc=2,
                           cw=[(1, 227), (2, 27)],
                           p="colorMasterCL")
        pm.colorIndexSliderGrp('colorISG', min=1, max=31,
                               value=1,
                               p='colorPartsRCL',
                               cc=lambda *args: (self.element.set_color_value()))
        pm.intField('colorValueInt', value=1, p='colorPartsRCL')
        pm.button('setColorBtm',
                  label='Set the Color',
                  w=255,
                  h=25,
                  bgc=self.button_bgc,
                  c=lambda *args: (self.builder.apply_color_value()),
                  p='colorMasterCL')


class RegisterWindow():

    def __init__(self):
        self.win = 'registerWindow'
        self.win_name = "Register Window"
        self.frame_bgc = [0.2, 0.2, 0.2]
        self.frame_layout_bgc = [0.3, 0.3, 0.3]
        self.button_bgc = [0.8, 0.8, 0.8]
        self.button_bgcA = [0.27, 0.27, 0.27]

        self.element = ElementUI()
        self.func = RegisterFunction()
        
        self.iconPath = self.func.getNoImageIconPath()

    def exist(self):
        if pm.window(self.win, q=True, ex=True):
            pm.deleteUI(self.win)
    
    def create(self):
        pm.window(self.win,
                  title=self.win_name,
                  w=200,
                  h=250,
                  mb=1,
                  nm=1,
                  s=1)

        self.create_contents()
        return True
    
    def show(self):
        self.exist()
        self.create()
        pm.showWindow(self.win)

    def create_contents(self):
        pm.columnLayout('mainCL', w=265, adj=True)

        self.create_preference_frame()
        self.create_icon_frame()
        self.create_option_frame()

    def create_preference_frame(self):
        pm.frameLayout(label="Preference",
                       bgc=self.frame_bgc,
                       cl=True,
                       w=262,
                       mh=2,
                       mw=2,
                       p='mainCL')
        pm.columnLayout('preferenceCL',
                        bgc=self.frame_layout_bgc,
                        w=130,
                        adj=True,
                        h=70)
        pm.checkBoxGrp("customExportCB",
                       numberOfCheckBoxes=1,
                       label1="Custom Export Path: ",
                       adj=1,
                       changeCommand=lambda *args: (self.func.enableSwitchExportPath()),
                       columnAttach=[(1, 'left', 7), (2, 'both', 13)],
                       p="preferenceCL")

        pm.textFieldButtonGrp("customExportTFB",
                              buttonLabel="Select",
                              editable=False,
                              enableButton=False,
                              label="Export Path: ",
                              buttonCommand=lambda *args: (self.func.selectExportPath()),
                              columnWidth3=[80, 130, 60],
                              columnOffset3=[0, 110, 0],
                              adj=2,
                              p="preferenceCL")
        pm.textFieldGrp("shapeNameTF",
                        label="Shape Name: ",
                        columnWidth2=[80, 110],
                        adj=2,
                        columnAttach=[(1, 'both', 0), (2, 'right', 43)],
                        p="preferenceCL")
        pm.separator(height=1, style='none')
        pm.setParent('..')

    def create_icon_frame(self):
        pm.frameLayout(label="Icon image",
                       bgc=self.frame_bgc,
                       cl=True,
                       w=262,
                       mh=2,
                       mw=2,
                       p='mainCL')
        pm.columnLayout('iconCL',
                        bgc=self.frame_layout_bgc,
                        adj=1,
                        columnOffset=["both", 5],
                        p="mainCL")
        pm.iconTextButton('iconTB',
                          style='iconOnly',
                          image=self.iconPath,
                          p='iconCL')
        pm.button(label="Convert Curve To Stroke Shape", h=20,
                  bgc=self.button_bgcA,
                  c=lambda *args: (self.func.convertCurveToStroke()),
                  p='iconCL')
        pm.formLayout('buttonFL', p="iconCL")
        b1 = pm.button(label="Capture New Image",
                       h=20,
                       bgc=self.button_bgcA,
                       c=lambda *args: (self.func.captureNewImage()),
                       p='buttonFL')
        b2 = pm.button(label="Load",
                       h=20,
                       c=lambda *args: (self.func.loadImage()),
                       bgc=self.button_bgcA,
                       p='buttonFL')
        pm.formLayout('buttonFL',
                      e=True,
                      attachForm=[(b1, 'left', 0), (b2, 'right', 0)],
                      attachControl=[b2, 'left', 0, b1],
                      attachPosition=[b1, 'right', 0, 50])
        pm.setParent('..')

    def create_option_frame(self):
        pm.frameLayout(label="Options",
                       bgc=self.frame_bgc,
                       cl=True,
                       w=262,
                       mh=2,
                       mw=2,
                       p='mainCL')
        pm.columnLayout('optionCL',
                        bgc=self.frame_layout_bgc,
                        w=130,
                        adj=2,
                        columnOffset=["both", 5],
                        p="mainCL")
        pm.optionMenuGrp("optionTabMenu", 
                         label="Tab: ",
                         p="optionCL",
                         adj=2)
        pm.menuItem(label="2D")
        pm.menuItem(label="3D")
        pm.menuItem(label="Direction")
        pm.optionMenuGrp("optionFileTypeMenu",
                         label="File Type: ",
                         p="optionCL",
                         adj=2)
        pm.menuItem(label="mayaAscii")
        pm.menuItem(label="json")
        pm.columnLayout('buttonCL',
                        bgc=self.frame_layout_bgc,
                        w=130,
                        adj=1,
                        columnOffset=["both", 2],
                        p="mainCL")
        pm.button(label="Register Curve", h=30,
                  bgc=self.button_bgc, p='buttonCL')
        pm.separator(height=3, style='none')

        pm.setParent('..')


class DefalutValue():
    controlGrp = 'control_GRP'
    con = 'CON'
    jnt = 'JNT'
    zero = 'ZERO'


class ElementUI():

    def get_method_type(self):
        return pm.radioButtonGrp(ui('methodTypeRC'), q=True, sl=True)

    def get_selection_type(self):
        return pm.radioButtonGrp(ui('selectionTypeRC'), q=True, sl=True)

    def get_axis_type(self):
        return pm.radioButtonGrp(ui('axisTypeRBG'), q=True, sl=True)

    def get_color_at(self):
        return pm.radioButtonGrp(ui('colorPlaceAtRBG'), q=True, sl=True)

    def get_selections(self):
        selections = pm.ls(sl=True, l=True)
        selName = [sel.name() for sel in selections]
        
        types = self.get_selection_type()
        optionvar.write(ui('selectionTypeRC'), types)
        # types is 'selected' mode
        items = []
        if types == 1:
            items.extend(selName)

        # types is 'hierarchy' mode
        elif types == 2:
            for sel in selName:
                children = pm.listRelatives(sel, ad=True, f=True)
                sel_items = [child.name() for child in children]
                sel_items.append(sel)
                sel_items.reverse()

                sel_items.pop(-1)
                items.extend(sel_items)
        return items

    def get_name(self, node):
        name_type = pm.menuItem(ui('menuRadioA'), q=True, rb=True)
        ctrl_name = []

        defalut = DefalutValue()
        if name_type:
            split_name = rename.split_vertical_line(node)[0]
            if defalut.jnt in node:
                ctrl_name.append(split_name.replace(defalut.jnt, defalut.con))
            else:
                name = "{}_{}".format(split_name, defalut.con)
                ctrl_name.append(name)
        else:
            split_name = rename.split_vertical_line(node)[0]
            renamed_ctrl = rename.compile_id_name(split_name[0], 'ctrl')
            if pm.objExists(renamed_ctrl):
                renamed_ctrl = rename.compile_id_name(
                    split_name[0], 'ctrlBatting@')
                ctrl_name.append(rename.get_right_name(renamed_ctrl))
            else:
                ctrl_name.append(renamed_ctrl)
        return ctrl_name

    def get_int_value(self):
        index = pm.colorIndexSliderGrp('colorISG', q=True, value=True)
        return index

    def get_color_button_label(self):
        label = pm.button("setColorBtm", q=True, l=True)
        return label

    def get_color_value(self):
        pre_color_id = pm.colorIndexSliderGrp('colorISG', query=True, value=True)
        color_id = pre_color_id - 1
        return color_id

    def set_color_value(self):
        val = self.get_int_value()
        pm.intField('colorValueInt', e=True, value=val)

    def set_slider_value(self, color_id):
        color_value = color_id + 1
        pm.colorIndexSliderGrp('colorISG',
                               edit=True,
                               value=color_value)
        pm.intField('colorValueInt',
                    e=True,
                    value=color_value
                    )
        
        label = self.get_color_button_label()
        if not label == "Set the Color":
            pm.button("setColorBtm",
                      e=True,
                      l="Set the Color",
                      bgc=[0.8, 0.8, 0.8])
        
        return color_value

    def change_color_button_name(self):
        label = self.get_color_button_label()
        if label == "Set the Color":
            pm.button("setColorBtm",
                      e=True,
                      l="Uncheck Enable Override",
                      bgc=[0.2, 0.2, 0.2])
        pm.colorIndexSliderGrp('colorISG',
                        edit=True,
                        value=1)
        pm.intField('colorValueInt',
                    e=True,
                    value=1
                    )

    def create_icon_button(self, icon_name, func):
        icon_dir_path = icon.get_icon_path()
        path_list = ['controller', '{}.png'.format(icon_name)]
        icon_path = os.path.join(icon_dir_path, *path_list)

        builder = ControlBuilder()
        command = lambda *args: (builder.build_controller('controller.{}'.format(func)))
        btn = pm.nodeIconButton(style='iconOnly',
                                c=command,
                                image1=icon_path)
        return btn


class ControlBuilder():

    def __init__(self):
        self.element = ElementUI()
        self.default = DefalutValue()
    
    def build_controller(self, ctrl_name):
        selection = self.element.get_selections()
        method = self.element.get_method_type()

        if not pm.objExists(self.default.controlGrp):
            pm.createNode('transform', n=self.default.controlGrp)

        if method == 1:
            self.create_ctrl(ctrl_name, selection)
        elif method == 2:
            self.replace_ctrl(ctrl_name, selection)

    def create_ctrl(self, ctrl_name, selection):
        ctrls = []

        # if selected, it makes ctrl on position selected
        if selection:
            for i in selection:
                # create and rename ctrl
                ctrl = eval(ctrl_name + '()')
                name = self.element.get_name(i)[0]
                ctrls.append(name)
                name = pm.rename(ctrl, name)

                # set color
                self.apply_color_value(target=name)

                # zero out and place to target
                space = rigging.create_init_space(id_name=self.default.zero,
                                                  nodes=name,
                                                  idlwr=False)
                position.snap_to_target(space, i)
                pm.parent(space, self.default.controlGrp)

        # if no selected, it makes ctrl on world axis
        else:
            ctrl = eval(ctrl_name + '()')
            ctrl = pm.rename(ctrl, 'control_CON')
            ctrls.append(str(ctrl))
            space = rigging.create_init_space(nodes=ctrl)
            pm.parent(space, self.default.controlGrp)

        # select curve generated
        pm.select(ctrls, r=True)
        return ctrls

    def replace_ctrl(self, ctrl_name, selection):
        if not selection:
            return

        ctrls = []
        for sel in selection:
            selection_shp = pm.listRelatives(sel, s=True)
            for shp in selection_shp:
                if pm.objectType(shp) == 'nurbsCurve':
                    pm.parent(shp, s=True, rm=True)

            ctrl = str(eval('{}()'.format(ctrl_name)))
            ctrl_shape = pm.listRelatives(ctrl, s=True)
            rename_ctrl_shape = pm.rename(ctrl_shape, '{}Shape#'.format(sel))

            pm.parent(rename_ctrl_shape, sel, s=True, r=True)
            pm.delete(ctrl)
            ctrls.append(sel)
        pm.select(ctrls)

    def apply_color_value(self, target=None):
        color_type = self.element.get_color_at()
        color_value = self.element.get_color_value()
        color_label = self.element.get_color_button_label()

        pre_target = []
        if not target:
            trg = [i for i in pm.selected(l=True)]
            pre_target.extend(trg)
        else:
            pre_target.append(target)
        
        for i in pre_target:
            post_targets = None
            if color_type == 1:
                post_targets = [i]
            if color_type == 2:
                post_targets = i.getShapes()
            
            for trg in post_targets:
                if color_label == "Set the Color":
                    pm.setAttr('{}.overrideEnabled'.format(trg), 1)
                    pm.setAttr('{}.overrideColor'.format(trg), color_value)
                else:
                    pm.setAttr('{}.overrideEnabled'.format(trg), 0)


class EditControlShape():

    def __init__(self):
        self.element = ElementUI()

    def rotate_ctrl_shape(self, axis):
        sel = pm.ls(sl=True)

        axis_type = self.element.get_axis_type()
        axis_name = []
        if axis_type == 1:
            axis_name.append('objectCenter')
        elif axis_type == 2:
            axis_name.append('objectPivot')
        controller.rotate_ctrl_shape(sel, axis, axis_name[0])

    def scale_ctrl_shape(self, axis):
        sel = pm.ls(sl=True)

        axis_type = self.element.get_axis_type()
        axis_name = []
        if axis_type == 1:
            axis_name.append('objectCenter')
        elif axis_type == 2:
            axis_name.append('objectPivot')
        controller.scale_ctrl_shape(sel, axis, axis_name[0])

    def select_shape_mode(self):
        if not pm.filterExpand(sm=9):
            return

        sel = pm.ls(sl=True, l=True)
        if sel:
            cur_shape = pm.listRelatives(sel, s=True)
            cvs = []
            for i in cur_shape:
                cv = pm.ls(i + '.cv[*]')
                cvs.extend(cv)
            pm.select(cvs)
        else:
            return None

    def set_curve_mode(self):
        if pm.button(ui('curveModeBT'), q=True, l=True) == 'Curve Selection':
            pm.button(ui('curveModeBT'), e=True,
                      l='Reset Mode', bgc=[0.15, 0.15, 0.15])
            pm.selectType(alo=False, nc=True)
        else:
            pm.button(ui('curveModeBT'), e=True,
                      l='Curve Selection', bgc=[0.8, 0.8, 0.8])
            pm.selectType(alo=True)


class RegisterFunction():
    
    def __init__(self):
        self.filePath = []
    
    def getNoImageIconPath(self):
        dir_path = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(dir_path, "icon", "no-photos.png")
        return full_path
    
    def enableSwitchExportPath(self):
        cb = pm.checkBoxGrp("customExportCB", q=True, v1=True)
        if not cb:
            pm.textFieldButtonGrp("customExportTFB",
                                  e=True,
                                  editable=False,
                                  enableButton=False)
        else:
            pm.textFieldButtonGrp("customExportTFB",
                                  e=True,
                                  editable=True,
                                  enableButton=True)
    
    def selectExportPath(self):
        filename = pm.fileDialog2(fileMode=2,
                                  dialogStyle=2,
                                  caption="Export To Custom Path",
                                  okCaption="Select")
        if not filename:
            return
        pm.textFieldButtonGrp("customExportTFB",
                              e=True,
                              insertText=filename[0])
    
    def export(self):
        pass
    
    def convertCurveToStroke(self, *args):
        """Export selection, prompt for name, and create icon as well.
        """
        strokes = pm.ls(type='stroke')
        
        curve = pm.selected(type="transform")
        if not curve:
            pm.warning("Please select a nurbsCurve")
            return
        
        # create the icon
        pm.runtime.ResetTemplateBrush()
        brush = pm.getDefaultBrush()
        pm.setAttr('{}.brushWidth'.format(brush), 0.06)
        pm.setAttr('{}.glow'.format(brush), 0.03)
        pm.setAttr('{}.screenspaceWidth'.format(brush), 1)
        pm.setAttr('{}.distanceScaling'.format(brush), 0.01)
        pm.setAttr('{}.color1'.format(brush), 0.35, 0.85, 0.60, type='double3')

        pm.select(curve)
        pm.runtime.AttachBrushToCurves(curve)
        
    def deleteAllStrokes(self):
        strokes = [x for x in pm.ls(type='stroke')]
        for each in strokes:
            pm.delete(pm.listRelatives(each, parent=True, pa=True))

    def captureNewImage(self, width=32, height=32):
        """ This renders a shelf-sized icon and hopefully places it in your icon directory
        """
        image_name = self.getShapeName()
        cam = self.getCurrentCamera()

        png_format = 32
        pm.setAttr('defaultRenderGlobals.currentRenderer', 'mayaSoftware', type='string')
        pm.setAttr('defaultRenderGlobals.imageFormat', png_format)
        pm.setAttr('defaultRenderGlobals.imfkey', 'xpm', type='string')
        pm.setAttr('defaultRenderGlobals.imageFilePrefix', image_name, type='string')

        pm.setAttr('{}.backgroundColor'.format(cam), 0.8, 0.8, 0.8, type='double3')
        image = pm.render(cam, xresolution=width, yresolution=height)
        base = os.path.basename(image)
        filePath = os.path.join(self.getFilePath(), base)
        
        # here we attempt to move the rendered icon to a more generalized icon location
        if filePath:
            self.filePath.append(filePath)
            shutil.move(image, filePath)
            pm.displayInfo("Export Path: {}".format(filePath))

        pm.iconTextButton('iconTB',
                          e=True,
                          style='iconOnly',
                          image=self.getNoImageIconPath())

        pm.iconTextButton('iconTB',
                          e=True,
                          style='iconOnly',
                          image=filePath)

        return filePath
    
    def getCurrentCamera(self):
        """
        Returns the camera that you're currently looking through.
        If the current highlighted panel isn't a modelPanel,
        """
        panel = pm.getPanel(withFocus=True)
        if pm.getPanel(typeOf=panel) != 'modelPanel':
            for p in pm.getPanel(visiblePanels=True):
                if pm.getPanel(typeOf=p) == 'modelPanel':
                    panel = p
                    pm.setFocus(panel)
                    break

        if pm.getPanel(typeOf=panel) != 'modelPanel':
            OpenMaya.MGlobal.displayWarning('Please highlight a camera viewport.')
            return False

        cam_shape = pm.modelEditor(panel, query=True, camera=True)
        if not cam_shape:
            return False

        if pm.nodeType(cam_shape) == 'transform':
            return cam_shape
        elif pm.nodeType(cam_shape) == 'camera':
            return pm.listRelatives(cam_shape, parent=True, path=True)[0]

    def loadImage(self):
        filePath = pm.fileDialog2(fileMode=1,
                                dialogStyle=2,
                                caption="Load an icon image",
                                okCaption="Load")
        if not filePath:
            return
        
        pm.iconTextButton('iconTB',
                            e=True,
                            style='iconOnly',
                            image=filePath[0])
    
    def getShapeName(self):
        name = pm.textFieldGrp("shapeNameTF",
                                q=True,
                                text=True)
        return name
    
    def getFilePath(self):
        filePath = pm.textFieldButtonGrp("customExportTFB",
                                         q=True,
                                         text=True)
        return filePath
    
    def getTabType(self):
        tab = pm.optionMenuGrp("optionTabMenu",
                               q=True,
                               value=True)
        return tab
    
    def getFileType(self):
        fileType = pm.optionMenuGrp("optionFileTypeMenu",
                                    q=True,
                                    value=True)
        return fileType
    
    
class IconLayoutIO():
    
    FILE_NAME = "iconLayout.json"
    
    def __init__(self):
        self.filePath = self.getLayoutDataPath()
        self.data = self.getLayoutData()
        
    def __importData(self):
        """Return the contents of a json file. Expecting, but not limited to,
        a dictionary.

        Returns:
            dict: contents of json file, expected dict
        """
        try:
            with open(self.filePath, "r") as f:
                data = json.load(f)
                return data
        except Exception as e:
            print(e)
            return None

    def __exportData(self, data):
        """export data, dict, to filepath provided

        Args:
            data (dict): expected dict, not limited to
            filePath (string): path to output json file
        """
        try:
            with open(self.filePath, "w") as json_file:
                json.dump(data, json_file, sort_keys=True, indent=4)

            msg = "icon layout data exported: {}"
            pm.displayInfo(msg.format(self.filePath))

        except Exception as e:
            print(e)

    def getLayoutDataPath(self):
        dirName = os.path.dirname(__file__)
        return os.path.join(dirName, "data", self.FILE_NAME)
    
    def getLayoutData(self):
        if not self.filePath:
            self.filePath = self.fileDialog(mode=1)

        data = self.__importData()
        if data is None:
            return
        
        return data
        
    def sortLayoutOrderData(self):
        items = []
        for tabDict in self.sortTabOrderData():
            pre_order = {}
            for index, tittleData in tabDict.items():
                for curveData in tittleData:
                    for tabName, data in curveData.items():
                        name = data[0]
                        tabNum = data[1]
                        layoutIndex = data[2]["layoutIndex"]
                        pre_order[layoutIndex] = [tabName, tabNum, {name:data[2]}]
            sortItems = sorted(pre_order.items(), key=lambda x: x[1])
            items.extend(dict(sortItems).values())
        return items
    
    def sortTabOrderData(self):
        allItems = []
        for tabDict in self.sortTabMainOrderData():
            pre_order = {}
            for tittle, data in tabDict.items():
                indexList = []
                numTab = data["numberOfTab"]
                for name, contentData in data["contents"].items():
                    tabIndex = contentData["tabIndex"]
                    # print tittle, name, contentData
                    for i in range(1, data["numberOfTab"] + 1):
                        if i == tabIndex:
                            indexList.append({tittle:[name, numTab, contentData]})
                pre_order[tabIndex] = indexList
            allItems.append(pre_order)
            # sortItems = sorted(pre_order.items(), key=lambda x: x[1])
        return allItems
    
    def collectLayoutInfo(self):
        pass

    def sortTabMainOrderData(self):
        indexDict = {}
        for mainTab, tabInfo in self.data.items():
            index = tabInfo["indexOrder"]
            indexDict[index] = {mainTab:tabInfo}
        sortItems = sorted(indexDict.items(), key=lambda x: x[1])
        return dict(sortItems).values()
    
    def generateTab(self):
        mainTab = pm.tabLayout("mainTab",
                    innerMarginWidth=5,
                    innerMarginHeight=5,
                    parent='MakeMasterCL'
                    )
        
        layoutDict, subTabLayout = {}, []
        for tabName, tabNum, curveData in self.sortLayoutOrderData():
            tabLayName = "tabLayout{}".format(tabName)
            subTabName = "subTab{}".format(tabName)

            for curveName, data in curveData.items():
                path = data["path"]
                tabIndex = data["tabIndex"]
                layoutIndex = data["layoutIndex"]
                if not pm.rowColumnLayout(tabLayName, ex=True):
                    lay = pm.rowColumnLayout(
                                tabLayName,
                                w=250,
                                h=127,
                                nc=7,
                                p=mainTab)
                    if len(tabName) <= 10:
                        centerTab = tabName.center(14)
                    else:
                        centerTab = tabName
                    layoutDict[centerTab] = tabLayName
                
                if not pm.tabLayout(subTabName, ex=True):
                    subTab = pm.tabLayout(subTabName,
                                          innerMarginWidth=5,
                                          innerMarginHeight=5,
                                          p=lay
                                          )
                    subTabLayout.append(subTab)
                    pm.setParent('..')
                
        for subTab in subTabLayout:
            for i in range(1, 8):
                subTabLayName = "subTabLayout{}{}".format(tabName, i)
                subRowLayout = pm.rowColumnLayout(
                                    subTabLayName,
                                    w=242,
                                    h=102,
                                    nc=7,
                                    p=subTab)
                pm.setParent('..')
                pm.tabLayout(subTab,
                             e=True,
                             tabLabel=(subRowLayout, str(i).center(2)))
            pm.setParent('..')

        # self.create_icon_button(curveName, subLayoutDict[tabIndex], path)

        layout = []
        for tabName, layName in layoutDict.items():
            layout.append([layName, tabName])
        
        pm.tabLayout(mainTab,
                     edit=True,
                     tabLabel=((layout[0][0], layout[0][1]),
                               (layout[1][0], layout[1][1]),
                               (layout[2][0], layout[2][1])))
        
        return layout
    
    def create_icon_button(self, name, parent, path):
        btn = pm.nodeIconButton(style='iconOnly',
                                image1=path,
                                annotation=name,
                                parent=parent)
        return btn
    
    def layoutIconTab(self, data):
        pass
    
    def saveLayout(self, path):
        pass
    
    def changeLayoutOrder(self, data):
        pass
    