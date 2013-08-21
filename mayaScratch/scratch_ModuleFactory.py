import cgm.core
cgm.core._reload()
import maya.cmds as mc

from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_PuppetMeta as cgmPM
from cgm.core import cgm_RigMeta as cgmRigMeta
import Red9.core.Red9_Meta as r9Meta
from cgm.core.rigger import ModuleFactory as mFactory
from cgm.core.rigger import TemplateFactory as tFactory
from cgm.core.rigger import JointFactory as jFactory

from cgm.core import cgm_PuppetMeta as cgmPM

reload(mFactory)
reload(tFactory)
reload(jFactory)
mFactory.get_rollJointCountList(leg)
from cgm.core.classes import SnapFactory as Snap
reload(Snap)
from cgm.core.rigger import ModuleControlFactory as mControlFactory
reload(mControlFactory)
from cgm.lib import search
obj = mc.ls(sl=True)[0] or False
obj = ''
objList = []

#>>> Modules
#=======================================================
m1 = cgmPM.cgmEyeball(name = 'eye')
m1 = cgmMeta.cgmNode('eye_part')
m1.__verify__()
m1 = r9Meta.MetaClass('spine_part')
m1 = r9Meta.MetaClass('neck_part')
a = cgmPM.cgmPuppet(name = 'MorphyEye')
a.connectModule(m1)
m1 = r9Meta.MetaClass('l_leg_part')
m1.setState('skeleton',force=True)
m1.setState('rig',force=True)
m1.getPartNameBase()
mFactory.isSkeletonized(m1)
mFactory.isTemplated(m1)
mFactory.doSize(m1,geo = ['pSphere1'])
mFactory.isSized(m1)
mFactory.doTemplate(m1)
mFactory.isModule(m1)
a._verifyMasterControl()
a.getGeo()
m1.coreNames.value
m1.templateNull.handles

mFactory.getGeneratedCoreNames(m1)
m1.rigNull.getMessage('rigJoints',False)
len( m1.rigNull.getMessage('rigJoints',False) )
len( m1.rigNull.getMessage('skinJoints',False) )

for o in m1.rigNull.getMessage('rigJoints',False):
    cgmMeta.cgmObject(o).getConstraintsTo()
    
for o in m1.rigNull.getMessage('skinJoints',False):
    cgmMeta.cgmObject(o).getConstraintsTo()

m1.rigNull.skinJoints[0].getConstraintsTo()
cgmMeta.cgmObject().isConstrainedBy()
reload(mFactory)
m1.getState()
mFactory.isRigConnected(m1)
mFactory.isRigged(m1)
mFactory.rigConnect(m1)
mFactory.rigDisconnect(m1)
mFactory.doRig(m1)

mFactory.deleteRig(m1)


