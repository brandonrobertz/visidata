import dpkt
import struct

from visidata import *

def _ord(c):
    return struct.unpack('B', c)[0]

def mac_addr(address):
    """Convert a MAC address to a readable/printable string
    """
    return ':'.join('%02x' % b for b in address)

def ip_addr(address):
    return '.'.join('%d' % b for b in address)

def getattrs(obj, attrs, default):
    for a in attrs:
        obj = getattr(obj, a)
    return obj

def ColumnAttr(name, *attrs, **kwargs):
    'Column using getattr/setattr of given attr.'
    if not attrs:
        attrs = name.split('.')

    return Column(name,
            getter=lambda col,row,attrs=attrs: getattrs(row, attrs, None),
            setter=lambda col,row,val,attrs=attrs: setattr(row, attr, val),
            **kwargs)

class PCAPSheet(Sheet):
    # @todo get columns from __hdr_fields__ and set getter for special cases
    columns = [
        Column('eth_dst', 'dst', type=mac_addr),
        ColumnAttr('eth_src', 'src', type=mac_addr),
        ColumnAttr('eth_type', 'type'),
        ColumnAttr('eth_data', 'data', type=len),
        ColumnAttr('ip', width=0),
        ColumnAttr('ip.tcp', width=0),
        ColumnAttr('ip.udp', width=0),
        ColumnAttr('ip.icmp', width=0),
        ColumnAttr('ip.dst', type=ip_addr),
        ColumnAttr('ip.tcp.dport', type=int),
        ColumnAttr('ip.udp.dport', type=int),
        ColumnAttr('ip6.dst', type=mac_addr),
    ]

    def reload(self):
        f = self.source.open_bytes()
        pcap = dpkt.pcap.Reader(f)
        self.rows = []
        for ts, buf in pcap:
            eth = dpkt.ethernet.Ethernet(buf)
            self.rows.append(eth)

def open_pcap(p):
    return PCAPSheet(p.name, source = p)
