
import re

from pyjade.lexer import Lexer as _Lexer

class Lexer(_Lexer):
    RE_ASSIGNMENT = re.compile(r'^(-\s*var\s+)?(\w+)\s*=\s*([^;\n]+)([\s;]*)')
    RE_STRING = re.compile(r'^\|([^\n]+)')
