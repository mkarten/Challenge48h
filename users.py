import hashlib


class User:
    def __init__(
        self, username, password, email, firstName, lastName, phoneNumber, usertype
    ):
        self.username = username
        h = hashlib.new("sha256")
        b = bytearray(password, encoding="utf8")
        h.update(b)
        self.password = h.hexdigest()
        self.email = email
        self.firstName = firstName
        self.lastName = lastName
        self.phoneNumber = phoneNumber
        self.events = {}
        self.type = usertype