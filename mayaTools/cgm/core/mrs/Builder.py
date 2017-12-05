"""
------------------------------------------
Builder: cgm.core.mrs
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

================================================================
"""
import random
import re
import copy
import time
import os
# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
from Red9.core import Red9_AnimationUtils as r9Anim

#========================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#========================================================================

import maya.cmds as mc


# From cgm ==============================================================
from cgm.core import cgm_General as cgmGEN
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_RigMeta as RIGMETA
from cgm.core import cgm_PuppetMeta as PUPPETMETA
from cgm.core.classes import GuiFactory as CGMUI
reload(CGMUI)
from cgm.core.lib import curve_Utils as CURVES
from cgm.core.lib import attribute_utils as ATTR
from cgm.core.lib import position_utils as POS
from cgm.core.lib import math_utils as MATH
from cgm.core.lib import distance_utils as DIST
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import rigging_utils as RIGGING
from cgm.core.rigger.lib import joint_Utils as JOINTS
from cgm.core.lib import search_utils as SEARCH
from cgm.core.lib import rayCaster as RAYS
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.classes import NodeFactory as NODEFAC
from cgm.core.cgmPy import path_Utils as PATH
from cgm.core.mrs import RigBlocks as RIGBLOCKS
from cgm.core.lib import shared_data as SHARED
from cgm.core.mrs.lib import builder_utils as BUILDERUTILS
from cgm.core.mrs.lib import general_utils as BLOCKGEN
import cgm.core.tools.lib.tool_chunks as UICHUNKS

_d_blockTypes = {}


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Factory
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
#=====================================================================================================
import cgm.core.classes.GuiFactory as cgmUI
mUI = cgmUI.mUI

#>>> Root settings =============================================================
__version__ = 'ALPHA 0.11162017'


class ui(cgmUI.cgmGUI):
    USE_Template = 'cgmUITemplate'
    WINDOW_NAME = 'cgmBuilder_ui'    
    WINDOW_TITLE = 'Builder - {0}'.format(__version__)
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = True
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created  
    DEFAULT_SIZE = 550,400
    __modes = 'space','orient','follow'
    
    _d_ui_annotations = {'select':"Select rigBlocks in maya from ui.",
                         'rebuild':"Rebuild blocks from define state",
                         'save blockDat':'Save current blockDat to the block',
                         'load blockDat':'Load existing blockDat from the block to current settings',
                         'reset blockDat': 'Reset blockDat to defaults as defined by the module',
                         'copy blockDat': 'Copy the blockDat from one block to another',
                         'verify':"Verify the attributes rigBlocks"}    
    
    def insert_init(self,*args,**kws):
            if kws:log.debug("kws: %s"%str(kws))
            if args:log.debug("args: %s"%str(args))
            log.info(self.__call__(q=True, title=True))
    
            self.__version__ = __version__
            self.__toolName__ = 'Builder'		
            #self.l_allowedDockAreas = []
            self.WINDOW_TITLE = ui.WINDOW_TITLE
            self.DEFAULT_SIZE = ui.DEFAULT_SIZE

            self.uiPopUpMenu_parent = False
            self._l_toEnable = []
            #self.create_guiOptionVar('dynParentMode',  defaultValue = ui.__modes[0])       
            self.uiScrollList_parents = False
            self.uiPopUpMenu_blocks = None
            
            self._blockRoot = None
            self._blockCurrent = None
            self._blockFactory = RIGBLOCKS.factory()
            
            self.create_guiOptionVar('blockAttrsFrameCollapse',defaultValue = 0) 
            self.create_guiOptionVar('blockInfoFrameCollapse',defaultValue = 0) 
            try:self.var_rigBlockCreateSizeMode
            except:self.var_rigBlockCreateSizeMode = cgmMeta.cgmOptionVar('cgmVar_rigBlockCreateSizeMode', defaultValue = 'selection')
            
            
    def build_menus(self):
        self.uiMenu_block = mUI.MelMenu( l='Block', pmc=self.buildMenu_block)         
        self.uiMenu_add = mUI.MelMenu( l='Add', pmc=self.buildMenu_add) 
        #self.uiMenu_switch = mUI.MelMenu( l='Switch', pmc=self.buildMenu_switch) 
        #self.uiMenu_pivot = mUI.MelMenu( l='Pivot', pmc=self.buildMenu_pivot)         
        self.uiMenu_snap = mUI.MelMenu( l='Snap', pmc=self.buildMenu_snap)                 
        self.uiMenu_help = mUI.MelMenu( l='Help', pmc=self.buildMenu_help)         
        
    
    def buildMenu_block( self, *args, **kws):
        self.uiMenu_block.clear()  
        _str_context = "Context: {0} {1}".format(self._l_contextStartModes[self.var_contextStartMode.value],
                                        self._l_contextModes[self.var_contextMode.value])
        #c = cgmGEN.Callback(self.uiFunc_contextualCall,'select',None,**{}))
        
        
        _d_ui_annotations = {'select':"Select rigBlocks in maya from ui. Context: {0}".format(_str_context),
                             'rebuild':"Rebuild blocks from define state. Context: {0}".format(_str_context),
                             'select':"Select the contextual blocks. Context: {0}".format(_str_context),
                             'Buildable Status': "Get the block modules buildable status. Context: {0}".format(_str_context),
                             'Verify Proxy Geo':"Verify the proxy geo of blocks. Context: {0}".format(_str_context),
                             'Get blockDat':"Get block dat. Context: {0}".format(_str_context),
                             'select':"Select the contextual blocks. Context: {0}".format(_str_context),
                             'select':"Select the contextual blocks. Context: {0}".format(_str_context),
                             'select':"Select the contextual blocks. Context: {0}".format(_str_context),
                             'verify':"Verify the attributes rigBlocks. Context: {0}".format(_str_context)}        
        
        mUI.MelMenuItem(self.uiMenu_block, l="Clear active",
                        en = bool(self._blockCurrent),
                        ann = _d_ui_annotations.get('Clear Active',"NEED select"),
                        c = cgmGEN.Callback(self.uiFunc_block_clearActive))
        
        
        
        mUI.MelMenuItem(self.uiMenu_block, l="Context: {0} ---".format(_str_context),
                        en=False)  
        
        
        mUI.MelMenuItem(self.uiMenu_block, l="Select",
                        ann = _d_ui_annotations.get('select',"NEED select"),
                        c = cgmGEN.Callback(self.uiFunc_contextualCall,'select'))
        mUI.MelMenuItem(self.uiMenu_block, l="Rebuild",
                        ann = _d_ui_annotations.get('rebuild',"NEED rebuild"),
                        c = cgmGEN.Callback(self.uiFunc_contextualCall,'rebuild'))        
        mUI.MelMenuItem(self.uiMenu_block, l="Verify",
                        ann = _d_ui_annotations.get('verify',"NEED verify"),
                        c = cgmGEN.Callback(self.uiFunc_contextualCall,'verify'))
        mUI.MelMenuItem(self.uiMenu_block, l="Buildable?",
                        ann = _d_ui_annotations.get('Buildable Status',"Nope"),
                        c = cgmGEN.Callback(self.uiFunc_contextualCall,'getModuleStatus'))
        mUI.MelMenuItem(self.uiMenu_block, l="Visualize Heirarchy",
                        c = cgmGEN.Callback(self.uiFunc_contextualCall,'VISUALIZEHEIRARCHY'))
        
        mUI.MelMenuItem(self.uiMenu_block, l="Verify Proxy Mesh",
                        ann = _d_ui_annotations.get('Verify Proxy Geo',"Nope"),
                        c = cgmGEN.Callback(self.uiFunc_contextualCall,'verify_proxyMesh'))
        
        
        _mBlockDat = mUI.MelMenuItem(self.uiMenu_block, l="BlockDat",subMenu=True)
        

        mUI.MelMenuItem(self.uiMenu_block, l="Report",
                        en=False)       
        
        _mSkeleton = mUI.MelMenuItem(self.uiMenu_block, l="Skeleton",
                                     subMenu = True)         

      
        #>>BlockData ---------------------------------------------------------------------
        mUI.MelMenuItem(_mBlockDat, l="Save",
                        ann = self._d_ui_annotations.get('save blockDat') + _str_context,
                        c = cgmGEN.Callback(self.uiFunc_contextualCall,'saveBlockDat'))        
        mUI.MelMenuItem(_mBlockDat, l="Load",
                        ann = self._d_ui_annotations.get('load blockDat') + _str_context,
                        c = cgmGEN.Callback(self.uiFunc_contextualCall,'loadBlockDat'))        
        mUI.MelMenuItem(_mBlockDat, l="Copy - TO DO",
                        en=False,
                        ann = self._d_ui_annotations.get('copy blockDat') + _str_context,
                        c = cgmGEN.Callback(self.uiFunc_contextualCall,'loadBlockDat'))  
        mUI.MelMenuItem(_mBlockDat, l="Query",
                        ann = self._d_ui_annotations.get('Get blockDat','nope') + _str_context,
                        c = cgmGEN.Callback(self.uiFunc_contextualCall,'getBlockDat'))  
        mUI.MelMenuItem(_mBlockDat, l="Reset",
                        c = cgmGEN.Callback(self.uiFunc_contextualCall,'resetBlockDat'), 
                        ann = self._d_ui_annotations.get('reset blockDat') + _str_context)
          
        #>>Skeleton -----------------------------------------------------------------------
        mUI.MelMenuItem(_mSkeleton, l="Generate",
                        ann = _d_ui_annotations.get('Skeletonize',"NEED Skeletonize"),
                        c = cgmGEN.Callback(self.uiFunc_contextualCall,'skeletonize'))        
        mUI.MelMenuItem(_mSkeleton, l="Delete",
                        ann = _d_ui_annotations.get('DeleteSkeleton',"NEED load DeleteSkeleton"),
                        c = cgmGEN.Callback(self.uiFunc_contextualCall,'loadBlockDat'))          
  
    
    def buildMenu_snap( self, force=False, *args, **kws):
        if self.uiMenu_snap and force is not True:
            return
        self.uiMenu_snap.clear()
        
        UICHUNKS.uiSection_snap(self.uiMenu_snap)
            
        mUI.MelMenuItemDiv(self.uiMenu_snap)
        
        mUI.MelMenuItem(self.uiMenu_snap, l='Rebuild',
                        c=cgmGEN.Callback(self.buildMenu_snap,True))
        log.info("Snap menu rebuilt")
            
    def buildMenu_add( self, force=False, *args, **kws):
        if self.uiMenu_add and force is not True:
            log.info("No load...")
            return
        
        self.uiMenu_add.clear()   
        
        _d = RIGBLOCKS.get_modules_dat()#...refresh data
            
        for b in _d[1]['blocks']:
            if _d[0][b].__dict__.get('__menuVisible__'):
                mUI.MelMenuItem(self.uiMenu_add, l=b,
                                c=cgmGEN.Callback(self.uiFunc_block_build,b),
                                ann="{0} : {1}".format(b, self.uiFunc_block_build))
        
        d_sections = {}
        for c in _d[1].keys():
            d_sections[c] = []
            if c == 'blocks':continue
            for b in _d[1][c]:
                if _d[0][b].__dict__.get('__menuVisible__'):
                    d_sections[c].append( [b,cgmGEN.Callback(self.uiFunc_block_build,b)] )
                    
        for s in d_sections.keys():
            if d_sections[s]:
                _sub = mUI.MelMenuItem( self.uiMenu_add, subMenu=True,
                                        l=s)                
                for option in d_sections[s]:
                    mUI.MelMenuItem(_sub, l=option[0],
                                    c=option[1],
                                    ann="{0} : {1}".format(option[0], option[1])
                                    )

        mUI.MelMenuItemDiv(self.uiMenu_add)
        uiOptionMenu_blockSizeMode(self, self.uiMenu_add)        
        mUI.MelMenuItem(self.uiMenu_add, l='Rebuild',
                        c=cgmGEN.Callback(self.buildMenu_add,True))
        log.info("Add menu rebuilt")

    def uiUpdate_building(self):
        _str_func = 'uiUpdate_building'   
        
        self.uiUpdate_scrollList_blocks()
        
        
            
    def uiFunc_block_build(self, blockType = None):
        _str_func = 'uiFunc_block_build'
        
        #index = _indices[0]
        #_mBlock = self._ml_blocks[_index]
        mActiveBlock = None
        if self._blockCurrent:
            mActiveBlock = self._blockCurrent.mNode
            
        _sizeMode = self.var_rigBlockCreateSizeMode.value
        if _sizeMode == 'selection' and not mc.ls(sl=True):
            #if blockType not in ['master']:
                #log.info("|{0}| >> Must have selection for size mode: {1}.".format(_str_func,_sizeMode))        
                #return False
            _sizeMode = None
        
        _mBlock = cgmMeta.createMetaNode('cgmRigBlock',blockType = blockType, size = _sizeMode, blockParent = mActiveBlock)
        
        log.info("|{0}| >> [{1}] | Created: {2}.".format(_str_func,blockType,_mBlock.mNode))        
        
        self.uiUpdate_building()
        self.uiFunc_block_setActive(self._ml_blocks.index(_mBlock))
       
    def uiFunc_blockManange_fromScrollList(self,**kws):          
        _str_func = 'uiFunc_blockManange_fromScrollList'
        _indices = self.uiScrollList_blocks.getSelectedIdxs()
        
        _mode = kws.get('mode',None)
        _fromPrompt = None
        
        if not _indices:
            log.error("|{0}| >> Nothing selected".format(_str_func))                                                        
            return False
        
        if not self._ml_blocks:
            log.error("|{0}| >> No blocks detected".format(_str_func))                                                        
            return False            
        
        _index = _indices[0]
        _mBlock = self._ml_blocks[_index]
        
        _mActiveBlock = self._blockCurrent
        _str_activeBlock = False
        if _mActiveBlock:
            _str_activeBlock = _mActiveBlock.mNode    
    
        _done = False    
        if _mode is not None:
            log.debug("|{0}| >> mode: {1}".format(_str_func,_mode)) 
            if _mode == 'setParentToActive':
                if not _mActiveBlock:
                    log.error("|{0}| >> mode: {1} requires active block".format(_str_func,_mode)) 
                    return
                _mBlock.p_blockParent = _mActiveBlock
            elif  _mode == 'clearParentBlock':
                _mBlock.p_blockParent = False

                
                
        self.uiUpdate_scrollList_blocks(_mBlock)
        
    def uiFunc_contextualCall(self,*args,**kws):
        _str_func = ''
        
        _startMode = self.var_contextStartMode.value   
        _contextMode = self._l_contextModes[self.var_contextMode.value]
        
        if _startMode == 0 :#Active
            mBlock = self._blockCurrent
            
            if not mBlock:
                log.error("|{0}| >> No Active block".format(_str_func))
                return False
        else:
            _indices = self.uiScrollList_blocks.getSelectedIdxs()
            if not _indices:
                log.error("|{0}| >> Nothing selected".format(_str_func))                                                        
                return False    
            if not self._ml_blocks:
                log.error("|{0}| >> No blocks detected".format(_str_func))                                                        
                return False    
            
            _index = _indices[0]
            try:mBlock = self._ml_blocks[_index]   
            except:
                log.error("|{0}| >> Failed to query index: {1}".format(_str_func,_index))                                                        
                return False                   
        
        RIGBLOCKS.contextual_method_call(mBlock,_contextMode,*args,**kws)
        self.uiUpdate_scrollList_blocks(mBlock)
        self.uiUpdate_blockDat()
        
            
    def uiScrollList_block_select(self): 
        _str_func = 'uiScrollList_block_select'  

        if self.uiPopUpMenu_blocks:
            self.uiPopUpMenu_blocks.clear()
            self.uiPopUpMenu_blocks.delete()
            self.uiPopUpMenu_blocks = None        

        _indices = self.uiScrollList_blocks.getSelectedIdxs() or []
        #log.debug("|{0}| >> indices: {1}".format(_str_func, _indices))    
    
        if not _indices:
            return
        _ml = self._ml_blocks
        _index = _indices[0]
        _mBlock = _ml[_index]
        
        if _mBlock.mNode == None:
            log.warning("|{0}| >> Index failed to query: {1}. Reloading list....".format(_str_func, _index))                        
            self.uiUpdate_scrollList_blocks()
            return
        
        _mActiveBlock = self._blockCurrent
        _str_activeBlock = False
        if _mActiveBlock:
            _str_activeBlock = _mActiveBlock.mNode
    
        self.uiPopUpMenu_blocks = mUI.MelPopupMenu(self.uiScrollList_blocks,button = 3)
        _popUp = self.uiPopUpMenu_blocks 
        
        _b_active = False
        if _mActiveBlock:
            _b_active = True
            
        #>>>Heirarchy ------------------------------------------------------------------------------------------
        _menu_parent = mUI.MelMenuItem(_popUp,subMenu=True,
                                       label = "Parent")
        mUI.MelMenuItem(_menu_parent,
                        en = _b_active,
                        ann = 'Set parent block to active block: {0}'.format(_str_activeBlock),
                        c = cgmGEN.Callback(self.uiFunc_blockManange_fromScrollList,**{'mode':'setParentToActive'}),
                        label = "To active")        
        mUI.MelMenuItem(_menu_parent,
                        ann = 'Clear parent block',
                        c = cgmGEN.Callback(self.uiFunc_blockManange_fromScrollList,**{'mode':'clearParentBlock'}),
                        label = "Clear")            
        
        #>>Utilities ------------------------------------------------------------------------------------------       
        mUI.MelMenuItem(_popUp,
                        label = "Select",
                        en=True,
                        c=cgmGEN.Callback(_mBlock.select))            
        mUI.MelMenuItem(_popUp,
                        label = "Verify",
                        en=True,
                        c=cgmGEN.Callback(_mBlock.verify))   
        
        #>>Queries -----------------------------------------------------------------------------------------------
        _queries = mUI.MelMenuItem(_popUp, subMenu = True,
                                   label = "Queries",
                                   en=True,)   
        
        _d_queries = {'getBlockChildren':{'asMeta':False},
                      'getBlockParents':{'asMeta':False},
                      'getBlockHeirarchyBelow':{'asMeta':False,'report':True},
                      'printBlockDat':{},
                      'getModuleStatus':{},
                      'getBlockDat':{'report':True}}
        for q,d_kws in _d_queries.iteritems():
            mUI.MelMenuItem(_queries,
                            label = q,
                            c=cgmGEN.Callback( _mBlock.string_methodCall, q, **d_kws) )             
        
        return
        #>>Context ============================================================================================
        _menu_context = mUI.MelMenuItem(_popUp,subMenu=True,
                                       label = "Context: {0}".format(self._l_contextModes[self.var_contextMode.value]))
         
        
        
        _menu_blockDat = mUI.MelMenuItem(_menu_context,subMenu=True,
                                         label = "blockDat")        
        _menu_state = mUI.MelMenuItem(_menu_context,subMenu=True,
                                      label = "state")         
        mUI.MelMenuItem(_menu_context,
                         en=False,
                         label = "skeletonize")   
        mUI.MelMenuItem(_menu_context,
                        en=False,
                        label = "Mesh")           
        #self.uiUpdate_scrollList_blocks()
        return
    
    
        if len(_indices) == 1:
            _b_single = True
    
            log.debug("|{0}| >> Single pop up mode".format(_str_func))  
            _short = ml_parents[_indices[0]].p_nameShort
            mUI.MelMenuItem(_popUp,
                            label = "Single: {0}".format(_short),
                            en=False)            
        else:
            log.debug("|{0}| >> Multi pop up mode".format(_str_func))  
            mUI.MelMenuItem(_popUp,
                            label = "Mutli",
                            en=False)  
            _b_single = False
    
    
        if _b_single:
            mUI.MelMenuItem(_popUp,
                            label ='Alias',
                            ann = 'Enter value desired in prompt',
                            c = cgmGEN.Callback(self.uiFunc_parentManage_fromScrollList,**{'mode':'alias'}))
            mUI.MelMenuItem(_popUp,
                            label ='Clear Alias',
                            ann = 'Remove any alias',
                            c = cgmGEN.Callback(self.uiFunc_parentManage_fromScrollList,**{'mode':'aliasClear'}))
    
        mUI.MelMenuItem(_popUp,
                        label ='Select',
                        ann = 'Select specified indice parents',
                        c = cgmGEN.Callback(self.uiFunc_parentManage_fromScrollList,**{'mode':'select'}))  
        mUI.MelMenuItem(_popUp,
                        label ='Move Up',
                        ann = 'Move selected up in list',
                        c = cgmGEN.Callback(self.uiFunc_dynParents_reorder,0)) 
        mUI.MelMenuItem(_popUp,
                        label ='Move Down',
                        ann = 'Move selected down in list',
                        c = cgmGEN.Callback(self.uiFunc_dynParents_reorder,1)) 
    
        self._ml_objList = cgmMeta.validateObjListArg( CONTEXT.get_list(getTransform=True) )        
        uiMenu_changeSpace(self,_popUp)
    
        return
    
    def uiFunc_block_clearActive(self):
        #self.uiField_inspector(edit=True, label = '')
        self.uiField_report(edit=True, label = '')        
        self._blockCurrent = None
        self.uiFrame_blockAttrs.clear()
        self.uiFrame_blockInfo.clear()
        
        
    def uiFunc_block_setActive(self, index = None):
        _str_func = 'uiFunc_block_setActive'
          
        
        _ml = self._ml_blocks
        if not _ml:
            self.uiFunc_block_clearActive()
            return
                
        if index is not None:
            if index in self._ml_blocks:
                index = self._ml_blocks.index(index)
            if index not in range(len(_ml)):
                log.warning("|{0}| >> Invalid index: {1}".format(_str_func, index))    
                return
        else:
            _indices = self.uiScrollList_blocks.getSelectedIdxs() or []
            #log.debug("|{0}| >> indices: {1}".format(_str_func, _indices))    
        
            if not _indices:
                log.warning("|{0}| >> Nothing selected".format(_str_func))                    
                return
            
            index = _indices[0]
        
        if _ml[index].mNode == None:
            log.warning("|{0}| >> Index failed to query: {1}. Reloading list....".format(_str_func, index))            
            self.uiUpdate_scrollList_blocks()                    
            return
        
        log.info("|{0}| >> To set: {1}".format(_str_func, _ml[index].mNode))
        
        self._blockFactory.set_rigBlock( _ml[index] )
        self._blockCurrent = _ml[index]
        _short = self._blockCurrent.p_nameShort
        
        #>>>Inspector ======================================================================================
        #>>>Report -----------------------------------------------------------------------------------------
        
        _l_report = ["Active: {0}".format(self._blockCurrent.p_nameShort), self._blockCurrent.blockType]
        
        if ATTR.get(_short,'side'):
            _l_report.append( ATTR.get_enumValueString(_short,'side'))
        
        if self._blockCurrent.isReferenced():
            _l_report.insert(0,"Referenced!")
            
        #self.uiField_inspector(edit=True, label = '{0}'.format(' | '.join(_l_report)))
        self.uiField_report(edit=True, label = '[ ' + '{0}'.format(' ] [ '.join(_l_report))+ ' ]')
        
        #>>>Settings ----------------------------------------------------------------------------------------
        self.uiUpdate_blockDat()#<<< build our blockDat frame
                
        #>>>Info ----------------------------------------------------------------------------------------
        self.uiFrame_blockInfo.clear()
        
        for l in self._blockCurrent.atBlockUtils('get_infoBlock_report'):
            mUI.MelLabel(self.uiFrame_blockInfo,l=l)
            
        #>>>Attrs ----------------------------------------------------------------------------------------
        self.uiFrame_blockAttrs.clear()
        
        for a in self._blockCurrent.getAttrs(ud=True):
            if a in ['blockDat']:
                continue
            if a not in ['attributeAliasList']:
                if ATTR.get_type(_short,a) == 'enum':
                    mUI.MelLabel(self.uiFrame_blockAttrs,l="{0}:{1}".format(a,ATTR.get_enumValueString(_short,a)))                   
                else:
                    mUI.MelLabel(self.uiFrame_blockAttrs,l="{0}:{1}".format(a,ATTR.get(_short,a)))
        
         
    def uiCallback_setAttrFromField(self, obj, attr, attrType, field):
        _v = field.getValue()
        ATTR.set(obj,attr,_v)
        
        if attrType == 'enum':
            field.setValue(ATTR.get_enumValueString(obj,attr))            
        else:
            field.setValue(ATTR.get(obj,attr))
        
    def uiCallback_blockDatButton(self,func,*args,**kws):
        func(*args,**kws)
        self.uiUpdate_blockDat()
        
    def uiUpdate_blockDat(self):
        self.uiFrame_blockSettings.clear()
        #_d_ui_annotations = {}
    
        _mBlockDat = mUI.MelHLayout(self.uiFrame_blockSettings,ut='cgmUISubTemplate',padding = 2)
        CGMUI.add_Button(_mBlockDat, "Save",
                         cgmGEN.Callback(self._blockCurrent.saveBlockDat),
                         self._d_ui_annotations.get('save blockDat'))       
        CGMUI.add_Button(_mBlockDat, "Load",
                         cgmGEN.Callback(self._blockCurrent.loadBlockDat),
                         self._d_ui_annotations.get('load blockDat') )       
        CGMUI.add_Button(_mBlockDat, "Copy",
                         cgmGEN.Callback(self.uiFunc_contextualCall,'loadBlockDat'),
                         self._d_ui_annotations.get('copy blockDat'),                         
                         en=False)         
    
        CGMUI.add_Button(_mBlockDat,'Reset',
                         cgmGEN.Callback(self._blockCurrent.resetBlockDat), 
                         self._d_ui_annotations.get('reset blockDat'))                                
        CGMUI.add_Button(_mBlockDat,'Refresh',
                         cgmGEN.Callback(self.uiUpdate_blockDat),
                         "Resync the ui blockDat with any changes you've made in viewport.")
    
        _mBlockDat.layout()                
        
        
        _short = self._blockCurrent.p_nameShort
        
        _l_attrs = []
        for a in self._blockCurrent.getAttrs():
            try:
                _type = ATTR.get_type(_short,a)
                if not ATTR.is_hidden(_short,a) or ATTR.is_keyable(_short,a):
                    if a not in ['translateX','translateY','translateZ',
                                 'rotateX','rotateY','rotateZ','baseSize',
                                 'scaleX','scaleY','scaleZ']:
                        _l_attrs.append(a)
                        """if ATTR.get_type(_short,a) == 'enum':
                                mUI.MelLabel(self.uiFrame_blockSettings,l="{0}:{1}".format(a,ATTR.get_enumValueString(_short,a)))                    
                            else:
                                mUI.MelLabel(self.uiFrame_blockSettings,l="{0}:{1}".format(a,ATTR.get(_short,a)))"""        
                elif _type in ['string'] and '_' in a and not a.endswith('dict'):
                    _l_attrs.append(a)
                elif a in ['puppetName','cgmName']:
                    _l_attrs.append(a)
            except: pass
    
        _sidePadding = 25
        self._d_attrFields = {}
        _l_attrs.sort()
        for a in _l_attrs:
            _type = ATTR.get_type(_short,a)
    
            _hlayout = mUI.MelHSingleStretchLayout(self.uiFrame_blockSettings,padding = 5)
            mUI.MelSpacer(_hlayout,w=_sidePadding)
    
            _hlayout.setStretchWidget(mUI.MelSeparator(_hlayout,))            
    
            if _type not in ['bool']:#Some labels parts of fields
                mUI.MelLabel(_hlayout,l="{0} -".format(a))   
    
            if _type == 'bool':
                mUI.MelCheckBox(_hlayout, l="- {0}".format(a),
                                #annotation = "Copy values",		                           
                                value = ATTR.get(_short,a),
                                onCommand = cgmGEN.Callback(ATTR.set,_short,a,1),
                                offCommand = cgmGEN.Callback(ATTR.set,_short,a,0))
    
            elif _type in ['double','doubleAngle','doubleLinear','float']:
                self._d_attrFields[a] = mUI.MelFloatField(_hlayout,w = 50,
                                                          value = ATTR.get(_short,a),                                                          
                                                          )
                self._d_attrFields[a](e=True,
                                      cc  = cgmGEN.Callback(self.uiCallback_setAttrFromField,_short, a, _type,
                                                            self._d_attrFields[a]),
                                      )
            elif _type == 'long':
                self._d_attrFields[a] = mUI.MelIntField(_hlayout,w = 50,
                                                         value = ATTR.get(_short,a),
                                                         maxValue=20,
                                                         minValue=1,
                                                          )
                self._d_attrFields[a](e=True,
                                      cc  = cgmGEN.Callback(self.uiCallback_setAttrFromField,_short, a, _type,
                                                            self._d_attrFields[a]),
                                      )                
            elif _type == 'string':
                self._d_attrFields[a] = mUI.MelTextField(_hlayout,w = 75,
                                                         text = ATTR.get(_short,a),
                                                          )
                self._d_attrFields[a](e=True,
                                      cc  = cgmGEN.Callback(self.uiCallback_setAttrFromField,_short, a, _type,
                                                            self._d_attrFields[a]),
                                      )
            elif _type == 'enum':
                _optionMenu = mUI.MelOptionMenu(_hlayout)
                _optionMenu(e=True,
                            cc = cgmGEN.Callback(self.uiCallback_setAttrFromField,_short, a, _type,
                                                 _optionMenu),) 
                for option in ATTR.get_enumList(_short,a):
                    _optionMenu.append(option)
                _optionMenu.setValue(ATTR.get_enumValueString(_short,a))
            else:
                mUI.MelLabel(_hlayout,l="{0}({1}):{2}".format(a,_type,ATTR.get(_short,a)))        
    
            mUI.MelSpacer(_hlayout,w=_sidePadding)                
            _hlayout.layout()            
        
    def buildMenu_help( self, *args):
        self.uiMenu_help.clear()
        mUI.MelMenuItem( self.uiMenu_help, l="Get Call Size",
                         c=lambda *a: RIGBLOCKS.get_callSize('selection' ) )      
        mc.menuItem(parent=self.uiMenu_help,
                    l = 'Get Help',
                    c='import webbrowser;webbrowser.open("https://http://docs.cgmonks.com/mrs.html");',                        
                    rp = 'N')    
        mUI.MelMenuItem( self.uiMenu_help, l="Log Self",
                         c=lambda *a: cgmUI.log_selfReport(self) )   
        mUI.MelMenuItem( self.uiMenu_help, l="Update Display",
                         c=lambda *a: self.uiUpdate_building() )      
        
 
    def uiFunc_clear_loaded(self):
        _str_func = 'uiFunc_clear_loaded'  
        self._mNode = False
        self._mGroup = False
        self._utf_obj(edit=True, l='',en=False)      
        self.uiField_report(edit=True, l='...')
        #self.uiReport_objects()
        self.uiScrollList_parents.clear()
        
        for o in self._l_toEnable:
            o(e=True, en=False)        
        
    
    def uiUpdate_scrollList_blocks(self, select = None):
        _str_func = 'uiUpdate_scrollList_blocks'          
        self.uiScrollList_blocks.clear()
        
        _ml = []
        _l_strings = []
        
        _ml,_l_strings = BLOCKGEN.get_uiScollList_dat()
        
        for i,s in enumerate(_l_strings):
            log.debug("|{0}| >> {1} : {2}".format(_str_func,_ml[i].mNode,s)) 
                    
        #_ml = BLOCKGEN.get_from_scene()
        
        self._ml_blocks = _ml
        
        _len = len(_ml)
        
        if not _ml:
            log.warning("|{0}| >> No blocks found in scene.".format(_str_func)) 
            self.uiFunc_block_clearActive()
            return False      

        #...menu...
        _progressBar = cgmUI.doStartMayaProgressBar(_len,"Processing...")
        
        try:
            for i,strEntry in enumerate(_l_strings):
                self.uiScrollList_blocks.append(strEntry)

        except Exception,err:
            try:
                log.error("|{0}| >> err: {1}".format(_str_func, err))  
                for a in err:
                    log.error(a)
                cgmUI.doEndMayaProgressBar(_progressBar)
            except:
                raise Exception,err

        cgmUI.doEndMayaProgressBar(_progressBar) 
        
        if select:
            if select in self._ml_blocks:
                self.uiScrollList_blocks.selectByIdx(self._ml_blocks.index(select))
                    
    def build_layoutWrapper(self,parent):
        _str_func = 'build_layoutWrapper'
    
        _MainForm = mUI.MelFormLayout(self,ut='cgmUITemplate')
        
        ui_tabs = mUI.MelTabLayout( _MainForm,w=180 )
        
        uiTab_setup = mUI.MelFormLayout(ui_tabs,ut='cgmUITemplate')#mUI.MelColumnLayout(ui_tabs)
        self.uiTab_setup = uiTab_setup
        
        uiTab_utils = mUI.MelColumnLayout( ui_tabs )
        
        for i,tab in enumerate(['Setup','Utils']):
            ui_tabs.setLabel(i,tab)
            
        self.buildTab_setup(uiTab_setup)
        #self.buildTab_create(uiTab_create)
        #self.buildTab_update(uiTab_update)
    
        _row_cgm = cgmUI.add_cgmFooter(_MainForm)            
        _MainForm(edit = True,
                  af = [(ui_tabs,"top",0),
                        (ui_tabs,"left",0),
                        (ui_tabs,"right",0),                        
                        (_row_cgm,"left",0),
                        (_row_cgm,"right",0),                        
                        (_row_cgm,"bottom",0),
    
                        ],
                  ac = [(ui_tabs,"bottom",0,_row_cgm),
                        ],
                  attachNone = [(_row_cgm,"top")])
        
    def buildTab_setup(self,parent):
        _MainForm = parent
        #_MainForm = mUI.MelScrollLayout(parent)	        
        _row_report = mUI.MelHLayout(_MainForm ,ut='cgmUIInstructionsTemplate',h=20)
        self.uiField_report = mUI.MelLabel(_row_report,
                                           bgc = SHARED._d_gui_state_colors.get('help'),
                                           label = '...',
                                           h=20)
        _row_report.layout()         
        
        
        _LeftColumn = mUI.MelObjectScrollList(_MainForm, ut='cgmUISubTemplate',
                                              allowMultiSelection=False,en=True,
                                              dcc = cgmGEN.Callback(self.uiFunc_block_setActive),
                                              selectCommand = self.uiScrollList_block_select,
                                              
                                              w = 200)
        #dcc = self.uiFunc_dc_fromList,
        #selectCommand = self.uiFunc_selectParent_inList)
    
                                    #dcc = cgmGEN.Callback(self.uiFunc_attrManage_fromScrollList,**{'mode':'value'}),
        self.uiScrollList_blocks = _LeftColumn
        self._l_toEnable.append(self.uiScrollList_blocks)        
        
        
        _RightColumn = mUI.MelScrollLayout(_MainForm,useTemplate = 'cgmUITemplate')
        
        
        #=============================================================================================
        #>> Top
        #=============================================================================================
        cgmUI.add_Header('Active',overrideUpper=True) 
        """self.uiField_inspector= mUI.MelLabel(_RightColumn,
                                             bgc = SHARED._d_gui_state_colors.get('help'),
                                             label = '...',
                                             h=20)  """
        
        #Context mode  -------------------------------------------------------------------------------          
        self.create_guiOptionVar('contextMode',defaultValue = 0)       
    
        _rc_contextMode = mUI.MelRadioCollection()
        
        self._l_contextModes = ['self','below','root','scene']
        _d_ann = {'self':'Context is only of the active/sel block',
                  'below':'Context is active/sel block and below',
                  'root':'Context is active/sel root and below',
                  'scene':'Context is all blocks in the scene. Careful skippy!',}
        
        #build our sub section options
        #MelHSingleStretchLayout
        _row_contextModes = mUI.MelHSingleStretchLayout(_RightColumn,ut='cgmUISubTemplate',padding = 5)
        mUI.MelSpacer(_row_contextModes,w=1)
        mUI.MelLabel(_row_contextModes,l = 'Context:')
        _row_contextModes.setStretchWidget( mUI.MelSeparator(_row_contextModes) )
    
        _on = self.var_contextMode.value
        for i,item in enumerate(self._l_contextModes):
            if i == _on:_rb = True
            else:_rb = False
            _rc_contextMode.createButton(_row_contextModes,label=self._l_contextModes[i],sl=_rb,
                                             ann = _d_ann[item],
                                             onCommand = cgmGEN.Callback(self.var_contextMode.setValue,i))
            mUI.MelSpacer(_row_contextModes,w=2)

        _row_contextModes.layout()         
  
        #Context Start  -------------------------------------------------------------------------------          
        self.create_guiOptionVar('contextStartMode',defaultValue = 0)       
    
        _rc_contextStartMode = mUI.MelRadioCollection()
    
        self._l_contextStartModes = ['active','selected']
        _d_ann = {'active':'Context begins with active block',
                  'selected':'Context beghins with selected block in the picker on the left',}
    
        #build our sub section options
        #MelHSingleStretchLayout
        _row_contextStartModes = mUI.MelHSingleStretchLayout(_RightColumn,ut='cgmUISubTemplate',padding = 5)
        mUI.MelSpacer(_row_contextStartModes,w=1)
        mUI.MelLabel(_row_contextStartModes,l = 'Begin actions with:')
        _row_contextStartModes.setStretchWidget( mUI.MelSeparator(_row_contextStartModes) )
        
        _on = self.var_contextStartMode.value
        for i,item in enumerate(self._l_contextStartModes):
            if i == _on:_rb = True
            else:_rb = False
            _rc_contextStartMode.createButton(_row_contextStartModes,label=self._l_contextStartModes[i],sl=_rb,
                                              ann = _d_ann[item],
                                              onCommand = cgmGEN.Callback(self.var_contextStartMode.setValue,i))
            mUI.MelSpacer(_row_contextStartModes,w=2)
    
        _row_contextStartModes.layout()       
        
        #Push Rows  -------------------------------------------------------------------------------  
        mc.setParent(_RightColumn)
        CGMUI.add_LineSubBreak()
        _row_push = mUI.MelHLayout(_RightColumn,ut='cgmUISubTemplate',padding = 2)
        CGMUI.add_Button(_row_push,'Define>',
                         cgmGEN.Callback(self.uiFunc_contextualCall,'changeState','define',**{}))
        CGMUI.add_Button(_row_push,'<Template>',
                         cgmGEN.Callback(self.uiFunc_contextualCall,'changeState','template',**{}))
                         
        CGMUI.add_Button(_row_push,'<PreRig>',
                         cgmGEN.Callback(self.uiFunc_contextualCall,'changeState','prerig',**{}))

        CGMUI.add_Button(_row_push,'<Rig',
                         cgmGEN.Callback(self.uiFunc_contextualCall,'changeState','rig',**{}))

        _row_push.layout()
               
        
        #Settings Frame ------------------------------------------------------------------------------------
        self.create_guiOptionVar('blockSettingsFrameCollapse',defaultValue = 0)       
    
        _frame_blockSettings = mUI.MelFrameLayout(_RightColumn,label = 'Block Dat',vis=True,
                                                  collapse=self.var_blockSettingsFrameCollapse.value,
                                                  collapsable=True,
                                                  enable=True,
                                                  useTemplate = 'cgmUIHeaderTemplate',
                                                  expandCommand = lambda:self.var_blockSettingsFrameCollapse.setValue(0),
                                                  collapseCommand = lambda:self.var_blockSettingsFrameCollapse.setValue(1)
                                                  )	
        self.uiFrameLayout_blockSettings = _frame_blockSettings
    
        _frame_settings_inside = mUI.MelColumnLayout(_frame_blockSettings,useTemplate = 'cgmUISubTemplate')  
        self.uiFrame_blockSettings = _frame_settings_inside           
        
        #Info ------------------------------------------------------------------------------------
        _frame_info = mUI.MelFrameLayout(_RightColumn,label = 'Info',vis=True,
                                        collapse=self.var_blockInfoFrameCollapse.value,
                                        collapsable=True,
                                        enable=True,
                                        useTemplate = 'cgmUIHeaderTemplate',
                                        expandCommand = lambda:self.var_blockInfoFrameCollapse.setValue(0),
                                        collapseCommand = lambda:self.var_blockInfoFrameCollapse.setValue(1)
                                        )	
        self.uiFrameLayout_blockInfo = _frame_info
        
        _frame_info_inside = mUI.MelColumnLayout(_frame_info,useTemplate = 'cgmUISubTemplate')  
        self.uiFrame_blockInfo = _frame_info_inside        
        
        
        #Settings ------------------------------------------------------------------------------------
        _frame_attr = mUI.MelFrameLayout(_RightColumn,label = 'Attrs',vis=True,
                                        collapse=self.var_blockAttrsFrameCollapse.value,
                                        collapsable=True,
                                        enable=True,
                                        useTemplate = 'cgmUIHeaderTemplate',
                                        expandCommand = lambda:self.var_blockAttrsFrameCollapse.setValue(0),
                                        collapseCommand = lambda:self.var_blockAttrsFrameCollapse.setValue(1)
                                        )	
        self.uiFrameLayout_blockAttrs = _frame_attr
        
        _frame_attr_inside = mUI.MelColumnLayout(_frame_attr,useTemplate = 'cgmUISubTemplate')  
        self.uiFrame_blockAttrs = _frame_attr_inside

        #>>> Layout form ---------------------------------------------------------------------------------------
        _MainForm(edit = True,
                  af = [(_row_report,"top",0),
                        (_row_report,"left",0),
                        (_row_report,"right",0),
                        
                        (_LeftColumn,"left",0),
                        (_RightColumn,"right",0),                        
                        (_RightColumn,"bottom",0),
                        (_LeftColumn,"bottom",0),

                        ],
                  ac = [(_LeftColumn,"top",0,_row_report),
                        (_RightColumn,"top",0,_row_report),
                        (_RightColumn,"left",0,_LeftColumn),
                        
                        #(_RightColumn,"bottom",0,_row_cgm),
                        #(_LeftColumn,"bottom",0,_row_cgm),

                        
                       ],
                  attachNone = [])#(_row_cgm,"top")	  
        
        self.uiUpdate_building()        
        
        
    def build_layoutWrapperOLD(self,parent):
        _str_func = 'build_layoutWrapper'
        self._d_uiCheckBoxes = {}
        
        _MainForm = mUI.MelFormLayout(parent,ut='cgmUISubTemplate')
        
        #_header_top = cgmUI.add_Header('cgmDynParentGroup',overrideUpper=True)     
        _row_report = mUI.MelHLayout(_MainForm ,ut='cgmUIInstructionsTemplate',h=20)
        self.uiField_report = mUI.MelLabel(_row_report,
                                           bgc = SHARED._d_gui_state_colors.get('help'),
                                           label = '...',
                                           h=20)
        _row_report.layout()         
        
        #_LeftColumn = mUI.MelColumn(_MainForm,ut='cgmUISubTemplate',w=100)
        #cgmUI.add_Header('Blocks',overrideUpper=True)  
        
        _LeftColumn = mUI.MelObjectScrollList(_MainForm, #ut='cgmUISubTemplate',
                                              allowMultiSelection=False,en=True,
                                              dcc = cgmGEN.Callback(self.uiFunc_block_setActive),
                                              selectCommand = self.uiScrollList_block_select,
                                              w = 200)
        #dcc = self.uiFunc_dc_fromList,
        #selectCommand = self.uiFunc_selectParent_inList)
    
                                    #dcc = cgmGEN.Callback(self.uiFunc_attrManage_fromScrollList,**{'mode':'value'}),
        self.uiScrollList_blocks = _LeftColumn
        self._l_toEnable.append(self.uiScrollList_blocks)        
        
        
        _RightColumn = mUI.MelColumnLayout(_MainForm,useTemplate = 'cgmUITemplate')
        
        cgmUI.add_Header('Inspector',overrideUpper=True)
        """
        self.uiField_inspector= mUI.MelLabel(_RightColumn,
                                             bgc = SHARED._d_gui_state_colors.get('help'),
                                             label = '...',
                                             h=20) """
        
        
        _frame_attr = mUI.MelFrameLayout(_RightColumn,label = 'Attr',vis=True,
                                        collapse=self.var_attrFrameCollapse.value,
                                        collapsable=True,
                                        enable=True,
                                        useTemplate = 'cgmUIHeaderTemplate',
                                        expandCommand = lambda:self.var_attrFrameCollapse.setValue(0),
                                        collapseCommand = lambda:self.var_attrFrameCollapse.setValue(1)
                                        )	
        _frame_attr_inside = mUI.MelColumnLayout(_frame_attr,useTemplate = 'cgmUISubTemplate')     
        CGMUI.add_Button(_frame_attr_inside)
        
        #>>>CGM Row
        _row_cgm = cgmUI.add_cgmFooter(_MainForm)
        
               
        #>>> Layout form ---------------------------------------------------------------------------------------
        _MainForm(edit = True,
                  af = [(_row_report,"top",0),
                        (_row_report,"left",0),
                        (_row_report,"right",0),
                        
                        (_LeftColumn,"left",0),
                        (_RightColumn,"right",0),                        
                       
                        (_row_cgm,"left",0),
                        (_row_cgm,"right",0),                        
                        (_row_cgm,"bottom",0),

                        ],
                  ac = [(_LeftColumn,"top",0,_row_report),
                        (_RightColumn,"top",0,_row_report),
                        (_RightColumn,"left",0,_LeftColumn),
                        
                        (_RightColumn,"bottom",0,_row_cgm),
                        (_LeftColumn,"bottom",0,_row_cgm),

                        
                       ],
                  attachNone = [(_row_cgm,"top")])	        
        
        self.uiUpdate_building()
        
        #_sel = mc.ls(sl=True)
        #if _sel:
            #self.uiFunc_load_selected()                

        return



def uiOptionMenu_blockSizeMode(self, parent, callback = cgmGEN.Callback):
    uiMenu = mc.menuItem( parent = parent, l='Create Mode:', subMenu=True)
    
    try:self.var_rigBlockCreateSizeMode
    except:self.var_rigBlockCreateSizeMode = cgmMeta.cgmOptionVar('cgmVar_rigBlockCreateSizeMode', defaultValue = 'selection')

    try:#>>>
        _str_section = 'Contextual TD mode'
        uiRC = mc.radioMenuItemCollection()
        #self.uiOptions_menuMode = []		
        _v = self.var_rigBlockCreateSizeMode.value

        for i,item in enumerate(['selection','default']):
            if item == _v:
                _rb = True
            else:_rb = False
            mc.menuItem(parent=uiMenu,collection = uiRC,
                        label=item,
                        c = callback(self.var_rigBlockCreateSizeMode.setValue,item),                                  
                        rb = _rb)                
    except Exception,err:
        log.error("|{0}| failed to load. err: {1}".format(_str_section,err))
        cgmGEN.cgmException(Exception,err)

                        
    



