from PyInstaller.utils.hooks import collect_data_files

# Hook global variables
# =====================
#
# For the package ``pyi_hooksample`` to be frozen successfully,
# the module ``pyi_hooksample._hidden`` needs to be frozen, too,
# as well as all data-files.
# This hook takes care about this.
# For more information see
# `hook global variables
# <https://pyinstaller.readthedocs.io/en/stable/hooks.html#hook-global-variables>`_
# in the manual for more information.

hiddenimports = ["scr_core.basic"]
# The ``excludes`` parameter of `collect_data_files
# <https://pyinstaller.readthedocs.io/en/stable/hooks.html#useful-items-in-pyinstaller-utils-hooks>`_
# excludes ``rthooks.dat`` from the frozen executable, which is only needed when
# freezeing, but not when executing the frozen program.
datas = collect_data_files('scr_core', excludes=['__pyinstaller'])