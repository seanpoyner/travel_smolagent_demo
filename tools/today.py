from datetime import date
from smolagents.tools import Tool

class CurrentDateTool(Tool):
    name = "current_date"
    description = "Provides today's date in YYYY-MM-DD format."
    inputs = {}
    output_type = "string"

    def forward(self) -> str:
        return date.today().strftime("%Y-%m-%d")
