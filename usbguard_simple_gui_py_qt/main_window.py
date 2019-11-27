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

from PySide2.QtCore import QSize, QItemSelection
from PySide2.QtGui import Qt
from PySide2.QtWidgets import (QApplication,
                               QDialog,
                               QTableView,
                               QHeaderView,
                               QHBoxLayout,
                               QAbstractItemView,
                               QStyle,
                               QVBoxLayout,
                               QPushButton,
                               QWidget)
from . import APP_NAME
from .device import Device, DeviceModel
from .rules import RuleTarget
from .usbguard_dbus_interface import (CallbackEventType,
                                      EventPresenceChangeType,
                                      UsbguardDbusInterface)


class MainWindow(QDialog):
    def __init__(
        self,
        app: QApplication,
        usbguard_dbus: UsbguardDbusInterface
    ) -> None:
        super().__init__()

        self._app = app
        self._usbguard_dbus = usbguard_dbus

        self._register_dbus_callbacks()
        self._device_model = DeviceModel(self._usbguard_dbus.list_devices())
        self._device_table = self._create_device_table()
        self._controls_section = self._create_controls_section()
        self._init_window_content_and_aspect()

    def _register_dbus_callbacks(self) -> None:
        self._usbguard_dbus.register_callback(
            CallbackEventType.DEVICE_PRESENCE_CHANGED,
            self._on_device_presence_changed)

        self._usbguard_dbus.register_callback(
            CallbackEventType.DEVICE_POLICY_CHANGED,
            self._on_device_policy_changed)

    def _create_device_table(self) -> QTableView:
        device_table = QTableView()
        device_table.setModel(self._device_model)
        device_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        device_table.setSelectionMode(QAbstractItemView.SingleSelection)

        device_table.selectionModel().selectionChanged.connect(
            self._on_device_table_selection_changed)

        horizontal_header = device_table.horizontalHeader()
        vertical_header = device_table.verticalHeader()
        horizontal_header.setSectionResizeMode(QHeaderView.ResizeToContents)
        vertical_header.setSectionResizeMode(QHeaderView.ResizeToContents)
        horizontal_header.setStretchLastSection(True)

        return device_table

    def _create_controls_section(self) -> QWidget:
        btn_allow = QPushButton('Allow')
        btn_allow.clicked.connect(self._on_allow_click)

        btn_block = QPushButton('Block')
        btn_block.clicked.connect(self._on_block_click)

        btn_reject = QPushButton('Reject')
        btn_reject.clicked.connect(self._on_reject_click)

        layout = QHBoxLayout()
        layout.addWidget(btn_allow)
        layout.addWidget(btn_block)
        layout.addWidget(btn_reject)
        layout.setContentsMargins(0, 0, 0, 0)

        controls_section = QWidget()
        controls_section.setLayout(layout)
        controls_section.hide()  # will show only on selection

        return controls_section

    def _init_window_content_and_aspect(self) -> None:
        window_layout = QVBoxLayout()
        window_layout.addWidget(self._device_table)
        window_layout.addWidget(self._controls_section)
        self.setLayout(window_layout)

        screen_geom = self._app.desktop().availableGeometry(self)
        window_size = QSize(screen_geom.width(), screen_geom.height()) * 0.8
        self.setGeometry(QStyle.alignedRect(
            Qt.LeftToRight, Qt.AlignCenter, window_size, screen_geom))

        self.setWindowTitle(APP_NAME)

    def _on_device_table_selection_changed(
        self,
        selected: QItemSelection,
        _deselected: QItemSelection
    ) -> None:
        self._controls_section.setVisible(not selected.isEmpty())

    def _on_device_presence_changed(
        self,
        device: Device,
        event: EventPresenceChangeType,
        _target: int
    ) -> None:
        if event is EventPresenceChangeType.REMOVE:
            self._device_model.remove_device(device)
        else:
            self._device_model.update_or_add_device(device)

    def _on_device_policy_changed(
        self,
        device: Device,
        _resolved_target_old: int,
        _resolved_target_new: int,
        _resolved_rule_id: int
    ) -> None:
        self._device_model.update_or_add_device(device)

    def _on_allow_click(self):
        device = self._get_selected_device()
        self._usbguard_dbus.apply_device_policy(
            device.device_id, RuleTarget.ALLOW, False)

    def _on_block_click(self):
        device = self._get_selected_device()
        self._usbguard_dbus.apply_device_policy(
            device.device_id, RuleTarget.BLOCK, False)

    def _on_reject_click(self):
        device = self._get_selected_device()
        self._usbguard_dbus.apply_device_policy(
            device.device_id, RuleTarget.REJECT, False)

    def _get_selected_device(self) -> Device:
        selection = self._device_table.selectionModel().selection()
        row = selection.first().topLeft().row()
        device = self._device_model.devices[row]
        return device


def main() -> None:
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)

    usbguard_dbus = UsbguardDbusInterface()

    main_window = MainWindow(app, usbguard_dbus)
    main_window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
