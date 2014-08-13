
import os.path

from pyjade.parser import Parser as _Parser
from pyjade import nodes

from .lexer import Lexer

class Parser(_Parser):
    def __init__(self, *args, **kwargs):
        super(Parser, self).__init__(*args, **kwargs)
        self.lexer = Lexer(self.input, **self.options)

    def parseInclude(self):
        path = self.expect('include').val.strip()
        abs_path = os.path.normpath(os.path.join(os.path.dirname(self.filename), path))
        return nodes.Include(abs_path)
