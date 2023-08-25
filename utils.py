from lark import Lark, Transformer

filepath = 'Mon Gara.glyphs'
with open(filepath) as f:
    raw_content = f.read()


class Tree2Json(Transformer):

    def string(self, s):
        (s,) = s
        return str(s)
    
    def quoted_string(self, s):
        (s,) = s
        return str(s[1:-1])
    
    def number(self, n):
        (n,) = n
        n = float(n)
        if n == int(n):
            return int(n)
        return n
    
    list = list
    pair = tuple
    dict = dict


glyphs_parser = Lark(r'''
    ?value : dict
           | list
           | string
           | quoted_string
           | SIGNED_NUMBER -> number

    list : "(" [value ("," value)*] ")"
    dict : "{" [(pair ";")*] "}"
    pair : string "=" value

    string : /[a-zA-Z0-9_.-]+/
    quoted_string : ESCAPED_STRING | MULTILINE_QUOTED_STRING

    MULTILINE_QUOTED_STRING : /"([^"\\]*(\\.[^"\\]*)*)"/

    %import common.ESCAPED_STRING
    %import common.SIGNED_NUMBER
    %import common.WS
    %ignore WS

    ''', start='value', parser='lalr', transformer=Tree2Json())

parsed = glyphs_parser.parse(raw_content)
