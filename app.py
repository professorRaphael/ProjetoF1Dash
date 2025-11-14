from __future__ import annotations

from pathlib import Path

from dash import Dash

from controller.callbacks import register_callbacks
from model.f1_model import F1DataModel
from view.layout import create_layout


def create_app() -> Dash:
    base_path = Path("data")

    model = F1DataModel(base_path=base_path)

    app = Dash(
        __name__,
        title="Dashboard Fórmula 1",
    )

    app.layout = create_layout(model)
    register_callbacks(app, model)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
