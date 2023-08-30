# Proof of concept for grouping of glyphs based on their shapes

import re

from glyphsLib import GSFont

from utils import layer_to_numpy, unicode_to_glyph_name, glyph_name_to_unicode, layer_to_svg_code


def analyze_layer(layer, blocks=3):
    arr = layer_to_numpy(layer, scaling=0.5)
    height, width = arr.shape
    block_height = height // blocks
    block_width = width // blocks
    block_size = block_height * block_width

    for i in range(blocks):
        for j in range(blocks):
            block = arr[i * block_height:(i + 1) * block_height, j * block_width:(j + 1) * block_width]
            print('{:.3f}'.format(block.sum() / block_size, 5), end='  ')
        print()


font = GSFont('SourceHanSansSC Experiment.glyphs')

threshold = 0.2

# for char in ['中','㒰','㒱','㓀']:
#     print(char)
#     layer = font.glyphs[unicode_to_glyph_name(char)].layers[0]
#     analyze_layer(layer)

for glyph in font.glyphs:
    if re.match(r'uni[0-9a-fA-F]{4}', glyph.name) is None:
        continue
    print(glyph_name_to_unicode(glyph.name))
    analyze_layer(glyph.layers[0])
