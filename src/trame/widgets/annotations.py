from trame_annotations.widgets.annotations import *  # noqa F403 F401


def initialize(server):
    from trame_annotations import module

    server.enable_module(module)
