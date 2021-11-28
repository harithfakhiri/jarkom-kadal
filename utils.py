from ctypes import resize


FORMAT = 'utf-8'
MAX_DATA_LENGTH = 32768
MAX_PACKET_LENGTH = MAX_DATA_LENGTH + 9
FLAG = {
    'DATA': 0x0,
    'SYN' : 0x40,
    'ACK' : 0x8,
    'FIN' : 0x80,
    'SYN-ACK': 0x48,
    'FIN-ACK': 0x88
}

class Utils:
    def __init__(self, sequence, acknowledge, flag, checksum=None, data=None):
        self.sequence = sequence
        self.acknowledge = acknowledge
        self.flag = flag
        self.checksum = checksum
        self.data = data

    def bitHeader(self):
        sequence = format(self.sequence, '032b')
        acknowledge = format(self.acknowledge, '032b')
        flag = format(FLAG[self.flag], '08b')
        empty = format(0x0, '08b')
        header = f"{sequence}{acknowledge}{flag}{empty}"

        return header

    def toBytes(self):
        header = self.bitHeader()
        header = header + self.Checkingsum()
        header = int(header, 2).to_bytes(12, 'big')

        if (self.data):
            final_bytes = header + self.data
        else :
            final_bytes = header

        return final_bytes

    def Checkingsum(self):
        header = self.bitHeader()
        integer_sum = 0

        # count header sum
        for i in range(0, (len(header)), 16):
            integer_sum = Utils.ones_comp_add16(
                integer_sum, int(header[i:i+16], 2))

        # count data sum
        if self.data:
            data = bin(int.from_bytes(self.data, byteorder="big"))[2:]
            for i in range(0, len(data), 16):
                integer_sum = Utils.ones_comp_add16(
                    integer_sum, int(data[i:i+16], 2))
        checksum = ''.join(
            '1' if i == '0' else '0' for i in format(integer_sum, '016b'))

        return checksum

    @ staticmethod
    def convert_to_packet(bytes):
        sequence = int.from_bytes(bytes[0:4], byteorder='big')
        acknowledge = int.from_bytes(bytes[4:8], byteorder='big')

        flag = list(FLAG.keys())[list(FLAG.values()).index(
            int.from_bytes(bytes[8:9], byteorder='big'))]
        empty = int.from_bytes(bytes[9:10], byteorder='big')
        checksum = format(int.from_bytes(
            bytes[10:12], byteorder='big'), '016b')
        data = bytes[12:]

        packet = Utils(sequence, acknowledge, flag, checksum, data)

        return packet

    @ staticmethod
    def ones_comp_add16(num1, num2):
        result = num1+num2
        return result if result < (1 << 16) else (result+1) % (1 << 16)
