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

import signal
import sys
from PySide2.QtWidgets import QApplication, QDialog
from . import APP_NAME
from .device import Device
from .usbguard_dbus_interface import (CallbackEventType,
                                      EventPresenceChangeType,
                                      UsbguardDbusInterface)


class MainWindow(QDialog):
    def __init__(self, usbguard_dbus: UsbguardDbusInterface) -> None:
        super().__init__()
        self.setWindowTitle(APP_NAME)

        self._usbguard_dbus = usbguard_dbus
        self._usbguard_dbus.register_callback(
            CallbackEventType.DEVICE_PRESENCE_CHANGED,
            self._on_device_presence_changed
        )

    def _on_device_presence_changed(
        self,
        device: Device,
        event: EventPresenceChangeType,
        target: int
    ) -> None:
        # TODO: to be implemented...
        print(f'{type(self).__name__}: device presence changed')
        print(f'\t{device}')
        print(f'\t{event}')
        print(f'\ttarget = {target}')


def main() -> None:
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)

    usbguard_dbus = UsbguardDbusInterface()

    main_window = MainWindow(usbguard_dbus)
    main_window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
