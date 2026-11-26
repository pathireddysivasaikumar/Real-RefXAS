"""Formatting for the Frank QC panel and plot images."""
import base64
import io


def figure_image(figure, *, image_format="png", tight=True):
    buffer = io.BytesIO()
    figure.savefig(buffer, format=image_format, dpi=150, bbox_inches="tight" if tight else None)
    return f"data:image/{image_format};base64," + base64.b64encode(buffer.getvalue()).decode("ascii")
