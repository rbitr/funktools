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

## Example 1

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

## Example 2

```python
def plotxy(x : List[float], y: List[float], xlabel: str="", ylabel: str="") -> Dict:
    plt.scatter(x, y)

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    output = BytesIO()
    plt.savefig(output, format='png')
    im_data = output.getvalue()
    image_data = base64.b64encode(im_data).decode("utf-8")
    plt.close()
    return {"image":image_data}

template(plotxy)

#{'name': 'plotxy',
# 'description': 'This function creates a scatter plot using the provided x and y data, sets optional x and y axis labels, saves the plot as a PNG image, encodes it in base64, and returns the encoded image data as a dictionary.',
# 'input_schema': {'type': 'object',
#  'properties': {'x': {'type': 'array',
#    'items': {'type': 'number'},
#    'description': 'A list of float values representing the x-coordinates of the data points to be plotted.'},
#   'y': {'type': 'array',
#    'items': {'type': 'number'},
#    'description': 'A list of float values representing the y-coordinates of the data points to be plotted.'},
#   'xlabel': {'default': '',
#    'type': 'string',
#    'description': 'An optional string parameter to set the label for the x-axis. Default is an empty string.'},
#   'ylabel': {'default': '',
#    'type': 'string',
#    'description': 'An optional string parameter to set the label for the y-axis. Default is an empty string.'}},
#  'required': ['x', 'y']}}

