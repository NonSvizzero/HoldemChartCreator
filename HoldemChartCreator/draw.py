from PIL import Image, ImageDraw, ImageFont
from HoldemChartCreator.hands import hands

DEFAULT_BORDER = 3
MIN_CELL_SIZE = 20
CELL_PADDING_PERCENTAGE = 0.2
CHART_MARGIN = 10
RANGES_PADDING_TOP = 10
RANGES_SCALE_X = 0.6
RANGE_SIZE_RATIO = 0.15
TEXT_MARGIN = 5
RANGE_HEIGHT = 40

def create_chart(width, height, colors, ranges, bd=DEFAULT_BORDER, bg='black'):
    img = Image.new("RGBA", (int(width * (1 + RANGES_SCALE_X)), height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw_chart(bd, bg, colors, draw, height, width)
    draw_ranges(draw, ranges, width + CHART_MARGIN, RANGES_PADDING_TOP, width * RANGES_SCALE_X - CHART_MARGIN * 2)
    return img


def draw_chart(bd, bg, colors, draw, height, width):
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
                text_offset = NW[0] + int(0.25 * cell_w), \
                              NW[1] + int(0.35 * cell_h)
            else:
                text_offset = NW[0] + int(0.18 * cell_w), \
                              NW[1] + int(0.35 * cell_h)
            draw.text(text_offset, hand, font=font, fill=color['fg'])


def draw_ranges(draw, ranges, x, y, w):
    longest = max((range['name'] for range in ranges), key=len)
    for i, range in enumerate(ranges):
        font = scale_font(w * (1 - RANGE_SIZE_RATIO * 1.5), text=longest)
        box_x, box_y = x, y + (RANGES_PADDING_TOP + RANGE_HEIGHT) * i
        draw.rectangle((box_x, box_y, box_x + w * RANGE_SIZE_RATIO, box_y + w * RANGE_SIZE_RATIO), fill=range['color'], outline="black")
        draw.text((box_x + w * RANGE_SIZE_RATIO + TEXT_MARGIN, box_y), range['name'], font=font, fill='black')

def calculate_boundaries(size, bd=DEFAULT_BORDER):
    x = int((size - bd) / 13) - bd
    if x < MIN_CELL_SIZE:
        raise ValueError
    l = (size - bd - (x + bd) * 13) // 2
    r = size - (x + bd) * 13 - l - bd
    return l, x, r


def scale_font(size, text="XXx", font="consola.ttf"):
    x = 1
    f = ImageFont.truetype(font, x)
    while f.getsize(text)[0] < size:
        x += 1
        f = ImageFont.truetype(font, x)
    return f


def main():
    pass


if __name__ == '__main__':
    main()
