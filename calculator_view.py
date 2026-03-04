"""
Discord UI Calculator View component.
Provides an interactive calculator with button interface.
"""
import ast
import operator
import discord
from discord.ui import Button, View
from typing import List, Tuple


# Inline safe math evaluator (previously in safe_eval.py)
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def safe_eval(expression: str):
    """Safely evaluate a math expression."""
    try:
        tree = ast.parse(expression, mode='eval')
        return _eval_node(tree.body)
    except Exception:
        return "Error"


def _eval_node(node):
    """Recursively evaluate an AST node."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    elif isinstance(node, ast.BinOp) and type(node.op) in SAFE_OPERATORS:
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        return SAFE_OPERATORS[type(node.op)](left, right)
    elif isinstance(node, ast.UnaryOp) and type(node.op) in SAFE_OPERATORS:
        return SAFE_OPERATORS[type(node.op)](_eval_node(node.operand))
    else:
        raise ValueError("Unsafe expression")


def format_result(value) -> str:
    """Format a numeric result for display."""
    if value == "Error":
        return "Error"
    if isinstance(value, float) and value == int(value):
        return str(int(value))
    return str(value)


class CalculatorView(View):
    """Interactive calculator with Discord button interface."""
    
    def __init__(self):
        super().__init__(timeout=300)  # 5 minute timeout
        self.current_input = ""
        self.result = None
        self._setup_buttons()

    def _setup_buttons(self):
        """Set up all calculator buttons."""
        # Row 1: 7, 8, 9, /, ⌫
        self._add_button_row([
            ("7", discord.ButtonStyle.secondary),
            ("8", discord.ButtonStyle.secondary),
            ("9", discord.ButtonStyle.secondary),
            ("/", discord.ButtonStyle.primary),
            ("⌫", discord.ButtonStyle.secondary),
        ])
        
        # Row 2: 4, 5, 6, *, C
        self._add_button_row([
            ("4", discord.ButtonStyle.secondary),
            ("5", discord.ButtonStyle.secondary),
            ("6", discord.ButtonStyle.secondary),
            ("*", discord.ButtonStyle.primary),
            ("C", discord.ButtonStyle.danger),
        ])
        
        # Row 3: 1, 2, 3, -, (
        self._add_button_row([
            ("1", discord.ButtonStyle.secondary),
            ("2", discord.ButtonStyle.secondary),
            ("3", discord.ButtonStyle.secondary),
            ("-", discord.ButtonStyle.primary),
            ("(", discord.ButtonStyle.secondary),
        ])
        
        # Row 4: 0, ., =, +, )
        self._add_button_row([
            ("0", discord.ButtonStyle.secondary),
            (".", discord.ButtonStyle.secondary),
            ("=", discord.ButtonStyle.success),
            ("+", discord.ButtonStyle.primary),
            (")", discord.ButtonStyle.secondary),
        ])
        
        # Row 5: Close button
        close_btn = Button(label="Close", style=discord.ButtonStyle.danger, custom_id="Close")
        close_btn.callback = self._create_callback("Close")
        self.add_item(close_btn)

    def _add_button_row(self, buttons: List[Tuple[str, discord.ButtonStyle]]):
        """Add a row of buttons to the view."""
        for label, style in buttons:
            button = Button(label=label, style=style, custom_id=label)
            button.callback = self._create_callback(label)
            self.add_item(button)

    def _create_callback(self, label: str):
        """Create a callback function for a button."""
        async def callback(interaction: discord.Interaction):
            await self._handle_button(interaction, label)
        return callback

    async def _handle_button(self, interaction: discord.Interaction, label: str):
        """Handle button press."""
        if label == "C":
            # Clear all
            self.current_input = ""
            self.result = None
        elif label == "⌫":
            # Backspace
            self.current_input = self.current_input[:-1]
            self.result = None
        elif label == "=":
            # Calculate result using safe evaluator
            if self.current_input:
                self.result = safe_eval(self.current_input)
        elif label == "Close":
            # Delete the calculator message
            await interaction.message.delete()
            return
        else:
            # Append to input
            if self.result is not None:
                # Start fresh input after a result
                self.current_input = ""
                self.result = None
            self.current_input += label

        # Update display
        if self.result is not None:
            display = f"**Result:** {format_result(self.result)}"
        else:
            display = self.current_input or "0"
        
        await interaction.response.edit_message(content=f"```{display}```", view=self)
