from platform import machine, system
from praline.common.file_system import which


def get_architecture():
    m = machine()
    if m == 'i386':
        return 'x86'
    elif m == 'AMD64' or m == 'x86_64':
        return 'x86_64'
    else:
        raise RuntimeError(f"unrecognized architecture {m}")


platform = str(system()).lower()

architecture = get_architecture()
