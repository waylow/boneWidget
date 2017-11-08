import bpy
import numpy
from .jsonFunctions import objectDataToDico

def boneMatrix(widget,matchBone):
    widget.matrix_local = matchBone.bone.matrix_local
    widget.scale = [matchBone.bone.length,matchBone.bone.length,matchBone.bone.length]
    widget.data.update()    

def fromWidgetFindBone(widget):
    matchBone = None
    for ob in bpy.context.scene.objects :
        if ob.type == "ARMATURE" : 
            for bone in ob.pose.bones :
                if bone.custom_shape == widget:
                    matchBone = bone
                    
    return matchBone

def createWidget(bone,widget,relative,size,scale,slide):
    C = bpy.context
    D = bpy.data
    
    if bone.custom_shape_transform :
        matrixBone = bone.custom_shape_transform
    else :
        matrixBone = bone
    
    if bone.custom_shape :
        bone.custom_shape.name = bone.custom_shape.name+"_old"
        bone.custom_shape.data.name = bone.custom_shape.data.name+"_old"
        if C.scene.objects.get(bone.custom_shape.name) :
            C.scene.objects.unlink(bone.custom_shape)
        
    newData = D.meshes.new(bone.name)
    
    if relative == True :
        boneLength = 1
    else : 
        boneLength = (1/bone.bone.length)
    
    newData.from_pydata(numpy.array(widget['vertices'])*[size*scale[0]*boneLength,size*scale[2]*boneLength,size*scale[1]*boneLength]+[0,slide,0],widget['edges'],widget['faces'])
    newData.update(calc_edges=True)

    newObject = D.objects.new('WGT-%s'%bone.name,newData)    
        
    newObject.data = newData
    newObject.name = 'WGT-%s'%bone.name
    C.scene.objects.link(newObject)
    newObject.matrix_local = matrixBone.bone.matrix_local
    newObject.scale = [matrixBone.bone.length,matrixBone.bone.length,matrixBone.bone.length]
    C.scene.update()
    
    bone.custom_shape = newObject
    bone.bone.show_wire = True
    newObject.layers = [False,False,False,False,False,False,False,False,False,True,False,False,False,False,False,False,False,False,False,False]
    
def symmetrizeWidget(bone):
    C = bpy.context
    D = bpy.data
    
    widget = bone.custom_shape
    if findMirrorObject(bone).custom_shape_transform :
        mirrorBone = findMirrorObject(bone).custom_shape_transform
    else :
        mirrorBone = findMirrorObject(bone)
    mirrorWidget = mirrorBone.custom_shape
    
    if mirrorWidget :
        mirrorWidget.name = mirrorWidget.name+"_old"
        mirrorWidget.data.name = mirrorWidget.data.name+"_old"
        if C.scene.objects.get(mirrorWidget.name) :
            C.scene.objects.unlink(mirrorWidget)
        
    newData = widget.data.copy()  
    for vert in newData.vertices :
        vert.co = numpy.array(vert.co)*(-1,1,1)
    
    newObject = widget.copy()
    newObject.data = newData
    newData.update()
    newObject.name = 'WGT-%s'%mirrorBone.name
    C.scene.objects.link(newObject)
    newObject.matrix_local = mirrorBone.bone.matrix_local
    newObject.scale = [mirrorBone.bone.length,mirrorBone.bone.length,mirrorBone.bone.length]
    
    C.scene.update()
    mirrorBone.custom_shape = newObject
    mirrorBone.bone.show_wire = True
    newObject.layers = [False,False,False,False,False,False,False,False,False,True,False,False,False,False,False,False,False,False,False,False]    
    
    
def editWidget(active_bone):
    C = bpy.context
    D = bpy.data
    widget = active_bone.custom_shape
    
    armature = active_bone.id_data
    bpy.ops.object.mode_set(mode='OBJECT')
    C.active_object.select = False
    
    if C.space_data.lock_camera_and_layers == False :
        visibleLayers = numpy.array(bpy.context.space_data.layers)+widget.layers-armature.layers
        bpy.context.space_data.layers = visibleLayers.tolist()   
        
    else :
        visibleLayers = numpy.array(bpy.context.scene.layers)+widget.layers-armature.layers
        bpy.context.scene.layers = visibleLayers.tolist()   
    
    if C.space_data.local_view :
        bpy.ops.view3d.localview()
    
    bpy.context.scene.objects.active = widget      
    bpy.ops.object.mode_set(mode='EDIT')
      
def returnToArmature(widget):
    C = bpy.context
    D = bpy.data
          
    bone = fromWidgetFindBone(widget)
    armature = bone.id_data
    
    if C.active_object.mode == 'EDIT':
        bpy.ops.object.mode_set(mode='OBJECT')
    
    if C.space_data.lock_camera_and_layers == False :
        visibleLayers = numpy.array(bpy.context.space_data.layers)-widget.layers+armature.layers
        bpy.context.space_data.layers = visibleLayers.tolist()   
        
    else :
        visibleLayers = numpy.array(bpy.context.scene.layers)-widget.layers+armature.layers
        bpy.context.scene.layers = visibleLayers.tolist()   
       
    if C.space_data.local_view :
        bpy.ops.view3d.localview()
    bpy.context.scene.objects.active = armature
    armature.select = True
    bpy.ops.object.mode_set(mode='POSE')
    armature.data.bones[bone.name].select = True
    armature.data.bones.active = armature.data.bones[bone.name]
            

def findMirrorObject(object):
    if object.name.endswith("L") :
        suffixe = 'R'
    elif object.name.endswith("R") :
        suffixe = 'L'

    objectName = list(object.name)
    objectBaseName = objectName[:-1]
    mirroredObjectName = "".join(objectBaseName)+suffixe
    
    if object.id_data.type == 'ARMATURE' :
        return object.id_data.pose.bones.get(mirroredObjectName)
    else :
        return bpy.context.scene.objects.get(mirroredObjectName)
    
def findMatchBones():
    C = bpy.context
    D = bpy.data
    
    widgetsAndBones = {}
    
    if bpy.context.object.type == 'ARMATURE':
        for bone in C.selected_pose_bones : 
            if bone.name.endswith("L") or bone.name.endswith("R"):
                widgetsAndBones[bone] = bone.custom_shape            
                mirrorBone = findMirrorObject(bone)
                if mirrorBone :
                    widgetsAndBones[mirrorBone]= mirrorBone.custom_shape 
        
        armature = bpy.context.object
        activeObject = C.active_pose_bone
    else :
        for shape in C.selected_objects : 
            bone = fromWidgetFindBone(shape)
            if bone.name.endswith("L") or bone.name.endswith("R"):
                widgetsAndBones[fromWidgetFindBone(shape)] = shape
            
                mirrorShape = findMirrorObject(shape)
                if mirrorShape :
                   widgetsAndBones[mirrorShape]= mirrorShape
        
        activeObject = fromWidgetFindBone(C.object)
        armature = activeObject.id_data
    return (widgetsAndBones,activeObject,armature)

    