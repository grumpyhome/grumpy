# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from '__go__/net' import (
    IPv4 as _IPv4, IP as _IP, LookupAddr as _LookupAddr, LookupIP as
    _LookupIP, ParseIP as _ParseIP)
from '__go__/syscall' import (
    AF_INET,
    AF_INET6,
    AF_UNIX,
    SHUT_RD,
    SHUT_RDWR,
    SHUT_WR,
    SO_REUSEADDR,
    SOL_SOCKET,
    SOCK_DGRAM,
    SOCK_RAW,
    SOCK_SEQPACKET,
    SOCK_STREAM,
    Accept as _Accept,
    Bind as _Bind,
    Close as _Close,
    Connect as _Connect,
    Getpeername as _Getpeername,
    Getsockname as _Getsockname,
    Listen as _Listen,
    Recvfrom as _Recvfrom,
    Sendto as _Sendto,
    SetNonblock as _SetNonblock,
    SetsockoptInt as _SetsockoptInt,
    SetsockoptTimeval as _SetsockoptTimeval,
    Shutdown as _Shutdown,
    SockaddrInet4 as _SockaddrInet4,
    SockaddrInet6 as _SockaddrInet6,
    SockaddrUnix as _SockaddrUnix,
    Socket as _Socket,
    Timespec as _Timespec)
import math


#TIPC_*
#has_ipv6  # boolean value indicating if IPv6 is supported
# UNIX
#SO_*
#SOMAXCONN
#MSG_*
#SOL_*
#IPPROTO_*
#IPPORT_*
#INADDR_*
#IP_*
#IPV6_*
#EAI_*
#AI_*
#NI_*
#TCP_*
# Windows
#SIO_*
#RCVALL_*

#SHUT_RD
#SHUT_WR
#SHUT_RDWR


class error(IOError):
  pass


class gaierror(error):
  pass


class herror(error):
  pass


class timeout(error):
  pass


class socket(object):

  def __init__(self, family=AF_INET, type=SOCK_STREAM, proto=0, fd=None):
    if fd is None:
      fd, err = _Socket(family, type, proto)
      if err:
        raise error(err.Error())
    self._fd = fd
    self.family = family
    self.type = type
    self.proto = proto

  def accept(self):
    fd, sockaddr, err = _Accept(self._fd)
    if err:
      raise error(err.Error())
    return (socket(self.family, self.type, self.proto, fd),
            self._get_address(sockaddr))

  def bind(self, address):
    sockaddr = self._parse_address(address)
    err = _Bind(self._fd, sockaddr)
    if err:
      raise error(err.Error())

  def close(self):
    _Close(self._fd)

  def connect(self, address):
    self.connect_ex(address)

  def connect_ex(self, address):
    addr = self._parse_address(address)
    err = _Connect(self._fd, addr)
    if err:
      raise error(err)

  def fileno(self):
    return self._fd

  def listen(self, backlog):
    err = _Listen(self._fd, backlog)
    if err:
      raise error(err.Error())

  def getpeername(self):
    sockaddr, err = _Getpeername(self._fd)
    if err:
      raise error(err.Error())
    return self._get_address(sockaddr)

  def getsockname(self):
    sockaddr, err = _Getsockname(self._fd)
    if err:
      raise error(err.Error())
    return self._get_address(sockaddr)

  def getsockopt(self, level, optname, buflen=None):
    val, err = _GetsockoptInt(self._fd, level, optname)
    if err:
      raise error(err)
    return val

  def recv(self, bufsize, flags=0):
    data, _ = self.recvfrom(bufsize, flags)
    return data

  def recv_into(self, buffer, nbytes=0, flags=0):
    n, _ = self.recvfrom_into(buffer, nbytes, flags)
    return n

  def recvfrom(self, bufsize, flags=0):
    buffer = bytearray(bufsize)
    n, addr = self.recvfrom_into(buffer, bufsize, flags)
    return str(buffer[:n]), addr

  def recvfrom_into(self, buffer, nbytes=0, flags=0):
    n, _, err = _Recvfrom(self._fd, buffer, flags)
    if err:
      raise error(err.Error())
    return n, None

  def setsockopt(self, level, optname, value):
    err = _SetsockoptInt(self._fd, level, optname, value)
    if err:
      raise error(err.Error())

  def send(self, string, flags=0):
    sockaddr, err = _Getsockname(self._fd)
    if err:
      raise error(err)
    err = _Sendto(self._fd, string, flags, sockaddr)
    if err:
      raise error(err)
    return len(string)

  def sendto(self, string, flags_or_address, address=None):
    raise NotImplementedError

  def sendall(self, string, flags=0):
    return self.send(string, flags)

  def setblocking(self, flag):
    err = _SetNonblock(fd, int(not flag))
    if err:
      raise error(err.Error())

  def settimeout(self, value):
    if value is None:
      timevalue = None
    else:
      timeval = _Timeval.new()
      frac, integer = math.modf(value)
      timeval.Sec = int(integer)
      timeval.Usec = int(frac * 1000000.0)
    err = _SetsockoptTimeval(self._fd, level, SO_RCVTIMEO, timeval)
    if err:
      raise error(err)

  def gettimeout(self):
    raise NotImplementedError

  def shutdown(self, how):
    err = _Shutdown(self._fd, how)
    if err:
      raise error(err)

  def _parse_address(self, address):
    if self.family == AF_UNIX:
      sockaddr = _SockaddrUnix.new()
      sockaddr.Name, = address
      return sockaddr
    host, port = address
    if not host:
      host = '127.0.0.1'
    ip = _ParseIP(host)
    if ip:
      ips = [ip]
    else:
      ips, err = _LookupIP(host)
      if err:
        raise error(err.Error())
    if self.family == AF_INET:
      convert = _IP.To4
    else:
      convert = _IP.To6
    for ip in ips:
      ip = convert(ip)
      if ip:
        break
    else:
      raise error('cannot resolve address')
    if self.family == AF_INET:
      sockaddr = _SockaddrInet4.new()
    else:
      sockaddr = _SockaddrInet6.new()
    sockaddr.Port = port
    sockaddr.Addr[:] = ip
    return sockaddr

  def _get_address(self, sockaddr):
    if isinstance(sockaddr, type(_SockaddrUnix.new())):
      return (sockaddr.Name,)
    return _IPv4(*sockaddr.Addr).String(), sockaddr.Port


def fromfd(fd, family, type, proto=None):
  return socket(family, type, proto, fd)


def gethostbyname(hostname):
  raise NotImplementedError


def gethostbyaddr(ipaddr):
  names, err = _LookupAddr(ipaddr)
  if err:
    return error(err)
  return names[0], [], [ipaddr]


def gethostname():
  raise NotImplementedError


def getprotobyname(proto):
  raise NotImplementedError


# --> port number
def getservbyname(servicename, protocolname=None):
  raise NotImplementedError


def getservbyport(portnumber, protocolname=None):
  raise NotImplementedError


def socketpair(family=None, type=None, proto=None):
  raise NotImplementedError


def ntohs(n):
  raise NotImplementedError


def ntohl(n):
  raise NotImplementedError


def htons(n):
  raise NotImplementedError


def htonl(n):
  raise NotImplementedError


# --> List of (family, socktype, proto, canonname, sockaddr)
def getaddrinfo(host, port, family=None, socktype=None, proto=None, flags=None):
  raise NotImplementedError


# --> (host, port)
def getnameinfo(sockaddr, flags):
  raise NotImplementedError


# -> 32-bit packed IP representation
def inet_aton(ipaddr):
  return ''.join(chr(int(n)) for n in ipaddr.split('.'))


# -> IP address string
def inet_ntoa(ipaddr):
  return ''.join(ord(c) for c in ipaddr)


# -> None | float
def getdefaulttimeout():
  raise NotImplementedError


def setdefaulttimeout(to):
  raise NotImplementedError