from PIL import Image, ImageDraw, ImageFont
from HoldemChartCreator.hands import hands

DEFAULT_BORDER = 5
MIN_CELL_SIZE = 20
CELL_PADDING_PERCENTAGE = 0.1


def create_chart(width, height, colors, bd=DEFAULT_BORDER, bg='black'):
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    margin_l, cell_w, margin_r = calculate_boundaries(width, bd=bd)
    margin_t, cell_h, margin_b = calculate_boundaries(height, bd=bd)
    font = scale_font(min(cell_h, cell_w) * (1 - 2 * CELL_PADDING_PERCENTAGE))
    draw.rectangle(((margin_l, margin_t), (width - margin_r, height - margin_b)), fill=bg)
    for i, (hands_row, colors_row) in enumerate(zip(hands, colors)):
        for j, (hand, color) in enumerate(zip(hands_row, colors_row)):
            NW = (margin_l + bd + (cell_w + bd) * j, margin_t + bd + (cell_h + bd) * i)
            SE = (margin_l + (cell_w + bd) * (j + 1), margin_t + (cell_h + bd) * (i + 1))
            draw.rectangle((NW, SE), fill=color['bg'])
            if i == j:
                text_offset = NW[0] + int(CELL_PADDING_PERCENTAGE * 2.5 * cell_w), \
                              NW[1] + int(CELL_PADDING_PERCENTAGE * 2.5 * cell_h)
            else:
                text_offset = NW[0] + int(CELL_PADDING_PERCENTAGE * cell_w), \
                              NW[1] + int(CELL_PADDING_PERCENTAGE * 2.5 * cell_h)
            draw.text(text_offset, hand, font=font, fill=color['fg'])
    return img


def calculate_boundaries(size, bd=DEFAULT_BORDER):
    x = int((size - bd) / 13) - bd
    if x < MIN_CELL_SIZE:
        raise ValueError
    l = (size - bd - (x + bd) * 13) // 2
    r = size - (x + bd) * 13 - l - bd
    return l, x, r


def scale_font(size, font="consola.ttf"):
    x = 1
    f = ImageFont.truetype(font, x)
    while f.getsize("XXx")[0] < size:
        x += 1
        f = ImageFont.truetype(font, x)
    return f


def main():
    pass


if __name__ == '__main__':
    main()
