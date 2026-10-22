"""NeuroVision object detection MCP tool."""

from collections.abc import Callable
import json
from urllib.request import urlopen

from src.mcp.tooling import McpTool, PropertyList


def get_visible_objects(args: dict) -> str:
    """Read the latest detections from the local vision server."""
    try:
        with urlopen(
            "http://127.0.0.1:8080/detections",
            timeout=3,
        ) as response:
            detections = json.load(response)

        return json.dumps(
            {
                "source": "NeuroVision camera",
                "objects": detections,
                "instruction": (
                    "Describe the detected objects in Turkish. "
                    "These are model predictions, not certain facts."
                ),
            },
            ensure_ascii=False,
        )

    except Exception as exc:
        return json.dumps(
            {
                "error": "NeuroVision camera server unavailable",
                "details": str(exc),
            },
            ensure_ascii=False,
        )


def register_neurovision_tools(
    add_tool: Callable[[McpTool], None],
) -> None:
    add_tool(
        McpTool(
            "get_visible_objects",
            (
                "Kameranın şu anda gördüğü nesneleri algılar. "
                "Kullanıcı 'Ne görüyorsun?', 'Karşında ne var?' "
                "veya 'Etrafındaki nesneleri söyle' dediğinde "
                "bu aracı çağır. Sonucu Türkçe açıkla."
            ),
            PropertyList([]),
            get_visible_objects,
        )
    )
