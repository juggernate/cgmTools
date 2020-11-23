"""
------------------------------------------
shared_dat: cgm.core.mrs.lib.shared_dat
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

================================================================
"""
__MAYALOCAL = 'BLOCKSHARE'

import cgm.core.lib.shared_data as CORESHARE

d_outlinerColors = {'master':{'main':CORESHARE._d_colors_to_RGB['yellowLight']},
                    'face':{'main':CORESHARE._d_colors_to_RGB['greenWhite']},
                    'limb':{'main':CORESHARE._d_colors_to_RGB['blueSkyWhite']},
                    'head':{'main':CORESHARE._d_colors_to_RGB['redWhite']},
                    'segment':{'main':CORESHARE._d_colors_to_RGB['orange']},
                    'handle':{'main':CORESHARE._d_colors_to_RGB['purpleWhite']}}
for k,d in d_outlinerColors.iteritems():
    d['sub'] = [v * .8 for v in d['main']]
    
for k in ['eye','brow','muzzle']:
    d_outlinerColors[k] = d_outlinerColors['face']

d_defaultAttrs= {'version':'string',#Attributes to be initialzed for any module
                'blockType':'string',
                #'moduleTarget':'messageSimple',
                'baseDat':'string',
                'baseSize':'float3',
                'cgmName':'string',
                'cgmDirection':'string',
                'cgmPosition':'string',
                'blockState':'define:form:prerig:skeleton:rig',
                'blockDat':'string',#...for pickle?
                'baseDat':'string',
                'blockProfile':'string',
                'blockParent':'messageSimple',
                'blockMirror':'messageSimple'}
d_defaultAttrSettings = {'blockState':'define'}


_l_requiredSkeletonDat = ('__d_controlShapes__','__l_jointAttrs__','__l_buildOrder__')
_l_requiredRigDat = []

_l_blockStates = ('define','form','prerig','skeleton','rig')
_l_requiredModuleDat = ('__version__',
                        'form','is_form','formDelete',
                        'prerig','is_prerig','prerigDelete',
                        'rig','is_rig','rigDelete')

_l_controlOrder = ('root','settings','fk','ik','pivots','segmentHandles','direct','face','spacePivots')

_l_buildProfiles = ('unityLow','unityMed','unityHigh','unityToon','feature')

d_build_profiles = {
    'unityLow':{'numRoll':0,
                'scaleSetup':False,
                'squashMeasure':0,
                'squash':0,
                   },
    'unityMed':{'numRoll':1,
                'scaleSetup':False,
                'squashMeasure':0,
                'squash':0,
               },
    'unityHigh':{'numRoll':3,
                 'scaleSetup':False,
                 'squashMeasure':0,
                 'squash':0,
               },
    'unityToon':{'numRoll':3,
                 'scaleSetup':True,
                 'squashMeasure':'arcLength',
                 'squash':'simple',
               },        
    'feature':{'numRoll':3,
               'scaleSetup':True,
               'squashMeasure':'arcLength',
               'squash':'simple',
               }
}





#These are our default attrs to make library. To be called via modules
_d_attrsTo_make = {'side':'none:left:right:center',
                   'position':'string',#'none:upper:lower:front:back:top:bottom',
                   'baseUp':'float3',
                   'baseAim':'float3',
                   'basePoint':'float3',
                   'blockProfile':'string',
                   'nowState':'define:form:prerig:skeleton:rig',
                   'controlOffset':'float',
                   'conDirectOffset':'float',                   
                   'jointRadius':'float',                   
                   'basicShape':'circle:square:pyramid:semiSphere:sphere:cube',
                   'proxyShape':'cube:sphere:cylinder:cone:torus',
                   'attachPoint':'base:end:closest:surface:index',
                   'attachIndex':'int',
                   'squashStretch':'none:single:double',
                   'addCog':'bool',
                   'addAim':'bool',
                   'addPivot':'bool',
                   'addMotionJoint':'bool',
                   'jointRadius':'float',                 
                   'jointDepth':'float',
                   
                   'proxy':'off:lock:on',
                   'addScalePivot':'bool',                   
                   'loftShape':'circle:wideUp:wideDown:widePos:wideNeg:diamond:square:squareRoundUp:squareRoundDown:squareUp:squareDown:squarePos:squareNeg:squircle:squircleDiamond:squircleUp:squircleDown:squirclePos:squircleNeg:triUp:triDown:triPos:triNeg:digit',
                   'loftSides':'int',     
                   'loftSplit':'int',
                   'loftList':'enumDatList',
                   'loftDegree':'linear:cubic',
                   
                   'controlType':'main:sub:direct:extra',
                   'formEndAim':'none:back:block',
                   'nameList':'stringDatList',
                   'namesHandles':'stringDatList',
                   'namesJoints':'stringDatList',
                   'hasRootJoint':'bool',
                   'hasJoint':'bool',
                   'nameIter':'string',
                   'numControls':'int',
                   'numJoints':'int',
                   'numRoll':'int',
                   'numShapers':'int',
                   'numSubShapers':'int',
                   'numSpacePivots':'int',
                   'hasLeverJoint':'bool',
                   'buildLeverBase':'bool',#...fkRoot is our clav like setup
                   'hasEndJoint':'bool',                   
                   'offsetMode':'default:proxyAverage',                   
                   'buildDirect':'bool',
                   'ikOrientToWorld':'bool',
                   'ikSetup':'none:rp:spline:ribbon',
                   'ikBase':'none:cube:simple:hips',
                   'ikEnd':'none:bank:foot:paw:hand:tipBase:tipEnd:tipMid:tipCombo:proxy',
                   'buildProfile':'none:unityLow:unityMed:humanIK:feature',
                   'buildAdditiveScale':'bool',
                   'buildSDK':'none:dag:only',
                   'customStartOrientation':'bool',
                   'offsetMode':'default:proxyAverage',
                   'moduleTarget':'messageSimple',
                   'squashMeasure' : 'none:arcLength:pointDist',
                   'squash' : 'none:simple:single:both',
                   'squashExtraControl' : 'bool',
                   'squashFactorMax':'float',
                   'squashFactorMin':'float',
                   'ribbonAim': 'none:stable:stableBlend',
                   #'ribbonConnectBy': 'constraint:matrix',
                   'ribbonConnectBy': 'constraint:matrix',                 
                   
                   'ribbonParam': 'fixed:floating:blend',
                   'shapeDirection':":".join(CORESHARE._l_axis_by_string),
                   'segmentMidIKControl':'bool',
                   'spaceSwitch_direct':'bool',
                   'spaceSwitch_fk':'bool',
                   'scaleSetup':'bool',
                   'settingsPlace':'start:end',
                   'settingsDirection':'up:down:out:in',
                   'proxyDirect':'bool',
                   'proxyGeoRoot':'none:loft:ball',
                   'proxyType':'none:castMesh',
                   'proxyBuild':'bool',
                   'meshBuild':'bool',
                   'visBoundingBox':'bool',
                   'visRotatePlane':'bool',
                   'visLabels':'bool',
                   'visProximityMode':'off:inherit:proximity',
                   'parentToDriver':'bool',
                   'visJointHandle':'bool',
                   'visMeasure':'bool',}

_l_defineHandlesOrder = ('end','start','up','rp','aim','lever')
_l_pivotOrder = ('center','back','front','left','right')
_d_pivotBankNames = {'default':{'left':'outer','right':'inner'},
                      'right':{'left':'inner','right':'outer'}}

_d_mirrorAttrCheck = {'loftShape':{'widePos':'wideNeg',
                                   'wideNeg':'widePos',
                                   'triPos':'triNeg',
                                   'triNeg':'triPos'},
                      'testing':{}}

#>> State Attr Masks =================================================================================
_l_attrMask_all = ('visibility')
_l_attrMask_form = ('baseSize','blockScale')
_l_attrMask_prerig = ()
_l_attrMask_rig = ()

#>> Modules data =================================================================================
__l_faceModules__ = ('eyebrow','eyelids','eyeball','mouthnose')
__l_moduleJointSingleHooks__ = ('scaleJoint')
__l_moduleJointMsgListHooks__ = ('helperJoints','defHelp_joints')
__l_moduleControlMsgListHooks__ = ('spacePivots')


#>>General ======================================================================================
str_defaultFont = 'arial'

