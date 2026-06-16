from pytest import fail
from rottnest.procedures.procedure_manager.mpsc_channel import MPSCChannelProvider, MPSCChannelState, MPSC_CHANNEL_CAPACITY

import unittest

DEBUG_CHANNEL1 = 'debug_channel_tag1'
DEBUG_CHANNEL2 = 'debug_channel_tag2'
DEBUG_CHANNEL3 = 'debug_channel_tag3'
DEBUG_CHANNEL4 = 'debug_channel_tag4'
DEBUG_CHANNEL5 = 'debug_channel_tag5'

class MPSCChannelTestSuite(unittest.TestCase):
    '''
      MPSC Channel creation tests  
    '''
    def test_channel_provider_get_instance(self):

        provider = MPSCChannelProvider.get_instance()
        assert provider is not None


    def test_channel_provider_create_channel(self):
        provider = MPSCChannelProvider.get_instance()
        if provider is not None:
            state, channel = provider.create_channel(DEBUG_CHANNEL1)

            if channel is not None:
                assert MPSCChannelState.CHANNEL_CREATED == state
                assert MPSCChannelState.CHANNEL_CREATED == channel.get_state()
                assert 0 == channel.get_length()
                assert MPSC_CHANNEL_CAPACITY == channel.get_capacity()
                assert DEBUG_CHANNEL1 == channel.get_key()
            else:
                fail("Unable to retrieve channel")

        else:
            fail("Unable to retrieve provider")

    def test_channel_provider_set_state(self):
        
        provider = MPSCChannelProvider.get_instance()
        if provider is not None:
            
            state, channel = provider.create_channel(DEBUG_CHANNEL2)

            assert MPSCChannelState.CHANNEL_CREATED == state

            if channel is not None:
                channel.set_state(MPSCChannelState.CHANNEL_ACTIVE)
                assert MPSCChannelState.CHANNEL_ACTIVE == channel.get_state()
            else:
                fail("Unable to retrieve channel")
        else:
            fail("Unable to retrieve provider")
        
    def test_channel_provider_enqueue(self):
        
        provider = MPSCChannelProvider.get_instance()
        if provider is not None:
            state, channel = provider.create_channel(DEBUG_CHANNEL3)
            if channel is not None:
                provider.close_channel(channel.get_key())
                provider.recreate_channel(channel.get_key())        
            else:
                fail("Unable to retrieve channel")
        else:
            fail("Unable to retrieve provider")



    def test_channel_close_recreate(self):
        provider = MPSCChannelProvider.get_instance()
        if provider is not None:
            state, channel = provider.create_channel(DEBUG_CHANNEL4)
            if channel is not None:
                assert state == MPSCChannelState.CHANNEL_CREATED
                provider.close_channel(channel.get_key())
                state, channel = provider.recreate_channel(channel.get_key())        
                assert state == MPSCChannelState.CHANNEL_CREATED
            else:
                fail("Unable to retrieve channel")
        else:
            fail("Unable to retrieve provider")


    def test_channel_create_existing_failure(self):

        provider = MPSCChannelProvider.get_instance()
        if provider is not None:
            state, channel = provider.create_channel(DEBUG_CHANNEL5)
            if channel is not None:
                provider.close_channel(channel.get_key())
                provider.create_channel(channel.get_key())        
                state, channel = provider.create_channel(channel.get_key())        
                assert state == MPSCChannelState.CHANNEL_EXISTS
            else:
                fail("Unable to retrieve channel")
        else:
            fail("Unable to retrieve provider")
        

if __name__ == '__main__':
    unittest.main()
