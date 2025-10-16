from pdfparser import PDFParser
import fitz
import traceback
import collections

"""
1. Take out text
2. chunck it
3. use the pdf logic to figure out the common font size
4. create dicts with relevant details
5. We can do analysis of common patterns
"""

pdf_path = "12 SEPTEMBER 2025.pdf"


def main():

    try:
        
        pages = fitz.open(pdf_path)

        previous_dict = {} 
        previous_chunk_no = None
        all_styles = []
        for page in pages:
            blocks = page.get_text('dict')
            sorted_blocks = sorted(blocks["blocks"], key=lambda b: (b["bbox"][1], b["bbox"][0]))
            parser = PDFParser(sorted_blocks)
            all_styles += parser.getStyleTuples(blocks=sorted_blocks)
            
        most_common = collections.Counter(all_styles).most_common(1)[0][0]
        print(most_common) # do something for heading and sub-headings (quick-thought: count-based?)
        print(f"most common= {most_common}")
        distinct_styles = list(set(all_styles))
        print(distinct_styles) # we got distinct styles

        #check for same font over all fonts if it is same fonts then a different logic has to be font. 
        sorted_styles_on_size = sorted(distinct_styles, key= lambda item: (item[0], item[1]), reverse=True)
        #Even after sorting if it is the same size then we should look for other ways to find semantics.
        print(sorted_styles_on_size)

        #divide the tuples into different groups based on whether it is in the same level as common text. In the group having the common tuple, place it at the very end. Anything below the common font should be handled carefully.
        ix = sorted_styles_on_size.index(most_common)
        larger, same, smaller = [], [], []
        for index, style_tuple in enumerate(sorted_styles_on_size):
            if index == ix:
                continue
            if style_tuple[0] == most_common[0]:
                same.append(style_tuple)
            elif style_tuple[0] > most_common[0]:
                larger.append(style_tuple)
            else:
                smaller.append(style_tuple)
        same.append(most_common)


    except FileNotFoundError:
        print("File not found!")
    except Exception as e:
        print(f"The following Exception Occured: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()