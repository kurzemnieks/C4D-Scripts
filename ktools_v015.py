import c4d
from c4d import plugins, gui, utils, bitmaps, storage, documents
import collections, os
#-----------------------------------------------------------------------------------#


def RemoveEmptySelectionTags(obj):
    if obj is None:
        return

    c4d.documents.GetActiveDocument().AddUndo(c4d.UNDOTYPE_DELETE,obj)

    tags = obj.GetTags()
    remove_tags = []
    for tag in tags:
        if type(tag) is c4d.SelectionTag:
            sel = tag.GetBaseSelect()
            if sel.GetCount() == 0:
                remove_tags.append(tag)

    for tag in remove_tags:
        #parent = tag.GetObject()
        tag.Remove()
        #index = getTagNr(tag)
        #parent.KillTag(c4d.Tpolygonselection,index)

    c4d.documents.GetActiveDocument().EndUndo()
    c4d.EventAdd()



def RemoveMaterialsWithEmptySelection(obj):
    if obj is None:
        return

    c4d.documents.GetActiveDocument().AddUndo(c4d.UNDOTYPE_DELETE,obj)

    tags = obj.GetTags()

    sel_tags_dic = {}
    for tag in tags:
        if type(tag) is c4d.SelectionTag:
            sel_tags_dic[tag.GetName()] = tag

    for tag in tags:
        if type(tag) is c4d.TextureTag:
            sel_name = tag[c4d.TEXTURETAG_RESTRICTION]
            mtl_assign = tag.GetParameter(c4d.TEXTURETAG_MATERIAL, c4d.DESCFLAGS_GET_NONE )
                        
            if sel_name is None and mtl_assign is not None:
                continue
            if len(sel_name)==0 and mtl_assign is not None:
                continue

            sel_tag = sel_tags_dic.get(sel_name,None)

            remove_mtl = False            

            if sel_tag is None:
                remove_mtl = True #no selection tag found
            else:
                if sel_tag.GetBaseSelect().GetCount() == 0:
                    remove_mtl = True #empty selection

            if remove_mtl is True:
                tag.Remove() #remove texture tag

    c4d.documents.GetActiveDocument().EndUndo()
    c4d.EventAdd()

#-----------------------------------------------------------------------------------#
def RecursiveFunc(obj, func):
    if obj is None:
        return
    func(obj)
    RecursiveFunc(obj.GetNext(),func)
    RecursiveFunc(obj.GetDown(),func)


#-----------------------------------------------------------------------------------#
def CleanSelectionTagsCommand():
    obj = c4d.documents.GetActiveDocument().GetFirstObject()
    RecursiveFunc(obj,RemoveEmptySelectionTags)

def CleanMaterialsWithNoSelection():
    obj = c4d.documents.GetActiveDocument().GetFirstObject()
    RecursiveFunc(obj,RemoveMaterialsWithEmptySelection)

#-----------------------------------------------------------------------------------#
# PYP Code Below
#-----------------------------------------------------------------------------------#
# Command Classes
class CleanSelectionTags(plugins.CommandData):
    dialog = None

    def Execute(self,doc):
        CleanSelectionTagsCommand()
        return True

class CleanMaterialTags(plugins.CommandData):
    dialog = None

    def Execute(self,doc):
        CleanMaterialsWithNoSelection()
        return True

#-----------------------------------------------------------------------------------#

PLUGIN_ID_CLEANER_S=1032221
PLUGIN_ID_CLEANER_M=1032222

if __name__=='__main__':

    print("====================================")
    print("KTools v0.15")
    print("====================================")

    csel_bmp = bitmaps.BaseBitmap()
    dir, f = os.path.split(__file__)
    fn = os.path.join(dir, "res", "clean_selections.tif")
    csel_bmp.InitWith(fn)
    c4d.plugins.RegisterCommandPlugin(id=PLUGIN_ID_CLEANER_S,str="Clean Empty Selection Tags",
        help="Clean empty polygon selection tags from all objects",info=0,
        dat=CleanSelectionTags(),icon=csel_bmp)

    cmtl_bmp = bitmaps.BaseBitmap()
    fn = os.path.join(dir, "res", "clean_materials.tif")
    cmtl_bmp.InitWith(fn)
    c4d.plugins.RegisterCommandPlugin(id=PLUGIN_ID_CLEANER_M,str="Clean Materials",
        help="Clean texture tags that have invalid or empty selection tags",info=0,
        dat=CleanMaterialTags(),icon=cmtl_bmp)