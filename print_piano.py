#print('│\033[43m│abc')

WHITE = ' '
WHITE_LEFT = WHITE_RIGHT = WHITE_SEP = '┃'
WHITE_BOTTOM = '━'
WHITE_BOTTOM_LEFT = '┗'
WHITE_BOTTOM_RIGHT = '┛'
WHITE_BOTTOM_SEP = '┻'

BLACK = '▉'
BLACK = ' '
BLACK_LEFT = BLACK_RIGHT = '┃'
BLACK_BOTTOM = '━'
BLACK_BOTTOM_LEFT = '┗'
BLACK_BOTTOM_RIGHT = '┛'

BLACK_WHITE_CROSS = '┳'
BLACK_WHITE_CROSS_LEFT = '┣'
BLACK_WHITE_CROSS_RIGHT = '┫'

def get_piano_line(labels, width, char, left_char, right_char, sep_char):
    line = ''
    left = True

    for label in labels:
        if left:
            line += left_char
        else:
            line += sep_char
        line += label.center(width - 1, char)
        left = False
    line += right_char
    return line

def get_white_piano(notes, keys, note_width, height):
    empty_labels = [''] * len(notes)
    y_label1 = max(height - 5, 0)
    y_label2 = max(height - 3, 0)

    for y in range(height - 1):
        if y == y_label1:
            labels = notes
        elif y == y_label2:
            labels = keys
        else:
            labels = empty_labels
        yield get_piano_line(labels, note_width, WHITE, WHITE_LEFT, WHITE_RIGHT, WHITE_SEP)
    yield get_piano_line(empty_labels, note_width, WHITE_BOTTOM, WHITE_BOTTOM_LEFT, WHITE_BOTTOM_RIGHT, WHITE_BOTTOM_SEP)

def get_piano(notes, keys, acc_notes, acc_keys, width, height):
    note_width = (width - 1) // len(notes)
    bnote_width = note_width // 2
    bheight = int(height * 2 / 3)

    empty_labels = [''] * len(acc_notes)
    y_label1 = max(bheight - 5, 0)
    y_label2 = max(bheight - 3, 0)

    for y, line in enumerate(get_white_piano(notes, keys, note_width, height)):
        line = list(line)
        if y == y_label1:
            labels = acc_notes
        elif y == y_label2:
            labels = acc_keys
        else:
            labels = empty_labels
        if y < bheight:
            for x, note in enumerate(acc_notes):
                if note is None:
                    continue
                bx = (x * note_width) - bnote_width // 2
                bwidth = bnote_width
                if bx < 0:
                    bwidth += bx
                    bx = 0
                if bx + bwidth > len(line):
                    bwidth = len(line) - bx

                if y == bheight - 1:
                    line[bx:bx+bwidth] = BLACK_BOTTOM_LEFT + labels[x].center(bwidth - 2, BLACK_BOTTOM) + BLACK_BOTTOM_RIGHT
                    line[x * note_width] = BLACK_WHITE_CROSS
                    line[0] = BLACK_WHITE_CROSS_LEFT
                    line[-1] = BLACK_WHITE_CROSS_RIGHT
                else:
                    line[bx:bx+bwidth] = BLACK_LEFT + labels[x].center(bwidth - 2, BLACK) + BLACK_RIGHT
        yield ''.join(line)

def print_piano(*args, **kwargs):
    for line in get_piano(*args, **kwargs):
        print(line)

if __name__ == '__main__':
    print_piano(
        'GABCDEFGABCD',
        'qsdfghjklmù*',
        ('F#', 'G#', 'Bf', None, 'C#', 'Ef', None, 'F#', 'G#', 'Bf', None, 'C#', 'Ef'),
        'aze ty iop $ ',
        200,
        30,
    )
