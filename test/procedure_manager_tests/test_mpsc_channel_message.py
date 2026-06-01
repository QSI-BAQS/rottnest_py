from rottnest.procedures.procedure_manager.mpsc_channel import MPSCChannelMessage, MPSCChannelMessageKind

import unittest

DEBUG_CHANNEL1 = 'debug_channel_tag1'
DEBUG_CHANNEL2 = 'debug_channel_tag2'
DEBUG_CHANNEL3 = 'debug_channel_tag3'
DEBUG_CHANNEL4 = 'debug_channel_tag4'
DEBUG_CHANNEL5 = 'debug_channel_tag5'


class MPSCChannelMessageSuite(unittest.TestCase):


    def test_construct_message(self):

        msg = MPSCChannelMessage(MPSCChannelMessageKind.OBJECT, 'Hello!')

        assert msg.get_object() == 'Hello!'
        assert msg.get_message_kind == MPSCChannelMessageKind.OBJECT
        assert msg.is_iterable() is False
        
    def test_construct_message_iter(self):

        msg = MPSCChannelMessage(MPSCChannelMessageKind.ITERABLE, [1, 2, 3])

        assert msg.get_object() == [1, 2, 3]
        assert msg.get_message_kind == MPSCChannelMessageKind.ITERABLE
        assert msg.is_iterable()
        
    def test_construct_message_cls_method(self):

        msg = MPSCChannelMessage.make_object([1, 2, 3])

        assert msg.get_object() == 'Hello!'
        assert msg.get_message_kind == MPSCChannelMessageKind.OBJECT
        assert msg.is_iterable() is False
        
    def test_construct_message_iter_cls_method(self):

        msg = MPSCChannelMessage.make_iterable([1, 2, 3])

        assert msg.get_object() == [1, 2, 3]
        assert msg.get_message_kind() == MPSCChannelMessageKind.ITERABLE
        assert msg.is_iterable()
