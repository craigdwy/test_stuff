# No Shebang line. This file is meant to be imported


"""
This is an experiment to create dynamic classes and validate attributes supplied while constructing the class.
"""
import sys
import types
from yaml import load
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

_TEMPLATE_DATA = load(open('./data/test.yaml'), Loader=Loader)


def validate_attributes(self):
    """
    Ensure all attributes are supplied in construction of class.
    This returns a bool for now but should end with an exception in reality
    """
    out = set(self.__dict__["required_attributes"]).issubset([k for k, v in self.__dict__.items()])
    return out


def constructor(self, *args, **kwargs):
    """
    Constructor for dynamic classes
    """
    for dictionary in args:
        for k in dictionary:
            setattr(self, k, dictionary[k])
    for k in kwargs:
        setattr(self, k, kwargs[k])

    self.validate_attributes()


def class_factory(template_name, kwattrs):
    """
    Create dynamic Class objects and bind a constructor and validator to it
    """
    obj = type(template_name, (object,), kwattrs)
    obj.__init__ = types.MethodType(constructor, obj)
    obj.validate_attributes = types.MethodType(validate_attributes, obj)
    return obj


# go through template and create dynamic classes
dynamic_module = types.ModuleType(__name__)
for key, value in _TEMPLATE_DATA.items():
    attributes = {'required_attributes': value}
    class_obj = class_factory(key, attributes)
    setattr(dynamic_module, class_obj.__name__, class_obj)

sys.modules[__name__] = dynamic_module
