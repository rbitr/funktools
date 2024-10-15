# funktools
Generate JSON schemas for tool calling or function calling from python functions

```python
from funktools.utils import template

def x_times_y(x: int, y: int):
  return x*y

template(x_times_y)

#{'name': 'x_times_y', 'description': 'This function multiplies two numbers, x and y, and returns the result.', 'input_schema': {'type': 'object', 'properties': {'x': {'type': 'integer', 'description': 'The first number to be multiplied.'}, 'y': {'type': 'integer', 'description': 'The second number to be multiplied.'}}, 'required': ['x', 'y']}}
```

This utility generates JSON schemas to be used with [Anthropic's tool use capability](https://docs.anthropic.com/en/docs/build-with-claude/tool-use) from python functions. 

## Setup
```bash
git clone https://github.com/rbitr/funktools
cd funktools
pip install -e .
export ANTHROPIC_API_KEY = <your anthropic key>
```

## Example

```python
def get_weather(location : str, unit: Literal["celsius", "farhenheit", "kelvin"] = "celsius") -> str:
    """Gets the weather report at a location and date

    :param location: The location to search for a weather report, city, lat/lon, etc.
    :type location: str
    :param unit: The temperature unit in which to provide the temperature
    :type unit: str
    :return: Returns a short sentence describing the weather at the relevant location
        and date
    :rtype: str
    """
    pass

template(get_weather)

#{'name': 'get_weather',
# 'description': 'This function retrieves a weather report for a specified location and returns a short sentence describing the weather conditions. It allows the user to specify the temperature unit for the report.',
# 'input_schema': {'type': 'object',
#  'properties': {'location': {'type': 'string',
#    'description': 'The location for which to search for a weather report. This can be a city name, latitude/longitude coordinates, or other location identifier.'},
#   'unit': {'default': 'celsius',
#    'enum': ['celsius', 'farhenheit', 'kelvin'],
#    'type': 'string',
#    'description': 'The temperature unit to be used in the weather report (e.g., Celsius, Fahrenheit).'}},
#  'required': ['location']}}

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-3-5-sonnet-20240620",
    max_tokens=1024,
    tools=[
        template(get_weather)
    ],
    messages=[{"role": "user", "content": "What's the weather like in San Francisco? I'll be using the response to calculate the volume of some gasses"}],
)
print(response.content[0].text)
print(response.content[1].input)

#Certainly! I can help you get the weather information for San Francisco. Since you'll be using this information to calculate the volume of some gases, it would be most appropriate to use the Kelvin temperature scale, as it's commonly used in scientific calculations.

#Let's use the `get_weather` function to retrieve the weather information for San Francisco. I'll specify the unit as Kelvin for your calculations.
#{'location': 'San Francisco', 'unit': 'kelvin'}

```

