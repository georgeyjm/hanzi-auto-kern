import re

import pyvips
from glyphsLib import GSLayer, GSComponent


def get_layer_dimensions(layer: GSLayer) -> (int, int):
    ascender = layer.master.ascender
    descender = layer.master.descender
    height = ascender - descender # Will be incorrect for non-latin characters, this is something glyphsLib has to fix first, also overshoot is not implemented yet for the same reason
    width = layer.width
    return width, height

def layer_to_svg_code(layer: GSLayer, scaling: float=1) -> str:
    '''Converts a GSLayer into SVG code with headers and background.'''

    # Setup SVG parameters
    width, height = get_layer_dimensions(layer)
    y_offset = layer.master.ascender
    path_d = _layer_to_svg_path(layer, scaling, 0, y_offset)

    svg_code = f'<svg width="{width * scaling}" height="{height * scaling}" xmlns="http://www.w3.org/2000/svg">\
                 <rect width="100%" height="100%" fill="white"/>\
                 <path d="{path_d}" fill="black"/>\
                 </svg>'.replace('  ', '')
    return svg_code


def iter_shapes(layer: GSLayer):
    '''Recursively iterate over all shapes in a layer.'''

    for shape in layer.shapes:
        if isinstance(shape, GSComponent): # Component shape
            for component_shape in iter_shapes(shape.layer):
                yield component_shape
        else:
            yield shape


def _layer_to_svg_path(layer: GSLayer, scaling: float=1, x_offset: float=0.0, y_offset: float=0.0) -> str:
    '''Converts a GSLayer into SVG path code.'''

    path_d = ''
    for path in layer.shapes:
        # Component shape
        if isinstance(path, GSComponent):
            # Recursion for component's layer
            path_d += _layer_to_svg_path(path.layer, scaling, path.position.x + x_offset, -path.position.y + y_offset)
            continue

        # Path shape
        path_d += 'M {} {} '.format(
            (path.nodes[-1].position.x + x_offset) * scaling,
            (-path.nodes[-1].position.y + y_offset) * scaling
        )
        i = 0
        while i < len(path.nodes) - 1:
            node = path.nodes[i]
            if node.type == 'offcurve':
                assert node.nextNode.type == 'offcurve'
                assert node.nextNode.nextNode.type == 'curve'
                path_d += 'C {} {}, {} {}, {} {} '.format(
                    (node.position.x + x_offset) * scaling,
                    (-node.position.y + y_offset) * scaling,
                    (node.nextNode.position.x + x_offset) * scaling,
                    (-node.nextNode.position.y + y_offset) * scaling,
                    (node.nextNode.nextNode.position.x + x_offset) * scaling,
                    (-node.nextNode.nextNode.position.y + y_offset) * scaling
                )
                i += 2
            elif node.type == 'line':
                path_d += 'L {} {} '.format(
                    (node.position.x + x_offset) * scaling,
                    (-node.position.y + y_offset) * scaling
                )
            elif node.type == 'curve':
                raise ValueError
            i += 1
        path_d += 'Z '
    return path_d


def unicode_to_glyph_name(character: str) -> str:
    '''Converts a unicode character to its Glyphs-style glyph name (uniXXXX).'''
    # TODO: perhaps return directly for ASCII range?
    return 'uni' + hex(ord(character)).lstrip('0x').upper()


def glyph_name_to_unicode(glyph_name: str) -> str:
    '''Converts a glyph name to its corresponding unicode character.'''
    if (match := re.match(r'uni([0-9a-fA-F]{4})', glyph_name)) is None:
        return glyph_name
    return chr(int(match.groups()[0], 16))


def layer_to_numpy(layer: GSLayer, scaling: float=1):
    '''Converts a GSLayer into single-channel NumPy array with anti-aliasing.'''

    svg_code = layer_to_svg_code(layer) # Scaling will only be done later through pyvips
    im = pyvips.Image.svgload_buffer(bytes(svg_code, 'utf-8'), scale=scaling)
    arr = (255 - im.numpy()[:, :, 0]) / 255
    return arr
