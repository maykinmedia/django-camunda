from typing import Dict, List, Union

import inflection


def underscoreize(data: Union[List, Dict, str, None]) -> Union[List, Dict, str, None]:
    if isinstance(data, list):
        return [underscoreize(item) for item in data]

    if isinstance(data, dict):
        new_data = {}
        for key, value in data.items():
            new_key = inflection.underscore(key)
            # variables are dynamic names, can't make assumptions!
            if key == "variables":
                new_data[new_key] = value
            else:
                new_data[new_key] = underscoreize(value)
        return new_data

    return data
