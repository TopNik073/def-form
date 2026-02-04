from libcst import FunctionDef
from libcst import Param


def get_params_list(node: FunctionDef) -> list[Param]:
    params: list[Param] = []
    params.extend(node.params.params)

    if isinstance(node.params.star_arg, Param):
        params.append(node.params.star_arg)

    params.extend(node.params.kwonly_params)

    if isinstance(node.params.star_kwarg, Param):
        params.append(node.params.star_kwarg)

    return params
