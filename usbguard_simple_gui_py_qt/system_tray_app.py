# USBGuard Simple GUI Py/Qt
# Copyright (C) 2019  Marco Nicola
#
# This file is part of "USBGuard Simple GUI Py/Qt".
#
# "USBGuard Simple GUI Py/Qt" is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# "USBGuard Simple GUI Py/Qt" is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "USBGuard Simple GUI Py/Qt".  If not, see
# <https://www.gnu.org/licenses/>.

import os
import signal
import sys
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import (QAction,
                               QApplication,
                               QMenu,
                               QMessageBox,
                               QSystemTrayIcon)
from . import APP_NAME
from .device import Device
from .main_window import MainWindow
from .rules import RuleTarget
from .usbguard_dbus_interface import (CallbackEventType,
                                      EventPresenceChangeType,
                                      UsbguardDbusInterface)

SYSTEM_TRAY_APP_NAME = f'{APP_NAME} - System Tray App'


class SystemTrayApp:
    def __init__(
        self,
        app: QApplication,
        usbguard_dbus: UsbguardDbusInterface
    ) -> None:
        self._app = app
        self._main_window = MainWindow(app, usbguard_dbus)
        self._open_action = self._create_open_action()
        self._quit_action = self._create_quit_action()
        self._menu = self._create_menu()
        self._tray_icon = self._create_tray_icon()

        self._usbguard_dbus = usbguard_dbus
        self._register_dbus_callbacks()

    def start(self) -> None:
        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(
                None,
                SYSTEM_TRAY_APP_NAME,
                'System tray is not available.')
            sys.exit(1)

        if not QSystemTrayIcon.supportsMessages():
            QMessageBox.warning(
                None,
                SYSTEM_TRAY_APP_NAME,
                'The system tray does not support notification '
                '("balloon") messages.')

        self._tray_icon.show()

    def _create_open_action(self) -> QAction:
        action = QAction('Open')
        action.triggered.connect(self._open_window)
        return action

    def _create_quit_action(self) -> QAction:
        action = QAction('Quit')
        action.triggered.connect(self._quit_app)
        return action

    def _create_menu(self) -> QMenu:
        menu = QMenu()
        menu.addAction(self._open_action)
        menu.addSeparator()
        menu.addAction(self._quit_action)
        return menu

    def _create_tray_icon(self):
        icon_filename = os.path.join(os.path.dirname(__file__), 'icon.svg')
        icon = QIcon(icon_filename)
        tray_icon = QSystemTrayIcon()
        tray_icon.setContextMenu(self._menu)
        tray_icon.setIcon(icon)
        tray_icon.activated.connect(self._on_activated)
        tray_icon.messageClicked.connect(self._open_window)
        tray_icon.setToolTip(APP_NAME)
        return tray_icon

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason in (QSystemTrayIcon.DoubleClick, QSystemTrayIcon.Trigger):
            self._open_window()

    def _quit_app(self) -> None:
        self._app.quit()

    def _open_window(self) -> None:
        self._main_window.show()

    def _register_dbus_callbacks(self) -> None:
        if not QSystemTrayIcon.supportsMessages():
            # The user will be notified by `start()`
            return

        self._usbguard_dbus.register_callback(
            CallbackEventType.DEVICE_PRESENCE_CHANGED,
            self._on_device_presence_changed
        )
        self._usbguard_dbus.register_callback(
            CallbackEventType.DEVICE_PRESENCE_CHANGED_ERROR,
            self._on_device_presence_changed_error
        )

    def _on_device_presence_changed(
        self,
        device: Device,
        event: EventPresenceChangeType,
        _target: int
    ) -> None:
        if event is EventPresenceChangeType.REMOVE:
            self._show_removed_device_message(device)
        elif device.rule.target is RuleTarget.ALLOW:
            self._show_allowed_device_message(device)
        else:
            self._show_not_allowed_device_message(device)

    def _show_removed_device_message(self, device: Device):
        self._tray_icon.showMessage(
            f'USB device "{device.human_readable_name}" was removed',
            device.rule.human_repr,
            QSystemTrayIcon.Information)

    def _show_allowed_device_message(self, device: Device):
        self._tray_icon.showMessage(
            f'USB device "{device.human_readable_name}" was allowed',
            device.rule.human_repr,
            QSystemTrayIcon.Information)

    def _show_not_allowed_device_message(self, device: Device):
        self._tray_icon.showMessage(
            f'USB device "{device.human_readable_name}" is not allowed!',
            f'Click here to open {APP_NAME} and take action.\n\n'
            f'{device.rule.human_repr}',
            QSystemTrayIcon.Warning,
            100_000_000)

    def _on_device_presence_changed_error(self, error: Exception) -> None:
        self._tray_icon.showMessage(
            f'{APP_NAME} - Application Error',
            f'An error occurred while processing a device presence change '
            f'event.\n\nDetails:\n{error.__class__.__name__} - {str(error)}',
            QSystemTrayIcon.Critical,
            100_000_000)


def main() -> None:
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    usbguard_dbus = UsbguardDbusInterface()

    system_tray_app = SystemTrayApp(app, usbguard_dbus)
    system_tray_app.start()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
