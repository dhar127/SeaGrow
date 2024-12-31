from django import template

register = template.Library()

@register.filter(name='get_option')
def get_option(question, option_number):
    """
    Returns the option text for a given question and option number.
    The question is expected to be a dictionary with keys like 'option_1', 'option_2', etc.

    Args:
        question (dict): A dictionary containing question options.
        option_number (str): The number of the option to retrieve (e.g., '1', '2', etc.).

    Returns:
        str: The option text corresponding to the given number, or an empty string if not found.
    """
    option_key = f'option_{option_number}'
    return question.get(option_key, '')

@register.filter
def get_item(dictionary, key):
    try:
        return dictionary.get(key, '')
    except AttributeError:
        return ''
