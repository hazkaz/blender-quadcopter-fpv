from ensure_dependencies import ensure_deps
ensure_deps()

from mathutils import Vector, Euler, Quaternion, Matrix
from bpy.utils import register_class, unregister_class
from math import radians
import pygame
import time
import os
import bpy
bl_info = {
    "name": "Quadcopter FPV Simulator",
    "author": "WizardOfRobots",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View > Navigation > Quadcopter Mode",
    "description": "Fly any object/camera like a quadcopter FPV pilot",
    "warning": "Has Dependencies. Permission Needed. Controller/Gamepad required",
    "doc_url": "https://github.com/hazkaz/blender-quadcopter-fpv",
    "category": "Simulator",
}


os.environ["SDL_VIDEODRIVER"] = "dummy"


class QuadcopterSimulator(bpy.types.Operator):
    """Modal Operator which runs once every frame"""
    bl_idname = "wm.quadcopter_mode"
    bl_label = "Quadcopter Mode"

    _timer = None

    def __init__(self):
        super().__init__()
        self.cam_angle = radians(90 - 5)
        self.force_vect = Vector((0, 0, 0))
        self.velocity = Vector((0, 0, 0))
        self.air_resistance_factor = Vector((0.3, 0.3, 0.3))
        self.quadcopter_mass = 1
        self.fps = 30
        self.last_time = 0
        self.max_thrust = 30

    def _get_controller_vals(self):
        pitch_val = self.js.get_axis(1)
        roll_val = self.js.get_axis(0)
        yaw_val = self.js.get_axis(3)
        throttle_val = self.js.get_axis(2)
        return pitch_val, roll_val, throttle_val, yaw_val

    def modal(self, context, event):
        if event.type in {'RIGHTMOUSE', 'ESC'} or not context.window_manager.quadcopter_mode:
            context.window_manager.quadcopter_mode = False
            self.cancel(context)
            return {'CANCELLED'}

        if event.type == 'TIMER':
            ctime = time.perf_counter()
            delta_time = ctime - self.last_time
            # print(delta_time)
            #print(ctime - self.last_time,1.0/self.fps)
            if (delta_time) >= (1.0/self.fps):
                self.last_time = time.perf_counter()
                pygame.event.pump()
                pitch_val, roll_val, throttle_val, yaw_val = self._get_controller_vals()
                throttle_val += 1.0

                # rotation
                inverted_world_vector = self.cam.matrix_world.inverted()
                rotation_vect = Vector(
                    map(lambda x: x*0.2, (pitch_val, yaw_val, roll_val)))
                rotation_axis = -rotation_vect @ inverted_world_vector

                # thrust
                thrust_vect = Vector((0, 0, throttle_val))*self.max_thrust
                gravity_vect = Vector((0, 0, -9.8))
                thrust_vect.rotate(Euler((self.cam_angle, 0, 0)))
                thrust_vect = -thrust_vect @ inverted_world_vector
                thrust_vect /= self.quadcopter_mass
                net_force_vect = thrust_vect+gravity_vect
                self.force_vect = net_force_vect
                self.velocity += (self.force_vect*delta_time)

                self.cam.rotation_euler.rotate(Quaternion(
                    rotation_axis, rotation_vect.magnitude))
                self.cam.location += (self.velocity*delta_time)
                if self.record == True:
                    self.cam.keyframe_insert(data_path="location", index=-1)
                    self.cam.keyframe_insert(
                        data_path="rotation_euler", index=-1)

        return {'PASS_THROUGH'}

    def execute(self, context):
        wm = context.window_manager
        print(self.fps)
        self._timer = wm.event_timer_add(1/self.fps, window=context.window)
        wm.modal_handler_add(self)
        self.last_time = time.perf_counter()
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        self.fps = context.scene.render.fps
        self.cam = bpy.data.objects['Camera']
        self.record = context.tool_settings.use_keyframe_insert_auto
        if self.record == True:
            self.cam.keyframe_insert(data_path="location", frame=0)
            self.cam.keyframe_insert(data_path="rotation_euler", index=0)
        pygame.display.init()
        pygame.joystick.init()
        self.js = pygame.joystick.Joystick(0)
        self.js.init()
        return self.execute(context)

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        self.js.quit()


class QuadcopterConfigPanel(bpy.types.Panel):
    """Configure the QuadcopterSimulator"""
    bl_label = "Quadcopter Config Panel"
    bl_idname = "OBJECT_PT_quad"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Quadcopter"

    def draw(self, context):
        layout = self.layout
        obj = context.object
        row = layout.row()
        row.prop(context.window_manager,'quadcopter_mode',text="Quadcopter Mode", icon='ORIENTATION_GIMBAL',toggle=True)

def 

_classes = [
    QuadcopterSimulator,
    QuadcopterConfigPanel
]


def menu_func(self, context):
    self.layout.operator(QuadcopterSimulator.bl_idname)


def update_function(self,context):
    if self.quadcopter_mode:
        bpy.ops.wm.quadcopter_mode('INVOKE_DEFAULT')
    return


def register():
    for cls in _classes:
        register_class(cls)
    bpy.types.VIEW3D_MT_object.append(menu_func)
    bpy.types.WindowManager.quadcopter_mode = bpy.props.BoolProperty(default=False,update=update_function)


def unregister():
    for cls in _classes:
        unregister_class(cls)
    bpy.types.VIEW3D_MT_object.remove(menu_func)


if __name__ == "__main__":
    register()
