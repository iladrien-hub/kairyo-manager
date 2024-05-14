from PyQt5 import QtCore, QtGui, QtWidgets

from core.extension import KairyoExtension
from .widgets.settingswidget import SettingsWidget


class SettingsExtension(KairyoExtension):

    def on_setup_ui(self):
        menu = self.api.user_interface.add_menu('File')

        menu.addSeparator()
        action = menu.addAction('Settings')
        action.triggered.connect(self.on_settingsAction_triggered)
        action.setShortcut(QtGui.QKeySequence('Ctrl+Alt+S'))

    def on_settingsAction_triggered(self):
        widget = SettingsWidget()
        widget.setSettings(self.api.settings)
        widget.populateTree(self.api.user_interface.settings)

        dialog = self.api.user_interface.create_dialog('Settings', widget)
        dialog.show()

        widget.updateUi()
