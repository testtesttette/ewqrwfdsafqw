"""
Some exceptions used in other modules.
"""


class LicenseLackError(Exception):
    def __init__(self, num):
        super().__init__(self)
        self.num = num

    def __str__(self):
        return 'License lack:' + str(self.num) + '!'


class LicenseNumError(Exception):
    def __init__(self, num):
        super().__init__(self)
        self.num = num

    def __str__(self):
        return 'Unknown runtime error!'


class WrongKeyError(KeyError):
    def __init__(self, key):
        super().__init__(self)
        self.key = key

    def __str__(self):
        return "找不到'" + self.key + "'列!"
