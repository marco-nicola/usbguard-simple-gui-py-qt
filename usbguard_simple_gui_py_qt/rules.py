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
from enum import Enum, unique
from typing import Optional, TypeVar, Generic, List


@unique
class DeviceAttributeName(Enum):
    ID = 'id'
    HASH = 'hash'
    PARENT_HASH = 'parent-hash'
    NAME = 'name'
    SERIAL = 'serial'
    VIA_PORT = 'via-port'
    WITH_INTERFACE = 'with-interface'
    WITH_CONNECT_TYPE = 'with-connect-type'


@unique
class DeviceAttributeOperator(Enum):
    ALL_OF = 'all-of'
    ONE_OF = 'one-of'
    NONE_OF = 'none-of'
    EQUALS = 'equals'
    EQUALS_ORDERED = 'equals-ordered'


@unique
class RuleTarget(Enum):
    ALLOW = 'allow'
    BLOCK = 'block'
    REJECT = 'reject'


DeviceAttributeValueType = TypeVar('DeviceAttributeValueType')
@dataclass
class DeviceAttribute(Generic[DeviceAttributeValueType]):
    name: DeviceAttributeName
    operator: Optional[DeviceAttributeOperator]
    values: List[DeviceAttributeValueType]


@dataclass
class DeviceId:
    vendor_id: Optional[int]
    product_id: Optional[int]

    def __repr__(self) -> str:
        return f'{self.vendor_repr}:{self.product_repr}'

    @property
    def vendor_repr(self) -> str:
        return self._hex_repr(self.vendor_id)

    @property
    def product_repr(self) -> str:
        return self._hex_repr(self.product_id)

    @staticmethod
    def _hex_repr(value: Optional[int]) -> str:
        return '*' if value is None else '%04x' % value


@dataclass
class DeviceInterfaceType:
    iface_class: int
    iface_subclass: Optional[int]
    iface_protocol: Optional[int]

    def __repr__(self) -> str:
        return f'{self.cc}:{self.ss}:{self.pp}'

    @property
    def cc(self) -> str:
        return '%02x' % self.iface_class

    @property
    def ss(self) -> str:
        return self._hex_repr(self.iface_subclass)

    @property
    def pp(self) -> str:
        return self._hex_repr(self.iface_protocol)

    @staticmethod
    def _hex_repr(value: Optional[int]) -> str:
        return '*' if value is None else '%02x' % value
