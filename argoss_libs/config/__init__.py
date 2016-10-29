# -*- coding: UTF-8
try:
    from .default import *
except ImportError as err:
    raise ImportError(err)

if DEV:
    try:
        from .dev import *
    except ImportError as err:
        #print("There is no dev Config")
        pass
