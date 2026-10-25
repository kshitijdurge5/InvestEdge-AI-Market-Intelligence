"""
InvestEdge UI
=============

Main UI assembler.

Combines:

    ui_styles.py
    ui_components.py
    ui_html.py
    ui_javascript.py
"""

from __future__ import annotations

from fastapi.responses import HTMLResponse

from . import ui_styles
from . import ui_html
from . import ui_javascript


def _get_function(module, names):
    """Return the first matching callable."""

    for name in names:
        function = getattr(module, name, None)

        if callable(function):
            return function

    return None


def _get_styles() -> str:
    """Get CSS from ui_styles.py."""

    function = _get_function(
        ui_styles,
        [
            "get_styles",
            "styles",
            "build_styles",
        ],
    )

    if function is None:
        raise RuntimeError(
            "ui_styles.py must provide get_styles()."
        )

    return str(function())


def _get_html() -> str:
    """Get HTML from ui_html.py."""

    function = _get_function(
        ui_html,
        [
            "get_html",
            "build_html",
            "render_html",
            "html",
        ],
    )

    if function is None:
        raise RuntimeError(
            "ui_html.py must provide get_html()."
        )

    return str(function())


def _get_javascript() -> str:
    """Get JavaScript from ui_javascript.py."""

    function = _get_function(
        ui_javascript,
        [
            "get_javascript",
            "get_js",
            "javascript",
            "build_javascript",
        ],
    )

    if function is None:
        raise RuntimeError(
            "ui_javascript.py must provide get_javascript()."
        )

    return str(function())


def _replace_placeholders(
    html: str,
    styles: str,
    javascript: str,
) -> str:
    """
    Replace all supported placeholder formats.

    This makes ui.py tolerant of different placeholder
    styles used inside ui_html.py.
    """

    style_placeholders = [
        "[STYLES]",
        "{STYLES}",
        "{{STYLES}}",
        "<!-- STYLES -->",
        "<!--STYLES-->",
    ]

    javascript_placeholders = [
        "[JAVASCRIPT]",
        "{JAVASCRIPT}",
        "{{JAVASCRIPT}}",
        "<!-- JAVASCRIPT -->",
        "<!--JAVASCRIPT-->",
    ]

    for placeholder in style_placeholders:
        html = html.replace(
            placeholder,
            styles,
        )

    for placeholder in javascript_placeholders:
        html = html.replace(
            placeholder,
            javascript,
        )

    return html


def build_dashboard_html() -> str:
    """
    Build the complete InvestEdge dashboard.
    """

    styles = _get_styles()

    html = _get_html()

    javascript = _get_javascript()

    # Remember whether placeholders existed before replacement.
    had_style_placeholder = any(
        placeholder in html
        for placeholder in [
            "[STYLES]",
            "{STYLES}",
            "{{STYLES}}",
            "<!-- STYLES -->",
            "<!--STYLES-->",
        ]
    )

    had_javascript_placeholder = any(
        placeholder in html
        for placeholder in [
            "[JAVASCRIPT]",
            "{JAVASCRIPT}",
            "{{JAVASCRIPT}}",
            "<!-- JAVASCRIPT -->",
            "<!--JAVASCRIPT-->",
        ]
    )

    # Replace placeholders.
    html = _replace_placeholders(
        html,
        styles,
        javascript,
    )

    # ========================================================
    # Complete HTML document
    # ========================================================

    if "<!DOCTYPE html>" in html.upper():

        page = html

        # Inject CSS only if ui_html.py did not provide a
        # placeholder for it.

        if not had_style_placeholder:

            if "</head>" in page:

                page = page.replace(
                    "</head>",
                    styles + "\n</head>",
                    1,
                )

        # Inject JavaScript only if ui_html.py did not
        # provide a placeholder.

        if not had_javascript_placeholder:

            if "</body>" in page:

                page = page.replace(
                    "</body>",
                    javascript + "\n</body>",
                    1,
                )

            else:

                page += javascript

        return page

    # ========================================================
    # HTML fragment
    # ========================================================

    return f"""
<!DOCTYPE html>

<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <meta
        name="description"
        content="InvestEdge AI-powered market intelligence"
    >

    <meta
        name="theme-color"
        content="#07131f"
    >

    <title>InvestEdge — AI Market Intelligence</title>

    {styles}

</head>

<body>

    {html}

    {javascript}

</body>

</html>
"""


def dashboard() -> HTMLResponse:
    """
    Return the InvestEdge dashboard.
    """

    return HTMLResponse(
        content=build_dashboard_html(),
        status_code=200,
    )


__all__ = [
    "dashboard",
    "build_dashboard_html",
]