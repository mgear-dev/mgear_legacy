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
# Author:     Chad Vernon           ------------------          www.chadvernon.com
# Date:       2016 / 10 / 10

"""
Functions to work with skinCluster data.

This module is derivated from Chad Vernon's Skin IO.

`Chad Vernon's github <https://github.com/chadmv/cmt/tree/master/scripts/cmt/deform>`_
"""

#############################################
# GLOBAL
#############################################
import cPickle as pickle

import pymel.core as pm
import maya.OpenMaya as OpenMaya

FILE_EXT = ".gSkin"

######################################
##   Skin getters
######################################

def getSkinCluster(obj):
    
    skinCluster = None

    if  isinstance(obj, basestring):
        obj = pm.PyNode(obj)
    try:
        if pm.nodeType(obj.getShape()) in ["mesh", "nurbsSurface", "nurbsCurve"]:
            
            for shape in obj.getShapes():
                try:
                    skinCluster = pm.listHistory(shape, type="skinCluster")[0]
                except:
                    pass
    except:
        pm.displayWarning("%s: is not supported."% obj.name())
    
    return skinCluster

def getGeometryComponents(skinCls):
    fnSet = OpenMaya.MFnSet(skinCls.__apimfn__().deformerSet())
    members = OpenMaya.MSelectionList()
    fnSet.getMembers(members, False)
    dagPath = OpenMaya.MDagPath()
    components = OpenMaya.MObject()
    members.getDagPath(0, dagPath, components)
    return dagPath, components

def getCurrentWeights(skinCls, dagPath, components):
    weights = OpenMaya.MDoubleArray()
    util = OpenMaya.MScriptUtil()
    util.createFromInt(0)
    pUInt = util.asUintPtr()
    skinCls.__apimfn__().getWeights(dagPath, components, weights, pUInt)
    return weights

######################################
##   Skin Collectors
######################################

def collectInfluenceWeights(skinCls, dagPath, components, dataDic):
    weights = getCurrentWeights(skinCls, dagPath, components)

    influencePaths = OpenMaya.MDagPathArray()
    numInfluences = skinCls.__apimfn__().influenceObjects(influencePaths)
    numComponentsPerInfluence = weights.length() / numInfluences
    for ii in range(influencePaths.length()):
        influenceName = influencePaths[ii].partialPathName()
        influenceWithoutNamespace = pm.PyNode(influenceName).stripNamespace()
        dataDic['weights'][influenceWithoutNamespace] = \
                [weights[jj*numInfluences+ii] for jj in range(numComponentsPerInfluence)]


def collectBlendWeights(skinCls, dagPath, components, dataDic):
    weights = OpenMaya.MDoubleArray()
    skinCls.__apimfn__().getBlendWeights(dagPath, components, weights)
    dataDic['blendWeights'] = [weights[i] for i in range(weights.length())]



def collectData(skinCls, dataDic):
    dagPath, components = getGeometryComponents(skinCls)
    collectInfluenceWeights(skinCls, dagPath, components, dataDic)
    collectBlendWeights(skinCls, dagPath, components, dataDic)

    for attr in ['skinningMethod', 'normalizeWeights']:
        dataDic[attr] = pm.getAttr('%s.%s' % (skinCls, attr))

    dataDic['skinClsName'] = skinCls.name()


######################################
##   Skin export
######################################

def exportSkin(filePath=None, objs=None, *args):

    if not objs:
        if pm.selected():
            objs = pm.selected()
        else:
            pm.displayWarning("Please Select One or more objects")
            return False

    packDic = {
            "objs":[],
            "objDDic":[],
            "bypassObj":[]
            }

    if not filePath:
        startDir = pm.workspace(q=True, rootDirectory=True)
        filePath = pm.fileDialog2(dialogStyle=2, fileMode=0, startingDirectory=startDir,
                                    fileFilter='mGear Skin (*%s)' % FILE_EXT)
        filePath = filePath[0]
    if not filePath:
        return False

    if not filePath.endswith(FILE_EXT):
        filePath += FILE_EXT

    #object parsing
    for obj in objs:
        skinCls = getSkinCluster(obj)
        if not skinCls:
            pm.displayWarning(obj.name() + ": Skiped because don't have Skin Cluster")
            pass
        else:

            dataDic = {
                'weights':{},
                'blendWeights':[],
                'skinClsName':"",
                'objName':"",
                'nameSpace':""
                }

            dataDic["objName"] = obj.name()
            dataDic["nameSpace"] = obj.namespace()


            collectData(skinCls, dataDic)

            packDic["objs"].append(obj.name())
            packDic["objDDic"].append(dataDic)
            pm.displayInfo( 'Exported skinCluster %s (%d influences, %d vertices) %s' % ( skinCls.name(),
            len(dataDic['weights'].keys()), len(dataDic['blendWeights']), obj.name()))


    fh = open(filePath, 'wb')
    pickle.dump(packDic, fh, pickle.HIGHEST_PROTOCOL)
    fh.close()

    return True

######################################
##   Skin setters
######################################


def setInfluenceWeights(skinCls, dagPath, components, dataDic):
    unusedImports = []
    weights = getCurrentWeights(skinCls, dagPath, components)
    influencePaths = OpenMaya.MDagPathArray()
    numInfluences = skinCls.__apimfn__().influenceObjects(influencePaths)
    numComponentsPerInfluence = weights.length() / numInfluences

    for importedInfluence, importedWeights in dataDic['weights'].items():
        for ii in range(influencePaths.length()):
            influenceName = influencePaths[ii].partialPathName()
            influenceWithoutNamespace = pm.PyNode(influenceName).stripNamespace()
            if influenceWithoutNamespace == importedInfluence:
                for jj in range(numComponentsPerInfluence):
                    weights.set(importedWeights[jj], jj*numInfluences+ii)
                break
        else:
            unusedImports.append(importedInfluence)


    influenceIndices = OpenMaya.MIntArray(numInfluences)
    for ii in range(numInfluences):
        influenceIndices.set(ii, ii)
    skinCls.__apimfn__().setWeights(dagPath, components, influenceIndices, weights, False)


def setBlendWeights(skinCls, dagPath, components, dataDic):
    blendWeights = OpenMaya.MDoubleArray(len(dataDic['blendWeights']))
    for i, w in enumerate(dataDic['blendWeights']):
        blendWeights.set(w, i)
    skinCls.__apimfn__().setBlendWeights(dagPath, components, blendWeights)


def setData(skinCls, dataDic):
    dagPath, components = getGeometryComponents(skinCls)
    setInfluenceWeights(skinCls, dagPath, components, dataDic)
    setBlendWeights(skinCls, dagPath, components, dataDic)

    for attr in ['skinningMethod', 'normalizeWeights']:
        pm.setAttr('%s.%s' % (skinCls, attr), dataDic[attr])

######################################
##   Skin import
######################################
def getObjsFromSkinFile(filePath=None, *args):
    #retrive the object names inside gSkin file
    if not filePath:
        startDir = pm.workspace(q=True, rootDirectory=True)
        filePath = pm.fileDialog2(dialogStyle=2, fileMode=1, startingDirectory=startDir,
                                    fileFilter='mGear Skin (*%s)' % FILE_EXT)
    if not filePath:
        return
    if not isinstance(filePath, basestring):
        filePath = filePath[0]

    # Read in the file
    fh = open(filePath, 'rb')
    data = pickle.load(fh)
    fh.close()
    for x in data["objs"]:
        print x

def importSkin(filePath=None, *args):

    if not filePath:
        startDir = pm.workspace(q=True, rootDirectory=True)
        filePath = pm.fileDialog2(dialogStyle=2, fileMode=1, startingDirectory=startDir,
                                    fileFilter='mGear Skin (*%s)' % FILE_EXT)
    if not filePath:
        return
    if not isinstance(filePath, basestring):
        filePath = filePath[0]

    # Read in the file
    fh = open(filePath, 'rb')
    dataPack = pickle.load(fh)
    fh.close()

    for data in dataPack["objDDic"]:

        try:
            skinCluster = False
            objName = data["objName"]
            objNode = pm.PyNode(objName)

            meshVertices = pm.polyEvaluate(objNode, vertex=True)
            importedVertices = len(data['blendWeights'])
            if meshVertices != importedVertices:
                pm.displayWarning('Vertex counts do not match. %d != %d' %
                        (meshVertices, importedVertices))
                continue

            if  getSkinCluster(objNode):
                skinCluster = getSkinCluster(objNode)
            else:
                try:
                    joints = data['weights'].keys()
                    skinCluster = pm.skinCluster(joints, objNode, tsb=True, nw=2, n=data['skinClsName'])
                except:
                    notFound = data['weights'].keys()
                    sceneJoints = set([pm.PyNode(x).name()
                              for x in pm.ls(type='joint')])

                    for j in notFound:
                        if j in sceneJoints:
                            notFound.remove(j)
                    pm.displayWarning("Object: " + objName + " Skiped. Can't found corresponding deformer for the following joints: " + str(notFound))
                    continue
            if skinCluster:
                setData(skinCluster, data)
                print 'Imported skin for: %s' % objName


        except:
            pm.displayWarning("Object: " + objName + " Skiped. Can NOT be found in the scene" )

######################################
##   Skin Copy
######################################

def skinCopy(sourceMesh=None, targetMesh=None, *args):
    if not sourceMesh or not targetMesh:
        if len(pm.selected()) >=2:
            sourceMesh = pm.selected()[-1]
            targetMeshes = pm.selected()[:-1]
        else:
            pm.displayWarning("Please select target mesh/meshes and source mesh with skinCluster.")
            return
    else:
        targetMeshes = [targetMesh]

        #we check this here, because if not need to check when we work base on selection.
        if isinstance(sourceMesh, basestring):
            sourceMesh = pm.PyNode(sourceMesh)

    for targetMesh in targetMeshes:
        if  isinstance(targetMesh, basestring):
            sourceMesh = pm.PyNode(targetMesh)

        ss = getSkinCluster(sourceMesh)

        if ss:
            oDef = pm.skinCluster(sourceMesh, query=True, influence=True)
            skinCluster = pm.skinCluster(oDef, targetMesh, tsb=True, nw=2, n=targetMesh.name() + "_SkinCluster")
            pm.copySkinWeights( ss=ss.stripNamespace(), ds=skinCluster.name(), noMirror=True, ia="oneToOne", sm=True, nr=True)
        else:
            pm.displayError("Source Mesh :" + sourceMesh.name() + " Don't have skinCluster")

######################################
##   Skin Utils
######################################
def selectDeformers(*args):
    if pm.selected():
        try:
            oSel = pm.selected()[0]
            oColl = pm.skinCluster(oSel, query=True, influence=True)
            pm.select(oColl)
        except:
            pm.displayError("Select one object with skinCluster")
    else:
        pm.displayWarning("Select one object with skinCluster")



