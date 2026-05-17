from PySide6 import QtWidgets

if QtWidgets.QApplication.instance() is None:
    app = QtWidgets.QApplication(["-platform", "offscreen"])
