#=================================================================================================================================================
#=================================================================================================================================================
#	search - a part of rigger
#=================================================================================================================================================
#=================================================================================================================================================
#
# DESCRIPTION:
#	Series of tools for finding stuff
#
# REQUIRES:
# 	Maya
#
# AUTHOR:
# 	Josh Burton (under the supervision of python guru (and good friend) David Bokser) - jjburton@gmail.com
#	http://www.joshburton.com
# 	Copyright 2011 Josh Burton - All Rights Reserved.
#
# CHANGELOG:
#	0.1 - 02/09/2011 - added documenation
#   0.11 - 04/04/2011 - added cvListSimplifier
#
# FUNCTION KEY:
#   1) ????
#   2) ????
#   3) ????
#
#=================================================================================================================================================

import maya.cmds as mc
import maya.mel as mel

from cgm.lib import lists
from cgm.lib import attributes
from cgm.lib import dictionary
from cgm.lib import settings

namesDictionaryFile = settings.getNamesDictionaryFile()
typesDictionaryFile = settings.getTypesDictionaryFile()
settingsDictionaryFile = settings.getSettingsDictionaryFile()
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Modules
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnObjectMasterNull(obj):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns an objects module if it has one

    REQUIRES:
    obj(string)

    RETURNS:
    moduleNull(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """

    """ first check self"""
    if returnTagInfo(obj,'cgmModuleType') != 'master':
        return returnMatchedTagObjectUp(obj,'cgmModuleType','master')
    else:
        return obj
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnObjectModule(obj):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns an objects module if it has one

    REQUIRES:
    obj(string)

    RETURNS:
    moduleNull(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """

    """ first check self"""
    if returnTagInfo(obj,'cgmType') != 'module':
        return returnMatchedTagObjectUp(obj,'cgmType','module')
    else:
        return obj

def returnObjectsOwnedByModuleNull(moduleNull):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns all objeccts owned by a particular module

    REQUIRES:
    moduleNull(string) for example the templateNull

    RETURNS:
    objList(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    transformsList = mc.ls(tr=True)
    returnList = []
    for obj in transformsList:
        userAttrsBuffer = attributes.returnUserAttributes(obj)
        if userAttrsBuffer > 0:
            for attr in userAttrsBuffer:
                if attr == 'cgmOwnedBy':
                    messageObject = attributes.returnMessageObject(obj,attr)
                    if messageObject == moduleNull:
                        returnList.append(obj)
    return returnList

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Tag stuff
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnTagInfo(obj,tag):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Reads the data from a tag

    REQUIRES:
    obj(string) - object to read the tag from
    tag(string) - cgmName, cgmType, etc

    RETURNS:
    Success - read data
    Failure - false
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    assert mc.objExists(obj) is True, "%s doesn't exist" %obj
    
    if (mc.objExists('%s%s%s' %(obj,'.',tag))) == True:
        messageQuery = (mc.attributeQuery (tag,node=obj,msg=True))
        if messageQuery == True:
            return attributes.returnMessageObject(obj,tag)
        else:
            infoBuffer = mc.getAttr('%s%s%s' % (obj,'.',tag))
            if len(list(infoBuffer)) > 0:
                return infoBuffer
            else:
                return False
    else:
        return False


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnNameTag(obj):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns name from a cgmName Tag

    REQUIRES:
    obj(string) - the object we're starting from

    RETURNS:
    Success - name(string)
    Failure - False
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    return (returnTagInfo(obj,'cgmName'))

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnType(obj):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns type from a cgmName Tag, if there is not tag it guesses it

    REQUIRES:
    obj(string) - the object we're starting from

    RETURNS:
    Success - type(string)
    Failure - False
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    if (mc.objExists('%s%s' %(obj,'.cgmType'))) == False:
        return returnObjectType(obj)
    else:
        return returnTagInfo(obj,'cgmType')

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def findRawTagInfo(obj,tag):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns tag info from the object if it exists. If not, it looks upstream
    before calling it quits. Also, it checks the types and names dictionaries for
    short versions

    REQUIRES:
    obj(string) - the object we're starting from
    tag(string)

    RETURNS:
    Success - name(string)
    Failure - False
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    """ first check the object for the tags """
    selfTagInfo = returnTagInfo(obj,tag)
    if selfTagInfo:
        return selfTagInfo
    else:
        """if it doesn't have one, we're gonna go find em """
        if tag == 'cgmType':
            """ get the type info and see if there's a short hand name for it """
            return returnType(obj)

        else:
            """ check up stream """
            upCheck = returnTagUp(obj,tag)
            if upCheck == False:
                return False
            else:
                tagInfo =  upCheck[0]
                return tagInfo



def returnTagInfoShortName(info,tagType):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns tag info from the object if it exists. If not, it looks upstream
    before calling it quits. Also, it checks the types and names dictionaries for
    short versions

    REQUIRES:
    obj(string) - the object we're starting from
    tag(string)

    RETURNS:
    Success - name(string)
    Failure - False
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    typesDictionary = dictionary.initializeDictionary(typesDictionaryFile)
    namesDictionary = dictionary.initializeDictionary(namesDictionaryFile)

    if tagType == 'cgmType':
        if info in typesDictionary:
            return typesDictionary.get(info)
        else:
            return info
    else:
        if info in namesDictionary:
            return namesDictionary.get(info)
        else:
            return info


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnTagUp(obj,tag):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns name from a cgmName Tag from the first object above the input
    object that has it

    REQUIRES:
    obj(string) - the object we're starting from

    RETURNS:
    Success - info(list) - [info,parentItCameFrom]
    Failure - False
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    parents = returnAllParents(obj)
    tagInfo = []
    for p in parents:
        info = returnTagInfo(p,tag)
        if info is not False:
            tagInfo.append(info)
            tagInfo.append(p)
            return tagInfo
    return False

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnTagDown(obj,tag):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns name from a cgmName Tag from the first object above the input
    object that has it

    REQUIRES:
    obj(string) - the object we're starting from

    RETURNS:
    Success - info(list) - [info,childItCameFrom]
    Failure - False
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    children = mc.listRelatives(obj,allDescendents=True,type='transform')
    tagInfo = []
    for c in children:
        info = returnTagInfo(c,tag)
        if info is not False:
            tagInfo.append(info)
            tagInfo.append(c)
            return tagInfo
    return False


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def returnMatchedTagObjectUp(obj,tagToMatch,infoToMatch):
    parents = returnAllParents(obj)
    for p in parents:
        tagInfo = returnTagInfo(p,tagToMatch)
        if tagInfo == infoToMatch:
            return p
    return False

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def returnMatchedTagsFromObjectList(objList,tagToMatch,infoToMatch):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns objects that match the input tag from a specific object list

    REQUIRES:
    objList(list)
    tagToMatch(string) - 'cgmName'
    infoToMatch(string) - the value to match

    RETURNS:
    returnList(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    returnList = []
    for obj in objList:
        tagInfo = findRawTagInfoTagInfo(obj,tagToMatch)
        if tagInfo == infoToMatch:
            returnList.append(obj)
    return returnList



#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# General
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def seekDownStream(startingNode,endObjType,incPlugs=False):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    ACKNOWLEDGEMENT:
    Pythonized from Scott Englert's MEL

    DESCRIPTION:
    Replacement for getAttr which get's message objects as well as parses double3 type
    attributes to a list

    REQUIRES:
    obj(string)
    attr(string)

    RETURNS:
    attrInfo(varies)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    #
    currentNode = startingNode
    destNodeType = ''
    timeOut = 0
    # do a loop to keep doing down stream on the connections till the type
    # of what we are searching for is found

    while destNodeType != endObjType:
        if timeOut == 50:
            guiFactory.warning('downStream seek timed out')
            break
        else:
            destNodeName = mc.listConnections(currentNode, scn = True, s= False)
            if not destNodeName:
                endNode = 'not found'
                break
            if incPlugs:
                destNodeNamePlug = mc.listConnections(currentNode, scn = True, p = True, s= False)
                endNode = destNodeName[0]
            else:
                endNode = destNodeName[0]
            # Get the Node Type
            destNodeTypeBuffer = mc.ls(destNodeName[0], st = True)
            destNodeType = destNodeTypeBuffer[1]

            if destNodeType == 'pairBlend':
                pairBlendInPlug = mc.listConnections(currentNode, scn = True, p = True, s= False)
                print ('pairBlendInPlug is %s' %pairBlendInPlug)
            else:
                currentNode = destNodeName[0]
            timeOut +=1
    return endNode
    """
		if($destNodeType[1] == "pairBlend"){
			string $pairBlendInPlug[] = `listConnections -scn true -p on -s off $currentNode`;
			string $plugName = `match "[^\.]*$" $pairBlendInPlug[0]`;
			string $strippedPlug = `match "[^in].*[^0-9]" $plugName`;
			string $outputPlug = ("out" + $strippedPlug);

			$currentNode = ($destNodeName[0] + "." + $outputPlug);

		} else {
			// now make the currentNode what we just found so we can loop it again
			$currentNode = $destNodeName[0];
		}
		$timeOut++;
	}

	return $endNode;
	}
	"""

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Maya, OS info
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnMayaInfo():
    mayaInfoDict = {}
    mayaInfoDict['year'] =  mc.about(file=True)
    mayaInfoDict['qtVersion'] =  mc.about(qtVersion=True)
    mayaInfoDict['version'] =  mc.about(version=True)
    mayaInfoDict['apiVersion'] =  mc.about(apiVersion=True)
    mayaInfoDict['product'] =  mc.about(product=True)
    mayaInfoDict['qtVersion'] =  mc.about(qtVersion=True)
    mayaInfoDict['environmentFile'] =  mc.about(environmentFile=True)
    mayaInfoDict['operatingSystem'] =  mc.about(operatingSystem=True)
    mayaInfoDict['operatingSystemVersion'] =  mc.about(operatingSystemVersion=True)
    mayaInfoDict['currentTime'] =  mc.about(currentTime=True)

    return mayaInfoDict

def returnFontList():
    bufferList = (mc.fontDialog(FontList = True))
    return bufferList

def returnMainChannelBoxName():
    import maya.mel as mel
    mel.eval('string $channelBox')
    mel.eval('global string $gChannelBoxName')
    channelBox = mel.eval('$channelBox =  $gChannelBoxName')
    return channelBox

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Timeline/Animation
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnTimelineInfo():
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns timeline info as a dictionary
    {currentTime,sceneStart,sceneEnd,rangeStart,rangeEnd}

    REQUIRES:
    nothing

    RETURNS:
    returnDict(dict)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    returnDict = {}
    returnDict['currentTime'] = mc.currentTime(q=True)
    returnDict['sceneStart'] = mc.playbackOptions(q=True,animationStartTime=True)
    returnDict['sceneEnd'] = mc.playbackOptions(q=True,animationEndTime=True)
    returnDict['rangeStart'] = mc.playbackOptions(q=True,min=True)
    returnDict['rangeEnd'] = mc.playbackOptions(q=True,max=True)

    return returnDict

def returnListOfKeyIndices(obj):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Return a list of the time indexes of the keyframes on an object
    {currentTime,sceneStart,sceneEnd,rangeStart,rangeEnd}

    REQUIRES:
    nothing

    RETURNS:
    returnDict(dict)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    initialTimeState = mc.currentTime(q=True)
    keyFrames = []

    firstKey = mc.findKeyframe(obj,which = 'first')
    lastKey = mc.findKeyframe(obj,which = 'last')

    keyFrames.append(firstKey)
    mc.currentTime(firstKey)
    while mc.currentTime(q=True) != lastKey:
        keyBuffer = mc.findKeyframe(obj,which = 'next')
        keyFrames.append(keyBuffer)
        mc.currentTime(keyBuffer)

    keyFrames.append(lastKey)

    # Put the time back where we found it
    mc.currentTime(initialTimeState)

    return keyFrames


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Referencing
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnReferencePrefix(obj):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns a reference prefix of an object. False if it is not referenced

    REQUIRES:
    obj(string) - object

    RETURNS:
    prefix(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    """ first check if referenced """
    if mc.referenceQuery(obj, isNodeReferenced=True) == True:
        splitBuffer = obj.split(':')
        return (splitBuffer[0])
    else:
        return False


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Object search
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnObjectType(obj):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Asks maya what the object type is

    REQUIRES:
    obj(string) - object

    RETURNS:
    type(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    objShapes = mc.listRelatives(obj,shapes=True,fullPath=True)

    # Standard
    if objShapes > 0:
        return mc.objectType(objShapes[0])
    else:
        """ see if it's a shape """
        parent = returnParentObject(obj)
        isShape = False
        if parent !=False:
            parentShapes = mc.listRelatives(parent,shapes=True,fullPath=True)
            if parentShapes != None:
                matchObjName = mc.ls(obj, long=True)
                if matchObjName[0] in parentShapes:
                    isShape = True
        if isShape == True:
            return 'shape'
        else:
            # Case specific
            if '.vtx[' in obj:
                return 'polyVertex'

            if '.cv[' in obj:
                mainObjType = mc.objectType(obj)
                if mainObjType == 'nurbsCurve':
                    return 'curveCV'
                else:
                    return 'surfaceCV'

            if '.e[' in obj:
                return 'polyEdge'
            if '.f[' in obj:
                return 'polyFace'
            if '.map[' in obj:
                return 'polyUV'
            if '.uv[' in obj:
                return 'nurbsUV'
            if '.sf[' in obj:
                return 'surfacePatch'
            if '.u[' or '.v' in obj:
                mainObjType = mc.objectType(obj)
                if mainObjType == 'nurbsCurve':
                    return 'curvePoint'
                if mainObjType == 'nurbsSurface':
                    return 'isoparm'
            if '.ep[' in obj:
                return 'editPoint'


            return mc.objectType(obj)
        return mc.objectType(objShapes[0])
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Joint Search stuff
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnNonJointObjsInHeirarchy(root):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Search for non joint stuff in a heirarchy chain (example - ik effector)

    REQUIRES:
    root(string) - the root of the heirarchy to check

    RETURNS:
    List of non joint stuff found
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    heirarchy = mc.listRelatives (root)
    heirarchyJoints = mc.listRelatives (root, type = 'joint')
    for item in heirarchy:
        if item in heirarchyJoints:
            heirarchy.remove (item)
    return heirarchy


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnJointHeirarchyCount(startJoint):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Count joints

    REQUIRES:
    startJoint(string) - the root of the heirarchy to check

    RETURNS:
    numberOfJoints(int)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    heirarchyJoints = []
    heirarchyJoints.append (startJoint)
    childrenJoints = returnChildrenJoints (startJoint)
    for joint in childrenJoints:
        heirarchyJoints.append(joint)
    return len(heirarchyJoints)


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnJointHeirarchy(startJoint):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Gets the joints in a heirarchy to a nice list

    REQUIRES:
    startJoint(string) - the root of the heirarchy to check

    RETURNS:
    joints(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    heirarchyJoints = []
    heirarchyJoints.append (startJoint)
    childrenJoints = returnChildrenJoints (startJoint)
    for joint in childrenJoints:
        heirarchyJoints.append(joint)
    return heirarchyJoints

def returnChildrenJoints(root, allDescendents=True):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns children joints of the input object

    REQUIRES:
    obj(string)
    allDescendents(bool) - true or false -True is default

    RETURNS:
    childrenJoints(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    heirarchyJoints = mc.listRelatives (root, allDescendents=True, type = 'joint')
    heirarchyJoints.reverse()
    return heirarchyJoints
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Heirarchy stuff
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnAllChildrenObjects(obj,fullPath=False):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns children of the input object

    REQUIRES:
    obj(string)

    RETURNS:
    children(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    childrenBuffer = []
    childrenBuffer = mc.listRelatives (obj, allDescendents=True,type='transform',fullPath=fullPath)
    return childrenBuffer

def returnChildrenObjects(obj,fullPath=False):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns children of the input object

    REQUIRES:
    obj(string)

    RETURNS:
    children(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    childrenBuffer = []
    childrenBuffer = mc.listRelatives (obj, children = True,type='transform',fullPath=fullPath)
    return childrenBuffer

def returnParentObject(obj,fullPath=True):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns parent of the input object

    REQUIRES:
    obj(string)
    fullPath(bool) - default is True

    RETURNS:
    parent(obj)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    parentBuffer = mc.listRelatives(obj,parent=True,type='transform',fullPath=fullPath)
    if parentBuffer > 0:
        return parentBuffer[0]
    return False
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnAllParents(obj,shortNames=False):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns parents of the input object

    REQUIRES:
    obj(string)

    RETURNS:
    parents(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    parentList = []
    tmpObj = obj
    noParent = False
    while noParent == False:
        tmpParent = mc.listRelatives(tmpObj,allParents=True,fullPath=True)
        if tmpParent > 0:
            if shortNames:
                buffer = mc.ls(tmpParent[0],shortNames=True)
                parentList.append(buffer[0])
            else:
                parentList.append(tmpParent[0])
            tmpObj = tmpParent[0]
            tmpParent = mc.listRelatives(tmpObj,allParents=True,fullPath=True)
        else:
            noParent = True
    return parentList
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Stuff with brackets!
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnSelectedToList():
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns the selected to a list

    REQUIRES:
    A selection

    RETURNS:
    newList(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    selected = []
    selected = (mc.ls (sl=True))
    return selected


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnIndiceFromName(obj):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns indice from an object name

    REQUIRES:
    obj(string) - obj.component[x]

    RETURNS:
    indice(int)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    """ strip out the first [ and following """
    stripBuffer1 = obj.split('[')
    stripBuffer2 = stripBuffer1[-1].split(']')
    """ strip out the ] """
    return int(stripBuffer2[0])

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnCVCoordsToList(surfaceCV):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns cv coordinates from a surface CV

    REQUIRES:
    surfaceCV(string)

    RETURNS:
    coordinates(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    coordinates = []
    """ strip out the first [ and following """
    stripBuffer1 = '['.join(surfaceCV.split('[')[-2:-1])
    stripBuffer2 = '['.join(surfaceCV.split('[')[-1:])
    """ strip out the ] """
    coordinates.append (']'.join(stripBuffer1.split(']')[-2:-1]))
    coordinates.append (']'.join(stripBuffer2.split(']')[-2:-1]))
    return coordinates
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Selection Conversion
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnEdgeLoopFromEdge(polyEdge):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns an edgeloop from an edge

    REQUIRES:
    polyEdge(string)

    RETURNS:
    edgeList(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    splitBuffer = polyEdge.split('.')
    polyObj = splitBuffer[0]
    edges = mc.polySelect([polyObj],edgeLoop = (returnIndiceFromName(polyEdge)))
    mc.select(cl=True)
    edges = lists.returnListNoDuplicates(edges)
    returnList = []
    for edge in edges:
        returnList.append('%s%s%i%s' %(polyObj,'.e[',edge,']'))
    return returnList

def returnVertsFromEdge(polyEdge):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns an edgeloop from an edge

    REQUIRES:
    polyEdge(string)

    RETURNS:
    edgeList(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    mc.select(cl=True)
    mc.select(polyEdge)
    mel.eval("PolySelectConvert 3")
    edgeVerts = mc.ls(sl=True,fl=True)
    mc.select(cl=True)
    return edgeVerts

def returnVertsFromFace(polyFace):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns the vertices of a face

    REQUIRES:
    polyFace(string)

    RETURNS:
    faceVerts(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    mc.select(cl=True)
    mc.select(polyFace)
    mel.eval("PolySelectConvert 3")
    faceVerts = mc.ls(sl=True,fl=True)
    mc.select(cl=True)
    return faceVerts



#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Node reading
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnBlendShapeAttributes(blendshapeNode):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns cv coordinates from a surface CV

    REQUIRES:
    surfaceCV(string)

    RETURNS:
    coordinates(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    return (mc.listAttr((blendshapeNode+'.weight'),m=True))

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# cgmSettings stuff
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnOutFromOrientation(orientation):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns cv coordinates from a surface CV

    REQUIRES:
    surfaceCV(string)

    RETURNS:
    coordinates(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    directions = ['x','y','z']
    directionBuffer = list(orientation)
    direction = directionBuffer[2]
    for dir in directions:
        if dir == direction:
            return direction

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def returnAimUpOutVectorsFromOrientation(orientation):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns aim up and out vectors from an orientation

    REQUIRES:
    orientation(string) - ['xyz','yzx','zxy','xzy','yxz','zyx']

    RETURNS:
    infoList(list) - [aimVector(list),upVector(list),outVector(list)]
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    orientationOptions = ['xyz','yzx','zxy','xzy','yxz','zyx']
    orientationValues = {'x':[1,0,0],'y':[0,1,0],'z':[0,0,1]}
    infoList = []
    if not orientation in orientationOptions:
        print (orientation + ' is not an acceptable orientation. Expected one of the following:')
        print orientationOptions
        return False
    else:
        orientationKeys = list(orientation)
        infoList.append(orientationValues.get(orientationKeys[0]))
        infoList.append(orientationValues.get(orientationKeys[1]))
        infoList.append(orientationValues.get(orientationKeys[2]))
        return infoList
