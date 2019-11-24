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

from string import ascii_lowercase, whitespace
from typing import List, Optional, Union
from .rules import (DeviceAttribute,
                    DeviceAttributeName,
                    DeviceAttributeOperator,
                    DeviceId,
                    DeviceInterfaceType,
                    Rule,
                    RuleTarget)


class RuleParsingError(Exception):
    pass


class RuleParser:
    @staticmethod
    def parse(value: str) -> Rule:
        parser = RuleParser(value)
        parser._parse()
        return parser._rule

    def __init__(self, value: str) -> None:
        self._input_value: str = value
        self._value: str = value
        self._rule: Optional[Rule] = None

    _RESERVED_WORD_CHARS = f'{ascii_lowercase}-'

    def _parse(self) -> None:
        self._consume_optional_whitespaces()
        self._consume_target_and_init_rule()
        self._consume_attributes()

    def _consume_target_and_init_rule(self) -> None:
        word = self._consume_reserved_word()
        try:
            target = RuleTarget(word)
            self._rule = Rule(target=target)
        except ValueError as error:
            self._raise_error(str(error))

    def _consume_attributes(self) -> None:
        self._consume_optional_whitespaces()
        while self._value:
            self._consume_attribute()
            self._consume_optional_whitespaces()

    def _consume_attribute(self):
        name = self._consume_attribute_name()

        if name in self._rule.attributes:
            self._raise_error(f'attribute {name} already set')

        self._consume_mandatory_whitespaces()

        operator = self._consume_optional_operator()

        if operator:
            self._consume_mandatory_whitespaces()
            values = self._consume_multi_attributes_values(name)
        else:
            values = self._consume_single_or_multi_attribute_values(name)

        attribute = DeviceAttribute(name, operator, values)
        self._rule.attributes[name] = attribute

    def _consume_attribute_name(self) -> DeviceAttributeName:
        word = self._consume_reserved_word()

        try:
            return DeviceAttributeName(word)
        except ValueError as error:
            self._raise_error(str(error))

    def _consume_optional_operator(self) -> Optional[DeviceAttributeOperator]:
        for operator in DeviceAttributeOperator:
            word = operator.value
            if self._can_consume_exact_word(word):
                self._yank(len(word))
                return operator
        return None

    def _consume_single_or_multi_attribute_values(
        self,
        attribute_name: DeviceAttributeName
    ) -> List[Union[DeviceId, DeviceInterfaceType, str]]:
        if self._value.startswith('{'):
            return self._consume_multi_attributes_values(attribute_name)
        else:
            return [self._consume_single_attribute_value(attribute_name)]

    def _consume_multi_attributes_values(
        self,
        attribute_name: DeviceAttributeName
    ) -> List[Union[DeviceId, DeviceInterfaceType, str]]:
        self._yank_expected('{')
        self._consume_optional_whitespaces()

        values = []

        while self._value and not self._value.startswith('}'):
            value = self._consume_single_attribute_value(attribute_name)
            values.append(value)
            self._consume_optional_whitespaces()

        if not values:
            self._raise_error('multi-valued attribute has no values')

        self._yank_expected('}')
        return values

    def _consume_single_attribute_value(
        self,
        attribute_name: DeviceAttributeName
    ) -> Union[DeviceId, DeviceInterfaceType, str]:

        if attribute_name is DeviceAttributeName.ID:
            return self._consume_usb_device_id()
        elif attribute_name is DeviceAttributeName.WITH_INTERFACE:
            return self._consume_interface_type()
        else:
            return self._consume_string_attribute_value()

    def _consume_usb_device_id(self) -> DeviceId:
        vendor_id = self._consume_hex_number_or_asterisk(4)
        self._yank_expected(':')

        if vendor_id is None:
            self._yank_expected('*')
            product_id = None
        else:
            product_id = self._consume_hex_number_or_asterisk(4)

        return DeviceId(vendor_id, product_id)

    def _consume_interface_type(self) -> DeviceInterfaceType:
        iface_class = self._consume_hex_number(2)
        self._yank_expected(':')
        iface_subclass = self._consume_hex_number_or_asterisk(2)
        self._yank_expected(':')

        if iface_subclass is None:
            self._yank_expected('*')
            iface_protocol = None
        else:
            iface_protocol = self._consume_hex_number_or_asterisk(2)

        return DeviceInterfaceType(iface_class, iface_subclass, iface_protocol)

    def _consume_string_attribute_value(self) -> str:
        self._yank_expected('"')
        quotes_index = self._value.find('"')
        if quotes_index == -1:
            self._raise_error('cannot find end of string')
        content = self._yank(quotes_index)
        self._yank_expected('"')
        return content

    def _consume_hex_number_or_asterisk(self, length: int) -> Optional[int]:
        if self._value.startswith('*'):
            self._yank()
            return None

        return self._consume_hex_number(length)

    def _consume_hex_number(self, length: int) -> int:
        hex_number = self._yank(length)
        try:
            return int(hex_number, 16)
        except ValueError as error:
            return self._raise_error(str(error))

    def _consume_reserved_word(self) -> str:
        length = 0
        for char in self._value:
            if char in self._RESERVED_WORD_CHARS:
                length += 1
            else:
                break

        if length == 0:
            self._raise_error('reserved word expected')

        return self._yank(length)

    def _can_consume_exact_word(self, w: str) -> bool:
        value = self._value
        word_length = len(w)
        return value == w \
            or (len(value) > word_length
                and value.startswith(w)
                and value[word_length] in whitespace)

    def _consume_mandatory_whitespaces(self) -> None:
        if not self._value or self._value[0] not in whitespace:
            self._raise_error('whitespace expected')
        self._consume_optional_whitespaces()

    def _consume_optional_whitespaces(self) -> None:
        self._value = self._value.lstrip(whitespace)

    def _yank_expected(self, value: str):
        if not self._value.startswith(value):
            self._raise_error(f'"{value}" expected')
        self._yank(len(value))

    def _yank(self, length: int = 1) -> str:
        if length > len(self._value):
            self._raise_error('unexpected end of string')
        yanked_part = self._value[:length]
        self._value = self._value[length:]
        return yanked_part

    def _raise_error(self, message: str):
        pos = len(self._input_value) - len(self._value)
        raise RuleParsingError(f'parsing error at position {pos}: {message}')
