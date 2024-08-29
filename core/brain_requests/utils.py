def get_direction_for_numbers(data, asset_type):
    """
    Creates a mapping of word indices to their corresponding directions.

    Args:
        data (list): List of entries containing text and direction information.
        asset_type (str): Type of asset being processed.

    Returns:
        dict: Dictionary mapping word indices to their directions.
    """
    direction_map = {}
    for entry in data:
        start = entry["text"]["start"]
        end = entry["text"]["end"]
        direction = entry[asset_type]

        for num in range(start, end):
            direction_map[num] = direction

    return direction_map


def update_values(data, asset, asset_type, default_direction):
    """
    Updates the direction of words in the given data based on the asset's direction mapping.

    Args:
        data (dict): Dictionary containing word data.
        asset (dict): Asset containing direction mapping.
        asset_type (str): Type of asset being processed.
        default_direction (any): Default direction to use if not found in the mapping.

    Returns:
        dict: Updated data with direction information added to each word.
    """
    direction_map = get_direction_for_numbers(asset, asset_type)
    for i, each_word in enumerate(data["words"]):
        each_word[asset_type] = direction_map.get(i, default_direction)

    return data
