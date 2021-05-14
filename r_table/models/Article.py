class Article:
    def __init__(self,
        id,
        position, 
        last_name, 
        first_initial, 
        middle_initial,
        suffix,
        title,
        journal_name,
        fullname,
        first_name,
        middle_name,
        language,
        authors,
        mesh_terms="",
        affiliation_terms = "",
        full_title = "",
        year = 0):
        self.id = id
        self.position = position
        self.last_name = last_name
        self.first_initial = first_initial
        self.middle_initial = middle_initial
        self.suffix = suffix
        self.title = title
        self.journal_name = journal_name
        self.fullname = fullname
        self.first_name = first_name
        self.middle_name = middle_name
        self.language = language
        self.authors = authors
        self.mesh_terms = mesh_terms
        self.affiliation_terms = affiliation_terms
        self.full_title = full_title
        self.year = year


    def __repr__(self):
        return  self.id, str(self.position), self.last_name ,self.first_initial , self.middle_initial, self.suffix , self.title , self.journal_name , self.fullname , self.first_name , self.middle_name , self.language , self.authors, self.mesh_terms, self.affiliation_terms, self.full_title, self.year