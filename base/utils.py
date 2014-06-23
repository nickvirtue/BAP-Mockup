def find(f, seq):
    for item in seq:
        if f(item):
            return item

