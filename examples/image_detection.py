from trame.app import get_server
from trame.decorators import TrameApp
from trame.ui.vuetify3 import VAppLayout
from trame.widgets.vuetify3 import VLayout
from trame.widgets import html

from trame_annotations.widgets.annotations import ImageDetection


@TrameApp()
class ImageDetectionExample:
    def __init__(self, server=None):
        self.server = get_server(server, client_type="vue3")
        self._build_ui()

        self.server.state.selected_id = ""

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
                        annotations=(
                            [
                                {
                                    "id": 1,
                                    "category_id": 0,
                                    "label": "my category",
                                    "bbox": [60, 50, 100, 100],
                                },
                                {
                                    "id": 99,
                                    "category_id": 1,
                                    "label": "fallback label",
                                    "bbox": [140, 100, 100, 100],
                                },
                            ],
                        ),
                        categories=(
                            [
                                {
                                    "id": 1,
                                    "name": "my category",
                                },
                            ],
                        ),
                        identifier="my_image_id",
                        selected=("'my_image_id' === selected_id",),
                        hover=(self._on_image_hover, "[$event]"),
                        container_selector="#image-gallery",  # keeps annotation tooltip inside of selector target
                    )


def main():
    app = ImageDetectionExample()
    app.server.start()


if __name__ == "__main__":
    main()
