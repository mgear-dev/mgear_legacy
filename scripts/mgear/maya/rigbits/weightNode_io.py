#!/usr/bin/env python
"""
import weightNode_io

# Find all the weight Nodes
weightDrivers = pm.ls(type="weightDriver")

# any filePath
testPath = r"C:\Users\rafael\Documents\maya\scripts\testWeightNodes.json"

# Export listed weightDrivers
weightNode_io.exportNodes(testPath, weightDrivers)

# import all weight drivers from filePath
weightNode_io.importNodes(testPath)

Attributes:
    CTL_SUFFIX (str): ctl suffix shared from rbf_io
    DRIVEN_SUFFIX (str): suffix shared from rbf_io
    ENVELOPE_ATTR (str): name of the attr that disables rbf node(non enum)
    RBF_TYPE (str): maya/plugin node type
    WD_SUFFIX (str): name of the suffix for this rbf node type
    WNODE_DRIVERPOSE_ATTRS (dict): attrs and their type for querying/setting
    WNODE_SHAPE_ATTRS (list): of attrs to query for re-setting on create
    WNODE_TRANSFORM_ATTRS (list): of transform attrs to record

__author__ = "Rafael Villar"
__email__ = "rav@ravrigs.com"

"""
# python
import copy
import pprint

# maya
import maya.cmds as mc
import pymel.core as pm

# rbfSetup
import rbf_io
import rbf_node

# ==============================================================================
# Constants
# ==============================================================================

CTL_SUFFIX = rbf_node.CTL_SUFFIX
DRIVEN_SUFFIX = rbf_node.DRIVEN_SUFFIX
TRANSFORM_SUFFIX = rbf_node.TRANSFORM_SUFFIX

WNODE_DRIVERPOSE_ATTRS = {"poseMatrix": "matrix",
                          "poseParentMatrix": "matrix",
                          "poseMode": "enum",
                          "controlPoseAttributes": "stringArray",
                          "controlPoseValues": "doubleArray",
                          "controlPoseRotateOrder": "enum"}

WNODE_TRANSFORM_ATTRS = ["tx",
                         "ty",
                         "tz",
                         "rx",
                         "ry",
                         "rz",
                         "sx",
                         "sy",
                         "sz",
                         "v"]

WNODE_SHAPE_ATTRS = ['visibility',
                     'type',
                     'direction',
                     'invert',
                     'useRotate',
                     'angle',
                     'centerAngle',
                     'twist',
                     'twistAngle',
                     'useTranslate',
                     'grow',
                     'translateMin',
                     'translateMax',
                     'interpolation',
                     'iconSize',
                     'drawCone',
                     'drawCenterCone',
                     'drawWeight',
                     'outWeight',
                     'twistAxis',
                     'opposite',
                     'rbfMode',
                     'useInterpolation',
                     'allowNegativeWeights',
                     'scale',
                     'distanceType',
                     'drawOrigin',
                     'drawDriver',
                     'drawPoses',
                     'drawIndices',
                     'drawTwist',
                     'poseLength',
                     'indexDistance',
                     'driverIndex']

ENVELOPE_ATTR = "scale"

WD_SUFFIX = "_WD"
RBF_TYPE = "weightDriver"
# ==============================================================================
# General utils
# ==============================================================================


# Check for plugin
def loadWeightPlugin(dependentFunc):
    """ensure that plugin is always loaded prior to importing from json

    Args:
        dependentFunc (func): any function that needs to have plugin loaded

    Returns:
        func: pass through of function
    """
    try:
        pm.loadPlugin("weightDriver", qt=True)
    except RuntimeError:
        pm.displayWarning("RBF Manager couldn't find a valid RBF solver.")

    return dependentFunc


def createRBF(name, transformName=None):
    """Creates a rbf node of type weightDriver

    Args:
        name (str): name of node
        transformName (str, optional): specify name of transform

    Returns:
        list: pymel: trasnform, weightDriverShape
    """
    if transformName is None:
        transformName = "{}{}".format(name, TRANSFORM_SUFFIX)
    wd_ShapeNode = pm.createNode(RBF_TYPE, n=name)
    wd_transform = pm.listRelatives(wd_ShapeNode, p=True)[0]
    wd_transform = pm.rename(wd_transform, transformName)
    pm.setAttr("{}.type".format(wd_ShapeNode), 1)
    return wd_transform, wd_ShapeNode


def forceEvaluation(node):
    """force evaluation of the weightDriver node
    thank you Ingo

    Args:
        node (str): weightDriver to be recached
    """
    pm.setAttr("{}.evaluate".format(node), 1)


def getNodeConnections(node):
    """get all connections on weightDriver node

    Args:
        node (str): weightDriver node

    Returns:
        list: of connections and attrs to recreate,
        small list of supported nodes to be recreated
    """
    connections = []
    attributesToRecreate = []
    nodePlugConnections = pm.listConnections(node,
                                             plugs=True,
                                             scn=True,
                                             connections=True,
                                             sourceFirst=True)

    for connectPair in nodePlugConnections:
        srcPlug = connectPair[0].name()
        srcAttrName = connectPair[0].attrName(longName=True)
        destPlug = connectPair[1].name()
        destAttrName = connectPair[1].attrName(longName=True)
        connections.append([srcPlug, destPlug])
        # expand this list as we become more aware of the node
        if srcAttrName in ["solverGroupMessage"]:
            attributesToRecreate.append([srcPlug, "message"])
        if destAttrName in ["solverGroupMessage"]:
            attributesToRecreate.append([destPlug, "message"])
    return connections, attributesToRecreate


def getRBFTransformInfo(node):
    """get a dict of all the information to be serialized to/from json

    Args:
        node (str): name of weightDriverShape node

    Returns:
        dict: information to be recreated on import
    """
    tmp_dict = {}
    parentName = None
    nodeTransform = pm.listRelatives(node, p=True)[0]
    tmp_dict["name"] = nodeTransform.name()
    transformPar = pm.listRelatives(nodeTransform, p=True) or [None]
    if transformPar[0] is not None:
        parentName = transformPar[0].name()
    tmp_dict["parent"] = parentName
    for attr in WNODE_TRANSFORM_ATTRS:
        tmp_dict[attr] = nodeTransform.getAttr(attr)
    return tmp_dict


def getIndexValue(nodePlug, indices):
    """return the values of a compound attr at the specified index

    Args:
        nodePlug (node.attr): name to compound attr
        indices (int): of the attr to get

    Returns:
        list: of indecies
    """
    allValues = []
    if indices:
        indices = range(indices[-1] + 1)
    for index in indices:
        attrPlugIdex = "{}[{}]".format(nodePlug, index)
        val = mc.getAttr(attrPlugIdex)
        allValues.append(val)
    return allValues


def lengthenCompoundAttrs(node):
    """In maya, if a compound attr has a value of 0,0,0 it will skip creating
    the attribute. So to ensure that all indecies exist in the length of a
    compound we get fake get each index, forcing a create of that attr.

    # TODO Perhaps this can turned into a more useful function since we are
    already querying info that will be needed later on.

    Args:
        node (str): weightDriver to perform insanity check

    Returns:
        n/a: n/a
    """
    poseLen = mc.getAttr("{}.poses".format(node), mi=True)
    if poseLen is None:
        return
    attrSize = mc.getAttr("{}.input".format(node), s=True)
    valSize = mc.getAttr("{}.output".format(node), s=True)
    for poseIndex in poseLen:
        for index in range(attrSize):
            nodeInput = "{}.poses[{}].poseInput[{}]".format(node,
                                                            poseIndex,
                                                            index)
            mc.getAttr(nodeInput)

    for poseIndex in poseLen:
        for index in range(valSize):
            nodeValue = "{}.poses[{}].poseValue[{}]".format(node,
                                                            poseIndex,
                                                            index)
            mc.getAttr(nodeValue)


def getPoseInfo(node):
    """Get dict of the pose info from the provided weightDriver node

    Args:
        node (str): name of weightDriver

    Returns:
        dict: of poseInput:list of values, poseValue:values
    """
    lengthenCompoundAttrs(node)
    tmp_dict = {"poseInput": [],
                "poseValue": []}
    numberOfPoses = pm.getAttr("{}.poses".format(node), mi=True) or []
    for index in numberOfPoses:
        nameAttrInput = "{0}.poses[{1}].poseInput".format(node, index)
        nameAttrValue = "{0}.poses[{1}].poseValue".format(node, index)
        poseInputIndex = pm.getAttr(nameAttrInput, mi=True) or []
        poseValueIndex = pm.getAttr(nameAttrValue, mi=True) or []
        poseInput = getIndexValue(nameAttrInput, poseInputIndex)
        poseValue = getIndexValue(nameAttrValue, poseValueIndex)
        tmp_dict["poseInput"].append(poseInput)
        tmp_dict["poseValue"].append(poseValue)

    return tmp_dict


def getDriverListInfo(node):
    """used for when live connections are supported on the weightDriver
    # TODO - Complete support

    Args:
        node (str): name of weightDriverNode

    Returns:
        dict: driver:poseValue
    """
    driver_dict = {}
    numberOfDrivers = pm.getAttr("{}.driverList".format(node), mi=True) or []
    for dIndex in numberOfDrivers:
        nameAttrDriver = "{0}.driverList[{1}].pose".format(node, dIndex)
        numberOfPoses = pm.getAttr(nameAttrDriver, mi=True) or []
        poseInfo = {}
        for pIndex in numberOfPoses:
            attrDriverPose = "{}[{}]".format(nameAttrDriver, pIndex)
            poseIndex = "pose[{}]".format(pIndex)
            tmp_dict = {}
            for key in WNODE_DRIVERPOSE_ATTRS.keys():
                attrValue = pm.getAttr("{}.{}".format(attrDriverPose, key))
                if type(attrValue) == pm.dt.Matrix:
                    attrValue = attrValue.get()
                tmp_dict[key] = attrValue
            poseInfo[poseIndex] = tmp_dict
        driver_dict["driverList[{}]".format(dIndex)] = poseInfo
    return driver_dict


def setDriverNode(node, driverNode, driverAttrs):
    """set the node that will be driving the evaluation on our poses

    Args:
        node (str): name of weightDriver node
        driverNode (str): name of driver node
        driverAttrs (list): of attributes used to perform evaluations
    """
    for index, dAttr in enumerate(driverAttrs):
        driverPlug = "{}.{}".format(driverNode, dAttr)
        nodePlug = "{}.input[{}]".format(node, index)
        mc.connectAttr(driverPlug, nodePlug, f=True)


def getDriverNode(node):
    """get nodes that are driving weightDriver node

    Args:
        node (str): weightDriver node

    Returns:
        list: of driver nodes
    """
    drivers = list(set(pm.listConnections("{}.input".format(node),
                                          scn=True)))
    if node in drivers:
        drivers.remove(node)
    drivers = [str(dNode.name()) for dNode in drivers]
    return drivers


def setDrivenNode(node, drivenNode, drivenAttrs):
    """set the node to be driven by the weightDriver

    Args:
        node (str): weightDriver node
        drivenNode (str): name of node to be driven
        drivenAttrs (list): of attributes to be driven by weightDriver
    """
    for index, dAttr in enumerate(drivenAttrs):
        nodePlug = "{}.output[{}]".format(node, index)
        drivenPlug = "{}.{}".format(drivenNode, dAttr)
        mc.connectAttr(nodePlug, drivenPlug, f=True)


def getDrivenNode(node):
    """get driven nodes connected to weightDriver

    Args:
        node (str): weightDriver node

    Returns:
        list: of driven nodes
    """
    driven = list(set(pm.listConnections("{}.output".format(node),
                                         scn=True)))
    if node in driven:
        driven.remove(node)
    driven = [str(dNode.name()) for dNode in driven]
    return driven


def getAttrInOrder(node, attrWithIndex):
    """get the connected attributes of the provided compound attr in order
    of index - Sanity check

    Args:
        node (str): weightDriver node
        attrWithIndex (str): name of compound attr with indicies to query

    Returns:
        list: of connected attrs in order
    """
    attrsToReturn = []
    attrs = mc.getAttr("{}.{}".format(node, attrWithIndex), mi=True) or []
    for index in attrs:
        nodePlug = "{}.{}[{}]".format(node, attrWithIndex, index)
        connected = pm.listConnections(nodePlug, scn=True, p=True)
        if not connected:
            continue
            connected = [None]
        attrsToReturn.append(connected[0])
    return attrsToReturn


def getDriverNodeAttributes(node):
    """get the connected attributes of the provided compound attr in order
    of index - Sanity check

    Args:
        node (str): weightDriver node

    Returns:
        list: of connected attrs in order
    """
    attributesToReturn = []
    driveAttrs = getAttrInOrder(node, "input")
    attributesToReturn = [attr.attrName(longName=True) for attr in driveAttrs
                          if attr.nodeName() != node]
    return attributesToReturn


def getDrivenNodeAttributes(node):
    """get the connected attributes of the provided compound attr in order
    of index - Sanity check

    Args:
        node (str): weightDriver node

    Returns:
        list: of connected attrs in order
    """
    attributesToReturn = []
    drivenAttrs = getAttrInOrder(node, "output")
    attributesToReturn = [attr.attrName(longName=True) for attr in drivenAttrs
                          if attr.nodeName() != node]
    return attributesToReturn


def copyPoses(nodeA, nodeB, emptyPoseValues=True):
    """Copy poses from nodeA to nodeB with the option to be blank or node
    for syncing nodes OF EQUAL LENGTH IN POSE INFO

    Args:
        nodeA (str): name of weightedNode
        nodeB (str): name of weightedNode
        emptyPoseValues (bool, optional): should the copy just be the same
        number of poses but blank output value

    Returns:
        n/a: n/a
    """
    posesIndices = pm.getAttr("{}.poses".format(nodeA), mi=True) or [None]
    if len(posesIndices) == 1 and posesIndices[0] is None:
        return
    nodeA_poseInfo = getPoseInfo(nodeA)
    drivenAttrs = getDrivenNodeAttributes(nodeB)
    nodeBdrivenIndex = range(len(drivenAttrs))
    for attr, value in nodeA_poseInfo.iteritems():
        if value == ():
            continue
        numberOfPoses = len(value)
        for poseIndex in range(numberOfPoses):
            poseValues = value[poseIndex]
            for index, pIndexValue in enumerate(poseValues):
                pathToAttr = "{}.poses[{}].{}[{}]".format(nodeB,
                                                          poseIndex,
                                                          attr,
                                                          index)
                if attr == "poseInput":
                    valueToSet = pIndexValue
                elif attr == "poseValue" and emptyPoseValues:
                    if drivenAttrs[index] in rbf_node.SCALE_ATTRS:
                        valueToSet = 1.0
                    else:
                        valueToSet = 0.0
                if index > nodeBdrivenIndex:
                    continue
                pm.setAttr(pathToAttr, valueToSet)


def syncPoseIndices(srcNode, destNode):
    """Syncs the pose indices between the srcNode and destNode.
    The input values will be copied from the srcNode, the poseValues will
    be defaulted to 0 or 1(if scaleAttr)

    Args:
        srcNode (str): weightedDriver
        destNode (str): weightedDriver
    """
    src_poseInfo = getPoseInfo(srcNode)
    destDrivenAttrs = getDrivenNodeAttributes(destNode)
    for poseIndex, piValues in enumerate(src_poseInfo["poseInput"]):
        for index, piValue in enumerate(piValues):
            pathToAttr = "{}.poses[{}].poseInput[{}]".format(destNode,
                                                             poseIndex,
                                                             index)
            pm.setAttr(pathToAttr, piValue)

    for poseIndex, piValues in enumerate(src_poseInfo["poseValue"]):
        for index, piValAttr in enumerate(destDrivenAttrs):
            pathToAttr = "{}.poses[{}].poseValue[{}]".format(destNode,
                                                             poseIndex,
                                                             index)
            if piValAttr in rbf_node.SCALE_ATTRS:
                valueToSet = 1.0
            else:
                valueToSet = 0.0
            pm.setAttr(pathToAttr, valueToSet)


def getNodeInfo(node):
    """get a dictionary of all the serialized information from the desired
    weightDriver node for export/import/duplication

    Args:
        node (str): name of weightDriver node

    Returns:
        dict: collected node info
    """
    node = pm.PyNode(node)
    weightNodeInfo_dict = {}
    for attr in WNODE_SHAPE_ATTRS:
        weightNodeInfo_dict[attr] = node.getAttr(attr)
    weightNodeInfo_dict["transformNode"] = getRBFTransformInfo(node)
    connections, attributesToRecreate = getNodeConnections(node)
    weightNodeInfo_dict["connections"] = connections
    weightNodeInfo_dict["attributesToRecreate"] = attributesToRecreate
    weightNodeInfo_dict["poses"] = getPoseInfo(node)
    # is an attribute on the weightedDriver node
    weightNodeInfo_dict["driverList"] = getDriverListInfo(node)
    # actual source node that is driving the poses on node
    weightNodeInfo_dict["driverNode"] = getDriverNode(node)
    # attr on driver node pushing the poses
    weightNodeInfo_dict["driverAttrs"] = getDriverNodeAttributes(node)
    # node being driven by the setup
    weightNodeInfo_dict["drivenNode"] = getDrivenNode(node)
    # node.attrs being driven by the setup
    weightNodeInfo_dict["drivenAttrs"] = getDrivenNodeAttributes(node)
    driverContol = rbf_node.getDriverControlAttr(node.name())
    weightNodeInfo_dict["driverControl"] = driverContol
    weightNodeInfo_dict["setupName"] = rbf_node.getSetupName(node.name())
    drivenControlName = rbf_node.getConnectedRBFToggleNode(node.name(),
                                                           ENVELOPE_ATTR)
    weightNodeInfo_dict["drivenControlName"] = drivenControlName
    weightNodeInfo_dict["rbfType"] = RBF_TYPE
    driverPosesInfo = rbf_node.getDriverControlPoseAttr(node.name())
    weightNodeInfo_dict[rbf_node.DRIVER_POSES_INFO_ATTR] = driverPosesInfo
    return weightNodeInfo_dict


def setTransformNode(transformNode, transformInfo):
    """set the transform node of a weightedDriver with the information from
    dict

    Args:
        transformNode (str): name of transform nodes
        transformInfo (dict): information to set on transform node
    """
    parent = transformInfo.pop("parent", None)
    if parent is not None:
        pm.parent(transformNode, parent)
    for attr, value in transformInfo.iteritems():
        # transformNode.setAttr(attr, value)
        pm.setAttr("{}.{}".format(transformNode, attr), value)


def deletePose(node, indexToPop):
    """gather information on node, remove desired index and reapply

    Args:
        node (str): weightDriver
        indexToPop (int): pose index to remove
    """
    node = pm.PyNode(node)
    posesInfo = getPoseInfo(node)
    poseInput = posesInfo["poseInput"]
    poseValue = posesInfo["poseValue"]
    currentLength = range(len(poseInput))
    poseInput.pop(indexToPop)
    poseValue.pop(indexToPop)
    setPosesFromInfo(node, posesInfo)
    attrPlug = "{}.poses[{}]".format(node, currentLength[-1])
    pm.removeMultiInstance(attrPlug, b=True)


def addPose(node, poseInput, poseValue, posesIndex=None):
    """add pose to the weightDriver node provided. Also used for editing an
    existing pose, since you can specify the index. If non provided assume new

    Args:
        node (str): weightedDriver
        poseInput (list): list of the poseInput values
        poseValue (list): of poseValue values
        posesIndex (int, optional): at desired index, if none assume latest/new
    """
    if posesIndex is None:
        posesIndex = len(pm.getAttr("{}.poses".format(node), mi=True) or [])

    for index, value in enumerate(poseInput):
        attrPlug = "{}.poses[{}].poseInput[{}]".format(node, posesIndex, index)
        pm.setAttr(attrPlug, value)

    for index, value in enumerate(poseValue):
        attrPlug = "{}.poses[{}].poseValue[{}]".format(node, posesIndex, index)
        pm.setAttr(attrPlug, value)


def setPosesFromInfo(node, posesInfo):
    """set a large number of poses from the dictionary provided

    Args:
        node (str): weightDriver
        posesInfo (dict): of poseInput/PoseValue:values
    """
    for attr, value in posesInfo.iteritems():
        if value == ():
            continue
        numberOfPoses = len(value)
        for poseIndex in range(numberOfPoses):
            poseValues = value[poseIndex]
            for index, pIndexValue in enumerate(poseValues):
                pathToAttr = "poses[{}].{}[{}]".format(poseIndex,
                                                       attr,
                                                       index)
                node.setAttr(pathToAttr, pIndexValue)


def setDriverListFromInfo(node, driverListInfo):
    """set driverlist node with information from dict proivided

    Args:
        node (pynode): name of driver node
        driverListInfo (dict): attr/value
    """
    for attr, posesInfo in driverListInfo.iteritems():
        # attrDriver = "{}.pose".format(attr)
        numberOfPoses = len(posesInfo.keys())
        for pIndex in range(numberOfPoses):
            poseIndex = "pose[{}]".format(pIndex)
            poseAttrIndex = "{}.{}".format(attr, poseIndex)
            for driverAttr, attrType in WNODE_DRIVERPOSE_ATTRS.iteritems():
                fullPathToAttr = "{}.{}".format(poseAttrIndex, driverAttr)
                attrValue = posesInfo[poseIndex][driverAttr]
                if attrType == "enum":
                    node.setAttr(fullPathToAttr, attrValue)
                elif attrType == "matrix":
                    attrValue = pm.dt.Matrix(attrValue)
                    node.setAttr(fullPathToAttr, attrValue, type=attrType)
                else:
                    node.setAttr(fullPathToAttr, attrValue, type=attrType)


def setWeightNodeAttributes(node, weightNodeAttrInfo):
    """set the attribute information on the weightDriver node provided from
    the info dict

    Args:
        node (pynode): name of weightDrivers
        weightNodeAttrInfo (dict): of attr:value
    """
    failedAttrSets = []
    for attr, value in weightNodeAttrInfo.iteritems():
        try:
            pm.setAttr("{}.{}".format(node, attr), value)
        except Exception as e:
            failedAttrSets.append([attr, value, e])
    if failedAttrSets:
        pprint.pprint(failedAttrSets)


def createVectorDriver(driverInfo):
    # future vector driver support starts here
    pass


def recreateAttributes(node, attributesToRecreate):
    """add any attributes to the provided node from list

    Args:
        node (str): name of node
        attributesToRecreate (list): of attrs to add
    """
    for attrInfo in attributesToRecreate:
        attrPlug = attrInfo[0]
        attrType = attrInfo[1]
        attrName = attrPlug.split(".")[1]
        if pm.objExists(attrPlug):
            continue
        pm.addAttr(node, ln=attrName, at=attrType)


def recreateConnections(connectionsInfo):
    """recreate connections from dict

    Args:
        connectionsInfo (dict): of nodes.attr plugs to try and recreate
    """
    failedConnections = []
    for attrPair in connectionsInfo:
        try:
            pm.connectAttr(attrPair[0], attrPair[1], f=True)
        except Exception as e:
            failedConnections.append([attrPair, e])
    if failedConnections:
        print "The Following Connections failed..."
        pprint.pprint(failedConnections)


@loadWeightPlugin
def createRBFFromInfo(weightNodeInfo_dict):
    """create an rbf node from the dictionary provided information

    Args:
        weightNodeInfo_dict (dict): of weightDriver information

    Returns:
        list: of all created weightDriver nodes
    """
    createdNodes = []
    weightNodeInfo_dict = copy.deepcopy(weightNodeInfo_dict)
    for weightNodeName, weightInfo in weightNodeInfo_dict.iteritems():
        rbfType = weightInfo.pop("rbfType", RBF_TYPE)
        connectionsInfo = weightInfo.pop("connections", {})
        posesInfo = weightInfo.pop("poses", {})
        transformNodeInfo = weightInfo.pop("transformNode", {})
        driverListInfo = weightInfo.pop("driverList", {})
        attributesToRecreate = weightInfo.pop("attributesToRecreate", [])
        # hook for future support of vector
        driverInfo = weightInfo.pop("vectorDriver", {})
        driverNodeName = weightInfo.pop("driverNode", {})
        driverNodeAttributes = weightInfo.pop("driverAttrs", {})
        drivenNodeName = weightInfo.pop("drivenNode", {})
        drivenNodeAttributes = weightInfo.pop("drivenAttrs", {})
        transformName = transformNodeInfo.pop("name", None)
        setupName = weightInfo.pop("setupName", "")
        drivenControlName = weightInfo.pop("drivenControlName", "")
        driverControl = weightInfo.pop("driverControl", "")
        driverControlPoseInfo = weightInfo.pop(rbf_node.DRIVER_POSES_INFO_ATTR,
                                               {})
        transformNode, node = createRBF(weightNodeName,
                                        transformName=transformName)
        rbf_node.setSetupName(node.name(), setupName)
        if drivenNodeName and drivenNodeName[0].endswith(DRIVEN_SUFFIX):
            rbf_node.addDrivenGroup(drivenControlName)
        rbf_node.createRBFToggleAttr(drivenControlName)
        rbf_node.setDriverControlAttr(node.name(), driverControl)
        setTransformNode(transformNode, transformNodeInfo)
        setWeightNodeAttributes(node, weightInfo)
        recreateAttributes(node, attributesToRecreate)
        setPosesFromInfo(node, posesInfo)
        setDriverListFromInfo(node, driverListInfo)
        createVectorDriver(driverInfo)
        rbf_node.setDriverControlPoseAttr(node.name(), driverControlPoseInfo)
        recreateConnections(connectionsInfo)
        createdNodes.append(node.name())
    return createdNodes


def getNodesInfo(weightDriverNodes):
    """convenience function to get a dict of all the provided nodes

    Args:
        weightDriverNodes (list): names of all weightDriver nodes

    Returns:
        dict: collected serialized informtiaon
    """
    weightNodeInfo_dict = {}
    for wdNode in weightDriverNodes:
        wdNode = pm.PyNode(wdNode)
        weightNodeInfo_dict[wdNode.name()] = getNodeInfo(wdNode)
    return weightNodeInfo_dict


def exportNodes(filePath, weightDriverNodes):
    """export serialized node information to the specified filepath

    Args:
        filePath (str): path/to/file.ext
        weightDriverNodes (list): of weightDriver nodes
    """
    weightNodeInfo_dict = getNodesInfo(weightDriverNodes)
    rbf_io._exportData(weightNodeInfo_dict, filePath)
    print "Weight Driver Nodes successfully exported: {}".format(filePath)


def importNodes(filePath):
    """create nodes from serialized data from the provided json filepath

    Args:
        filePath (str): path/to/file
    """
    weightNodeInfo_dict = rbf_io._importData(filePath)
    createRBFFromInfo(weightNodeInfo_dict)


class RBFNode(rbf_node.RBFNode):
    """when subclassed everything that need be overrided is information
    specific to the module rbf node.

    Attributes:
        name (str): name of the node that either exists or to be created
        rbfType (str): nodeType to create node of supported type
        transformNode (str): name of transform node
    """

    def __init__(self, name):
        self.rbfType = RBF_TYPE
        super(RBFNode, self).__init__(name)

    def nodeType_suffix(self):
        return WD_SUFFIX

    def create(self):
        name = self.formatName()
        transformNode, node = createRBF(name)
        self.transformNode = transformNode.name()
        self.name = node.name()

    def getPoseInfo(self):
        return getPoseInfo(self.name)

    def getNodeInfo(self):
        return getNodeInfo(pm.PyNode(self.name))

    def lengthenCompoundAttrs(self):
        lengthenCompoundAttrs(self.name)

    def addPose(self, poseInput, poseValue, posesIndex=None):
        if posesIndex is None:
            posesIndex = len(self.getPoseInfo()["poseInput"])
        self.updateDriverControlPoseAttr(posesIndex)
        addPose(self.name,
                poseInput,
                poseValue,
                posesIndex=posesIndex)

    def deletePose(self, indexToPop):
        deletePose(self.name, indexToPop)

    def getDriverNode(self):
        return getDriverNode(self.name)

    def getDriverNodeAttributes(self):
        return getDriverNodeAttributes(self.name)

    def getDrivenNode(self):
        return getDrivenNode(self.name)

    def getDrivenNodeAttributes(self):
        return getDrivenNodeAttributes(self.name)

    def getTransformParent(self):
        return getRBFTransformInfo(self)["name"]

    def setDriverNode(self, driverNode, driverAttrs):
        setDriverNode(self.name, driverNode, driverAttrs)

    def setDrivenNode(self, drivenNode, drivenAttrs, parent=True):
        setDrivenNode(self.name, drivenNode, drivenAttrs)
        if parent:
            mc.parent(self.transformNode, drivenNode)
        if drivenNode.endswith(DRIVEN_SUFFIX):
            drivenControlName = drivenNode.replace(DRIVEN_SUFFIX, CTL_SUFFIX)
            if not mc.objExists(drivenControlName):
                return
            rbf_node.createRBFToggleAttr(drivenControlName)
            rbf_node.connectRBFToggleAttr(drivenControlName,
                                          self.name,
                                          self.getRBFToggleAttr())

    def copyPoses(self, nodeB):
        poseInfo = self.getDriverControlPoseAttr()
        nodeB.setDriverControlPoseAttr(poseInfo)
        copyPoses(self.name, nodeB)

    def forceEvaluation(self):
        forceEvaluation(self.transformNode)

    def getRBFToggleAttr(self):
        return ENVELOPE_ATTR

    def syncPoseIndices(self, srcNode):
        poseInfo = srcNode.getDriverControlPoseAttr()
        self.setDriverControlPoseAttr(poseInfo)
        syncPoseIndices(srcNode, self.name)
