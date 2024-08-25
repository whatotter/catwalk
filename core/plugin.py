"""
plugin loading system
"""
import os
import importlib
from core.printl import info
  
plugins = {}

class CatwalkManagers():
    def __init__(self, folder:str="managers"):
        r = {}

        for item in os.listdir(f"./{folder}"):
            if ".py" in item:
                
                item = item.replace('.py','')
                if len(item) == 0:
                    continue

                importfolder = folder.replace("/", ".")

                FUCK = "{}.{}".format(importfolder, item).replace("..", ".")

                plugins[item] = importlib.import_module(FUCK)

                objects = [x for x in dir(plugins[item]) if x.startswith("Catwalk")]

                for x in objects:
                    #z = plugins[item].Plugin()
                    z = getattr(plugins[item], x)
                    r[item+"::"+x] = {"functions": [y for y in dir(z) if not y.startswith("_")], "module": z}
                    info("[PL] loading class \"{}\"".format(item+"::"+x))
            

        self.modules = r
        self.moduleList = []

        for k,v in self.modules.items():
            self.moduleList += v["functions"]

    def run(self, plugin:object, target:str, *args, **kwargs):
        """
        run a command using it's class and function name, alongside args

        plugin: class/object the function is in, for example "MyClass"
        target: the function in that object to call, for example "MyFunction"
        *args: passed to the called function
        **kwargs: passed to the called function

        returns the function passed, for example the actual object of "MyFunction"
        """
        func = getattr(plugin, target)
        return func(*args, **kwargs)
    
    def getOriginModule(self, function):
        """
        gets the class/object that a function came from, for calling, used in conjunction with self.run()

        function: function to find

        returns False if not found, returns the object otherwise
        """

        for k,v in self.modules.items():
            if function in list(v["functions"]):
                return v["module"]
        return False
    
class CatwalkPlugins():
    def __init__(self, folder:str="webplugins"):
        r = {}

        for item in os.listdir(f"./{folder}"):
            if ".py" in item:
                
                item = item.replace('.py','')
                if len(item) == 0:
                    continue

                importfolder = folder.replace("/", ".")

                FUCK = "{}.{}".format(importfolder, item).replace("..", ".")

                plugins[item] = importlib.import_module(FUCK)

                objects = [x for x in dir(plugins[item]) if x.startswith("CWWP")]

                for x in objects:
                    #z = plugins[item].Plugin()
                    z = getattr(plugins[item], x)
                    r[item+"::"+x] = {"functions": [y for y in dir(z) if not y.startswith("_")], "module": z}
                    info("[PL] loading class \"{}\"".format(item+"::"+x))
            

        self.modules = r
        self.moduleList = []

        for k,v in self.modules.items():
            self.moduleList += v["functions"]

    def run(self, plugin:object, target:str, *args, **kwargs):
        """
        run a command using it's class and function name, alongside args

        plugin: class/object the function is in, for example "MyClass"
        target: the function in that object to call, for example "MyFunction"
        *args: passed to the called function
        **kwargs: passed to the called function

        returns the function passed, for example the actual object of "MyFunction"
        """
        func = getattr(plugin, target)
        return func(*args, **kwargs)
    
    def getvar(self, plugin:object, target:str):
        return getattr(plugin, target)
    
    def getOriginModule(self, function):
        """
        gets the class/object that a function came from, for calling, used in conjunction with self.run()

        function: function to find

        returns False if not found, returns the object otherwise
        """

        for k,v in self.modules.items():
            if function in list(v["functions"]):
                return v["module"]
        return False