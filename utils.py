from glyphsLib import GSLayer, GSComponent


def layer_to_svg_code(layer: GSLayer, scaling: float=1) -> str:
    '''Convert a GSLayer into SVG code string.'''

    # Setup SVG parameters
    ascender = layer.master.ascender
    descender = layer.master.descender
    height = ascender - descender # Will be incorrect for non-latin characters, this is something glyphsLib has to fix first
    path_d = ''

    for path in layer.shapes:
        if isinstance(path, GSComponent): # Component path
            # TODO: return the raw SVG path for that component (without headers and stuff)
            continue
        path_d += 'M {} {} '.format(path.nodes[-1].position.x * scaling, (height - path.nodes[-1].position.y + descender) * scaling)
        i = 0
        while i < len(path.nodes) - 1:
            node = path.nodes[i]
            if node.type == 'offcurve':
                assert node.nextNode.type == 'offcurve'
                assert node.nextNode.nextNode.type == 'curve'
                path_d += 'C {} {}, {} {}, {} {} '.format(
                    node.position.x * scaling,
                   (height - node.position.y + descender) * scaling,
                    node.nextNode.position.x * scaling,
                   (height - node.nextNode.position.y + descender) * scaling,
                    node.nextNode.nextNode.position.x * scaling,
                   (height - node.nextNode.nextNode.position.y + descender) * scaling
                )
                i += 2
            elif node.type == 'line':
                path_d += 'L {} {} '.format(
                    node.position.x * scaling,
                   (height - node.position.y + descender) * scaling
                )
            elif node.type == 'curve':
                raise ValueError
            i += 1
        path_d += 'Z'
    
    svg_code = f'<svg width="{layer.width * scaling}" height="{height * scaling}" xmlns="http://www.w3.org/2000/svg">\
                 <rect width="100%" height="100%" fill="white"/>\
                 <path d="{path_d}" fill="black"/>\
                 </svg>'.replace('  ', '')
    return svg_code
