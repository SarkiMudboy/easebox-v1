from typing import Dict, Tuple, List, Any, Optional
from pydantic.core import ErrorDetails
from pydantic import ValidationError, Field
from typing_extensions import Annotated

PhoneNumber = Annotated[str, Field(
                            pattern="^0[879][01]\d{8}$|^234[897][01]\d{8}$|^\+234[897][01]\d{8}$",
                            max_length=13, min_length=11
                            )]

MESSAGES = {
    "email": "Please provide a valid email address",
}

def handle_errors(errors: ValidationError) -> Dict[str: List[ErrorDetails]]:
    parsed_errors: List[ErrorDetails] = []

    for error in errors:
        message = MESSAGES.get(error["type"])

        if message:
            ctx = error.get("ctx")

            error["msg"] = (message.format(**ctx) if ctx else message)

        parsed_errors.append(error)

    return dict(errors=parsed_errors)