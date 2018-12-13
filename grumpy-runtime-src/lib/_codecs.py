# coding: utf-8

def ascii_decode(data, errors=None):
    raise NotImplementedError()


def ascii_encode(str_, errors=None,):
    raise NotImplementedError()


def charmap_build(map_):  # Not 2.7
    raise NotImplementedError()


def charmap_decode(data, errors=None, mapping=None):  # Not 2.7
    raise NotImplementedError()


def charmap_encode(str_, errors=None, mapping=None):  # Not 2.7
    raise NotImplementedError()


def charbuffer_encode(*args, **kwargs):
    raise NotImplementedError()


def charmap_build(*args, **kwargs):
    raise NotImplementedError()


def charmap_decode(*args, **kwargs):
    raise NotImplementedError()


def charmap_encode(*args, **kwargs):
    raise NotImplementedError()


def decode(obj, encoding='utf-8', errors='strict'):
    """
    Decodes obj using the codec registered for encoding.

    Default encoding is 'utf-8'.  errors may be given to set a
    different error handling scheme.  Default is 'strict' meaning that encoding
    errors raise a ValueError.  Other possible values are 'ignore', 'replace'
    and 'backslashreplace' as well as any other name registered with
    codecs.register_error that can handle ValueErrors.
    """
    raise NotImplementedError()


def encode(obj, encoding='utf-8', errors='strict'):
    """
    Encodes obj using the codec registered for encoding.

    The default encoding is 'utf-8'. Errors may be given to set a
    different error handling scheme.  Default is 'strict' meaning that encoding
    errors raise a ValueError.  Other possible values are 'ignore', 'replace'
    and 'backslashreplace' as well as any other name registered with
    codecs.register_error that can handle ValueErrors.
    """
    raise NotImplementedError()


def escape_decode(data, errors=None):
    raise NotImplementedError()


def escape_encode(data, errors=None):
    raise NotImplementedError()


def latin_1_decode(data, errors=None):
    raise NotImplementedError()


def latin_1_encode(str_, errors=None):
    raise NotImplementedError()


def lookup(encoding):
    """
    lookup(encoding) -> CodecInfo

    Looks up a codec tuple in the Python codec registry and returns
    a CodecInfo object.
    """
    raise NotImplementedError()


def lookup_error(errors):
    """
    lookup_error(errors) -> handler

    Return the error handler for the specified error handling name
    or raise a LookupError, if no handler exists under this name.
    """
    raise NotImplementedError()


def raw_unicode_escape_decode(data, errors=None):
    raise NotImplementedError()


def raw_unicode_escape_encode(str_, errors=None):
    raise NotImplementedError()


def readbuffer_encode(data, errors=None):
    raise NotImplementedError()


def register(search_function):
    """
    Register a codec search function. Search functions are expected to take
    one argument, the encoding name in all lower case letters, and return
    a tuple of functions (encoder, decoder, stream_reader, stream_writer)
    (or a CodecInfo object).
    """
    raise NotImplementedError()


def register_error(errors, handler):
    """
    Register the specified error handler under the name
    errors. handler must be a callable object, that
    will be called with an exception instance containing
    information about the location of the encoding/decoding
    error and must return a (replacement, new position) tuple.
    """
    raise NotImplementedError()


def unicode_escape_decode(data, errors=None):
    raise NotImplementedError()


def unicode_escape_encode(str_, errors=None):
    raise NotImplementedError()


def unicode_internal_decode(obj, errors=None):
    raise NotImplementedError()


def unicode_internal_encode(obj, errors=None):
    raise NotImplementedError()


def utf_16_be_decode(data, errors=None, final=False):
    raise NotImplementedError()


def utf_16_be_encode(str_, errors=None):
    raise NotImplementedError()


def utf_16_decode(data, errors=None, final=False):
    raise NotImplementedError()


def utf_16_encode(str_, errors=None, byteorder=0):
    raise NotImplementedError()


def utf_16_ex_decode(data, errors=None, byteorder=0, final=False):
    raise NotImplementedError()


def utf_16_le_decode(data, errors=None, final=False):
    raise NotImplementedError()


def utf_16_le_encode(str_, errors=None,):
    raise NotImplementedError()


def utf_32_be_decode(data, errors=None, final=False):
    raise NotImplementedError()


def utf_32_be_encode(str_, errors=None):
    raise NotImplementedError()


def utf_32_decode(data, errors=None, final=False):
    raise NotImplementedError()


def utf_32_encode(str_, errors=None, byteorder=0):
    raise NotImplementedError()


def utf_32_ex_decode(data, errors=None, byteorder=0, final=False):
    raise NotImplementedError()


def utf_32_le_decode(data, errors=None, final=False):
    raise NotImplementedError()


def utf_32_le_encode(str_, errors=None,):
    raise NotImplementedError()


def utf_7_decode(data, errors=None, final=False):
    raise NotImplementedError()


def utf_7_encode(str_, errors=None):
    raise NotImplementedError()


def utf_8_decode(data, errors=None, final=False):
    raise NotImplementedError()


def utf_8_encode(str_, errors=None):
    raise NotImplementedError()
