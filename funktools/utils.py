
from typing import List, Union, Callable, Dict, Literal
from pydantic.v1 import validate_arguments
from functools import cache
import anthropic
import inspect
import json
import dis
import os

@cache
def get_descriptions(func : Callable) -> Dict:

    client = anthropic.Anthropic()

    args = list(inspect.signature(func).parameters.keys())

    if func.__doc__:

        source = "docstring and arguments"
        _text = (f"<function name>{func.__name__}</function name>\n\n"
                f"<docstring>{func.__doc__}</docstring>\n\n<arguments>{args}</arguments>")

    else:

        try:
            function_source = inspect.getsource(func)
            source = "function source"

            _text = (f"<function name>{func.__name__}</function name>\n\n"
                    f"<source code>{function_source}</source code>")

        except OSError:  
            
            function_source = dis.Bytecode(func).dis()
            source = "python bytecode and arguments"

            _text = (f"<function name>{func.__name__}</function name>\n\n"
                    f"<source code>{function_source}</source code>\n\n<arguments>{args}</arguments>")
        

    _system= ("You are assisting parsing python docstrings into individual descriptions of "
        "the arguments to a function. From the {source} provided below, "
        "return json that contains a key for each argument, with the corresponding value "
        "describing that argument. Also return an summary description of the function "
        "in a key called 'summary' that explains clearly what the function does. ")
    
    message = client.messages.create(
    model="claude-3-5-sonnet-20240620",
    max_tokens=2048,
    temperature=0,
    system= _system.format(source=source),
                
 
    messages=[
        {
            "role": "user",
            "content": [
                    {
                        "type": "text",
                        "text": _text,
                    },
                ] },
        {
            "role": "assistant",
            "content": [
                    {
                        "type": "text",
                        "text": "{",
                    },
        ] }]
    )
    
    return json.loads("{" + message.content[0].text)

def template(func: Callable) -> str:

    _func_model = validate_arguments(func).model
    func_schema = json.loads(_func_model.schema_json())["properties"]

    for _ex in ["v__duplicate_kwargs", "args", "kwargs"]:
        if _ex in func_schema:
            func_schema.pop(_ex)


    try:
        signature = inspect.signature(func)
    except ValueError as e:
        raise ValueError(
            f"Failed to get signature for function {func.__name__}: {str(e)}"
        )

    required = [
        param.name
        for param in signature.parameters.values()
        if param.default == inspect._empty
    ]

    descriptions = get_descriptions(func)

    for arg,props in func_schema.items():
        if arg in descriptions:
                props["description"] = descriptions[arg]
        else:
                props["description"] = descriptions[arg]

        if "title" in props:
            props.pop("title")

    schema = {
                "name": func.__name__,
                "description": descriptions["summary"] if "summary" in descriptions else (func.__doc__ or "").strip(),
                "input_schema": {
                    "type": "object",
                    "properties": func_schema,
                    "required": required,
            }
    }

    return schema
