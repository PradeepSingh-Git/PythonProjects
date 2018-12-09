from .vxl import XLCOM
from .kvaser import KVASER
try:
    from .gigabox import GIGABOX
except ImportError, e:
    print e
    print 'INFO: To use a GIGABOX device, please execute LATTE\Com\Trunk\drivers\gigabox\Install_Pythonnet_for_GtFrNET.bat'