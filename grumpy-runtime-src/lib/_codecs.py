def ascii_decode(*args, **kwargs):
    raise NotImplementedError()


def ascii_encode(*args, **kwargs):
    raise NotImplementedError()


def charbuffer_encode(*args, **kwargs):
    raise NotImplementedError()


def charmap_build(*args, **kwargs):
    raise NotImplementedError()


def charmap_decode(*args, **kwargs):
    raise NotImplementedError()


def charmap_encode(*args, **kwargs):
    raise NotImplementedError()


def decode(obj, encoding=None, errors=None) -> object:
    """
    decode(obj, [encoding[,errors]]) -> object

    Decodes obj using the codec registered for encoding. encoding defaults
    to the default encoding. errors may be given to set a different error
    handling scheme. Default is 'strict' meaning that encoding errors raise
    a ValueError. Other possible values are 'ignore' and 'replace'
    as well as any other name registered with codecs.register_error that is
    able to handle ValueErrors.
    """
    raise NotImplementedError()


def encode(obj, encoding=None, errors=None) -> object:
    """
    encode(obj, [encoding[,errors]]) -> object

    Encodes obj using the codec registered for encoding. encoding defaults
    to the default encoding. errors may be given to set a different error
    handling scheme. Default is 'strict' meaning that encoding errors raise
    a ValueError. Other possible values are 'ignore', 'replace' and
    'xmlcharrefreplace' as well as any other name registered with
    codecs.register_error that can handle ValueErrors.
    """
    raise NotImplementedError()


def escape_decode(*args, **kwargs):
    raise NotImplementedError()


def escape_encode(*args, **kwargs):
    raise NotImplementedError()


def latin_1_decode(*args, **kwargs):
    raise NotImplementedError()


def latin_1_encode(*args, **kwargs):
    raise NotImplementedError()


def lookup(encoding) -> 'CodecInfo':
    """
    lookup(encoding) -> CodecInfo

    Looks up a codec tuple in the Python codec registry and returns
    a CodecInfo object.
    """
    raise NotImplementedError()


def lookup_error(errors) -> 'handler':
    """
    lookup_error(errors) -> handler

    Return the error handler for the specified error handling name
    or raise a LookupError, if no handler exists under this name.
    """
    raise NotImplementedError()


def raw_unicode_escape_decode(*args, **kwargs):
    raise NotImplementedError()


def raw_unicode_escape_encode(*args, **kwargs):
    raise NotImplementedError()


def readbuffer_encode(*args, **kwargs):
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


def unicode_escape_decode(*args, **kwargs):
    raise NotImplementedError()


def unicode_escape_encode(*args, **kwargs):
    raise NotImplementedError()


def unicode_internal_decode(*args, **kwargs):
    raise NotImplementedError()


def unicode_internal_encode(*args, **kwargs):
    raise NotImplementedError()


def utf_16_be_decode(*args, **kwargs):
    raise NotImplementedError()


def utf_16_be_encode(*args, **kwargs):
    raise NotImplementedError()


def utf_16_decode(*args, **kwargs):
    raise NotImplementedError()


def utf_16_encode(*args, **kwargs):
    raise NotImplementedError()


def utf_16_ex_decode(*args, **kwargs):
    raise NotImplementedError()


def utf_16_le_decode(*args, **kwargs):
    raise NotImplementedError()


def utf_16_le_encode(*args, **kwargs):
    raise NotImplementedError()


def utf_32_be_decode(*args, **kwargs):
    raise NotImplementedError()


def utf_32_be_encode(*args, **kwargs):
    raise NotImplementedError()


def utf_32_decode(*args, **kwargs):
    raise NotImplementedError()


def utf_32_encode(*args, **kwargs):
    raise NotImplementedError()


def utf_32_ex_decode(*args, **kwargs):
    raise NotImplementedError()


def utf_32_le_decode(*args, **kwargs):
    raise NotImplementedError()


def utf_32_le_encode(*args, **kwargs):
    raise NotImplementedError()


def utf_7_decode(*args, **kwargs):
    raise NotImplementedError()


def utf_7_encode(*args, **kwargs):
    raise NotImplementedError()


def utf_8_decode(*args, **kwargs):
    raise NotImplementedError()


def utf_8_encode(*args, **kwargs):
    raise NotImplementedError()
