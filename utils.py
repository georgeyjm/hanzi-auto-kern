import re

from lark import Lark, Transformer


class GlyphsFile:

    def __init__(self, filepath):
        self.masters = {}
        self.glyphs = {}

        self.raw_data = self._parse_raw_glyphs_file(filepath)
        self._parse_json_into_objects()

    def _parse_raw_glyphs_file(self, filepath):
        with open(filepath) as f:
            parsed = _glyphs_parser.parse(f.read())
            return parsed

    def _parse_json_into_objects(self):
        # Masters
        for master in self.raw_data['fontMaster']:
            master_obj = Master(master['id'], master['name'])
            self.masters[master['id']] = master_obj
        
        # Glyphs
        for glyph in self.raw_data['glyphs']:
            glyph_obj = Glyph(self, glyph['glyphname'], glyph.get('unicode')) # For e.g. .liga glyphs, there is no unicode
            self.glyphs[glyph['glyphname']] = glyph_obj
            for layer in glyph['layers']:
                if 'shapes' not in layer: # Empty glyph
                    layer_obj = GlyphLayer(glyph_obj, layer['layerId'], None, None, True, layer['width'], [])
                else:
                    is_default = 'associatedMasterId' not in layer
                    master_id = layer.get('associatedMasterId', layer['layerId'])
                    name = layer.get('name', self.masters[master_id].name)
                    layer_obj = GlyphLayer(glyph_obj, layer['layerId'], name, master_id, is_default, layer['width'], layer['shapes'])
                glyph_obj.layers.append(layer_obj)


class Glyph:

    def __init__(self, file, name, unicode):
        self.file = file
        self.name = name
        self.unicode = unicode
        self.layers = []
    
    def __repr__(self):
        return f'<Glyph "{self.name}">'


class GlyphLayer:

    def __init__(self, glyph, layer_id, name, master_id, is_default, width, shapes):
        self.glyph = glyph
        self.id = layer_id
        self.name = name
        self.master_id = master_id # self.master?
        self.is_default = is_default
        self.width = width
        self.shapes = shapes # unparsed raw data, should we parse it?
    
    @property
    def height(self):
        ascender = 840
        descender = 160
        height = ascender + descender
        return height
    
    def __repr__(self):
        return f'<Layer "{self.name}" of "{self.glyph.name}">'
    
    def to_svg_code(self, scaling=1) -> str:
        descender = 160
        svg_code = '<svg width="{}" height="{}" xmlns="http://www.w3.org/2000/svg"><rect width="100%" height="100%" fill="white"/>'.format(self.width * scaling, self.height * scaling)
        for path in self.shapes:
            if 'ref' in path: # Component path
                # TODO: return the raw SVG path for that component (without headers and stuff)
                continue
            path_d = 'M {} {} '.format(path['nodes'][-1][0] * scaling, (self.height - path['nodes'][-1][1] - descender) * scaling)
            i = 0
            while i < len(path['nodes']) - 1:
                node = path['nodes'][i]
                if node[2] == 'o':
                    assert path['nodes'][i + 1][2] == 'o'
                    assert path['nodes'][i + 2][2] in ('c', 'cs')
                    path_d += 'C {} {}, {} {}, {} {} '.format(node[0] * scaling, (self.height - node[1] - descender) * scaling, path['nodes'][i + 1][0] * scaling, (self.height - path['nodes'][i + 1][1] - descender) * scaling, path['nodes'][i + 2][0] * scaling, (self.height - path['nodes'][i + 2][1] - descender) * scaling)
                    i += 2
                elif node[2] == 'l':
                    path_d += 'L {} {} '.format(node[0] * scaling, (self.height - node[1] - descender) * scaling)
                elif node[2] == 'c':
                    raise ValueError
                i += 1
            path_d += 'Z'
            svg_code += '<path d="{}" fill="black" fill-rule="evenodd"/>'.format(path_d)
        svg_code += '</svg>'
        return svg_code


class Master:

    def __init__(self, master_id, name):
        self.id = master_id
        self.name = name
        self.metrics = {}
        # baseline is also 0

        # self.metrics = 


        {
          "over": 16,
          "pos": 880
        },




class Metric:

    def __init__(self, metric_type, index, filters_string):
        self.type = metric_type
        self.index = index
        matched = re.match(r'(.+) == "(.+)"', filters_string).groups() # TODO: only works for one filter rn
        self.filters = dict((matched))
        # TODO: given a character, return if it passes all filters


class _GlyphsTransformer(Transformer):
    '''Transformer to parse Glyphs file into JSON.'''

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


_glyphs_parser = Lark(r'''
    ?value : dict
           | list
           | string
           | quoted_string
           | SIGNED_NUMBER -> number

    list : "(" [value ("," value)*] ")"
    dict : "{" [(pair ";")*] "}"
    pair : string "=" value

    string : /[a-zA-Z0-9_.]+/
    quoted_string : /"([^"\\]*(\\.[^"\\]*)*)"/

    %import common.SIGNED_NUMBER
    %import common.WS
    %ignore WS

    ''', start='value', parser='lalr', transformer=_GlyphsTransformer())
