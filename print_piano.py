#print('│\033[43m│abc')

WHITE = ' '
WHITE_LEFT = WHITE_RIGHT = WHITE_SEP = '┃'
WHITE_BOTTOM = '━'
WHITE_BOTTOM_LEFT = '┗'
WHITE_BOTTOM_RIGHT = '┛'
WHITE_BOTTOM_SEP = '┻'

#BLACK = BLACK_BOTTOM = ' '
#BLACK_LEFT = BLACK_BOTTOM_LEFT = '\033[43m '
#BLACK_RIGHT = BLACK_BOTTOM_RIGHT = ' \033[0m'

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

def get_piano(notes, keys, width, height):
    empty_labels = [''] * len(notes)
    note_width = (width - 1) // len(notes)

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

def print_piano(*args, **kwargs):
    for line in get_piano(*args, **kwargs):
        print(line)

if __name__ == '__main__':
    print_piano(
        'GABCDEFGABCD',
        'qsdfghjklmù*',
        150,
        20,
    )
