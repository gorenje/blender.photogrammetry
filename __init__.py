import bpy

bl_info = {
    'name': 'Photogrammetry Plugin',
    'description': 'Support Functionality',
    'author': 'Dildodonkey Inc.',
    'license': 'GPL',
    'deps': '',
    'version': (0, 0, 1),
    "blender": (2, 80, 0),
    'warning': '',
    'category': 'Mesh'
}
bl_info['blender'] = getattr(bpy.app, "version")

PLUGIN_VERSION = str(bl_info['version']).strip('() ').replace(',', '.')
is_plugin_enabled = False

class PhotogrammetryMeshCloseHole(bpy.types.Operator):
    """Extrude and close hole"""
    bl_idname = "mesh.photogrammetry_fill_loop"
    bl_label = "Close Hole"
    bl_options = {'REGISTER', 'UNDO'}

    steps: bpy.props.IntProperty(name="Steps", default=2, min=1, max=100)

    def execute(self,context):
        factor = (0.9, 0.9, 0.9)
        if self.steps > 2: factor = (0.5, 0.5, 0.5)

        for x in range(self.steps):
            bpy.ops.mesh.extrude_region(use_normal_flip=False,
                                        use_dissolve_ortho_edges=False,
                                        mirror=False)

            bpy.ops.transform.resize(value=factor,
                                     orient_type='GLOBAL',
                                     orient_matrix=((1, 0, 0),
                                                    (0, 1, 0),
                                                    (0, 0, 1)),
                                     orient_matrix_type='GLOBAL',
                                     mirror=True,
                                     use_proportional_edit=False,
                                     proportional_edit_falloff='SMOOTH',
                                     proportional_size=1,
                                     use_proportional_connected=False,
                                     use_proportional_projected=False)

        bpy.ops.mesh.merge(type='CENTER')

        return {'FINISHED'}

class PhotogrammetryRemoveNonConnected(bpy.types.Operator):
    """Select main mesh and this will remove all non connected mesh parts"""
    bl_idname = "mesh.photogrammetry_rm_unconnected"
    bl_label = "Remove Unconnected"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self,context):
        bpy.ops.mesh.select_linked(delimit=set())
        bpy.ops.mesh.select_all(action='INVERT')
        bpy.ops.mesh.delete(type='VERT')

        return {'FINISHED'}

class PhotogrammetryInit(bpy.types.Operator):
    """Move object to origin, merge mesh, remove duplicates and set clip start"""
    bl_idname = "object.photogrammetry_init"
    bl_label = "Initialise"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.context.space_data.clip_start = 0.0001
        bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN', center='MEDIAN')
        bpy.context.object.active_material.use_backface_culling = False
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles()
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.editmode_toggle()

        return {'FINISHED'}

# menu containing all tools
class VIEW3D_MT_edit_mesh_photogrammetry(bpy.types.Menu):
    bl_label = "Photogrammetry"

    def draw(self, context):
        layout = self.layout
        for cls in [PhotogrammetryRemoveNonConnected,
                    PhotogrammetryMeshCloseHole]:
            layout.operator(cls.bl_idname, text=cls.bl_label)

class VIEW3D_MT_object_context_photogrammetry(bpy.types.Menu):
    bl_label = "Photogrammetry"

    def draw(self, context):
        layout = self.layout

        for cls in [PhotogrammetryInit]:
            layout.operator(cls.bl_idname, text=cls.bl_label)

clz = [
    VIEW3D_MT_object_context_photogrammetry,
    VIEW3D_MT_edit_mesh_photogrammetry,
    PhotogrammetryInit,
    PhotogrammetryRemoveNonConnected,
    PhotogrammetryMeshCloseHole,
]

addon_keymaps = []

def edit_menu_func(self, context):
    self.layout.menu("VIEW3D_MT_edit_mesh_photogrammetry")

def object_menu_func(self, context):
    self.layout.menu("VIEW3D_MT_object_context_photogrammetry")

def register():
    for cls in clz: bpy.utils.register_class(cls)

    bpy.types.VIEW3D_MT_edit_mesh_context_menu.append(edit_menu_func)
    bpy.types.VIEW3D_MT_object_context_menu.append(object_menu_func)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='Mesh',space_type='EMPTY',region_type='WINDOW')

        for let,stps in [('E',1),('D',2),('C',3)]:
            kmi = km.keymap_items.new(PhotogrammetryMeshCloseHole.bl_idname,
                                      let, 'PRESS', shift=True, oskey=True)
            kmi.properties.steps = stps
            kmi.active = True
            addon_keymaps.append((km, kmi))

def unregister():
    for km, kmi in addon_keymaps: km.keymap_items.remove(kmi)
    for cls in clz: bpy.utils.unregister_class(cls)

    addon_keymaps.clear()

    bpy.types.VIEW3D_MT_edit_mesh_context_menu.remove(edit_menu_func)
    bpy.types.VIEW3D_MT_object_context_menu.remove(object_menu_func)

# This allows you to run the script directly from Blender's Text editor
# to test the add-on without having to install it.
if __name__ == "__main__":
    register()