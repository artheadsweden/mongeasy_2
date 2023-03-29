def snake_to_pascal(s: str):
    """
    Convert a snake_case string to PascalCase.

    Example:
    snake_to_pascal('my_snake_string') -> 'MySnakeString'
    """
    words = s.split('_')
    return ''.join(w.capitalize() for w in words)


def pascal_to_snake(s: str):
    """
    Convert a PascalCase string to snake_case.

    Example:
    pascal_to_snake('MyPascalString') -> 'my_pascal_string'
    """
    result = ''
    for i, c in enumerate(s):
        if i == 0:
            result += c.lower()
        elif c.isupper():
            result += '_' + c.lower()
        else:
            result += c
    return result
