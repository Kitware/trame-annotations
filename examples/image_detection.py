from trame.app import get_server
from trame.decorators import TrameApp
from trame.ui.vuetify3 import VAppLayout
from trame.widgets.vuetify3 import VLayout
from trame.widgets import html

from trame_annotations.widgets.annotations import ImageDetection

ANNOTATIONS = [
    {
        "id": 1,
        "category_id": 0,
        "label": "if matching category, should not be shown",
        "bbox": [60, 50, 100, 100],  # xmin, ymin, width, height  <-- COCO format
    },
    {
        "id": 99,
        "category_id": 1,
        "label": "fallback label",
        "bbox": [140, 100, 100, 100],
    },
]

CATEGORIES = [{"id": 1, "name": "my category"}]


@TrameApp()
class ImageDetectionExample:
    def __init__(self, server=None):
        self.server = get_server(server, client_type="vue3")
        self.server.state.selected_id = ""
        self._build_ui()

    def _on_image_hover(self, event):
        self.server.state.selected_id = event["id"]

    def _build_ui(self):
        extra_args = {}
        if self.server.hot_reload:
            extra_args["reload"] = self._build_ui

        with VAppLayout(self.server, full_height=True) as self.ui:
            with VLayout():
                with html.Div(
                    style="padding: 10px;",
                    id="image-gallery",
                ):
                    ImageDetection(
                        src="https://placecats.com/300/200",
                        annotations=("annotations", ANNOTATIONS),
                        categories=("categories", CATEGORIES),
                        line_width=20,
                        line_opacity=0.5,
                        identifier="my_image_id",
                        selected=("'my_image_id' === selected_id",),
                        hover=(self._on_image_hover, "[$event]"),
                        container_selector="#image-gallery",  # keeps annotation tooltip inside of selector target
                    )
                    ImageDetection(
                        style="width: 200px;",
                        src="https://placecats.com/500/500",
                        annotations=("annotations", ANNOTATIONS),
                        identifier="bigger_but_smaller",
                        selected=("'bigger_but_smaller' === selected_id",),
                        hover=(self._on_image_hover, "[$event]"),
                        container_selector="#image-gallery",  # keeps annotation tooltip inside of selector target
                    )


def main():
    app = ImageDetectionExample()
    app.server.start()


if __name__ == "__main__":
    main()
