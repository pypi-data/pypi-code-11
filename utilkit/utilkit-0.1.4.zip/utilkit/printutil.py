"""
Printing helper functions, for pretty printing/formatting of data and more
"""

def to_even_columns(data, headers=None):
    """
    Nicely format the 2-dimensional list into evenly spaced columns
    """
    result = ''
    col_width = max(len(word) for row in data for word in row) + 2  # padding
    if headers:
        header_width = max(len(word) for row in headers for word in row) + 2
        if header_width > col_width:
            col_width = header_width

        result += "".join(word.ljust(col_width) for word in headers) + "\n"
        result += '-' * col_width * len(headers) + "\n"

    for row in data:
        result += "".join(word.ljust(col_width) for word in row) + "\n"
    return result


def to_smart_columns(data, headers=None, padding=2):
    """
    Nicely format the 2-dimensional list into columns
    """
    result = ''
    col_widths = []
    for row in data:
        col_counter = 0
        for word in row:
            try:
                col_widths[col_counter] = max(len(word), col_widths[col_counter])
            except IndexError:
                col_widths.append(len(word))
            col_counter += 1

    if headers:
        col_counter = 0
        for word in headers:
            try:
                col_widths[col_counter] = max(len(word), col_widths[col_counter])
            except IndexError:
                col_widths.append(len(word))
            col_counter += 1

    # Add padding
    col_widths = [width + padding for width in col_widths]
    total_width = sum(col_widths)

    if headers:
        col_counter = 0
        for word in headers:
            result += "".join(word.ljust(col_widths[col_counter]))
            col_counter += 1
        result += "\n"
        result += '-' * total_width + "\n"

    for row in data:
        col_counter = 0
        for word in row:
            result += "".join(word.ljust(col_widths[col_counter]))
            col_counter += 1
        result += "\n"
    return result
