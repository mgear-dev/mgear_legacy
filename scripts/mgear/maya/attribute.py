"""Attribute creation functions"""

#############################################
# GLOBAL
#############################################
import collections
import mgear
import pymel.core as pm
import maya.cmds as cmds
import pymel.core.datatypes as datatypes


#############################################
# NODE
#############################################

def addAttribute(node,
                 longName,
                 attributeType,
                 value=None,
                 niceName=None,
                 shortName=None,
                 minValue=None,
                 maxValue=None,
                 keyable=True,
                 readable=True,
                 storable=True,
                 writable=True,
                 channelBox=False):
    """Add attribute to a node

    Arguments:
        node (dagNode): The object to add the new attribute.
        longName (str): The attribute name.
        attributeType (str): The Attribute Type. Exp: 'string', 'bool',
            'long', etc..
        value (float or int): The default value.
        niceName (str): The attribute nice name. (optional)
        shortName (str): The attribute short name. (optional)
        minValue (float or int): minimum value. (optional)
        maxValue (float or int): maximum value. (optional)
        keyable (bool): Set if the attribute is keyable or not. (optional)
        readable (bool): Set if the attribute is readable or not. (optional)
        storable (bool): Set if the attribute is storable or not. (optional)
        writable (bool): Set if the attribute is writable or not. (optional)
        channelBox (bool): Set if the attribute is in the channelBox or not,
            when the attribute is not keyable. (optional)

    Returns:
        str: The long name of the new attribute
    """
    if node.hasAttr(longName):
        mgear.log("Attribute already exists", mgear.sev_error)
        return

    data = {}

    if shortName is not None:
        data["shortName"] = shortName
    if niceName is not None:
        data["niceName"] = niceName
    if attributeType == "string":
        data["dataType"] = attributeType
    else:
        data["attributeType"] = attributeType

    if minValue is not None and minValue is not False:
        data["minValue"] = minValue
    if maxValue is not None and maxValue is not False:
        data["maxValue"] = maxValue

    data["keyable"] = keyable
    data["readable"] = readable
    data["storable"] = storable
    data["writable"] = writable

    if value is not None and attributeType not in ["string"]:
        data["defaultValue"] = value

    node.addAttr(longName, **data)

    if value is not None:
        node.setAttr(longName, value)

    if channelBox:
        node.attr(longName).set(channelBox=True)
    return node.attr(longName)


def addColorAttribute(node,
                      longName,
                      value=False,
                      keyable=True,
                      readable=True,
                      storable=True,
                      writable=True,
                      niceName=None,
                      shortName=None):
    """
    Add a color attribute to a node

    Arguments:
        node (dagNode): The object to add the new attribute.
        longName (str): The attribute name.
        value (list of flotat): The default value in a list for RGB.
            exp [1.0, 0.99, 0.13].
        keyable (bool): Set if the attribute is keyable or not. (optional)
        readable (bool): Set if the attribute is readable or not. (optional)
        storable (bool): Set if the attribute is storable or not. (optional)
        writable (bool): Set if the attribute is writable or not. (optional)
        niceName (str): The attribute nice name. (optional)
        shortName (str): The attribute short name. (optional)

    Returns:
        str: The long name of the new attribute

    """
    if node.hasAttr(longName):
        mgear.log("Attribute already exists", mgear.error)
        return

    data = {}

    data["attributeType"] = "float3"
    if shortName is not None:
        data["shortName"] = shortName
    if niceName is not None:
        data["niceName"] = niceName

    data["usedAsColor"] = True
    data["keyable"] = keyable
    data["readable"] = readable
    data["storable"] = storable
    data["writable"] = writable

    # child nested attr
    dataChild = {}
    dataChild["attributeType"] = 'float'
    dataChild["parent"] = longName

    node.addAttr(longName, **data)
    node.addAttr(longName + "_r", **dataChild)
    node.addAttr(longName + "_g", **dataChild)
    node.addAttr(longName + "_b", **dataChild)

    if value:
        node.setAttr(longName + "_r", value[0])
        node.setAttr(longName + "_g", value[1])
        node.setAttr(longName + "_b", value[2])

    return node.attr(longName)


def addEnumAttribute(node,
                     longName,
                     value,
                     enum,
                     niceName=None,
                     shortName=None,
                     keyable=True,
                     readable=True,
                     storable=True,
                     writable=True):
    """
    Add an enumerate attribute to a node

    Arguments:
        node (dagNode): The object to add the new attribute.
        longName (str): The attribute name.
        value (int): The default value.
        enum (list of str): The list of elements in the enumerate control
        niceName (str): The attribute nice name. (optional)
        shortName (str): The attribute short name. (optional)
        keyable (bool): Set if the attribute is keyable or not. (optional)
        readable (bool): Set if the attribute is readable or not. (optional)
        storable (bool): Set if the attribute is storable or not. (optional)
        writable (bool): Set if the attribute is writable or not. (optional)

    Returns:
        str: The long name of the new attribute
    """

    if node.hasAttr(longName):
        mgear.log("Attribute '" + longName + "' already exists",
                  mgear.sev_warning)
        return

    data = {}

    if shortName is not None:
        data["shortName"] = shortName
    if niceName is not None:
        data["niceName"] = niceName

    data["attributeType"] = "enum"
    data["en"] = ":".join(enum)

    data["keyable"] = keyable
    data["readable"] = readable
    data["storable"] = storable
    data["writable"] = writable

    node.addAttr(longName, **data)
    node.setAttr(longName, value)

    return node.attr(longName)


def addProxyAttribute(sourceAttrs, targets, duplicatedPolicy=None):
    """Add proxy paramenter to a list of target dagNode
    Duplicated channel policy, stablish the rule in case the channel already
    exist on the target.

    Duplicate policy options

    ================    =======================================================
    index               This policy will add an index to avoid clashing channel
                        names
    fullName            This policy will add the name of the source object to
                        the channel
    merge               This policy will merge the channels
    ================    =======================================================

    Arguments:
        sourceAttrs (attr or list of attr): The parameters to be connected as
            proxy
        targets (dagNode or list of dagNode): The list of dagNode to add the
            proxy paramenter
        duplicatedPolicy (string, optional): Set the duplicated channel policy
    """
    if not isinstance(targets, list):
        targets = [targets]
    if not isinstance(sourceAttrs, list):
        sourceAttrs = [sourceAttrs]
    for sourceAttr in sourceAttrs:
        for target in targets:
            attrName = sourceAttr.longName()
            if target.hasAttr(sourceAttr.longName()):
                if duplicatedPolicy == "index":
                    i = 0
                    while target.hasAttr(sourceAttr.longName() + str(i)):
                        i += 1
                    attrName = sourceAttr.longName() + str(i)
                elif duplicatedPolicy == "fullName":
                    attrName = "{}_{}".format(sourceAttr.nodeName(),
                                              sourceAttr.longName())

            if not target.hasAttr(attrName):
                target.addAttr(attrName, pxy=sourceAttr)
            else:
                pm.displayWarning(
                    "The proxy channel %s already exist on: %s."
                    % (sourceAttr.longName(), target.name()))


def moveChannel(attr, sourceNode, targetNode, duplicatedPolicy=None):
    """Move channels  keeping the output connections.
    Duplicated channel policy, stablish the rule in case the channel already
    exist on the target.

    NOTE: For the moment move channel only supports type double and enum

    Duplicate policy options

    ================    =======================================================
    index               This policy will add an index to avoid clashing channel
                        names
    fullName            This policy will add the name of the source object to
                        the channel
    merge               This policy will merge the channels
    ================    =======================================================

    Arguments:
        attr (str): Name of the channel to move
        sourceNode (PyNoe or str): The source node with the channel
        targetNode (PyNoe or str): The target node for the channel
        duplicatedPolicy (None, str): Set the duplicated channel policy
    """
    if isinstance(sourceNode, str):
        sourceNode = pm.PyNode(sourceNode)
    if isinstance(targetNode, str):
        targetNode = pm.PyNode(targetNode)

    try:
        at = sourceNode.attr(attr)
        if pm.addAttr(at, q=True, usedAsProxy=True):
            pm.displayWarning("{} is a proxy channel and move operation is "
                              "not yet supported.".format(attr))
            return
    except Exception:
        pm.displayWarning("Looks like the {} is not in the"
                          " source: {}".format(attr, sourceNode.name()))
        return
    atType = at.type()
    if atType in ["double", "enum"]:

        newAtt = None
        attrName = attr
        nName = pm.attributeQuery(
            at.shortName(), node=at.node(), niceName=True)
        # define duplicated attribute policy
        if sourceNode.name() != targetNode.name():
            # this policy doesn't apply for rearrange channels
            if pm.attributeQuery(attr, node=targetNode, exists=True):
                if duplicatedPolicy == "index":
                    i = 0
                    while targetNode.hasAttr(attr + str(i)):
                        i += 1
                    attrName = attr + str(i)
                elif duplicatedPolicy == "fullName":
                    attrName = "{}_{}".format(sourceNode.name(), attr)

                elif duplicatedPolicy == "merge":
                    newAtt = pm.PyNode(".".join([targetNode.name(), attr]))

                else:
                    pm.displayWarning("Duplicated channel policy, is not "
                                      "defined. Move channel operation will "
                                      "fail if the channel already exist on "
                                      "the target.")
                    return False

        outcnx = at.listConnections(p=True)
        if not newAtt:
            # get the attr data
            value = at.get()
            if atType == "double":
                kwargs = {}
                min = at.getMin()
                if min:
                    kwargs["min"] = min
                max = at.getMax()
                if max:
                    kwargs["max"] = max
            elif atType == "enum":
                en = at.getEnums()
                oEn = collections.OrderedDict(sorted(en.items(),
                                                     key=lambda t: t[1]))
                enStr = ":".join([n for n in oEn])

            # delete old attr
            pm.deleteAttr(at)

            # rebuild the attr
            if atType == "double":
                pm.addAttr(targetNode,
                           ln=attrName,
                           niceName=nName,
                           at="double",
                           dv=value,
                           k=True,
                           **kwargs)
            elif atType == "enum":
                pm.addAttr(targetNode,
                           ln=attrName,
                           niceName=nName,
                           at="enum",
                           en=enStr,
                           dv=value,
                           k=True)

            newAtt = pm.PyNode(".".join([targetNode.name(), attrName]))
        else:
            pm.deleteAttr(at)

        for cnx in outcnx:
            try:
                pm.connectAttr(newAtt, cnx, f=True)
            except RuntimeError:
                pm.displayError("There is a problem connecting the "
                                "channel %s  maybe is already move? Please "
                                "check your configuration" % newAtt.name())

    else:
        pm.displayWarning("MoveChannel function can't handle an attribute "
                          "of type: %s. Only supported 'double' adn 'enum' "
                          "types." % atType)


def lockAttribute(node,
                  attributes=["tx", "ty", "tz",
                              "rx", "ry", "rz",
                              "sx", "sy", "sz",
                              "v"]):
    """Lock attributes of a node.

    By defaul will lock the rotation, scale and translation.

    Arguments:
        node(dagNode): The node with the attributes to lock.
        attributes (list of str): The list of the attributes to lock.

    Example:
        >>> att.lockAttribute(self.root_ctl, ["sx", "sy", "sz", "v"])

    """
    _lockUnlockAttribute(node, attributes, lock=True, keyable=False)


def unlockAttribute(node,
                    attributes=["tx", "ty", "tz",
                                "rx", "ry", "rz",
                                "sx", "sy", "sz",
                                "v"]):
    """Unlock attributes of a node.

    By defaul will unlock the rotation, scale and translation.

    Arguments:
        node(dagNode): The node with the attributes to unlock.
        attributes (list of str): The list of the attributes to unlock.

    Example:
        >>> att.unlockAttribute(self.root_ctl, ["sx", "sy", "sz", "v"])

    """
    _lockUnlockAttribute(node, attributes, lock=False, keyable=True)


def _lockUnlockAttribute(node, attributes, lock, keyable):
    """Lock or unlock attributes of a node.

    Arguments:
        node(dagNode): The node with the attributes to lock/unlock.
        attributes (list of str): The list of the attributes to lock/unlock.

    """
    if not isinstance(attributes, list):
        attributes = [attributes]

    for attr_name in attributes:
        node.setAttr(attr_name, lock=lock, keyable=keyable)


def setKeyableAttributes(nodes,
                         params=["tx", "ty", "tz",
                                 "ro", "rx", "ry", "rz",
                                 "sx", "sy", "sz"]):
    """Set keyable attributes of a node.

    By defaul will set keyable the rotation, scale and translation.

    Arguments:
        node(dagNode): The node with the attributes to set keyable.
        attributes (list of str): The list of the attributes to set keyable.
            Attrs not in the list will be locked
            if None, ["tx", "ty", "tz", "rorder", "rx", "ry", "rz", "sx", "sy",
                "sz"] is used

    """

    localParams = ["tx", "ty", "tz",
                   "ro", "rx", "ry", "rz",
                   "sx", "sy", "sz",
                   "v"]

    if not isinstance(nodes, list):
        nodes = [nodes]

    for attr_name in params:
        for node in nodes:
            node.setAttr(attr_name, lock=False, keyable=True)

    for attr_name in localParams:
        if attr_name not in params:
            for node in nodes:
                node.setAttr(attr_name, lock=True, keyable=False)


def setNotKeyableAttributes(nodes,
                            attributes=["tx", "ty", "tz",
                                        "ro", "rx", "ry", "rz",
                                        "sx", "sy", "sz",
                                        "v"]):
    """Set not keyable attributes of a node.

    By defaul will set not keyable the rotation, scale and translation.

    Arguments:
        node(dagNode): The node with the attributes to set keyable.
        attributes (list of str): The list of the attributes to set not keyable
    """

    if not isinstance(nodes, list):
        nodes = [nodes]

    for attr_name in attributes:
        for node in nodes:
            node.setAttr(attr_name, lock=False, keyable=False, cb=True)


def setRotOrder(node, s="XYZ"):
    """Set the rotorder of the object.

    Arguments:
        node (dagNode): The object to set the rot order on.
        s (str): Value of the rotorder.
            Possible values : ("XYZ", "XZY", "YXZ", "YZX", "ZXY", "ZYX")
    """

    a = ["XYZ", "YZX", "ZXY", "XZY", "YXZ", "ZYX"]

    if s not in a:
        mgear.log("Invalid Rotorder : " + s, mgear.siError)
        return False

    # Unless Softimage there is no event on the rotorder parameter to
    # automatically adapt the angle values
    # So let's do it manually using the EulerRotation class

    er = datatypes.EulerRotation([pm.getAttr(node + ".rx"),
                                  pm.getAttr(node + ".ry"),
                                  pm.getAttr(node + ".rz")],
                                 unit="degrees")
    er.reorderIt(s)

    node.setAttr("ro", a.index(s))
    node.setAttr("rotate", er.x, er.y, er.z)


def setInvertMirror(node, invList=None):
    """Set invert mirror pose values

    Arguments:
        node (dagNode): The object to set invert mirror Values

    """

    aDic = {"tx": "invTx",
            "ty": "invTy",
            "tz": "invTz",
            "rx": "invRx",
            "ry": "invRy",
            "rz": "invRz",
            "sx": "invSx",
            "sy": "invSy",
            "sz": "invSz"}

    for axis in invList:
        if axis not in aDic:
            mgear.log("Invalid Invert Axis : " + axis, mgear.siError)
            return False

        node.setAttr(aDic[axis], True)


def addFCurve(node, name="fcurve", keys=[]):
    """FCurve attribute

    Just a animCurveUU node connected to an attribute

    Warning:
        This Method is deprecated.

    Arguments:
        node (dagNode): The object to add the new fcurve attribute
        name (str): The attribute name
        key (list): list of keyframes and values

    Returns:
        Fcurve and attribute name

    """
    attr_name = addAttribute(node, name, "double", 0)
    attrDummy_name = addAttribute(node, name + "_dummy", "double", 0)

    for key in keys:
        # we use setDrivenKeyframe, because is the only workaround that I found
        # to create an animCurveUU with keyframes
        pm.setDrivenKeyframe(attr_name,
                             cd=attrDummy_name,
                             dv=key[0],
                             v=key[1],
                             itt=key[2],
                             ott=key[2])

    # clean dummy attr
    pm.deleteAttr(attrDummy_name)

    fCurve = pm.PyNode(attr_name).listConnections(type="animCurveUU")[0]

    return fCurve, attr_name

##########################################################
# PARAMETER DEFINITION
##########################################################


class ParamDef(object):
    """ParamDef (read as Parameter Definition)

    Encapsulate the attribute creation arguments in a handy object.
    Also include a creation method.

    Example:
        This can be use later to create attr or export the description to xml
        or json file

     Arguments:
        scriptName (str): Attribute fullName
        paranDef (dic): The stored param definition

    """

    def __init__(self, scriptName):

        self.scriptName = scriptName
        self.value = None
        self.valueType = None

    def create(self, node):
        """Add a parameter to property using the parameter definition.

        Arguments:
            node (dagNode): The node to add the attribute
        """
        attr_name = addAttribute(node,
                                 self.scriptName,
                                 self.valueType,
                                 self.value,
                                 self.niceName,
                                 self.shortName,
                                 self.minimum,
                                 self.maximum,
                                 self.keyable,
                                 self.readable,
                                 self.storable,
                                 self.writable)

        return node, attr_name


class ParamDef2(ParamDef):
    """ParamDef2 inherit from ParamDef

    Arguments:
        scriptName (str): Parameter scriptname.
        valueType (str): The Attribute Type. Exp: 'string', 'bool',
            'long', etc..
        value (float or int): Default parameter value.
        niceName (str): Parameter niceName.
        shortName (str): Parameter shortName.
        minimum (float or int): mininum value.
        maximum (float or int): maximum value.
        keyable (boo): If true is keyable
        readable (boo): If true is readable
        storable (boo): If true is storable
        writable (boo): If true is writable

    Returns:
        ParamDef: The stored parameter definition.

    """

    def __init__(self,
                 scriptName,
                 valueType,
                 value,
                 niceName=None,
                 shortName=None,
                 minimum=None,
                 maximum=None,
                 keyable=True,
                 readable=True,
                 storable=True,
                 writable=True):

        self.scriptName = scriptName
        self.niceName = niceName
        self.shortName = shortName
        self.valueType = valueType
        self.value = value
        self.minimum = minimum
        self.maximum = maximum
        self.keyable = keyable
        self.readable = readable
        self.storable = storable
        self.writable = writable


class FCurveParamDef(ParamDef):
    """Create an Fcurve parameter definition.

    Arguments:
        scriptName (str): Attribute fullName.
        keys (list): The keyframes to define the function curve.
        interpolation (int): the curve interpolation.
        extrapolation (int): the curve extrapolation.

    """

    def __init__(self,
                 scriptName,
                 keys=None,
                 interpolation=0,
                 extrapolation=0):

        self.scriptName = scriptName
        self.keys = keys
        self.interpolation = interpolation
        self.extrapolation = extrapolation
        self.value = None
        self.valueType = None

    def create(self, node):
        """Add a parameter to property using the parameter definition.

        Arguments:
            node (dagNode): The node to add the attribute

        """
        attr_name = addAttribute(node, self.scriptName, "double", 0)

        attrDummy_name = addAttribute(
            node, self.scriptName + "_dummy", "double", 0)

        for key in self.keys:
            pm.setDrivenKeyframe(
                attr_name, cd=attrDummy_name, dv=key[0], v=key[1])

        # clean dummy attr
        pm.deleteAttr(attrDummy_name)

        return node, attr_name


class colorParamDef(ParamDef):
    """Create a Color parameter definition.

    Arguments:
        scriptName (str): Attribute fullName
        value (list of float): The default value in a list for RGB.
            exp [1.0, 0.99, 0.13].

    """

    def __init__(self, scriptName, value=False):

        self.scriptName = scriptName
        self.value = value

    def create(self, node):
        """Add a parameter to property using the parameter definition.

        Arguments:
            node (dagNode): The node to add the attribute

        """
        attr_name = addColorAttribute(node, self.scriptName, value=self.value)

        return node, attr_name


class enumParamDef(ParamDef):
    """Create an enumarator parameter definition.

    Arguments:
        scriptName (str): Attribute fullName
        enum (list of str): The list of elements in the enumerate control.
        value (int): The default value.

    """

    def __init__(self, scriptName, enum, value=False):

        self.scriptName = scriptName
        self.value = value
        self.enum = enum
        self.valueType = None

    def create(self, node):
        """Add a parameter to property using the parameter definition.

        Arguments:
            node (dagNode): The node to add the attribute

        """
        attr_name = addEnumAttribute(
            node, self.scriptName, enum=self.enum, value=self.value)

        return node, attr_name


##########################################################
# Default Values functions
##########################################################

def get_default_value(node, attribute):
    """Get the default attribute value

    Args:
        node (str, PyNode): The object with the attribute
        attribute (str): The attribute to get the value

    Returns:
        variant: The attribute value
    """
    return pm.attributeQuery(attribute,
                             node=node,
                             listDefault=True)[0]


def set_default_value(node, attribute):
    """Set the default value to the attribute

    Args:
        node (str, PyNode): The object with the attribute to reset
        attribute (str): The attribute to reset
    """
    if not isinstance(node, pm.PyNode):
        node = pm.PyNode(node)

    defVal = get_default_value(node, attribute)
    try:
        node.attr(attribute).set(defVal)
    except RuntimeError:
        pass


def reset_selected_channels_value(objects=None, attributes=None):
    """Reset the the selected channels if not attribute is provided

    Args:
        objects (None, optional): The objects to reset the channels
        attribute (list, optional): The attribute to reset
    """
    if not objects:
        objects = cmds.ls(selection=True)
    if not attributes:
        attributes = getSelectedChannels()

    for obj in objects:
        for attr in attributes:
            set_default_value(obj, attr)


def reset_SRT(objects=None,
              attributes=["tx", "ty", "tz",
                          "rx", "ry", "rz",
                          "sx", "sy", "sz",
                          "v"]):
    """Reset Scale Rotation and translation attributes to default value

    Args:
        objects (None, optional): The objects to reset the channels
        attribute (list): The attribute to reset
    """
    reset_selected_channels_value(objects, attributes)


def smart_reset(*args):
    """Reset the SRT or the selected channels

    Checks first if we have channels selected. If not, will try to reset SRT

    Args:
        *args: Dummy
    """
    attributes = getSelectedChannels()
    if attributes:
        reset_selected_channels_value(objects=None, attributes=attributes)
    else:
        reset_SRT()

##########################################################
# GETTERS
##########################################################


def getSelectedChannels(userDefine=False):
    """Get the selected channels on the channel box

    Arguments:
        userDefine (bool, optional): If True, will return only the user
            defined channels. Other channels will be skipped.

    Returns:
        list: The list of selected channels names

    """
    # fetch maya's main channelbox
    mel_str = 'global string $gChannelBoxName; $temp=$gChannelBoxName;'
    channelBox = pm.mel.eval(mel_str)
    attrs = pm.channelBox(channelBox, q=True, sma=True)
    if userDefine:
        oSel = pm.selected()[0]
        uda = oSel.listAttr(ud=True)
        if attrs:
            attrs = [x for x in attrs if oSel.attr(x) in uda]
        else:
            return None

    return attrs


def getSelectedObjectChannels(oSel=None, userDefine=False, animatable=False):
    """Get the selected object channels.

    Arguments:
        oSel (None, optional): The  pynode with channels to get
        userDefine (bool, optional): If True, will return only the user
            defined channels. Other channels will be skipped.
        animatable (bool, optional): If True, only animatable parameters
            will be return

    Returns:
        list: The list of the selected object channels names
    """
    if not oSel:
        oSel = pm.selected()[0]

    channels = [x.name().rsplit(".", 1)[1]
                for x in oSel.listAttr(ud=userDefine, k=animatable)]

    return channels


##########################################################
# UTIL
##########################################################

def connectSet(source, target, testInstance):
    """Connect or set attributes

    Connects or set attributes depending if is instance of a instance check

    Args:
        source (str or Attr): Striname of the attribute or PyNode attribute
        target (str or Attr): Striname of the attribute or PyNode attribute
        testInstance (tuple): Tuple of types to check
    """
    if not isinstance(testInstance, tuple):
        testInstance = tuple(testInstance)

    if isinstance(source, testInstance):
        pm.connectAttr(source, target)
    else:
        pm.setAttr(target, source)


def get_next_available_index(attr):
    """get the next available index from a multi attr
    This function is a workaround because the connect attr flag next available
    is not working.

    The connectAttr to the children attribute is giving error
        i.e: pm.connectAttr(ctt.attr("parent"),
                             tpTagNode.attr("children"), na=True)
        if using the next available option flag
        I was expecting to use ctt.setParent(tagParent) but doest't work as
        expected.
        After reading the documentation this method looks prety
        useless.
        Looks like is boolean and works based on selection :(

    Args:
        attr (attr): Attr multi

    Returns:
        int: index
    """

    ne = attr.getNumElements()
    if ne == attr.numConnectedElements():
        return ne
    else:
        for e in range(ne):
            if not attr.attr(attr.elements()[e]).listConnections():
                return e

##########################################################
# Utility Channels
##########################################################


def add_mirror_config_channels(ctl, conf=[0, 0, 0, 0, 0, 0, 0, 0, 0]):
    """Add channels to configure the mirror posing

    Args:
     ctl (dagNode): Control Object
    """
    addAttribute(ctl,
                 "invTx",
                 "bool",
                 conf[0],
                 keyable=False,
                 niceName="Invert Mirror TX")
    addAttribute(ctl,
                 "invTy",
                 "bool",
                 conf[1],
                 keyable=False,
                 niceName="Invert Mirror TY")
    addAttribute(ctl,
                 "invTz",
                 "bool",
                 conf[2],
                 keyable=False,
                 niceName="Invert Mirror TZ")
    addAttribute(ctl,
                 "invRx",
                 "bool",
                 conf[3],
                 keyable=False,
                 niceName="Invert Mirror RX")
    addAttribute(ctl,
                 "invRy",
                 "bool",
                 conf[4],
                 keyable=False,
                 niceName="Invert Mirror RY")
    addAttribute(ctl,
                 "invRz",
                 "bool",
                 conf[5],
                 keyable=False,
                 niceName="Invert Mirror RZ")
    addAttribute(ctl,
                 "invSx",
                 "bool",
                 conf[6],
                 keyable=False,
                 niceName="Invert Mirror SX")
    addAttribute(ctl,
                 "invSy",
                 "bool",
                 conf[7],
                 keyable=False,
                 niceName="Invert Mirror SY")
    addAttribute(ctl,
                 "invSz",
                 "bool",
                 conf[8],
                 keyable=False,
                 niceName="Invert Mirror SZ")
