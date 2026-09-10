"""Effect registry. Each of the 150 codes is a function taking the base image
(float32 RGB array in [0,1], shape (1440, 1152, 3)) and returning an image of the
same shape/dtype (or a PIL image of the same size)."""
REGISTRY = {}


def effect(code):
    """Decorator: @effect('golden_hour') registers the function under that code."""
    code = code.strip().lstrip('/')

    def deco(fn):
        fn.code = code
        REGISTRY[code] = fn
        return fn
    return deco
