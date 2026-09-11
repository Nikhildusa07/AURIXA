from app.ai.tools.invoice import validate_invoice
from app.ai.tools.registry import ToolDefinition, tool_registry


tool_registry.register(
    ToolDefinition(
        name="invoice_validation",
        description="Validates invoice number and total.",
        handler=validate_invoice,
        requires_approval=False,
    )
)