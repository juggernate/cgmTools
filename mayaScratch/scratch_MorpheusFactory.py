import maya.cmds as mc

import Red9.core.Red9_Meta as r9Meta
reload(r9Meta)
from cgm.lib.classes import NameFactory as nameF
reload(nameF)
nameF.doNameObject()
from cgm.core.rigger import PuppetFactory as pFactory
from cgm.core.rigger import MorpheusFactory as morphyF
from cgm.core.rigger import ModuleFactory as mFactory
from cgm.core.rigger import TemplateFactory as tFactory
from cgm.core.rigger import JointFactory as jFactory

from cgm.core import cgm_PuppetMeta as cgmPM

from morpheusRig_v2.core import CustomizationFactory as CustomF
reload(CustomF)
reload(morphyF)
CustomF.go()

reload(pFactory)
reload(morphyF)
reload(mFactory)
reload(tFactory)
reload(jFactory)

obj = mc.ls(sl=True)[0] or False
obj = ''
objList = []

import cgm.core
cgm.core._reload()

#>>> Generate Morpheus asset Template
m1 = cgmMeta.cgmNode('Morphy_customizationNetwork')
m1.connectChildNode('Morphy_Body_GEO','baseBodyGeo')
CustomF.go('Morphy_customizationNetwork')
p = cgmPM.cgmMorpheusMakerNetwork(name = customizationNode)
p.jointList
p.leftJoints

#>>> Morpheus
#=======================================================
p = cgmPM.cgmMorpheusMakerNetwork('Morphy_customizationNetwork')
p.baseBodyGeo
p.connectChildNode('Morphy_puppetNetwork','mPuppet')
p = cgmPM.cgmPuppet("Morphy_puppetNetwork")
p.setState('skeleton',forceNew = True)
p.setState('template',forceNew = True)
p.setState('size',forceNew = True)

p.mNode
p.mNode
morphyF.verify_customizationData(p)['neck']
cgmPM.cgmPuppet('Morphy_puppetNetwork')
k = cgmPM.cgmMorpheusMakerNetwork('Morphy_customizationNetwork')
k.mNode
str_m1 = 'spine_part'
part = 'neck_part'
m2 = r9Meta.MetaClass(part)
#[2.4872662425041199, 132.08547973632812, 11.861419200897217] #
m1 = r9Meta.MetaClass(str_m1)
p.setState('skeleton')
log.info(m1.getState())
m1.getGeneratedCoreNames()
tFactory.updateTemplate(m2)
m2.setState('size')
m2.setState('skeleton',forceNew = True)
m2.setState('template',forceNew = False)
tFactory.returnModuleBaseSize(m2)
m2.rigNull.skinJoints
m2.moduleParent.rigNull.skinJoints
m2.templateNull.controlObjects
m2 = r9Meta.MetaClass('l_hand_part')