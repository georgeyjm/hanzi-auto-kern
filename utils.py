from glyphsLib import GSLayer, GSComponent


def layer_to_svg_code(layer: GSLayer, scaling: float=1) -> str:
    '''Convert a GSLayer into SVG code with headers and background.'''

    # Setup SVG parameters
    ascender = layer.master.ascender
    descender = layer.master.descender
    height = ascender - descender # Will be incorrect for non-latin characters, this is something glyphsLib has to fix first, also overshoot is not implemented yet for the same reason
    y_offset = ascender
    path_d = _layer_to_svg_path(layer, scaling, 0, y_offset)

    svg_code = f'<svg width="{layer.width * scaling}" height="{height * scaling}" xmlns="http://www.w3.org/2000/svg">\
                 <rect width="100%" height="100%" fill="white"/>\
                 <path d="{path_d}" fill="black"/>\
                 </svg>'.replace('  ', '')
    return svg_code


def _layer_to_svg_path(layer: GSLayer, scaling: float=1, x_offset: float=0.0, y_offset: float=0.0):
    '''Convert a GSLayer into SVG path code.'''

    path_d = ''
    for path in layer.shapes:
        # Component shape
        if isinstance(path, GSComponent):
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
