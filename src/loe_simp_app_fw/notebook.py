from typing import no_type_check

# Parse CLI or not
@no_type_check ## Skip type checker here because 
def _isNotebook():
    return get_ipython().__class__.__name__ # het_python() is globally available when using jupyter notebook

def isNotebook() -> bool:
    try:
        shell = _isNotebook()
        if shell == 'ZMQInteractiveShell':
            return True   # Jupyter notebook or qtconsole
        elif shell == 'TerminalInteractiveShell':
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False      # Probably standard Python interpreter
