import bpy
import socket
from .. operators.nodes import get_y_nodes

supported_textures = [
    'opacity',
    'ao',
    'albedo',
    'specular',
    'roughness',
    'metalness',
    'displacement',
    'translucency',
    'normal',
    'bump',
    'fuzz',
    'cavity',
    'curvature'
]

# Helper functions
def display_view3d():
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                override = {'window': window, 'screen': screen, 'area': area}
                return override
    return {}

def component_sort(component):
    return supported_textures.index(component['type'])

def get_component(components, name):
    return [component for component in components if component['type'] == name][0]

def add_components_tex(ntree, components):
    prefs = bpy.context.preferences.addons['Octane_Helper'].preferences
    y_exp = 620

    transform_node = ntree.nodes.new('ShaderNodeOctFullTransform')
    transform_node.name = 'transform'
    projection_node = ntree.nodes.new('ShaderNodeOctUVWProjection')
    projection_node.name = 'projection'
    
    texNodes = []

    for component in components:
        texNode = ntree.nodes.new('ShaderNodeOctImageTex')
        texNode.location = (-720, y_exp)
        texNode.image = bpy.data.images.load(component['path'])
        texNode.show_texture = True
        texNode.name = component['type']
        if(component['type'] == 'displacement' and prefs.disp_type == "VERTEX"):
            texNode.border_mode = 'OCT_BORDER_MODE_CLAMP'
        ntree.links.new(ntree.nodes['transform'].outputs[0], texNode.inputs['Transform'])
        ntree.links.new(ntree.nodes['projection'].outputs[0], texNode.inputs['Projection'])
        texNodes.append(texNode)
        y_exp += -320
    
    transform_node.location = (-1200, get_y_nodes(ntree, texNodes, 'Mid'))
    projection_node.location = (-1200, transform_node.location.y - 350)

def group_into_empty(objs, name):
    bpy.ops.object.empty_add(type='SPHERE', radius=0.2)
    empty = bpy.context.view_layer.objects.active
    empty.name = name
    for obj in objs:
        obj.parent = empty

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", port))
        except socket.error as e:
            if e.errno == errno.EADDRINUSE:
                return True
        s.close()
        return False

def is_official_here():
    if('load_plugin' in [handler.__name__.lower() for handler in bpy.app.handlers.load_post]):
        return True
    return False

def is_me_here():
    if('load_ms_module' in [handler.__name__.lower() for handler in bpy.app.handlers.load_post]):
        return True
    return False

def notify(msg, title, icon = 'INFO'):
    def draw(self, context):
        self.layout.label(text=msg)
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)