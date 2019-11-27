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

from enum import auto, Enum, IntEnum, unique
from typing import Callable, Dict, List, Set, Optional
from dbus import (Array,
                  Dictionary,
                  Interface,
                  String,
                  Struct,
                  SystemBus,
                  UInt32)
from dbus.mainloop.glib import DBusGMainLoop

from usbguard_simple_gui_py_qt.rules import RuleTarget
from .device import Device
from .rule_parsing import RuleParser

_BUS_NAME = 'org.usbguard1'
_POLICY_PATH = '/org/usbguard1/Policy'
_POLICY_IFACE_NAME = 'org.usbguard.Policy1'
_DEVICES_PATH = '/org/usbguard1/Devices'
_DEVICES_IFACE_NAME = 'org.usbguard.Devices1'


@unique
class CallbackEventType(Enum):
    DEVICE_PRESENCE_CHANGED = auto()
    DEVICE_PRESENCE_CHANGED_ERROR = auto()


@unique
class EventPresenceChangeType(IntEnum):
    PRESENT = 0
    INSERT = 1
    UPDATE = 2
    REMOVE = 3


class UsbguardDbusInterface:
    _TARGET_TO_INT = {
        RuleTarget.ALLOW: 0,
        RuleTarget.BLOCK: 1,
        RuleTarget.REJECT: 2,
    }

    def __init__(self) -> None:
        DBusGMainLoop(set_as_default=True)

        self._bus = SystemBus()

        self._policy_proxy = self._bus.get_object(_BUS_NAME, _POLICY_PATH)
        self._policy = Interface(self._policy_proxy, _POLICY_IFACE_NAME)

        self._devices_proxy = self._bus.get_object(_BUS_NAME, _DEVICES_PATH)
        self._devices = Interface(self._devices_proxy, _DEVICES_IFACE_NAME)

        self._devices.connect_to_signal(
            'DevicePresenceChanged', self._on_device_presence_changed)

        self._callbacks: Dict[CallbackEventType, Set[Callable]] = \
            { e: set() for e in CallbackEventType }

    def register_callback(
        self,
        event_type: CallbackEventType,
        callback: Callable
    ) -> None:
        callbacks = self._callbacks[event_type]
        if callback in callbacks:
            raise Exception(f'callback {callback} already registered')
        self._callbacks[event_type].add(callback)

    def unregister_callback(
        self,
        event_type: CallbackEventType,
        callback: Callable
    ) -> None:
        self._callbacks[event_type].remove(callback)

    def list_devices(self, query: str = 'match') -> List[Device]:
        response: Array[Struct[UInt32, String]] = \
            self._devices.listDevices(query)
        return [
            Device(
                device_id=int(device_struct[0]),
                rule=RuleParser.parse(str(device_struct[1])))
            for device_struct in response
        ]

    def apply_device_policy(
        self,
        device_id: int,
        target: RuleTarget,
        permanent: bool
    ) -> Optional[int]:
        response: UInt32 = self._devices.applyDevicePolicy(
            device_id,
            self._TARGET_TO_INT[target],
            permanent)
        return int(response) if permanent else None

    def _on_device_presence_changed(
        self,
        device_id: UInt32,
        event: UInt32,
        target: UInt32,
        device_rule: String,
        _attributes: Dictionary
    ) -> None:
        """
        :param device_id: Device id of the device.
        :param event: Type of the presence change event in numerical form.
            0 = Present, 1 = Insert, 2 = Update, 3 = Remove.
        :param target: The current authorization target of the device in
            numerical form.
        :param device_rule: Device specific rule.
        :param _attributes: A dictionary of device attributes and their values.
        """
        try:
            resolved_event = EventPresenceChangeType(int(event))
            resolved_target = int(target)
            device = Device(
                device_id=int(device_id),
                rule=RuleParser.parse(device_rule))
        except Exception as error:
            event_type = CallbackEventType.DEVICE_PRESENCE_CHANGED_ERROR
            for callback in self._callbacks[event_type]:
                callback(error)
            return

        event_type = CallbackEventType.DEVICE_PRESENCE_CHANGED
        for callback in self._callbacks[event_type]:
            callback(device, resolved_event, resolved_target)
