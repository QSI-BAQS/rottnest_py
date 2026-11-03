def underscore_case(name: str):
    '''
        Maps a string to underscore case
    '''
    name = ''.join(
        [
            [i, f'_{i}'][ord(i) < ord('a') and idx > 0]  
            for idx, i in enumerate(name)
        ]
    ).lower()
    return name

