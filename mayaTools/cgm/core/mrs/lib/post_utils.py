"""
------------------------------------------
cgm.core.mrs.lib.post_utils
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

================================================================
"""
# From Python =============================================================
import copy
import re
import pprint
import time
import os

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc
import maya.mel as mel    

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
import cgm.core.cgm_General as cgmGEN
from cgm.core.rigger import ModuleShapeCaster as mShapeCast
import cgm.core.cgmPy.os_Utils as cgmOS
import cgm.core.cgmPy.path_Utils as cgmPATH
import cgm.core.mrs.lib.ModuleControlFactory as MODULECONTROL
import cgm.core.rig.general_utils as CORERIGGEN
import cgm.core.lib.math_utils as MATH
import cgm.core.lib.transform_utils as TRANS
import cgm.core.lib.distance_utils as DIST
import cgm.core.lib.attribute_utils as ATTR
import cgm.core.tools.lib.snap_calls as SNAPCALLS
import cgm.core.classes.NodeFactory as NODEFACTORY
from cgm.core import cgm_RigMeta as cgmRigMeta
import cgm.core.lib.list_utils as LISTS
import cgm.core.lib.nameTools as NAMETOOLS
import cgm.core.lib.locator_utils as LOC
import cgm.core.rig.create_utils as RIGCREATE
import cgm.core.lib.snap_utils as SNAP
import cgm.core.lib.rayCaster as RAYS
import cgm.core.lib.rigging_utils as CORERIG
import cgm.core.lib.curve_Utils as CURVES
import cgm.core.rig.constraint_utils as RIGCONSTRAINT
import cgm.core.lib.constraint_utils as CONSTRAINT
import cgm.core.lib.position_utils as POS
import cgm.core.rig.joint_utils as JOINT
import cgm.core.lib.search_utils as SEARCH
import cgm.core.rig.ik_utils as IK
import cgm.core.mrs.lib.shared_dat as BLOCKSHARE
import cgm.core.lib.shapeCaster as SHAPECASTER
from cgm.core.cgmPy import validateArgs as VALID
import cgm.core.cgm_RigMeta as cgmRIGMETA


# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta

#=============================================================================================================
#>> Block Settings
#=============================================================================================================
__version__ = 'alpha.1.09122018'

log_start = cgmGEN.log_start

def skin_mesh(mMesh,ml_joints,**kws):
    try:
        _str_func = 'skin_mesh'
        log_start(_str_func)
        l_joints = [mObj.mNode for mObj in ml_joints]
        _mesh = mMesh.mNode
        """
        try:
            kws_heat = copy.copy(kws)
            _defaults = {'heatmapFalloff' : 1,
                         'maximumInfluences' : 2,
                         'normalizeWeights' : 1, 
                         'dropoffRate':7}
            for k,v in _defaults.iteritems():
                if kws_heat.get(k) is None:
                    kws_heat[k]=vars
                    
            skin = mc.skinCluster (l_joints,
                                   _mesh,
                                   tsb=True,
                                   bm=2,
                                   wd=0,
                                   **kws)
        except Exception,err:"""
        #log.warning("|{0}| >> heat map fail | {1}".format(_str_func,err))
        skin = mc.skinCluster (l_joints,
                               mMesh.mNode,
                               tsb=True,
                               bm=0,#0
                               maximumInfluences = 3,
                               wd=0,
                               normalizeWeights = 1,dropoffRate=5)
        """ """
        skin = mc.rename(skin,'{0}_skinCluster'.format(mMesh.p_nameBase))
        #mc.geomBind( skin, bindMethod=3, mi=3 )
        
      
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())

    

def backup(self,ml_handles = None):
    try:
        _str_func = 'segment_handles'
        log_start(_str_func)
        
        mBlock = self.mBlock
        mRigNull = self.mRigNull
        _offset = self.v_offset
        _jointOrientation = self.d_orientation['str']
        
        if not ml_handles:
            raise ValueError,"{0} | ml_handles required".format(_str_func)        
      
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())
    
    


d_default = {'twist':{'d':'rz', '+d':10.0, '-d':-10.0, '+':50, '-':-50, 'ease':{0:.25, 1:.5}},
           'side':{'d':'ry', '+d':10.0, '-d':-10.0, '+':25, '-':-25,'ease':{0:.25, 1:.5}},
           'roll':{'d':'rx', '+d':10.0, '-d':-10.0, '+':70, '-':-30,'ease':{0:.25, 1:.5}},}

def SDK_wip(ml = [], matchType = False,
            d_attrs = d_default, skipLever = True, skipFKBase = []):
    _str_func = 'siblingSDK_wip'
    log.info(cgmGEN.logString_start(_str_func))
    
    if not ml:
        ml = cgmMeta.asMeta(sl=1)
    else:
        ml = cgmMeta.asMeta(ml)
    
    #mParent -----------------------------------------------------------------------------
    mParent = ml[0].moduleParent
    mParentSettings = mParent.rigNull.settings
    
    #pprint.pprint([mParent,mParentSettings])
    _settings = mParentSettings.mNode

    #Siblings get ------------------------------------------------------------------------
    #mSiblings = mTarget.atUtils('siblings_get',excludeSelf=False, matchType = matchType)
    mSiblings = ml
    
    md = {}
    d_int = {}
    
    #Need to figure a way to get the order...
    for i,mSib in enumerate(mSiblings):
        log.info(cgmGEN.logString_start(_str_func, mSib.__repr__()))
        
        _d = {}
        
        ml_fk = mSib.atUtils('controls_get','fk')
        if not ml_fk:
            log.warning('missing fk. Skippping...')
            continue
        
        if skipLever or skipFKBase:
            if i in skipFKBase:
                ml_fk = ml_fk[1:]
            elif skipLever and mSib.getMessage('rigBlock') and mSib.rigBlock.getMayaAttr('blockProfile') in ['finger']:
                ml_fk = ml_fk[1:]
            
        #if 'thumb' not in mSib.mNode:
        #    ml_fk = ml_fk[1:]
            
        
        
        _d['fk'] = ml_fk
        ml_sdk = []
        

        
        for ii,mFK in enumerate(ml_fk):
            mSDK = mFK.getMessageAsMeta('sdkGroup')
            if not mSDK:
                mSDK =  mFK.doGroup(True,True,asMeta=True,typeModifier = 'sdk')            
            ml_sdk.append(mSDK)
            
            if not d_int.get(ii):
                d_int[ii] = []
            
            d_int[ii].append(mSDK)
            
        _d['sdk'] = ml_sdk
        
        md[mSib] = _d
        
    #pprint.pprint(md)
    #pprint.pprint(d_int)
    #return
    
    for a,d in d_attrs.iteritems():
        log.info(cgmGEN.logString_sub(_str_func,a))
        for i,mSib in enumerate(mSiblings):
            log.info(cgmGEN.logString_sub(_str_func,mSib))  
            d_sib = copy.deepcopy(d)
            d_idx = d.get(i,{})
            if d_idx:
                _good = True
                for k in ['d','+d','-d','+','-']:
                    if not d_idx.get(k):
                        _good = False
                        break
                if _good:
                    log.info(cgmGEN.logString_msg(_str_func,"Found d_idx on mSib | {0}".format(d_idx))) 
                    d_use = copy.deepcopy(d_idx)
            else:d_use = copy.deepcopy(d_sib)
            
            d2 = md[mSib]
            str_part = mSib.getMayaAttr('cgmName') or mSib.get_partNameBase()
            
            #_aDriver = "{0}_{1}".format(a,i)
            _aDriver = "{0}_{1}".format(a,str_part)
            if not mParentSettings.hasAttr(_aDriver):
                ATTR.add(_settings, _aDriver, attrType='float', keyable = True)            
            
            log.info(cgmGEN.logString_msg(_str_func,"d_sib | {0}".format(d_sib))) 
            for ii,mSDK in enumerate(d2.get('sdk')):
                
                d_cnt = d_idx.get(ii,{}) 
                if d_cnt:
                    log.info(cgmGEN.logString_msg(_str_func,"Found d_cnt on mSib | {0}".format(d_cnt))) 
                    d_use = copy.deepcopy(d_cnt)
                else:d_use = copy.deepcopy(d_sib)
                
                log.info(cgmGEN.logString_msg(_str_func,"{0}| {1} | {2}".format(i,ii,d_use))) 
                
                if d_use.get('skip'):
                    continue                
                
                d_ease = d_use.get('ease',{})
                v_ease = d_ease.get(ii,None)
                
                l_rev = d_sib.get('reverse',[])
                
                if  issubclass( type(d_use['d']), dict):
                    d_do = d_use.get('d')
                else:
                    d_do = {d_use['d'] : d_use}
                    
                    
                for k,d3 in d_do.iteritems():
                    
                    if d3.get('skip'):
                        continue

                    mc.setDrivenKeyframe("{0}.{1}".format(mSDK.mNode, k),
                                         currentDriver = "{0}.{1}".format(_settings, _aDriver),
                                         itt='linear',ott='linear',                                         
                                         driverValue = 0, value = 0)
                    
                    #+ ------------------------------------------------------------------
                    pos_v = d3.get('+')
                    pos_d = d_use.get('+d', 1.0)
                    if v_ease is not None:
                        pos_v = pos_v * v_ease
                    
                    if i in l_rev:
                        print("...rev pos")
                        pos_v*=-1
                    
                    ATTR.set_max("{0}.{1}".format(_settings, _aDriver),pos_d)
                    
                    if pos_v:
                        mc.setDrivenKeyframe("{0}.{1}".format(mSDK.mNode, k),
                                         currentDriver = "{0}.{1}".format(_settings, _aDriver),
                                         itt='linear',ott='linear',                                         
                                         driverValue = pos_d, value = pos_v)
                    
                    
                    #- ----------------------------------------------------------
                    neg_v = d3.get('-')
                    neg_d = d_use.get('-d', -1.0)
                    if v_ease is not None:
                        neg_v = neg_v * v_ease                
                    
                    if i in l_rev:
                        print("...rev neg")                        
                        neg_v*=-1
                            
                    ATTR.set_min("{0}.{1}".format(_settings, _aDriver),neg_d)
                        
                    if neg_v:
                        mc.setDrivenKeyframe("{0}.{1}".format(mSDK.mNode, k),
                                         currentDriver = "{0}.{1}".format(_settings, _aDriver),
                                         itt='linear',ott='linear',                                         
                                         driverValue = neg_d, value = neg_v)        
     



#bear...
d_toeClaws = {'twist':{'d':'rz', '+d':10.0, '-d':-10.0, '+':50, '-':-50, 'ease':{0:.25, 1:.5, 3:0}},
              'side':{'d':'ry', '+d':10.0, '-d':-10.0, '+':25, '-':-25,'ease':{0:.25, 1:.5, 3:0}},
              'roll':{'d':'rx', '+d':10.0, '-d':-10.0, '+':85, '-':-50},
              'spread':{'d':'ry','+d':10.0, '-d':-10.0,'+':1,'-':-1,
              #0:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-40, '-':25}},#thumb
              0:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-20, '-':60}},#index
              1:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-10, '-':20}},#middle
              2:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':10, '-':-20}},#ring
              3:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':20, '-':-60}}}#pinky                
              }

d_attrs_toesLever = {'twist':{'d':'rz', '+d':10.0, '-d':-10.0, '+':50, '-':-50, 'ease':{0:0.2, 1:.25, 1:.5, 3:0}},
                'side':{'d':'ry', '+d':10.0, '-d':-10.0, '+':25, '-':-25,'ease':{0:0.2, 1:.25, 1:.5, 3:0}},
                'roll':{'d':'rx', '+d':10.0, '-d':-10.0, '+':85, '-':-50,'ease':{0:.2,1:1,2:1,3:0}},
                'spread':{'d':'ry','+d':10.0, '-d':-10.0,'+':1,'-':-1,
                #0:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-40, '-':25}},#thumb
                0:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-10, '-':25},
                   1:{'d':'ry', '+d':10.0, '-d':-10.0, '+':0, '-':50}},#index
                1:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-5, '-':5},
                   1:{'d':'ry', '+d':10.0, '-d':-10.0, '+':0, '-':10}},#middle
                2:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':5, '-':-10},
                   1:{'d':'ry', '+d':10.0, '-d':-10.0, '+':0, '-':-20}},#ring
                3:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':10, '-':-30},
                   1:{'d':'ry', '+d':10.0, '-d':-10.0, '+':0, '-':-60}}}#pinky                
                }

d_attrs_toes3Lever = {'twist':{'d':'rz', '+d':10.0, '-d':-10.0, '+':50, '-':-50, 'ease':{0:0.2, 1:.25, 1:.5, 3:0}},
                      'side':{'d':'ry', '+d':10.0, '-d':-10.0, '+':25, '-':-25,'ease':{0:0.2, 1:.25, 1:.5, 3:0}},
                      'roll':{'d':'rx', '+d':10.0, '-d':-10.0, '+':85, '-':-50,'ease':{0:.2,1:1,2:1,3:0}},
                      'spread':{'d':'ry','+d':10.0, '-d':-10.0,'+':1,'-':-1,
                      #0:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-40, '-':25}},#thumb
                      0:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-10, '-':25},
                         1:{'d':'ry', '+d':10.0, '-d':-10.0, '+':0, '-':50}},#index
                      1:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-5, '-':5},
                         1:{'d':'ry', '+d':10.0, '-d':-10.0, '+':0, '-':10}},#middle
                      2:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':10, '-':-30},
                         1:{'d':'ry', '+d':10.0, '-d':-10.0, '+':0, '-':-60}}}#pinky                
                      }


d_fingers = {'twist':{'d':'rz', '+d':10.0, '-d':-10.0, '+':30, '-':-30, 'ease':{0:.25, 1:.5}},
             'side':{'d':'ry', '+d':10.0, '-d':-10.0, '+':25, '-':-25,'ease':{0:.5, 1:.7}},
             'roll':{
                 0:{0:{'d':'rx', '+d':10.0, '-d':-10.0, '+':10, '-':-40}},
                 'd':'rx', '+d':10.0, '-d':-10.0, '+':90, '-':-40},
             'spread':{'d':'ry','+d':10.0, '-d':-10.0,'+':1,'-':-1,
             0:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-40, '-':25}},#thumb
             1:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-10, '-':25}},#index
             2:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-5, '-':1}},#middle
             3:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':5, '-':-10}},#ring
             4:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':10, '-':-30}}}}#pinky

#thumb in x 35, y -11.9
#thumb out -38, 21 -11
d_fingersFlat = {'twist':{'d':'rz', '+d':10.0, '-d':-10.0, '+':30, '-':-30, 'ease':{0:.25, 1:.5}},
             'side':{'d':'ry', '+d':10.0, '-d':-10.0, '+':25, '-':-25,'ease':{0:.5, 1:.7}},
             'roll':{
                 0:{0:{'d':'rx', '+d':10.0, '-d':-10.0, '+':10, '-':-40}},
                 'd':'rx', '+d':10.0, '-d':-10.0, '+':90, '-':-40},
             'spread':{'d':'ry','+d':10.0, '-d':-10.0,'+':1,'-':-1,
             0:{0:{'d':{'ry':{'+':-11.9, '-':21},
                        'rz':{'+':-11},
                        'rx':{'+':35, '-':-38}},
                        '+d':10.0, '-d':-10.0}},#thumb
             1:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-10, '-':25}},#index
             2:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-5, '-':1}},#middle
             3:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':5, '-':-10}},#ring
             4:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':10, '-':-30}}}}#pinky


d_fingersPaw = {'twist':{'d':'rz', '+d':10.0, '-d':-10.0, '+':30, '-':-30, 'ease':{0:.25, 1:.5}},
                'side':{'d':'ry', '+d':10.0, '-d':-10.0, '+':25, '-':-25,'ease':{0:.5, 1:.7}},
                'roll':{
                    #0:{0:{'d':'rx', '+d':10.0, '-d':-10.0, '+':10, '-':-40}},
                    'd':'rx', '+d':10.0, '-d':-10.0, '+':80, '-':-40},
                'spread':{'d':'ry','+d':10.0, '-d':-10.0,'+':0,'-':0,
                0:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-40, '-':25}},#thumb
                1:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-25, '-':40}},#index
                2:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-5, '-':1}},#middle
                3:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':20, '-':-20}},#ring
                4:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':30, '-':-30}}}}#pinky
d_pawSimple = {'twist':{'d':'rz', '+d':10.0, '-d':-10.0, '+':30, '-':-30, 'ease':{0:.25, 1:.5}},
                'side':{'d':'ry', '+d':10.0, '-d':-10.0, '+':25, '-':-25,'ease':{0:.5, 1:.7}},
                'roll':{
                    #0:{0:{'d':'rx', '+d':10.0, '-d':-10.0, '+':10, '-':-40}},
                    'd':'rx', '+d':10.0, '-d':-10.0, '+':80, '-':-40},
                'spread':{'d':'ry','+d':10.0, '-d':-10.0,'+':0,'-':0,
                0:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-25, '-':40}},#index
                1:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-5, '-':1}},#middle
                2:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':20, '-':-20}},#ring
                3:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':30, '-':-30}}}}#pinky

d_pawFront= {'twist':{'d':'rz', '+d':10.0, '-d':-10.0, '+':30, '-':-30, 'ease':{0:.5,}},
               'side':{'d':'ry', '+d':10.0, '-d':-10.0, '+':25, '-':-25,'ease':{0:.5}},
               'roll':{'d':'rx', '+d':10.0, '-d':-10.0, '+':120, '-':-40, 'ease':{1:.3,}},
               'spread':{'d':'ry','+d':10.0, '-d':-10.0,'+':1,'-':-1,
               0:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-40, '-':25}},#thumb
               1:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-10, '-':25}},#index
               2:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-5, '-':1}},#middle
               3:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':5, '-':-10}},#ring
               4:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':10, '-':-30}}}}#pinky

d_dragonFront= {'twist':{'d':'rz', '+d':10.0, '-d':-10.0, '+':30, '-':-30, 'ease':{0:.5,2:0}},
               'side':{'d':'ry', '+d':10.0, '-d':-10.0, '+':25, '-':-25,'ease':{0:.5,2:0}},
               'roll':{'d':'rx', '+d':10.0, '-d':-10.0, '+':90, '-':-40, 'ease':{1:.5,2:0},
                       0:{0:{'d':'rx', '+d':10.0, '-d':-10.0, '+':60, '-':-40, 'ease':{1:.5,2:0}}}},
               'spread':{'d':'ry','+d':10.0, '-d':-10.0,'+':0,'-':0,
               0:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-40, '-':25}},#thumb
               1:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-10, '-':25}},#index
               2:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-5, '-':1}},#middle
               3:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':15, '-':-10}},#ring
               4:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':25, '-':-30}}}}#pinky

d_catPaw = {'twist':{'d':'rz', '+d':10.0, '-d':-10.0, '+':30, '-':-30, 'ease':{0:.5,}},
            'side':{'d':'ry', '+d':10.0, '-d':-10.0, '+':25, '-':-25,'ease':{0:.5}},
            'claw':{'d':'rx', '+d':10.0, '-d':-10.0, '+':20, '-':-120, 'ease':{0:0,}},            
            'roll':{'d':'rx', '+d':10.0, '-d':-10.0, '+':120, '-':-40, 'ease':{1:0,}},
            'spread':{'d':'ry','+d':10.0, '-d':-10.0,'+':1,'-':-1,
            0:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-10, '-':45}},#thumb
            1:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-10, '-':25}},#index
            2:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-5, '-':1}},#middle
            3:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':5, '-':-10}},#ring
            4:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':10, '-':-30}}}}#pinky

d_pawBack = {'twist':{'d':'rz', '+d':10.0, '-d':-10.0, '+':30, '-':-30, 'ease':{0:.5,}},
               'side':{'d':'ry', '+d':10.0, '-d':-10.0, '+':25, '-':-25,'ease':{0:.5}},
               'roll':{'d':'rx', '+d':10.0, '-d':-10.0, '+':120, '-':-40, 'ease':{1:.3,}},
               'spread':{'d':'ry','+d':10.0, '-d':-10.0,'+':1,'-':-1,
               0:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-10, '-':45}},#thumb
               1:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-10, '-':25}},#index
               2:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-5, '-':1}},#middle
               3:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':5, '-':-10}},#ring
               4:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':10, '-':-30}}}}#pinky


d_talons = {'twist':{'d':'rz', '+d':10.0, '-d':-10.0, '+':30, '-':-30, 'ease':{0:.25, 1:.5,2:0}, 'reverse':[0]},
              'side':{'d':'ry', '+d':10.0, '-d':-10.0, '+':25, '-':-25,'ease':{0:.25, 1:.5,2:0}, 'reverse':[0]},
              'roll':{'d':'rx', '+d':10.0, '-d':-10.0, '+':100, '-':-40, 'ease':{1:.5, 2:.5,2:0}},
              'spread':{'d':'ry','+d':10.0, '-d':-10.0,'+':0,'-':-0,
              0:{'skip':True},#thumb
              1:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-20, '-':25}},#index
              2:{0:{'d':'ry', '+d':10.0, '-d':-10.0,'+':0, '-':0}},#middle
              3:{0:{'d':'ry',  '+d':10.0, '-d':-10.0, '+':20, '-':-25}},#ring
              4:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':10, '-':-30}}}}#pinky

d_batToes = {'twist':{'d':'rz', '+d':10.0, '-d':-10.0, '+':30, '-':-30, 'ease':{0:.25, 1:.5,2:0}, 'reverse':[0]},
             'side':{'d':'ry', '+d':10.0, '-d':-10.0, '+':25, '-':-25,'ease':{0:.25, 1:.5,2:0}, 'reverse':[0]},
             'roll':{'d':'rx', '+d':10.0, '-d':-10.0, '+':100, '-':-40, 'ease':{1:.8, 2:.5,2:0}},
             'spread':{'d':'ry','+d':10.0, '-d':-10.0,'+':0,'-':-0,
             0:{'skip':True},#thumb
             1:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-20, '-':25}},#index
             2:{0:{'d':'ry', '+d':10.0, '-d':-10.0,'+':0, '-':0}},#middle
             3:{0:{'d':'ry',  '+d':10.0, '-d':-10.0, '+':20, '-':-25}},#ring
             4:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':10, '-':-30}}}}#pinky


d_dragonFrontBak = {'twist':{'d':'rz', '+d':10.0, '-d':-10.0, '+':30, '-':-30, 'ease':{0:.25, 1:.5}},
                 'side':{'d':'ry', '+d':10.0, '-d':-10.0, '+':25, '-':-25,'ease':{0:.25, 1:.5}},
                 'roll':{0:{0:{'d':'rx', '+d':10.0, '-d':-10.0, '+':10, '-':-40}},
                 'd':'rx', '+d':10.0, '-d':-10.0, '+':80, '-':-40},
                 'spread':{'d':'ry','+d':10.0, '-d':-10.0,'+':1,'-':-1,
                 0:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-10, '-':10}},#inner
                 1:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-20, '-':25}},#main
                 2:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-5, '-':-10}},#mid
                 3:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':40, '-':-30}},#end
                 4:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':10, '-':-30}}}}#pinky

d_tailFan7 = {'twist':{'d':'rz', '+d':10.0, '-d':-10.0, '+':30, '-':-30, 'ease':{0:.25, 1:.5}, 'reverse':[0,1,2]},
              'side':{'d':'ry', '+d':10.0, '-d':-10.0, '+':50, '-':-50,'ease':{0:.25, 1:.5}, 'reverse':[0,1,2]},
              'roll':{'d':'rx', '+d':10.0, '-d':-10.0, '+':100, '-':-40, 'ease':{0:.25, 1:.5, 2:.5}},
              'spread':{'d':'ry','+d':10.0, '-d':-10.0,'+':0,'-':-0,
              0:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':90, '-':-50}},
              1:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':60, '-':-30}},
              2:{0:{'d':'ry', '+d':10.0, '-d':-10.0,'+':30, '-':-20}},
              3:{'skip':True},#---middle
              4:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':30, '-':-20}},
              5:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':60, '-':-30}},
              6:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':90, '-':-50}},
              
              }}#pinky


def siblingSDK_wip(mTarget = 'L_ring_limb_part',matchType = False,
                   d_attrs = d_default):
    _str_func = 'siblingSDK_wip'
    log.info(cgmGEN.logString_start(_str_func))
    
    if mTarget is None:
        mTarget = cgmMeta.asMeta(sl=1)
        if mTarget:mTarget = mTarget[0]
    else:
        mTarget = cgmMeta.asMeta(mTarget)
        
    #mParent -----------------------------------------------------------------------------
    mParent = mTarget.moduleParent
    mParentSettings = mParent.rigNull.settings
    
    #pprint.pprint([mParent,mParentSettings])
    _settings = mParentSettings.mNode

    #Siblings get ------------------------------------------------------------------------
    mSiblings = mTarget.atUtils('siblings_get',excludeSelf=False, matchType = matchType)
    md = {}
    #Need to figure a way to get the order...
    for i,mSib in enumerate(mSiblings):
        log.info(cgmGEN.logString_start(_str_func, mSib.__repr__()))
        
        _d = {}
        
        ml_fk = mSib.atUtils('controls_get','fk')
        if not ml_fk:
            log.warning('missing fk. Skippping...')
            continue
        
        
        if 'thumb' not in mSib.mNode:
            ml_fk = ml_fk[1:]
            
        
        
        _d['fk'] = ml_fk
        ml_sdk = []
        
        str_part = mSib.get_partNameBase()

        
        for mFK in ml_fk:
            mSDK = mFK.getMessageAsMeta('sdkGroup')
            if not mSDK:
                mSDK =  mFK.doGroup(True,True,asMeta=True,typeModifier = 'sdk')            
            ml_sdk.append(mSDK)
            
            

        for a,d in d_attrs.iteritems():
            log.info("{0} | ...".format(a))
            
            _aDriver = "{0}_{1}".format(a,i)
            #_aDriver = "{0}_{1}".format(str_part,a)
            if not mParentSettings.hasAttr(_aDriver):
                ATTR.add(_settings, _aDriver, attrType='float', keyable = True)
            
            
            for mSDK in ml_sdk:
                mc.setDrivenKeyframe("{0}.{1}".format(mSDK.mNode, d['d']),
                                     currentDriver = "{0}.{1}".format(_settings, _aDriver),
                                     itt='linear',ott='linear',                                         
                                     driverValue = 0, value = 0)
                
                #+ ------------------------------------------------------------------
                pos_v = d.get('+')
                pos_d = d.get('+d', 1.0)
                
                if pos_v:
                    mc.setDrivenKeyframe("{0}.{1}".format(mSDK.mNode, d['d']),
                                     currentDriver = "{0}.{1}".format(_settings, _aDriver),
                                     itt='linear',ott='linear',                                         
                                     driverValue = pos_d, value = pos_v)
                
                
                #- ----------------------------------------------------------
                neg_v = d.get('-')
                neg_d = d.get('-d', -1.0)
                    
                if neg_v:
                    mc.setDrivenKeyframe("{0}.{1}".format(mSDK.mNode, d['d']),
                                     currentDriver = "{0}.{1}".format(_settings, _aDriver),
                                     itt='linear',ott='linear',                                         
                                     driverValue = neg_d, value = neg_v)        
 
            
        _d['sdk'] = ml_sdk
        md[mSib] = _d
        



#
def gather_worldStuff(groupTo = 'worldStuff',parent=True):
    ml = []
    for mObj in cgmMeta.asMeta(mc.ls('|*', type = 'transform')):
        if mObj.p_nameBase in ['cgmLightGroup','master','main','cgmRigBlocksGroup']:
            continue
        
        _type =  mObj.getMayaType()
        if _type in ['camera']:
            continue
        
        if mObj.isReferenced():
            continue
        
        print mObj
        print _type
        ml.append(mObj)
        
        
    if ml and parent:
        if not mc.objExists(groupTo):
            mGroup = cgmMeta.asMeta(mc.group(em=True))
            mGroup.rename(groupTo)
        else:
            mGroup = cgmMeta.asMeta(groupTo)
            
        for mObj in ml:
            log.info("Parenting to {0} | {1} | {2}".format(groupTo, mObj.p_nameShort, mObj.getMayaType()))
            mObj.p_parent = mGroup
    
    pprint.pprint(ml)
    return ml
        
def layers_getUnused(delete=False):
    ml = []
    for mObj in cgmMeta.asMeta(mc.ls(type = 'displayLayer')):
        if not mc.editDisplayLayerMembers(mObj.mNode, q=True):
            ml.append(mObj)
    
    if delete:
        for mObj in ml:
            if not mObj.isReferenced():
                log.info("Deleting  empty layer {0} ".format(mObj))
                mObj.delete()
        return True
    return ml

def shaders_getUnused(delete=False):
    ml = []
    for _type in ['lambert','blinn','phong','phongE']:
        for mObj in cgmMeta.asMeta(mc.ls(type = _type),noneValid=True) or []:
            if mObj in ml:
                continue
            log.info(cgmGEN.logString_sub("shaders_getUnused", mObj))
            
            if mObj.p_nameBase is '{0}1'.format(_type):
                log.info("default shader {0}".format(mObj))                
                continue
            
            try:
                for o in ATTR.get_driven("{0}.outColor".format(mObj.mNode),getNode=1):
                    if VALID.get_mayaType(o) == 'shadingEngine':
                        l = mc.sets(o, q=True) 
                        if not l:
                            log.info("Unused shader | {0}".format(mObj))
                            ml.append(mObj)
            except Exception,err:
                print err
            #if not mc.editDisplayLayerMembers(mObj.mNode, q=True):
                #ml.append(mObj)
    
    if delete:
        for mObj in ml:
            if not mObj.isReferenced():
                log.info("Deleting  empty layer | {0} ".format(mObj))
                mObj.delete()
        return True
    return ml


def refs_remove():
    for refFile in mc.file(query=True, reference=True):
        log.info("Removing | {0}".format(refFile))
        mc.file( refFile, removeReference=True )

    