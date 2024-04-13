import re

def ends_with_number_html(s):
    pattern = r'\d+\.html$'
    if re.search(pattern, s):
        return True
    return False


def write_page(path, content):
    f = open(path, "w")
    f.write(content)
    f.close()

def remove_spaces(s):
    return s.replace("&nbsp;", " ").replace("\n", "").replace("\t", "").replace(" ", "")
