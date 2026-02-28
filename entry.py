class Entry:
    def __init__(self, word):
        self.word = word
        self.definition = ""
        self.example = ""

    def set_definition(self, definition):
        self.definition = definition

    def set_example(self, example):
        self.example = example

    def __str__(self):
        return f'Word: {self.word}, Definition: {self.definition}, Example: {self.example}'
