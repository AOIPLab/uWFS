# This file was automatically generated by SWIG (http://www.swig.org).
# Version 2.0.9
#
# Do not make changes to this file unless you know what you are doing--modify
# the SWIG interface file instead.



from sys import version_info
if version_info >= (2,6,0):
    def swig_import_helper():
        from os.path import dirname
        import imp
        fp = None
        try:
            fp, pathname, description = imp.find_module('_acedev5', [dirname(__file__)])
        except ImportError:
            import _acedev5
            return _acedev5
        if fp is not None:
            try:
                _mod = imp.load_module('_acedev5', fp, pathname, description)
            finally:
                fp.close()
            return _mod
    _acedev5 = swig_import_helper()
    del swig_import_helper
else:
    import _acedev5
del version_info
try:
    _swig_property = property
except NameError:
    pass # Python < 2.2 doesn't have 'property'.
def _swig_setattr_nondynamic(self,class_type,name,value,static=1):
    if (name == "thisown"): return self.this.own(value)
    if (name == "this"):
        if type(value).__name__ == 'SwigPyObject':
            self.__dict__[name] = value
            return
    method = class_type.__swig_setmethods__.get(name,None)
    if method: return method(self,value)
    if (not static):
        self.__dict__[name] = value
    else:
        raise AttributeError("You cannot add attributes to %s" % self)

def _swig_setattr(self,class_type,name,value):
    return _swig_setattr_nondynamic(self,class_type,name,value,0)

def _swig_getattr(self,class_type,name):
    if (name == "thisown"): return self.this.own()
    method = class_type.__swig_getmethods__.get(name,None)
    if method: return method(self)
    raise AttributeError(name)

def _swig_repr(self):
    try: strthis = "proxy of " + self.this.__repr__()
    except: strthis = ""
    return "<%s.%s; %s >" % (self.__class__.__module__, self.__class__.__name__, strthis,)

try:
    _object = object
    _newclass = 1
except AttributeError:
    class _object : pass
    _newclass = 0


class dblArray(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, dblArray, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, dblArray, name)
    __repr__ = _swig_repr
    def __init__(self, *args): 
        this = _acedev5.new_dblArray(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _acedev5.delete_dblArray
    __del__ = lambda self : None;
    def __getitem__(self, *args): return _acedev5.dblArray___getitem__(self, *args)
    def __setitem__(self, *args): return _acedev5.dblArray___setitem__(self, *args)
    def cast(self): return _acedev5.dblArray_cast(self)
    __swig_getmethods__["frompointer"] = lambda x: _acedev5.dblArray_frompointer
    if _newclass:frompointer = staticmethod(_acedev5.dblArray_frompointer)
dblArray_swigregister = _acedev5.dblArray_swigregister
dblArray_swigregister(dblArray)

def dblArray_frompointer(*args):
  return _acedev5.dblArray_frompointer(*args)
dblArray_frompointer = _acedev5.dblArray_frompointer

acecsFAILURE = _acedev5.acecsFAILURE
acecsSUCCESS = _acedev5.acecsSUCCESS

def acedev5Init(*args):
  return _acedev5.acedev5Init(*args)
acedev5Init = _acedev5.acedev5Init

def acedev5Release(*args):
  return _acedev5.acedev5Release(*args)
acedev5Release = _acedev5.acedev5Release

def acedev5CheckElectronic(*args):
  return _acedev5.acedev5CheckElectronic(*args)
acedev5CheckElectronic = _acedev5.acedev5CheckElectronic

def acedev5GetNbActuator(*args):
  return _acedev5.acedev5GetNbActuator(*args)
acedev5GetNbActuator = _acedev5.acedev5GetNbActuator

def acedev5GetOffset(*args):
  return _acedev5.acedev5GetOffset(*args)
acedev5GetOffset = _acedev5.acedev5GetOffset

def acedev5Send(*args):
  return _acedev5.acedev5Send(*args)
acedev5Send = _acedev5.acedev5Send

def acedev5SendSingleActuator(*args):
  return _acedev5.acedev5SendSingleActuator(*args)
acedev5SendSingleActuator = _acedev5.acedev5SendSingleActuator

def acedev5SoftwareDACReset(*args):
  return _acedev5.acedev5SoftwareDACReset(*args)
acedev5SoftwareDACReset = _acedev5.acedev5SoftwareDACReset

def acedev5StartPattern(*args):
  return _acedev5.acedev5StartPattern(*args)
acedev5StartPattern = _acedev5.acedev5StartPattern

def acedev5StopPattern(*args):
  return _acedev5.acedev5StopPattern(*args)
acedev5StopPattern = _acedev5.acedev5StopPattern

def acedev5QueryPattern(*args):
  return _acedev5.acedev5QueryPattern(*args)
acedev5QueryPattern = _acedev5.acedev5QueryPattern

def acecsErrDisplay():
  return _acedev5.acecsErrDisplay()
acecsErrDisplay = _acedev5.acecsErrDisplay

def acecsErrGetStatus():
  return _acedev5.acecsErrGetStatus()
acecsErrGetStatus = _acedev5.acecsErrGetStatus

def acecsLogSet(*args):
  return _acedev5.acecsLogSet(*args)
acecsLogSet = _acedev5.acecsLogSet
# This file is compatible with both classic and new-style classes.

