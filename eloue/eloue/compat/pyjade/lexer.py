
import re

from pyjade.lexer import Lexer as _Lexer

class Lexer(_Lexer):
    RE_ASSIGNMENT = re.compile(r'^(-\s*var\s+)?(\w+) += *([^;\n]+)( *;? *)')
