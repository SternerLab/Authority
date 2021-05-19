class Author:
    def __init__(self, given_name, middle_name, surname, suffix,full_name):
        self.given_name = given_name
        self.middle_name = middle_name
        self.surname = surname
        self.suffix = suffix
        self.full_name = full_name

    def __repr__(self):
        return "given " + self.given_name + " middle " + self.middle_name + " surname " + self.surname
