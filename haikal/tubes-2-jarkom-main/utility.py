

MAX_PACKET = 32768
MAX_DATA = 32756 #jangan lupa ganti 32756


def pack(seq, ack, flag, data):
    # flag:
    # SYN : 0x40
    # ACK : 0x8
    # FIN : 0x80
    # SYN-ACK: 0x48
    # FIN_ACK: 0x88

    #checksum belum
    # packet = format(seq, "032b")+format(ack, "032b")+format(flag, "08b")+format(0, "08b")
    padding = 0
    packet = seq.to_bytes(4, 'big')+ack.to_bytes(4, 'big')+flag.to_bytes(1, 'big')+padding.to_bytes(1, 'big')
    if data is not None:
        checksum = (int.from_bytes(getsum(data), 'big') ^ 0xffff).to_bytes(2, 'big')
        packet = packet + checksum
        packet = packet + data
    return packet

def getHeader(packet):
    seq_num = int.from_bytes(packet[:4], 'big')
    ack_num = int.from_bytes(packet[4:8], 'big')
    flag = int.from_bytes(packet[8:9], 'big')
    return (seq_num, ack_num, flag)

def getData(packet):
    return packet[12:]

def getCheckSum(packet):
    return packet[10:12]

def getsum(data):
    sum = 0
    sum = sum.to_bytes(2, 'big')
    for i in range (0, len(data), 2):
        sum = (int.from_bytes(sum, 'big') + int.from_bytes(data[i:i+1], byteorder="big")).to_bytes(4, 'big')
        while (int.from_bytes(sum, 'big') > 0xff):
            sum = (int.from_bytes(sum[:-2], 'big') + int.from_bytes(data[i:i+1], "big")).to_bytes(4, 'big')
        sum = sum[:-2]

    return sum