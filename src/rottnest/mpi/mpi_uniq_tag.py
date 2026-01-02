next_tag = 1

def get_uniq_tag():
    global next_tag

    res = next_tag
    next_tag += 1

    return res
