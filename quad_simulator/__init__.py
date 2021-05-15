bl_info = {
    "name": "Quadcopter FPV Simulator",
    "author": "WizardOfRobots",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View > Navigation > Quadcopter Mode",
    "description": "Fly any object/camera like a quadcopter FPV pilot",
    "warning": "Has Dependencies. Permission Needed. Controller/Gamepad required",
    "doc_url": "https://github.com/hazkaz/blender-quadcopter-fpv",
    "category": "3D View",
}


import sys
import importlib
from collections import namedtuple

Dependency = namedtuple("Dependency", ["module", "package", "name"])

# Declare all modules that this add-on depends on, that may need to be installed. The package and (global) name can be
# set to None, if they are equal to the module name. See import_module and ensure_and_import_module for the explanation
# of the arguments. DO NOT use this to import other parts of your Python add-on, import them as usual with an
# "import" statement.
dependencies = (Dependency(module="pygame", package=None, name=None),)

modulesNames=['quad','ensure_dependencies']

 
modulesFullNames = {}
for currentModuleName in modulesNames:
    modulesFullNames[currentModuleName] = ('{}.{}'.format(__name__, currentModuleName))
 
for currentModuleFullName in modulesFullNames.values():
    if currentModuleFullName in sys.modules:
            importlib.reload(sys.modules[currentModuleFullName])
    else:
        globals()[currentModuleFullName] = importlib.import_module(currentModuleFullName)
        setattr(globals()[currentModuleFullName], 'modulesNames', modulesFullNames)
 
def register():
    for currentModuleName in modulesFullNames.values():
        if currentModuleName in sys.modules:
            if hasattr(sys.modules[currentModuleName], 'register'):
                sys.modules[currentModuleName].register()
        
 
def unregister():
    for currentModuleName in modulesFullNames.values():
        if currentModuleName in sys.modules:
            if hasattr(sys.modules[currentModuleName], 'unregister'):
                sys.modules[currentModuleName].unregister()
 
if __name__ == "__main__":
    register()