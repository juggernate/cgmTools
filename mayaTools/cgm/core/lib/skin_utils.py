"""
------------------------------------------
skin_utils: cgm.core.lib
Author: Josh Burton & David Bokser
email: jjburton@cgmonks.com
Website : http://www.cgmonks.com
------------------------------------------

"""
__MAYALOCAL = 'SKIN'

# From Python =============================================================
import copy
import re
import pprint

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGen
from cgm.core.cgmPy import validateArgs as VALID

from cgm.core.lib import attribute_utils as ATTR
from cgm.core.lib import name_utils as coreNames
from cgm.core.lib import search_utils as SEARCH
from cgm.core.lib import shared_data as SHARED
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import transform_utils as TRANS
import cgm.core.lib.name_utils as NAMES


from cgm.lib.zoo.zooPyMaya import skinWeights


def transfer_fromTo(source = None, targets = None):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Transfers the skin weighting from one object to another

    ARGUMENTS:
    A selection or a set cgmVar_SourceObject

    RETURNS:
    Nothing
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    _str_func = 'transfer_fromTo'
    
    # Check for selection, defaults to using that for targets
    _sel = mc.ls(sl=True,flatten=True) or []
    
    if not targets:
        if not source:
            targets = _sel[1:]  
        else:
            targets = _sel
          
    if not source:
        source = _sel[0]
        
    if not source or not targets:
        raise ValueError,"|{0}| >> Missing data. source: {1} | targets: {2}".format(_str_func,source,targets)

    for obj in targets:
        try:
            skinWeights.transferSkinning( source, obj )
        except Exception,err:
            log.error("|{0}| >> Target failure: {1} |  {2}".format(_str_func,obj,err))

def get_influences_fromSelected(*args):
    skinJoints = []
    for obj in mc.ls(sl=True):
        shapes = mc.listRelatives(obj, shapes=True)
        for shape in shapes if shapes else []:
            for skinCluster in mc.listConnections(type='skinCluster'):
                for joint in get_influences_fromCluster(skinCluster):
                    if joint not in skinJoints:
                        skinJoints.append(joint)
    
    mc.select(skinJoints)
    return skinJoints

def get_influences_fromCluster(skinCluster):
    return mc.skinCluster (skinCluster, q=True,weightedInfluence=True) or []

def get_influences_fromMatrix(skinCluster):
    return mc.listConnections(skinCluster+'.matrix') or []