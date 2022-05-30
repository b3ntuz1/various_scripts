'''
Функція замінює один елемент масиву на інший.
Це чиста функція, вона повертає нове значення.
'''
def replace_with(old, new, string):
    isstr = False
    if isinstance(string, str):
        string = list(string)
        isstr = True

    def wrap(i):
        nonlocal string
        if len(string) == i:
            return
        if string[i] == old:
            string = string[0:i] + [new] + string[i + 1:]
        wrap(i+1)
    wrap(0)
    if isstr:
        string = "".join(string)
    return string


if __name__ == "__main__":
    assert 'abcdef'.replace('c', 'W') == replace_with('c', 'W', 'abcdef')
    assert [9,2,3,4,5] == replace_with(1, 9, [1,2,3,4,5])
    assert 'hello'.replace('W', 'A') == replace_with('W', 'A', 'hello')
    s = 'hwllo world'
    assert s != replace_with('w', 'e', s)


