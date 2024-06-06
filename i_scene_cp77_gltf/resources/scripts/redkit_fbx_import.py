import xml.etree.ElementTree as ET
from pprint import pprint
import os
import bpy
def default_cp77_options():
    vers=bpy.app.version
    options = {
        'export_format': 'GLB',
        'check_existing': True,
        'export_skins': True,
        'export_yup': True,
        'export_cameras': False,
        'export_materials': 'NONE',
        'export_all_influences': True,
        'export_lights': False,
        'export_apply': False,
        'export_extras': True,
    }
    if vers[0] >= 4:
        options.update({
            'export_image_format': 'NONE',
            'export_try_sparse_sk': False,
        })

        if vers[1] >= 1:
            options.update({
                "export_shared_accessors": True,
                "export_try_omit_sparse_sk": False,
            })
        return options
#make sure meshes are exported with tangents, morphs and vertex colors
def cp77_mesh_options():
    options = {
        'export_animations': False,
        'export_tangents': True,
        'export_normals': True,
        'export_morph_tangent': True,
        'export_morph_normal': True,
        'export_morph': True,
        'export_colors': True,
        'export_attributes': True,
    }
    return options
from collections import deque

def find_bsdf_socket(node, target_type='BSDF_PRINCIPLED'):
    visited = set()
    queue = deque()
    
    # Add initial node's outputs to the queue
    for output in node.outputs:
        if output.is_linked:
            queue.append((node, output))
    
    while queue:
        current_node, current_socket = queue.popleft()
        visited.add(current_node)

        for link in current_socket.links:
            next_node = link.to_node
            next_socket = link.to_socket

            if next_node.type == target_type:
                return next_node, next_socket, next_socket.name

            if next_node not in visited:
                queue.append((next_node, next_socket))
                visited.add(next_node)
                
    return None

def rename_vgs(obj, armature):
    bone_names = {'head':	'Head','hroll'	:'HeadTip','pelvis':	'Hips','l_bicep':	'LeftArm','l_foot':	'LeftFoot','l_forearm'	:'LeftForeArm','l_hand'	:'LeftHand',
'l_index1'	:'LeftHandIndex1','l_index2':	'LeftHandIndex2','l_index3'	:'LeftHandIndex3','l_middle1':	'LeftHandMiddle1','l_middle2'	:'LeftHandMiddle2',
'l_middle3':	'LeftHandMiddle3','l_pinky1'	:'LeftHandPinky1','l_pinky2':	'LeftHandPinky2','l_pinky3':	'LeftHandPinky3','l_ring1':	'LeftHandRing1',
'l_ring2':	'LeftHandRing2','l_ring3'	:'LeftHandRing3','l_thumb1':	'LeftHandThumb1','l_thumb2':	'LeftHandThumb2','l_pinky0':	'LeftInHandPinky',
'l_shin':	'LeftLeg','l_shoulder'	:'LeftShoulder','l_toe'	:'LeftToeBase','l_thigh':	'LeftUpLeg','neck':	'Neck','Reference'	:'reference_joint','r_bicep'	:'RightArm',
'r_foot'	:'RightFoot','r_forearm':	'RightForeArm','r_hand'	:'RightHand','r_middle1':	'RightHandMiddle1','r_index1'	:'RightHandMiddle1','r_middle2':	'RightHandMiddle2',
'r_index2':	'RightHandMiddle2','r_middle3':	'RightHandMiddle3','r_index3':	'RightHandMiddle3','r_pinky1':	'RightHandPinky1','r_pinky2':	'RightHandPinky2',
'r_pinky3':	'RightHandPinky3','r_ring1'	:'RightHandRing1','r_ring2':	'RightHandRing2','r_ring3':	'RightHandRing3','r_thumb1':	'RightHandThumb1',
'r_thumb2':	'RightHandThumb2','r_index_knuckleRoll':	'RightInHandIndex','r_middle_knuckleRoll':	'RightInHandMiddle','r_pinky0':	'RightInHandPinky',
'r_pinky_knuckleRoll':	'RightInHandPinky','r_ring_knuckleRoll':	'RightInHandRing','r_thumb_roll':	'RightInHandThumb','r_shin':	'RightLeg',
'r_shoulder':	'RightShoulder','r_shoulderRoll':	'RightShoulder','r_toe':	'RightToeBase','r_thigh':	'RightUpLeg',
'torso':	'Spine','torso2':	'Spine1','torso3':	'Spine2','l_weapon':	'WeaponLeft','r_weapon':	'WeaponRight','Root':	'Root'}
    remove_list = []
    renamed=[]
    for vg in obj.vertex_groups:
        origname = vg.name
        if origname in bone_names:
            vg.name = bone_names[origname]
            armature.data.bones[origname].name = bone_names[origname]
            renamed.append( bone_names[origname])
            print(origname, '->', bone_names[origname])

        else:
            obj.vertex_groups.remove(vg)
            remove_list.append(origname)
            print('Removed vertex group:', origname)
    for bone in armature.data.bones:
        if bone.name not in bone_names and bone.name not in remove_list and bone.name not in renamed:
            remove_list.append(bone.name)
    # make the armature active
    bpy.ops.object.select_all(action='DESELECT')
    armature.select_set(True)
    armature.hide_set(False)
    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature

    # Enter edit mode
    bpy.ops.object.mode_set(mode='EDIT')
    for bone_name in remove_list:
        # Ensure the bone exists before attempting to remove it
        if bone_name in armature.data.edit_bones:
            bone = armature.data.edit_bones[bone_name]
            armature.data.edit_bones.remove(bone)

    # Return to object mode
    bpy.ops.object.mode_set(mode='OBJECT')

def oldfind_bsdf_socket(node, target_type='BSDF_PRINCIPLED'):
    def trace_connection(output_socket):
        for link in output_socket.links:
            next_node = link.to_node
            next_socket = link.to_socket
            if next_node.type == target_type:
                return next_node, next_socket,next_socket.name
            # Recursively trace the next node's output sockets
            result = trace_connection(next_socket)
            if result:
                return result
        return None,None,None
    # Iterate over all output sockets of the given node
    for output in node.outputs:
        result = trace_connection(output)
        if result:
            return result
    return None,None,None

def parse_redkit_materials(xml_file):
    # Read the xml file
    with open(xml_file, 'r') as file:
        lines = file.readlines()
    # the redkit material xml files arent valid xml, so cant use the standard xml parser without fixing them first (cant have multiple root elements)
    # Insert '<model>' after the first line
    lines.insert(1, '<model>\n')
    # Insert '</model>' at the end
    lines.append('</model>\n')
    # Parse the modified text file to XML
    xml_string = ''.join(lines)
    root = ET.fromstring(xml_string)
    mat_dict={}
    for idx,item in enumerate(root):
        if item.tag == 'mesh':
            mesh=mat_dict['Mesh_'+str(idx)] = {}  
            for cidx,child in enumerate(item):
                if child.tag == 'materials':
                    materials=mesh['Materials']={}
                    for midx,m in enumerate(child):
                        if m.tag == 'material':
                            material=materials['Material_'+str(midx)] = {}
                            for cchild in m:
                                if cchild.tag == 'param':
                                    material[cchild.attrib['name']]=cchild.attrib['value']
    return mat_dict

def import_redkit_fbx(filename):
    # Replace 'path/to/your/xml/file.xml' with the actual path to your XML file
    xml_file = filename.replace('.fbx','.xml')
    
    mat_dict = parse_redkit_materials(xml_file)
    #pprint(mat_dict)
    # Import the FBX file into Blender
    bpy.ops.import_scene.fbx(filepath=fbx_file)
    imported= bpy.context.selected_objects
    collection = bpy.data.collections.new(os.path.splitext(os.path.basename(filename))[0])
    bpy.context.scene.collection.children.link(collection)
    for o in imported:
        for parent in o.users_collection:
                parent.objects.unlink(o)
        collection.objects.link(o)  
    for obj in collection.objects:
        if 'lod1' in obj.name:
            obj.hide_set(True)
        if 'lod2' in obj.name:
            obj.hide_set(True)
    # could tidy up the materials, rename the textures? save the names to custom props?
    for mno,mesh in enumerate(mat_dict):
        for matno,mat in enumerate(mat_dict[mesh]['Materials']):
            mat_data = mat_dict[mesh]['Materials'][mat]
            





def export_redkit_to_glb(filename):
    objects = bpy.context.selected_objects
    meshes = [obj for obj in objects if obj.type == 'MESH' and not "Icosphere" in obj.name]
    armature_states = {}
    
    groupless_bones = set()
    bone_names = []
    limit_selected = True
    for mesh in meshes:

        # apply transforms
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        if not mesh.data.uv_layers:
            return {'CANCELLED'}

        #check submesh vertex count to ensure it's less than the maximum for import
        vert_count = len(mesh.data.vertices)
        if vert_count > 65535:
            message=(f"{mesh.name} has {vert_count} vertices.           Each submesh must have less than 65,535 vertices. See https://tinyurl.com/vertex-count")
            print(message=message)
            return {'CANCELLED'}

        #check that faces are triangulated, cancel export, switch to edit mode with the untriangulated faces selected and throw an error
        for face in mesh.data.polygons:
            if len(face.vertices) != 3:
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_mode(type='FACE')
                bpy.ops.mesh.select_face_by_sides(number=3, type='NOTEQUAL', extend=False)
                print("All faces must be triangulated before exporting. Untriangulated faces have been selected for you. See https://tinyurl.com/triangulate-faces")
                return {'CANCELLED'}
    options = default_cp77_options()
    
    options.update(cp77_mesh_options())
    for obj in objects:
        if obj.type == 'MESH' and obj.select_get():
            armature_modifier = None
            for modifier in obj.modifiers:
                if modifier.type == 'ARMATURE' and modifier.object:
                    armature_modifier = modifier
                    break

        if True:
            armature_modifier = None
            for modifier in obj.modifiers:
                if modifier.type == 'ARMATURE' and modifier.object:
                    armature_modifier = modifier
                    break
            if not armature_modifier:
                print(f"Armature missing from: {obj.name} Armatures are required for movement. If this is intentional, try 'export as static prop'. See https://tinyurl.com/armature-missing")
                return {'CANCELLED'}

            # Save the current selection
            selected_objects = bpy.context.selected_objects
            active_object = bpy.context.view_layer.objects.active

            armature = armature_modifier.object
            # Store original visibility and selection state
            armature_states[armature] = {"hide": armature.hide_get(),
                                        "select": armature.select_get()}
            rename_vgs(obj,armature)

            # Make necessary to armature visibility and selection state for export
            armature.hide_set(False)
            # Restore the original selection and active object
            bpy.ops.object.select_all(action='DESELECT')
            for obj in selected_objects:
                obj.select_set(True)
            if active_object:
                bpy.context.view_layer.objects.active = active_object

            armature.select_set(True)

            for bone in armature.pose.bones:
                bone_names.append(bone.name)

            if armature_modifier.object != mesh.parent:
                armature_modifier.object = mesh.parent


        if mesh.data.name != mesh.name:
            mesh.data.name = mesh.name

        if limit_selected:
            try:
                bpy.ops.export_scene.fbx(filepath=filename.replace('glb','fbx'), use_selection=True)
                bpy.ops.export_scene.gltf(filepath=filename, use_selection=True, **options)
                if not static_prop:
                    armature.hide_set(True)
            except Exception as e:
                print(e)
        # Create a set to avoid duplicating image saves
    saved_images = set()
    # going to save the images to the same folder as the output file
    export_folder = os.path.dirname(filename)
    # Iterate over the selected objects and export any images used to the folder
    for obj in objects:
        # Ensure the object is a mesh
        if obj.type == 'MESH':
            mesh_name=obj.name
            if mesh_name[-5:-1].upper() == 'LOD_':
                mesh_name=mesh_name[:-5]
            # Iterate over the object's materials
            for material_slot in obj.material_slots:
                material = material_slot.material
                print(material.name)
                if material and material.use_nodes:
                    material['Diffuse']='black.png'
                    material['Normal']='black.png'
                    for node in material.node_tree.nodes:
                        if node.type == 'TEX_IMAGE':
                            image = node.image
                            c=image.name.split(' Texture')[0]
                            if c=='Diffuse' or c=='Normal'  :
                                if image:
                                    # Construct the file path
                                    filepath = os.path.join(export_folder, mesh_name.replace('.','_')+'_'+material_slot.material.name.replace('.','_')+'_'+c+'.png')
                                    
                                    # Save the image
                                    image.filepath_raw = filepath
                                    image.file_format = 'PNG'  # Change the format if needed
                                    image.save()
                                    print("Saved image: ",filepath)
                                    material[c] = filepath
                                    # Add the image to the set of saved images
                                    saved_images.add(image.name)
    output_metal_base_json(objects,filename)

#################################################################################################################
# Initial attempt at getting metal_base info back out of blender.
# Simarilius, August 2023
##################################################################################################################

import bpy
import json
import os
import numpy as np
import copy

def make_rel(filepath):
    if 'base' in filepath:
        before,mid,after=filepath.partition('base\\')
        return mid+after
    else:
        return os.path.join('base','test',os.path.basename(filepath))

def get_node_by_key(nodes, label):
    valNodes = [node for node in nodes if node.label==label]
    if len(valNodes)>0:
        valNode=valNodes[0]
        return valNode
    else:
        return None

def extract_imgpath_and_setjson(nodes, Data, label):
    valNode = get_node_by_key(nodes, label)
    if valNode:
        imgpath=make_rel(valNode.image.filepath.replace('png','xbm'))
        Data[label]=imgpath

def extract_value_and_setjson(nodes, Data, label):
    valNode = get_node_by_key(nodes, label)
    if valNode:
        Data[label]=valNode.outputs[0].default_value

def extract_RGB_and_setjson(nodes, Data, label):
    valNode = get_node_by_key(nodes, label)
    if valNode:
        # order based on the create RGB node bit in common
        Data[label]['X']=valNode.outputs[0].default_value[0]
        Data[label]['Y']=valNode.outputs[0].default_value[1]
        Data[label]['Z']=valNode.outputs[0].default_value[2]
        Data[label]['W']=valNode.outputs[0].default_value[3]

##################################################################################################################
# These are from common.py in the plugin, can be replaced by an include if its put in the plugin 

def openJSON(path, mode='r',  ProjPath='', DepotPath=''):
    inproj=os.path.join(ProjPath,path)
    if os.path.exists(inproj):
        file = open(inproj,mode)
    else:
        file = open(os.path.join(DepotPath,path),mode)
    return file

    
##################################################################################################################
def output_metal_base_json(objects,filename):        
    
    current_file_path = os.path.abspath(__file__)
    current_directory = os.path.dirname(current_file_path)
    file = open( os.path.join(current_directory[:-7],"Template.material.json"),mode='r')
    if not file:
        print("No json found for Material Template")
        return
    mjson_temp = json.loads(file.read())
    file.close()
    all_mats = []
    for obj in objects:
        for material_slot in obj.material_slots:
            material_slot.material.name=obj.name.replace('.','_')+'_'+material_slot.material.name.replace('.','_')
            all_mats.append( material_slot.material)
            
    while len(mjson_temp['Materials'])<len(all_mats):
        mjson_temp['Materials'].append(copy.deepcopy(mjson_temp['Materials'][0]))
        mjson_temp['MaterialTemplates'].append(copy.deepcopy(mjson_temp['MaterialTemplates'][0]))


    for mno,material in enumerate(all_mats):
      
        mjentry=mjson_temp['Materials'][mno]
        
        nodes=material.node_tree.nodes
        print(material.name)
        mjentry['Name']=material.name

        valNode = True
        if valNode:
            mjentry['EnableMask']=valNode

        values = mjentry['Data']
        for Data in values:
            if Data=="BaseColor":
                values[Data]=make_rel(material["Diffuse"].replace('png','xbm'))
            
            if Data=="Normal":
                values[Data]=make_rel(material["Normal"].replace('png','xbm'))
            
    mi_filepath=filename[:-3]+'material.json'
    with open(mi_filepath, 'w') as outfile:
        json.dump(mjson_temp, outfile,indent=2)  
        print('Saved to ',mi_filepath)  


fbx_file = 'C:\\CPMod\\witchermod\\c_01_wa__triss.fbx'
#import_redkit_fbx(fbx_file)

export_redkit_to_glb('C:\\CPMod\\witchermod\\yennifer2.glb')
#xml_file = 'C:\\CPMod\\witchermod\\yennefer.xml'