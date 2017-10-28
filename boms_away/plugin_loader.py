import pkgutil
import importlib
import inspect

from . import  export_plugins

def load_export_plugins():
    """ Loads all export plugins stored in boms_away/export_plugins which
        adhere to the following rules:

        * Must be a base class of BomsAwayExporter
        * Must expose an 'export' function
        * Must have class variables: extension, wildcard
    """
    results = []
    for loader, name, is_pkg in pkgutil.walk_packages(export_plugins.__path__):
        # Skip private modules (i.e. base classes)
        if name.startswith('_'):
            continue
        full_name = export_plugins.__name__ + '.' + name
        mod = importlib.import_module(full_name)
        for obj_name in dir(mod):
            obj = getattr(mod, obj_name)
            if not inspect.isclass(obj):
                continue
            baseclass = obj.__bases__[0]

            if not baseclass.__name__ == 'BomsAwayExporter':
                continue

            if not obj().validate():
                continue

            results.append(obj)

    return results
