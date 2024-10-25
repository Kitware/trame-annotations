def test_import():
    from trame_annotations.widgets.annotations import ImageDetection  # noqa: F401

    # For components only, the CustomWidget is also importable via trame
    from trame.widgets.annotations import ImageDetection  # noqa: F401,F811
