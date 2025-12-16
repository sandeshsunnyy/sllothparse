from itertools import chain

def get_arranged_keys(chunk: dict) -> list[str]:
    """
    A helper function that arranges the keys of a dictionary according to semantics inherent

    Args:
    chunk: Of type dict refers to a single chunk containing: a heading, subheading/s, and a paragraph.

    Returns:
    A list of the ordered keys for the particular chunk
    """

    headings = []
    subheadings = []
    paragraphs = []

    for chunk_key in chunk.keys():
        if chunk_key[:1] == 'h':
            headings.append(chunk_key)
        elif chunk_key[:2] == 'sh':
            subheadings.append(chunk_key)
        else: 
            paragraphs.append(chunk_key)

    return chain(sorted(headings), sorted(subheadings), sorted(paragraphs))

def partition_data_based_on_item_idx(data: list , item_idx: int):
    sorted_values = sorted(data, key=lambda item: item[item_idx], reverse=True)
    all_values_at_idx = sorted(list(set([item[item_idx] for item in data])))    #sorted might not be needed, but just for safety.
    partitions = [[] for _ in range(len(all_values_at_idx))]

    partition_idx = 0
    for i in range(0, len(data)-1): 
        if sorted_values[i][item_idx] != sorted_values[i+1][item_idx]:
            partition_idx += 1
        else:
            partitions[partition_idx].append(sorted_values[i])
    partitions[partition_idx].append(sorted_values[i])

    return partitions


