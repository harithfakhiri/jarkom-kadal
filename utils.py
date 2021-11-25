from ctypes import resize


FORMAT = 'utf-8'
MAX_DATA_LENGTH = 32768
MAX_PACKET_LENGTH = MAX_DATA_LENGTH + 9
FLAG = {
    'SYN': 0x2,
    'ACK': 0x10,
    'FIN': 0x1,
    'DATA': 0x0,
    'SYN-ACK': 0x12,
    'FIN-ACK': 0x11
}

class Utils:
    def __init__(self, sequence, acknowledge, flag, checksum=None, data=None):
        self.sequence = sequence
        self.acknowledge = acknowledge
        self.flag = flag
        self.checksum = checksum
        self.data = data

    def __str__(self):
        return "sequence number: {} | acknowledgement number: {} | flags: {} | checksum: {} | data: {}".format(self.sequence, self.acknowledge, self.flag, self.checksum, self.data)

    def create_header_bit(self):
        sequence = format(self.sequence, '032b')

        acknowledge = format(self.acknowledge, '032b')

        flag = format(FLAG[self.flag], '08b')

        empty = format(0x0, '08b')

        header = f"{sequence}{acknowledge}{flag}{empty}"

        return header

    def create_data_bit(self):
        print(type(self.data))
        # return ''.join(format(ord(i), '08b') for i in self.data)
        return bin(int.from_bytes(self.data, byteorder="big"))[2:]

    def convert_to_bytes(self):
        header = self.create_header_bit()
        # print("checksum", self.create_checksum())
        header = header + self.create_checksum()
        # print(header)
        header = int(header, 2).to_bytes(12, 'big')
        # print(header)

        if (self.data):
            data = self.data
            return header + data

        return header

    def create_checksum(self):
        header = self.create_header_bit()
        integer_sum = 0

        # count header sum
        for i in range(0, (len(header)), 16):
            integer_sum = Utils.ones_comp_add16(
                integer_sum, int(header[i:i+16], 2))

        # count data sum
        if self.data:
            data = self.create_data_bit()
            for i in range(0, len(data), 16):
                integer_sum = Utils.ones_comp_add16(
                    integer_sum, int(data[i:i+16], 2))
        checksum = ''.join(
            '1' if i == '0' else '0' for i in format(integer_sum, '016b'))

        return checksum
    

    def validate_checksum(self):

        header_bit = self.create_header_bit()
        data_bit = self.create_data_bit()

        new_sum = 0
        for i in range(0, len(header_bit), 16):
            new_sum += int(header_bit[i:i+16], base=2)
        for i in range(0, len(data_bit), 16):
            new_sum += int(data_bit[i:i+16], base=2)
        new_sum += int(self.checksum, base=2)

        bit_sum = format(new_sum, '016b')
        for i in range(len(bit_sum)):
            if bit_sum[i] == '0':
                return False
        return True

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
