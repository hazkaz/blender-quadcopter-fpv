import bpy
import os
import time
import pygame
from math import radians
from mathutils import Vector, Euler, Quaternion, Matrix

os.environ["SDL_VIDEODRIVER"] = "dummy"

class QuadSimulator(bpy.types.Operator):
    """Operator which runs its self from a timer"""
    bl_idname = "wm.quad_simulator"
    bl_label = "Quad Simulator"

    _timer = None

    def __init__(self):
        super().__init__()
        self.cam_angle = radians(90  - 0)
        self.force_vect = Vector((0,0,0))
        self.velocity = Vector((0,0,0))
        self.air_resistance_factor = Vector((0.3,0.3,0.3))
        self.quadcopter_mass = 0.2
        self.fps = 30
        self.last_time=0
        self.max_thrust = 1
        
    def get_controller_vals(self):
            pitch_val = self.js.get_axis(1)
            roll_val = self.js.get_axis(0)
            yaw_val = self.js.get_axis(3)
            throttle_val = self.js.get_axis(2)
            return pitch_val,roll_val,throttle_val,yaw_val

    def modal(self, context, event):
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cancel(context)
            return {'CANCELLED'}

        if event.type == 'TIMER':
            ctime = time.perf_counter()
#            print(ctime - self.last_time,1.0/self.fps)
            if (ctime - self.last_time) >= (1.0/self.fps):
                self.last_time = time.perf_counter()                  
                pygame.event.pump()               
                pitch_val,roll_val,throttle_val,yaw_val = self.get_controller_vals()
                throttle_val +=1.0            
                
                # rotation            
                inverted_world_vector = self.cam.matrix_world.inverted()
                rotation_vect = Vector(map(lambda x:x*0.1, (pitch_val,yaw_val,roll_val)))
                rotation_axis = -rotation_vect @ inverted_world_vector

                # thrust
                thrust_vect = Vector((0,0,throttle_val))*self.max_thrust
                gravity_vect = Vector((0,0,-9.8))*self.quadcopter_mass
                thrust_vect.rotate(Euler((self.cam_angle,0,0)))
                thrust_vect =  -thrust_vect @ inverted_world_vector
                thrust_vect /= self.quadcopter_mass
                net_force_vect = thrust_vect+gravity_vect
                self.force_vect = net_force_vect
                self.velocity += self.force_vect*self.air_resistance_factor*0.01

                self.cam.rotation_euler.rotate(Quaternion(rotation_axis,rotation_vect.magnitude))
                self.cam.location+=self.velocity
                if self.record==True:
                    self.cam.keyframe_insert(data_path="location", index=-1)
                    self.cam.keyframe_insert(data_path="rotation_euler", index=-1)

        return {'PASS_THROUGH'}

    def execute(self, context):
        wm = context.window_manager
        print(self.fps)
        self._timer = wm.event_timer_add(1/self.fps, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def invoke(self,context, event):
        self.fps = context.scene.render.fps
        self.cam = bpy.data.objects['Camera']
        self.record = context.tool_settings.use_keyframe_insert_auto
        if self.record==True:
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

def menu_func(self,context):
    self.layout.operator(QuadSimulator.bl_idname)

def register():
    bpy.utils.register_class(QuadSimulator)
    bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
    bpy.utils.unregister_class(QuadSimulator)


if __name__ == "__main__":
    register()

