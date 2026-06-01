from pytest import fail
from rottnest.procedures.procedure_manager.mpsc_channel import MPSCChannelProvider, MPSCChannelState

import unittest

DEBUG_CHANNEL1 = 'debug_channel_tag1'
DEBUG_CHANNEL2 = 'debug_channel_tag2'
DEBUG_CHANNEL3 = 'debug_channel_tag3'
DEBUG_CHANNEL4 = 'debug_channel_tag4'
DEBUG_CHANNEL5 = 'debug_channel_tag5'
DEBUG_CHANNEL6 = 'debug_channel_tag6'


class MPSCChannelReaderWriterTestSuite(unittest.TestCase):



    def test_channel_provider_create_channel_reader_and_writer(self):
        provider = MPSCChannelProvider.get_instance()
        if provider is not None:
            state, channel = provider.create_channel(DEBUG_CHANNEL1)

            if channel is not None:
                assert MPSCChannelState.CHANNEL_CREATED == state
                assert MPSCChannelState.CHANNEL_CREATED == channel.get_state()

                reader, rstate = provider.get_reader(DEBUG_CHANNEL1)
                writer, wstate = provider.get_writer(DEBUG_CHANNEL1)
                assert MPSCChannelState.READER_CREATED == rstate
                assert MPSCChannelState.WRITER_CREATED == wstate

                
            else:
                fail("Unable to retrieve channel")

        else:
            fail("Unable to retrieve provider")



    def test_channel_provider_create_channel_reader_and_writer_write_one(self):
        provider = MPSCChannelProvider.get_instance()
        if provider is not None:
            state, channel = provider.create_channel(DEBUG_CHANNEL2)

            if channel is not None:
                assert MPSCChannelState.CHANNEL_CREATED == state
                assert MPSCChannelState.CHANNEL_CREATED == channel.get_state()

                reader, rstate = provider.get_reader(DEBUG_CHANNEL2)
                writer, wstate = provider.get_writer(DEBUG_CHANNEL2)

                if reader is not None and writer is not None:
                    writer.write('Hello World')
                    data = reader.read()

                    assert data is not None
                    assert data.get_object() is not None
                    assert data.get_object() == 'Hello World'
                else:
                    fail("Reader and/or Writer are None")

            else:
                fail("Unable to retrieve channel")

        else:
            fail("Unable to retrieve provider")
        

    def test_channel_provider_create_channel_reader_and_writer_write_many(self):
        provider = MPSCChannelProvider.get_instance()
        if provider is not None:
            state, channel = provider.create_channel(DEBUG_CHANNEL3)

            if channel is not None:
                assert MPSCChannelState.CHANNEL_CREATED == state
                assert MPSCChannelState.CHANNEL_CREATED == channel.get_state()

                reader, rstate = provider.get_reader(DEBUG_CHANNEL3)
                writer, wstate = provider.get_writer(DEBUG_CHANNEL3)

                if reader is not None and writer is not None:
                    for i in range(10):
                        writer.write([i])
                        data = reader.read()

                        assert data is not None
                        assert data.get_object() is not None
                        assert data.get_object()[0] == i
                else:
                    fail("Reader and/or Writer are None")

            else:
                fail("Unable to retrieve channel")

        else:
            fail("Unable to retrieve provider")

    def test_channel_provider_create_channel_reader_and_many_writer_write_many(self):
        provider = MPSCChannelProvider.get_instance()
        if provider is not None:
            state, channel = provider.create_channel(DEBUG_CHANNEL4)

            if channel is not None:
                assert MPSCChannelState.CHANNEL_CREATED == state
                assert MPSCChannelState.CHANNEL_CREATED == channel.get_state()
                writers = []
                
                reader, rstate = provider.get_reader(DEBUG_CHANNEL4)
                for _i in range(10):
                    writer, wstate = provider.get_writer(DEBUG_CHANNEL4)
                    writers.append(writer)
                
                
                if reader is not None and writer is not None:
                    for i in range(10):
                        writers[i].write([i])
                    for i in range(10):
                        data = reader.read()

                        assert data is not None
                        assert data.get_object() is not None
                        assert data.get_object()[0] == i
                else:
                    fail("Reader and/or Writer are None")

            else:
                fail("Unable to retrieve channel")

        else:
            fail("Unable to retrieve provider")
        
    def test_channel_provider_create_channel_reader_and_many_writer_write_many_read_all(self):
        provider = MPSCChannelProvider.get_instance()
        if provider is not None:
            state, channel = provider.create_channel(DEBUG_CHANNEL5)

            if channel is not None:
                assert MPSCChannelState.CHANNEL_CREATED == state
                assert MPSCChannelState.CHANNEL_CREATED == channel.get_state()
                writers = []
                
                reader, rstate = provider.get_reader(DEBUG_CHANNEL5)
                for _i in range(10):
                    writer, wstate = provider.get_writer(DEBUG_CHANNEL5)
                    writers.append(writer)
                
                
                if reader is not None and writer is not None:
                    for i in range(10):
                        writers[i].write([i])

                        
                    data_list = reader.read_all()

                    for data in data_list:
                        assert data is not None
                        assert data.get_object() is not None
                        assert data.get_object()[0] == i
                else:
                    fail("Reader and/or Writer are None")

            else:
                fail("Unable to retrieve channel")

        else:
            fail("Unable to retrieve provider")

    def test_channel_provider_create_channel_reader_and_many_writer_write_iter_many_read_all(self):
        provider = MPSCChannelProvider.get_instance()
        if provider is not None:
            state, channel = provider.create_channel(DEBUG_CHANNEL6)

            if channel is not None:
                assert MPSCChannelState.CHANNEL_CREATED == state
                assert MPSCChannelState.CHANNEL_CREATED == channel.get_state()
                writers = []
                
                reader, rstate = provider.get_reader(DEBUG_CHANNEL6)
                for _i in range(10):
                    writer, wstate = provider.get_writer(DEBUG_CHANNEL6)
                    writers.append(writer)
                
                
                if reader is not None and writer is not None:
                    for i in range(10):
                        writers[i].write_iter([i])

                        
                    data_list = reader.read_all()

                    for data in data_list:
                        assert data is not None
                        assert data.is_iterable()
                        assert data.get_object() is not None
                        assert data.get_object()[0] == i
                else:
                    fail("Reader and/or Writer are None")

            else:
                fail("Unable to retrieve channel")

        else:
            fail("Unable to retrieve provider")
            
    def test_channel_provider_create_channel_reader_and_writer_write_exceed_capacity(self):
        provider = MPSCChannelProvider.get_instance()
        if provider is not None:
            state, channel = provider.create_channel(DEBUG_CHANNEL2)

            if channel is not None:
                assert MPSCChannelState.CHANNEL_CREATED == state
                assert MPSCChannelState.CHANNEL_CREATED == channel.get_state()

                reader, rstate = provider.get_reader(DEBUG_CHANNEL2)
                writer, wstate = provider.get_writer(DEBUG_CHANNEL2)

                if reader is not None and writer is not None:
                    for i in range(4096):
                        result = writer.write(i)
                        assert result is True

                    
                    for i in range(10):
                        result = writer.write(i)
                        assert result is False

                    for i in range(4096):
                        data = reader.read()
                        assert data is not None
                        assert data.get_object() is not None
                        assert data.get_object() == i

                    for i in range(10):

                        data = reader.read()
                        assert data is None
                else:
                    fail("Reader and/or Writer are None")

            else:
                fail("Unable to retrieve channel")

        else:
            fail("Unable to retrieve provider")
        
if __name__ == '__main__':
    unittest.main()
