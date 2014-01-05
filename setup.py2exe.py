from distutils.core import setup
import py2exe
import os, glob

# py2exe setup script.
# http://starship.python.net/crew/theller/py2exe/
# tested with py2exe 0.5.4 python2.4.1
# python setup.py py2exe --bundle 1

# usage:
# python setup.py py2exe


import sys

sys.argv.extend(["py2exe", "--bundle", "1"])

dist_dir = "./1GAM-02-SpaceWar"
opts = {"py2exe": {
           "optimize": 1,
           #"ascii": True,
           "dist_dir": dist_dir,
           "excludes": ["tcl", "tk"],
           #"excludes": ["encodings"],
           #"includes": ["pyglet.media.drivers.directsound"],
           "includes": ["pygame._view"],
           "dll_excludes": ["MSVCR71.dll"],
         }
}

origIsSystemDLL = py2exe.build_exe.isSystemDLL
def isSystemDLL(pathname):
       if os.path.basename(pathname).lower() in ["sdl_ttf.dll", "libogg-0.dll"]:
               return 0
       return origIsSystemDLL(pathname)
py2exe.build_exe.isSystemDLL = isSystemDLL

setup(
    # The first three parameters are not required, if at least a
    # 'version' is given, then a versioninfo resource is built from
    # them and added to the executables.
    version = "0.7.3",
    description = "Classic turn-based tactical combat",
    name = "SpaceWar",

    # targets to build.  name of your exe here.
    windows = [{
               "script":"spacewar.py",
               "icon_resources":[(0,'spacewar.ico')],
               "dest_base": "SpaceWar",
               }],
    options = opts,
    zipfile = None, #"library.zip", #None, # This places the python zip library into the executable
    data_files=[],
)

def copy_data_dirs():
    import shutil
    shutil.copytree("data", os.path.join(dist_dir, "data"))
    shutil.copy("readme.txt", os.path.join(dist_dir, "readme.txt"))
    #shutil.copy("C:\\Python27-32\\Lib\\site-packages\\pygame\\libogg-0.dll", os.path.join(dist_dir, "libogg-0.dll"))


print "-" * 40
print "copying files"
print "-" * 40
copy_data_dirs()

