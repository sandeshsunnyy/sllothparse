from typing import Dict, List
from itertools import chain

def get_arranged_keys(chunk: Dict[str]) -> List[str]:
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

    return chain(headings.sort(), subheadings.sort(), paragraphs.sort())