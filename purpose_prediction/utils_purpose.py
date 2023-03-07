import sys


class Purpose:
    '''
    Analytics 32
    App Functionality 16
    Third-Party Advertising 8
    Product Personalization 4
    Developer's Advertising or Marketing 2
    Other Purposes 1
    '''
    purposes = ["Analytics", "App Functionality", "Third-Party Advertising",
                "Product Personalization", "Developer's Advertising or Marketing", "Other Purposes"]

    purposes2bit = {"Analytics": 32, "App Functionality": 16,  "Third-Party Advertising": 8,
                    "Product Personalization": 4, "Developer's Advertising or Marketing": 2, "Developer’s Advertising or Marketing": 2, "Other Purposes": 1, "Data Used to Track You": 0}

    bit2purposes = {32: 'Analytics', 16: 'App Functionality', 8: 'Third-Party Advertising',
                    4: 'Product Personalization', 2: 'Developer\'s Advertising or Marketing', 1: 'Other Purposes'}

    def __init__(self, purposes):
        if isinstance(purposes, int):
            self.purposes = purposes
        elif isinstance(purposes, str):
            self.purposes = self.purposes2bit[purposes]
        elif isinstance(purposes, list):
            self.purposes = 0
            for purpose in purposes:
                assert isinstance(purpose, str)
                if purpose not in self.purposes2bit:
                    print('purpose not in purposes2bit:', purpose)
                    continue
                self.purposes |= self.purposes2bit[purpose]
        else:
            raise TypeError('purposes must be int, str or list')

    def __str__(self) -> str:
        bit_repr = format(self.purposes, '06b')
        return bit_repr + ' ' + ', '.join(self.get_purpose_list())

    # -
    def __sub__(self, other: 'Purpose') -> 'Purpose':
        assert isinstance(other, Purpose)
        return Purpose(self.purposes & ~other.purposes)

    # &
    def __and__(self, other: 'Purpose') -> 'Purpose':
        assert isinstance(other, Purpose)
        return Purpose(self.purposes & other.purposes)

    def is_empty(self) -> bool:
        return self.purposes == 0

    def add_purpose(self, purpose: str) -> None:
        assert isinstance(purpose, str)
        assert purpose in self.purposes2bit
        self.purposes |= self.purposes2bit[purpose]

    def get_bits(self) -> int:
        return self.purposes

    def get_purpose_list(self) -> list:
        bit_repr = format(self.purposes, '06b')
        purposes = []
        for i in range(len(bit_repr)):
            if bit_repr[i] == '1':
                purposes.append(self.bit2purposes[2**(len(bit_repr)-i-1)])
        return purposes

    def is_proper_subset(self, other: 'Purpose') -> bool:
        assert isinstance(other, Purpose)
        return self.purposes & other.purposes == self.purposes and self.purposes != other.purposes


if __name__ == '__main__':
    a = Purpose(['App Functionality', 'Product Personalization'])
    b = Purpose(0b110010)
    c = Purpose(0)
    print(a)
    print(b)
    print(c)
    print(a-b)
    print(b-a)
