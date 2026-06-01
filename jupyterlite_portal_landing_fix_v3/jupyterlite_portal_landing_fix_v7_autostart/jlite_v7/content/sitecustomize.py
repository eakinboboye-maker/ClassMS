"""ClassLite automatic notebook setup.

Python imports this module automatically during kernel startup when the content
root is on sys.path. A second copy also exists in EEE355/ for kernels whose
working directory is the notebook folder.
"""

try:
    from _shared.classlite_autostart import run
    run()
except Exception:
    pass
