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

from enum import Enum, unique


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
