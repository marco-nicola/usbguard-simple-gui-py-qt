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

from dataclasses import dataclass
from typing import Any, List, Optional
from PySide2.QtCore import QAbstractTableModel, QModelIndex, Qt
from .rules import DeviceAttribute, DeviceAttributeName, Rule


@dataclass
class Device:
    device_id: int
    rule: Rule

    @property
    def human_readable_name(self) -> str:
        name = self.rule.name
        if name and len(name.values) == 1:
            return name.values[0]
        return f'#{self.device_id}'


class DeviceModel(QAbstractTableModel):
    _ATTRIBUTES = [
        DeviceAttributeName.ID,
        DeviceAttributeName.NAME,
        DeviceAttributeName.WITH_CONNECT_TYPE,
        DeviceAttributeName.VIA_PORT,
        DeviceAttributeName.HASH,
        DeviceAttributeName.PARENT_HASH,
        DeviceAttributeName.SERIAL,
        DeviceAttributeName.WITH_INTERFACE,
    ]

    _HEADER = [
        'Target',
        'ID',
        'Name',
        'With Connect Type',
        'Via Port',
        'Hash',
        'Parent Hash',
        'Serial',
        'With Interface',
    ]

    def __init__(self, devices: List[Device]) -> None:
        super().__init__()
        self.devices: List[Device] = devices

    def update_or_add_device(self, device: Device) -> None:
        row = self._find_row_by_device_id(device.device_id)
        if row is None:
            self._add_new_device(device)
        else:
            self._update_device_at_row(device, row)

    def remove_device(self, device: Device) -> None:
        row = self._find_row_by_device_id(device.device_id)

        if row is not None:
            del self.devices[row]
            self.headerDataChanged.emit(Qt.Vertical, row, row)
            self.dataChanged.emit(row, row)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.devices)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._HEADER)

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.DisplayRole
    ) -> Any:
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            return self._HEADER[section]
        elif section < len(self.devices):
            device = self.devices[section]
            return device.device_id

        return None

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if role != Qt.DisplayRole:
            return None

        row = index.row()
        column = index.column()
        device = self.devices[row]

        if column == 0:
            return device.rule.target.value
        else:
            attribute = self._ATTRIBUTES[column - 1]
            value = device.rule.attributes.get(attribute)
            return self._attribute_repr(value)

    def _add_new_device(self, device: Device) -> None:
        row = len(self.devices)
        self.devices.append(device)
        self.headerDataChanged.emit(Qt.Vertical, row, row)
        self.dataChanged.emit(row, row)

    def _update_device_at_row(self, device: Device, row: int) -> None:
        self.devices[row] = device
        self.dataChanged.emit(row, row)

    def _find_row_by_device_id(self, device_id: int) -> Optional[int]:
        for row, device in enumerate(self.devices):
            if device.device_id == device_id:
                return row
        return None

    @staticmethod
    def _attribute_repr(value: Optional[DeviceAttribute]) -> str:
        if value is None:
            return ''

        operator = value.operator
        values = value.values

        if len(values) == 1 and operator is None:
            return str(values[0])
        elif operator is None:
            return '\n'.join(map(str, values))
        else:
            values_repr = '\n'.join(f'    {str(v)}' for v in values)
            return f'{operator.value}:\n{values_repr}'
