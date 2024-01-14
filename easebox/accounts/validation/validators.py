from typing import Dict, Tuple, List, Any, Optional
from pydantic_core import ErrorDetails
from pydantic import ValidationError, Field
from typing_extensions import Annotated

PhoneNumber = Annotated[str, Field(
                            pattern="^0[879][01]\d{8}$|^234[897][01]\d{8}$|^\+234[897][01]\d{8}$",
                            max_length=13, min_length=11
                            )]

MESSAGES = {
    "email": "Please provide a valid email address",
}

def handle_errors(errors: ValidationError) -> Dict[str, Any]:
    parsed_errors: List[ErrorDetails] = []

    for error in errors:
        message = MESSAGES.get(error["type"])

        if message:
            ctx = error.get("ctx")

            error["msg"] = (message.format(**ctx) if ctx else message)

        loc, msg = error["loc"], error["msg"]

        if loc:

            if len(loc) > 1:
                new_error = {err:msg for err in error["loc"]}

            else:
                
                loc = loc[0]
                new_error = {loc:msg}

        else:

            new_error = {"error": msg}
        
        parsed_errors.append(new_error)

    return dict(errors=parsed_errors)