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

from unittest import TestCase
from usbguard_simple_gui_py_qt.rules import (DeviceAttribute,
                                             DeviceAttributeName,
                                             DeviceAttributeOperator,
                                             DeviceId,
                                             DeviceInterfaceType,
                                             RuleTarget)
from usbguard_simple_gui_py_qt.rule_parsing import RuleParser, RuleParsingError


class TestParseRule(TestCase):
    def test_invalid_empty_string(self):
        with self.assertRaises(RuleParsingError):
            RuleParser.parse('')

    def test_invalid_string_with_spaces(self):
        with self.assertRaises(RuleParsingError):
            RuleParser.parse('   ')

    def test_invalid_target(self):
        with self.assertRaises(RuleParsingError):
            RuleParser.parse('foo')

    def test_invalid_partially_matching_target(self):
        with self.assertRaises(RuleParsingError):
            RuleParser.parse('allowed')

    def test_valid_allow_target_alone(self):
        rule = RuleParser.parse('allow')
        self.assertEqual(rule.target, RuleTarget.ALLOW)

    def test_valid_block_target_alone(self):
        rule = RuleParser.parse('block')
        self.assertEqual(rule.target, RuleTarget.BLOCK)

    def test_valid_reject_target_alone(self):
        rule = RuleParser.parse('reject')
        self.assertEqual(rule.target, RuleTarget.REJECT)

    def test_invalid_attribute_name(self):
        with self.assertRaises(RuleParsingError):
            RuleParser.parse('allow foo "bar"')

    def test_invalid_id_without_value(self):
        with self.assertRaises(RuleParsingError):
            RuleParser.parse('allow id')

    def test_valid_single_valued_id_with_specific_vendor_and_product(self):
        rule = RuleParser.parse('allow id dead:beef')
        self.assertEqual(
            rule.id,
            DeviceAttribute(
                name=DeviceAttributeName.ID,
                operator=None,
                values=[DeviceId(57005, 48879)]))

    def test_valid_id_value_with_generic_vendor_and_product(self):
        rule = RuleParser.parse('allow id *:*')
        self.assertEqual(
            rule.id,
            DeviceAttribute(
                name=DeviceAttributeName.ID,
                operator=None,
                values=[DeviceId(None, None)]))

    def test_valid_id_value_with_generic_product_only(self):
        rule = RuleParser.parse('allow id cafe:*')
        self.assertEqual(
            rule.id,
            DeviceAttribute(
                name=DeviceAttributeName.ID,
                operator=None,
                values=[DeviceId(0xcafe, None)]))

    def test_invalid_id_value_with_specific_product_only(self):
        with self.assertRaises(RuleParsingError):
            RuleParser.parse('allow id *:0001')

    def test_invalid_id_vendor_too_short(self):
        with self.assertRaises(RuleParsingError):
            RuleParser.parse('allow id 123:1234')

    def test_invalid_id_vendor_too_long(self):
        with self.assertRaises(RuleParsingError):
            RuleParser.parse('allow id 12345:1234')

    def test_invalid_id_product_too_short(self):
        with self.assertRaises(RuleParsingError):
            RuleParser.parse('allow id 1234:123')

    def test_invalid_id_product_too_long(self):
        with self.assertRaises(RuleParsingError):
            RuleParser.parse('allow id 1234:12345')

    def test_invalid_id_vendor_hex(self):
        with self.assertRaises(RuleParsingError):
            RuleParser.parse('allow id jazz:1234')

    def test_invalid_id_product_hex(self):
        with self.assertRaises(RuleParsingError):
            RuleParser.parse('allow id 1234:jazz')

    def test_invalid_id_missing_separator(self):
        with self.assertRaises(RuleParsingError):
            RuleParser.parse('allow id 1234 1234')

    def test_invalid_id_wrong_separator(self):
        with self.assertRaises(RuleParsingError):
            RuleParser.parse('allow id 1234/1234')

    def test_valid_multi_valued_id_without_operator(self):
        rule = RuleParser.parse('allow id { dead:beef cafe:babe }')
        self.assertEqual(
            rule.id,
            DeviceAttribute(
                name=DeviceAttributeName.ID,
                operator=None,
                values=[DeviceId(0xdead, 0xbeef), DeviceId(0xcafe, 0xbabe)]))

    def test_valid_multi_valued_id_with_operator(self):
        rule = RuleParser.parse('allow id one-of { dead:beef cafe:babe }')
        self.assertEqual(
            rule.id,
            DeviceAttribute(
                name=DeviceAttributeName.ID,
                operator=DeviceAttributeOperator.ONE_OF,
                values=[DeviceId(0xdead, 0xbeef), DeviceId(0xcafe, 0xbabe)]))

    def test_valid_single_valued_with_interface_with_specific_cc_ss_pp(self):
        rule = RuleParser.parse('allow with-interface ab:cd:ef')
        self.assertEqual(
            rule.with_interface,
            DeviceAttribute(
                name=DeviceAttributeName.WITH_INTERFACE,
                operator=None,
                values=[DeviceInterfaceType(0xab, 0xcd, 0xef)]))

    def test_valid_with_interface_value_with_generic_pp(self):
        rule = RuleParser.parse('allow with-interface ab:cd:*')
        self.assertEqual(
            rule.with_interface,
            DeviceAttribute(
                name=DeviceAttributeName.WITH_INTERFACE,
                operator=None,
                values=[DeviceInterfaceType(0xab, 0xcd, None)]))

    def test_valid_with_interface_value_with_generic_ss_pp(self):
        rule = RuleParser.parse('allow with-interface ab:*:*')
        self.assertEqual(
            rule.with_interface,
            DeviceAttribute(
                name=DeviceAttributeName.WITH_INTERFACE,
                operator=None,
                values=[DeviceInterfaceType(0xab, None, None)]))

    def test_invalid_with_interface_value_with_generic_cc(self):
        with self.assertRaises(RuleParsingError):
            RuleParser.parse('allow with-interface *:cd:ef')

    def test_invalid_with_interface_value_with_generic_pp_only(self):
        with self.assertRaises(RuleParsingError):
            RuleParser.parse('allow with-interface ab:*:ef')

    def test_invalid_with_interface_value_cc_too_short(self):
        with self.assertRaises(RuleParsingError):
            RuleParser.parse('allow with-interface 1:12:12')

    def test_invalid_with_interface_value_cc_too_long(self):
        with self.assertRaises(RuleParsingError):
            RuleParser.parse('allow with-interface 123:12:12')

    def test_invalid_with_interface_cc_hex(self):
        with self.assertRaises(RuleParsingError):
            RuleParser.parse('allow with-interface no:12:12')

    def test_invalid_with_interface_value_ss_too_short(self):
        with self.assertRaises(RuleParsingError):
            RuleParser.parse('allow with-interface 12:1:12')

    def test_invalid_with_interface_value_ss_too_long(self):
        with self.assertRaises(RuleParsingError):
            RuleParser.parse('allow with-interface 12:123:12')

    def test_invalid_with_interface_ss_hex(self):
        with self.assertRaises(RuleParsingError):
            RuleParser.parse('allow with-interface 12:no:12')

    def test_invalid_with_interface_value_pp_too_short(self):
        with self.assertRaises(RuleParsingError):
            RuleParser.parse('allow with-interface 12:12:1')

    def test_invalid_with_interface_value_pp_too_long(self):
        with self.assertRaises(RuleParsingError):
            RuleParser.parse('allow with-interface 12:12:123')

    def test_invalid_with_interface_pp_hex(self):
        with self.assertRaises(RuleParsingError):
            RuleParser.parse('allow with-interface 12:12:no')

    def test_invalid_with_interface_missing_first_separator(self):
        with self.assertRaises(RuleParsingError):
            RuleParser.parse('allow with-interface 12 12:12')

    def test_invalid_with_interface_missing_second_separator(self):
        with self.assertRaises(RuleParsingError):
            RuleParser.parse('allow with-interface 12:12 12')

    def test_invalid_with_interface_invalid_first_separator(self):
        with self.assertRaises(RuleParsingError):
            RuleParser.parse('allow with-interface 12/12:12')

    def test_invalid_with_interface_invalid_second_separator(self):
        with self.assertRaises(RuleParsingError):
            RuleParser.parse('allow with-interface 12:12/12')

    def test_can_parse_multi_valued_with_interface_without_operator(self):
        rule = RuleParser.parse('allow with-interface { 12:34:56 ab:cd:ef }')
        self.assertEqual(
            rule.with_interface,
            DeviceAttribute(
                name=DeviceAttributeName.WITH_INTERFACE,
                operator=None,
                values=[
                    DeviceInterfaceType(0x12, 0x34, 0x56),
                    DeviceInterfaceType(0xab, 0xcd, 0xef),
                ]))

    def test_can_parse_multi_valued_with_interface_with_operator(self):
        rule = RuleParser.parse(
            'allow with-interface one-of { 12:34:56 ab:cd:ef }')
        self.assertEqual(
            rule.with_interface,
            DeviceAttribute(
                name=DeviceAttributeName.WITH_INTERFACE,
                operator=DeviceAttributeOperator.ONE_OF,
                values=[
                    DeviceInterfaceType(0x12, 0x34, 0x56),
                    DeviceInterfaceType(0xab, 0xcd, 0xef),
                ]))

    def test_valid_hash_single_value(self):
        rule = RuleParser.parse('allow hash "foo bar"')
        self.assertEqual(
            rule.hash,
            DeviceAttribute(
                name=DeviceAttributeName.HASH,
                operator=None,
                values=['foo bar']))

    def test_valid_hash_multi_values(self):
        rule = RuleParser.parse('allow hash { "foo bar" "baz" }')
        self.assertEqual(
            rule.hash,
            DeviceAttribute(
                name=DeviceAttributeName.HASH,
                operator=None,
                values=['foo bar', 'baz']))

    def test_valid_hash_multi_values_with_operator(self):
        rule = RuleParser.parse('allow hash one-of { "foo bar" "baz" }')
        self.assertEqual(
            rule.hash,
            DeviceAttribute(
                name=DeviceAttributeName.HASH,
                operator=DeviceAttributeOperator.ONE_OF,
                values=['foo bar', 'baz']))

    def test_valid_parent_hash_single_value(self):
        rule = RuleParser.parse('allow parent-hash "foo bar"')
        self.assertEqual(
            rule.parent_hash,
            DeviceAttribute(
                name=DeviceAttributeName.PARENT_HASH,
                operator=None,
                values=['foo bar']))

    def test_valid_parent_hash_multi_values(self):
        rule = RuleParser.parse('allow parent-hash { "foo bar" "baz" }')
        self.assertEqual(
            rule.parent_hash,
            DeviceAttribute(
                name=DeviceAttributeName.PARENT_HASH,
                operator=None,
                values=['foo bar', 'baz']))

    def test_valid_parent_hash_multi_values_with_operator(self):
        rule = RuleParser.parse('allow parent-hash one-of { "foo bar" "baz" }')
        self.assertEqual(
            rule.parent_hash,
            DeviceAttribute(
                name=DeviceAttributeName.PARENT_HASH,
                operator=DeviceAttributeOperator.ONE_OF,
                values=['foo bar', 'baz']))

    def test_valid_name_single_value(self):
        rule = RuleParser.parse('allow name "foo bar"')
        self.assertEqual(
            rule.name,
            DeviceAttribute(
                name=DeviceAttributeName.NAME,
                operator=None,
                values=['foo bar']))

    def test_valid_name_multi_values(self):
        rule = RuleParser.parse('allow name { "foo bar" "baz" }')
        self.assertEqual(
            rule.name,
            DeviceAttribute(
                name=DeviceAttributeName.NAME,
                operator=None,
                values=['foo bar', 'baz']))

    def test_valid_name_multi_values_with_operator(self):
        rule = RuleParser.parse('allow name one-of { "foo bar" "baz" }')
        self.assertEqual(
            rule.name,
            DeviceAttribute(
                name=DeviceAttributeName.NAME,
                operator=DeviceAttributeOperator.ONE_OF,
                values=['foo bar', 'baz']))

    def test_valid_serial_single_value(self):
        rule = RuleParser.parse('allow serial "foo bar"')
        self.assertEqual(
            rule.serial,
            DeviceAttribute(
                name=DeviceAttributeName.SERIAL,
                operator=None,
                values=['foo bar']))

    def test_valid_serial_multi_values(self):
        rule = RuleParser.parse('allow serial { "foo bar" "baz" }')
        self.assertEqual(
            rule.serial,
            DeviceAttribute(
                name=DeviceAttributeName.SERIAL,
                operator=None,
                values=['foo bar', 'baz']))

    def test_valid_serial_multi_values_with_operator(self):
        rule = RuleParser.parse('allow serial one-of { "foo bar" "baz" }')
        self.assertEqual(
            rule.serial,
            DeviceAttribute(
                name=DeviceAttributeName.SERIAL,
                operator=DeviceAttributeOperator.ONE_OF,
                values=['foo bar', 'baz']))

    def test_valid_via_port_single_value(self):
        rule = RuleParser.parse('allow via-port "foo bar"')
        self.assertEqual(
            rule.via_port,
            DeviceAttribute(
                name=DeviceAttributeName.VIA_PORT,
                operator=None,
                values=['foo bar']))

    def test_valid_via_port_multi_values(self):
        rule = RuleParser.parse('allow via-port { "foo bar" "baz" }')
        self.assertEqual(
            rule.via_port,
            DeviceAttribute(
                name=DeviceAttributeName.VIA_PORT,
                operator=None,
                values=['foo bar', 'baz']))

    def test_valid_via_port_multi_values_with_operator(self):
        rule = RuleParser.parse('allow via-port one-of { "foo bar" "baz" }')
        self.assertEqual(
            rule.via_port,
            DeviceAttribute(
                name=DeviceAttributeName.VIA_PORT,
                operator=DeviceAttributeOperator.ONE_OF,
                values=['foo bar', 'baz']))

    def test_valid_with_connect_type_single_value(self):
        rule = RuleParser.parse('allow with-connect-type "foo bar"')
        self.assertEqual(
            rule.with_connect_type,
            DeviceAttribute(
                name=DeviceAttributeName.WITH_CONNECT_TYPE,
                operator=None,
                values=['foo bar']))

    def test_valid_with_connect_type_multi_values(self):
        rule = RuleParser.parse('allow with-connect-type { "foo bar" "baz" }')
        self.assertEqual(
            rule.with_connect_type,
            DeviceAttribute(
                name=DeviceAttributeName.WITH_CONNECT_TYPE,
                operator=None,
                values=['foo bar', 'baz']))

    def test_valid_with_connect_type_multi_values_with_operator(self):
        rule = RuleParser.parse(
            'allow with-connect-type one-of { "foo bar" "baz" }')
        self.assertEqual(
            rule.with_connect_type,
            DeviceAttribute(
                name=DeviceAttributeName.WITH_CONNECT_TYPE,
                operator=DeviceAttributeOperator.ONE_OF,
                values=['foo bar', 'baz']))

    def test_attributes_cannot_be_repeated(self):
        with self.assertRaises(RuleParsingError):
            RuleParser.parse('allow id 1234:9876 id 5678:4321')

    def test_all_single_valued_attributes(self):
        rule = RuleParser.parse('''
            allow
            id cafe:babe
            hash "AbCd123"
            parent-hash "EfGh456"
            name "Foo Bar"
            serial "AB12CD34EF56"
            via-port "1-2"
            with-interface ab:cd:ef
            with-connect-type "hotplug"
        ''')
        self.assertEqual(
            rule.id,
            DeviceAttribute(
                name=DeviceAttributeName.ID,
                operator=None,
                values=[DeviceId(0xcafe, 0xbabe)]))
        self.assertEqual(
            rule.hash,
            DeviceAttribute(
                name=DeviceAttributeName.HASH,
                operator=None,
                values=['AbCd123']))
        self.assertEqual(
            rule.parent_hash,
            DeviceAttribute(
                name=DeviceAttributeName.PARENT_HASH,
                operator=None,
                values=['EfGh456']))
        self.assertEqual(
            rule.name,
            DeviceAttribute(
                name=DeviceAttributeName.NAME,
                operator=None,
                values=['Foo Bar']))
        self.assertEqual(
            rule.serial,
            DeviceAttribute(
                name=DeviceAttributeName.SERIAL,
                operator=None,
                values=['AB12CD34EF56']))
        self.assertEqual(
            rule.via_port,
            DeviceAttribute(
                name=DeviceAttributeName.VIA_PORT,
                operator=None,
                values=['1-2']))
        self.assertEqual(
            rule.with_interface,
            DeviceAttribute(
                name=DeviceAttributeName.WITH_INTERFACE,
                operator=None,
                values=[DeviceInterfaceType(0xab, 0xcd, 0xef)]))
        self.assertEqual(
            rule.with_connect_type,
            DeviceAttribute(
                name=DeviceAttributeName.WITH_CONNECT_TYPE,
                operator=None,
                values=['hotplug']))
