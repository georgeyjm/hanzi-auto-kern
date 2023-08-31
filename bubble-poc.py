# Proof of concept for grouping of glyphs based on their shapes

import numpy as np
import matplotlib.pyplot as plt
from skimage.morphology import convex_hull_image
from glyphsLib import GSFont, GSLayer

from utils import layer_to_numpy, unicode_to_glyph_name, glyph_name_to_unicode, layer_to_svg_code


def analyze_layer(layer: GSLayer, blocks: int=3):
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


def generate_convex_hull(arr: np.array) -> np.array:
    # arr = layer_to_numpy(layer)
    chull = convex_hull_image(arr)
    return chull.astype(float)


def min_horizontal_distance(left_arr: np.array, right_arr: np.array) -> int:
    '''Calculates the minimum horizontal distance between two shapes.'''

    min_dist = min(left_arr.shape[1], right_arr.shape[1])
    for row in range(len(left_arr)):
        if not left_arr[row].any() or not right_arr[row].any():
            continue
        dist = left_arr.shape[1] - np.max(np.where(left_arr[row])) + np.min(np.where(right_arr[row]))
        if dist < min_dist:
            min_dist = dist
    return min_dist - 1 # No overlap at all


def display_glyphs_with_kerning(arrs: list, kernings: list):
    '''Display glyphs (in np.array format) with given kerning values.
    Length of kernings should be 1 less than the length of layers.
    Note also that it is assumed all glyphs have the same height.'''

    # Build image
    canvas_width = sum(arr.shape[1] for arr in arrs) - sum(kernings)
    final = np.zeros((len(arrs[0]), canvas_width))
    offset = 0
    for i, arr in enumerate(arrs):
        final[:, offset:offset + arr.shape[1]] += arr
        if i == len(arrs) - 1: # No more adjustment of offset needed
            break
        offset += arr.shape[1] - kernings[i]

    # Show final image
    fig, ax = plt.subplots()
    ax.imshow(final, cmap=plt.cm.gray)
    plt.show()
    return final


font = GSFont('SourceHanSansSC Experiment.glyphs')

threshold = 0.2

# for char in ['中','㒰','㒱','㓀']:
#     print(char)
#     layer = font.glyphs[unicode_to_glyph_name(char)].layers[0]
#     analyze_layer(layer)

# for glyph in font.glyphs:
#     if re.match(r'uni[0-9a-fA-F]{4}', glyph.name) is None:
#         continue
#     print(glyph_name_to_unicode(glyph.name))
#     analyze_layer(glyph.layers[0])

# layer = font.glyphs[10000].layers[0]
# arr = layer_to_numpy(layer)
# chull = generate_convex_hull(arr)
# chull_diff = img_as_float(chull.copy())
# chull_diff[arr > 0] = 2
# fig, ax = plt.subplots()
# ax.imshow(chull_diff, cmap=plt.cm.gray)
# ax.set_title('Difference')
# plt.show()

display_arrs = []
kernings = []
for i in (10000, 10001, 10002, 10003):
    layer = font.glyphs[i].layers[0]
    arr = layer_to_numpy(layer)
    chull = generate_convex_hull(arr)
    chull[arr > 0] = 2 # Displaying both glyph and bubble, can be changed later on
    display_arrs.append(chull)
    if len(display_arrs) <= 1:
        continue
    kerning = min_horizontal_distance(display_arrs[-2], display_arrs[-1])
    kernings.append(kerning)
display_glyphs_with_kerning(display_arrs, kernings)



# 二分法 with min=RSB+LSB, max=min(width1, width2)
# start_min = left_glyph_rsb + right_glyph_lsb
# start_max = min(chull1.shape[1], chull2.shape[1])
# kern = (start_min + start_max) // 2
# while True:
#     canvas = np.zeros((chull1.shape[0], chull1.shape[1] + chull2.shape[1]))
#     canvas[:chull1.shape[0], :chull1.shape[1]] += chull1
#     canvas[chull1.shape[0] - kern:,:chull2.shape[1]] += chull2
