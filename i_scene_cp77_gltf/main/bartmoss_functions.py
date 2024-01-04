import bpy
from mathutils import Vector, Quaternion, Euler, Matrix
from math import radians
import idprop


def rotate_quat_180(self,context):
    if context.active_object and context.active_object.rotation_quaternion:
        active_obj =  context.active_object
        active_obj.rotation_mode = 'QUATERNION'

        rotation_quat = Quaternion((0, 0, 1), radians(180))
        active_obj.rotation_quaternion = rotation_quat @ active_obj.rotation_quaternion
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        # Update the object to reflect the changes
        active_obj.update_tag()
        active_obj.update_from_editmode()

        # Update the scene to see the changes
        bpy.context.view_layer.update()

    else:
        return{'FINISHED'}
    
    
def select_object(obj):
    for o in bpy.context.selected_objects:
        o.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    
def calculate_mesh_volume(obj):
    select_object(obj)
    bpy.ops.rigidbody.object_add()
    bpy.ops.rigidbody.mass_calculate(material='Custom', density=1) # density in kg/m^3
    volume = obj.rigid_body.mass
    return volume

def checkexists(meshname, Masters):
    groupname = os.path.splitext(os.path.split(meshname['$value'])[-1])[0]
    if groupname in Masters.children.keys() and len(Masters.children[groupname].objects)>0:
        return True
    else:
        return False

def get_pos(inst):
    pos=[0,0,0]
    if 'Position' in inst.keys():
        if 'Properties' in inst['Position'].keys():
            pos[0] = inst['Position']['Properties']['X']  
            pos[1] = inst['Position']['Properties']['Y']  
            pos[2] = inst['Position']['Properties']['Z']            
        else:
            if 'X' in inst['Position'].keys():
                pos[0] = inst['Position']['X']  
                pos[1] = inst['Position']['Y']  
                pos[2] = inst['Position']['Z']  
            else:
                pos[0] = inst['Position']['x']  
                pos[1] = inst['Position']['y']  
                pos[2] = inst['Position']['z']  
    elif 'position' in inst.keys():
        if 'X' in inst['position'].keys():
                pos[0] = inst['position']['X']  
                pos[1] = inst['position']['Y']  
                pos[2] = inst['position']['Z']  
    elif 'translation' in inst.keys():
        pos[0] = inst['translation']['X']  
        pos[1] = inst['translation']['Y']  
        pos[2] = inst['translation']['Z']  
    return pos

def get_rot(inst):
    rot=[0,0,0,0]
    if 'Orientation' in inst.keys():
        if 'Properties' in inst['Orientation'].keys():
            rot[0] = inst['Orientation']['Properties']['r']  
            rot[1] = inst['Orientation']['Properties']['i'] 
            rot[2] = inst['Orientation']['Properties']['j'] 
            rot[3] = inst['Orientation']['Properties']['k']            
        else:
            rot[0] = inst['Orientation']['r'] 
            rot[1] = inst['Orientation']['i'] 
            rot[2] = inst['Orientation']['j'] 
            rot[3] = inst['Orientation']['k'] 
    elif 'orientation' in inst.keys():
            rot[0] = inst['orientation']['r'] 
            rot[1] = inst['orientation']['i'] 
            rot[2] = inst['orientation']['j'] 
            rot[3] = inst['orientation']['k'] 
    elif 'Rotation' in inst.keys():
            rot[0] = inst['Rotation']['r'] 
            rot[1] = inst['Rotation']['i'] 
            rot[2] = inst['Rotation']['j'] 
            rot[3] = inst['Rotation']['k'] 
    elif 'rotation' in inst.keys():
            rot[0] = inst['rotation']['r'] 
            rot[1] = inst['rotation']['i'] 
            rot[2] = inst['rotation']['j'] 
            rot[3] = inst['rotation']['k'] 
    return rot

def set_pos(inst,obj):  
    #print(inst)  
    if 'Position'in inst.keys():
        if 'Properties' in inst['Position'].keys():
            inst['Position']['Properties']['X']= float("{:.9g}".format(obj.location[0] ))
            inst['Position']['Properties']['Y'] = float("{:.9g}".format(obj.location[1] ))
            inst['Position']['Properties']['Z'] = float("{:.9g}".format(obj.location[2] ))
        else:
            if 'X' in inst['Position'].keys():
                inst['Position']['X'] = float("{:.9g}".format(obj.location[0] ))
                inst['Position']['Y'] = float("{:.9g}".format(obj.location[1] ))
                inst['Position']['Z'] = float("{:.9g}".format(obj.location[2] ))
            else:
                inst['Position']['x'] = float("{:.9g}".format(obj.location[0] ))
                inst['Position']['y'] = float("{:.9g}".format(obj.location[1] ))
                inst['Position']['z'] = float("{:.9g}".format(obj.location[2] ))
    elif 'position' in inst.keys():
        inst['position']['X'] = float("{:.9g}".format(obj.location[0] ))
        inst['position']['Y'] = float("{:.9g}".format(obj.location[1] ))
        inst['position']['Z'] = float("{:.9g}".format(obj.location[2] ))
    elif 'translation' in inst.keys():
        inst['translation']['X'] = float("{:.9g}".format(obj.location[0] ))
        inst['translation']['Y'] = float("{:.9g}".format(obj.location[1] ))
        inst['translation']['Z'] = float("{:.9g}".format(obj.location[2] ))

def set_z_pos(inst,obj):  
    #print(inst)  
    if 'Position'in inst.keys():
        if 'Properties' in inst['Position'].keys():
            inst['Position']['Properties']['Z'] = float("{:.9g}".format(obj.location[2] ))
        else:
            if 'X' in inst['Position'].keys():
                inst['Position']['Z'] = float("{:.9g}".format(obj.location[2] ))
            else:
                inst['Position']['z'] = float("{:.9g}".format(obj.location[2] ))
    elif 'position' in inst.keys():
        inst['position']['Z'] = float("{:.9g}".format(obj.location[2] ))
    elif 'translation' in inst.keys():
        inst['translation']['Z'] = float("{:.9g}".format(obj.location[2] ))

def set_rot(inst,obj):
    if 'Orientation' in inst.keys():
        if 'Properties' in inst['Orientation'].keys():
            inst['Orientation']['Properties']['r'] = float("{:.9g}".format(obj.rotation_quaternion[0] ))
            inst['Orientation']['Properties']['i'] = float("{:.9g}".format(obj.rotation_quaternion[1] )) 
            inst['Orientation']['Properties']['j'] = float("{:.9g}".format(obj.rotation_quaternion[2] ))  
            inst['Orientation']['Properties']['k'] = float("{:.9g}".format(obj.rotation_quaternion[3] ))        
        else:
            inst['Orientation']['r'] = float("{:.9g}".format(obj.rotation_quaternion[0] ))
            inst['Orientation']['i'] = float("{:.9g}".format(obj.rotation_quaternion[1] ))
            inst['Orientation']['j'] = float("{:.9g}".format(obj.rotation_quaternion[2] ))
            inst['Orientation']['k'] = float("{:.9g}".format(obj.rotation_quaternion[3] ))
    elif 'Rotation' in inst.keys():
            inst['Rotation']['r'] = float("{:.9g}".format(obj.rotation_quaternion[0] ))
            inst['Rotation']['i'] = float("{:.9g}".format(obj.rotation_quaternion[1] )) 
            inst['Rotation']['j'] = float("{:.9g}".format(obj.rotation_quaternion[2] ))
            inst['Rotation']['k'] = float("{:.9g}".format(obj.rotation_quaternion[3] ))
    elif 'rotation' in inst.keys():
            inst['rotation']['r'] = float("{:.9g}".format(obj.rotation_quaternion[0] ))
            inst['rotation']['i'] = float("{:.9g}".format(obj.rotation_quaternion[1] )) 
            inst['rotation']['j'] = float("{:.9g}".format(obj.rotation_quaternion[2] ))
            inst['rotation']['k'] = float("{:.9g}".format(obj.rotation_quaternion[3] ))
    elif 'orientation' in inst.keys():
            inst['orientation']['r'] = float("{:.9g}".format(obj.rotation_quaternion[0] ))
            inst['orientation']['i'] = float("{:.9g}".format(obj.rotation_quaternion[1] )) 
            inst['orientation']['j'] = float("{:.9g}".format(obj.rotation_quaternion[2] ))
            inst['orientation']['k'] = float("{:.9g}".format(obj.rotation_quaternion[3] ))

def set_scale(inst,obj):
    if 'Scale' in inst.keys():
        if 'Properties' in inst['Scale'].keys():
            inst['Scale']['Properties']['X'] = float("{:.9g}".format(obj.scale[0] ))
            inst['Scale']['Properties']['Y'] = float("{:.9g}".format(obj.scale[1] ))
            inst['Scale']['Properties']['Z']= float("{:.9g}".format(obj.scale[2] ))
        else:
            inst['Scale']['X']  = float("{:.9g}".format(obj.scale[0] ))
            inst['Scale']['Y']  = float("{:.9g}".format(obj.scale[1] ))
            inst['Scale']['Z']  = float("{:.9g}".format(obj.scale[2] ))
    elif 'scale' in inst.keys():
            inst['scale']['X']  = float("{:.9g}".format(obj.scale[0] ))
            inst['scale']['Y']  = float("{:.9g}".format(obj.scale[1] ))
            inst['scale']['Z']  = float("{:.9g}".format(obj.scale[2] ))

def set_bounds(node, obj):
        node["Bounds"]['Max']["X"]= float("{:.9g}".format(obj.location[0] ))
        node["Bounds"]['Max']["Y"]= float("{:.9g}".format(obj.location[1] ))
        node["Bounds"]['Max']["Z"]= float("{:.9g}".format(obj.location[2] ))
        node["Bounds"]['Min']["X"]= float("{:.9g}".format(obj.location[0] ))
        node["Bounds"]['Min']["Y"]= float("{:.9g}".format(obj.location[1] ))
        node["Bounds"]['Min']["Z"]= float("{:.9g}".format(obj.location[2] ))

def find_col(NodeIndex,Inst_idx,Sector_coll):
    #print('Looking for NodeIndex ',NodeIndex,' Inst_idx ',Inst_idx, ' in ',Sector_coll)
    col=[x for x in Sector_coll.children if x['nodeIndex']==NodeIndex]
    if len(col)==0:
        return None
    elif len(col)==1:
        return col[0]
    else: 
        inst=[x for x in col if x['instance_idx']==Inst_idx]
        if len(inst)>0:
            return inst[0]
    return None

def find_wIDMN_col(NodeIndex,tl_inst_idx, sub_inst_idx,Sector_coll):
    #print('Looking for NodeIndex ',NodeIndex,' Inst_idx ',Inst_idx, ' in ',Sector_coll)
    col=[x for x in Sector_coll.children if x['nodeIndex']==NodeIndex]
    if len(col)==0:
        return None
    elif len(col)==1:
        return col[0]
    else: 
        inst=[x for x in col if x['tl_instance_idx']==tl_inst_idx and x['sub_instance_idx']==sub_inst_idx]
        if len(inst)>0:
            return inst[0]
    return None

def find_decal(NodeIndex,Inst_idx,Sector_coll):
    #print('Looking for NodeIndex ',NodeIndex,' Inst_idx ',Inst_idx, ' in ',Sector_coll)
    col=[x for x in Sector_coll.objects if x['nodeIndex']==NodeIndex]
    if len(col)==0:
        return None
    elif len(col)==1:
        return col[0]
    else: 
        inst=[x for x in col if x['instance_idx']==Inst_idx]
        if len(inst)>0:
            return inst[0]
    return None
    return volume
    
## Returns True if the given object has shape keys, works for meshes and curves
def hasShapeKeys(obj):

    if obj.id_data.type in ['MESH', 'CURVE']:
    
        return True if obj.data.shape_keys else False
    else:
        return False


# Return the name of the shape key data block if the object has shape keys.
def getShapeKeyName(obj):

    if hasShapeKeys(obj):
        return obj.data.shape_keys.name
        
    return ""

# returns a dictionary with all the property names for the objects shape keys.
def getShapeKeyProps(obj):

    props = {}
    
    if hasShapeKeys(obj):
        for prop in obj.data.shape_keys.key_blocks:
            props[prop.name] = prop.value
            
    return props
    
# returns a list of the given objects custom properties.
def getCustomProps(obj):

    props = []
    
    for prop in obj.keys():
        if prop not in '_RNA_UI' and isinstance(obj[prop], (int, float, list, idprop.types.IDPropertyArray)):
            props.append(prop)
            
    return props
    
    
# returns a list of modifiers for the given object
def getMods(obj):

    mods = []
    
    for mod in obj.modifiers:
        mods.append(mod.name)
        
    return mods
    
    
# returns a list with the modifier properties of the given modifier.
def getModProps(modifier):

    props = []
    
    for prop, value in modifier.bl_rna.properties.items():
        if isinstance(value, bpy.types.FloatProperty):
            props.append(prop)
            
    return props