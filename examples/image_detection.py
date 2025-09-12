from trame.app import get_server
from trame.decorators import TrameApp
from trame.ui.vuetify3 import VAppLayout
from trame.widgets.vuetify3 import VLayout
from trame.widgets import html

from trame_annotations.widgets.annotations import ImageDetection

ANNOTATIONS = [
    {
        "id": 0,
        "category_id": 0,
        "label": "if matching category, should not be shown.  Also really long label",
        "score": 0.4939393939393939,
        "bbox": [60, 50, 100, 100],  # xmin, ymin, width, height  <-- COCO format
    },
    {
        "id": 1,
        "category_id": 1,
        "label": "fallback label",
        "bbox": [140, 100, 100, 100],
    },
    {
        "id": 2,
        "category_id": 2,
        "bbox": [100, 75, 100, 100],
    },
    {
        "id": 3,
        "category_id": 0,
        "bbox": [120, 20, 100, 100],
    },
]

MODEL_ANNOTATIONS = {
    0: ANNOTATIONS[0:2],
    1: ANNOTATIONS[2:3],
    2: ANNOTATIONS[3:4],
}

CLASSIFICATIONS = [
    {
        "id": 12,
        "score": 0.9,
        "category_id": 0,
        "label": "if matching category, should not be shown. Also really long label",
    },
    {
        "id": 13,
        "score": 0,
        "category_id": 1,
        "label": "fallback label",
    },
    {
        "id": 14,
        "category_id": 2,
        "label": "another fallback label",
    },
    {
        "id": 15,
        "score": 0.8,
        "category_id": 0,
    },
]

MODEL_CLASSIFICATIONS = {
    0: CLASSIFICATIONS[0:2],
    1: CLASSIFICATIONS[2:3],
    2: CLASSIFICATIONS[3:4],
}

BOXES_AND_CLASSES = ANNOTATIONS + CLASSIFICATIONS

CATEGORIES = {0: {"name": "my category"}, 2: {"name": "other category"}}
MODELS = {0: {"name": "Model A"}, 1: {"name": "Model B"}, 2: {"name": "Model C"}}


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
                    style="padding: 10px; width: 30rem;",
                    id="image-gallery",
                ):
                    ImageDetection(
                        src="https://placecats.com/300/200",
                        annotations=("annotations", ANNOTATIONS),
                        categories=("categories", CATEGORIES),
                        identifier="my_image_id",
                        selected=("'my_image_id' === selected_id",),
                        hover=(self._on_image_hover, "[$event]"),
                        container_selector="#image-gallery",  # keeps annotation tooltip inside of selector target
                        style="height: 20rem;",
                    )

                    html.Hr()

                    ImageDetection(
                        src="https://placecats.com/300/200",
                        annotations=("model_annotations", MODEL_ANNOTATIONS),
                        categories=("categories", CATEGORIES),
                        models=("models", MODELS),
                        color_by="model",
                        container_selector="#image-gallery",  # keeps annotation tooltip inside of selector target
                        style="height: 20rem;",
                    )

                    html.Hr()

                    ImageDetection(
                        src="https://placecats.com/300/200",
                        annotations=("annotations", ANNOTATIONS),
                        line_width=20,
                        line_opacity=0.5,
                        identifier="bigger_but_smaller",
                        selected=("'bigger_but_smaller' === selected_id",),
                        hover=(self._on_image_hover, "[$event]"),
                        container_selector="#image-gallery",
                        style="height: 20rem;",
                    )

                    html.Hr()

                    ImageDetection(
                        src="https://placecats.com/200/200",
                        annotations=("classifications", CLASSIFICATIONS),
                        categories=("categories", CATEGORIES),
                        container_selector="#image-gallery",
                        style="height: 20rem;",
                    )

                    html.Hr()

                    ImageDetection(
                        src="https://placecats.com/200/200",
                        annotations=("model_classifications", MODEL_CLASSIFICATIONS),
                        categories=("categories", CATEGORIES),
                        models=("models", MODELS),
                        color_by="model",
                        container_selector="#image-gallery",
                        style="height: 20rem;",
                    )

                    html.Hr()

                    ImageDetection(
                        src="https://placecats.com/200/200",
                        categories=("categories", CATEGORIES),
                        annotations=("both", BOXES_AND_CLASSES),
                        score_threshold=0.5,
                        container_selector="#image-gallery",
                        style="height: 20rem;",
                    )


def main():
    app = ImageDetectionExample()
    app.server.start()


if __name__ == "__main__":
    main()
