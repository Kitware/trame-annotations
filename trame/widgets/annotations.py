from trame_annotations.widgets.annotations import *


def initialize(server):
    from trame_annotations import module

    server.enable_module(module)
