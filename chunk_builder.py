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
        all_blocks = []
        for page in pages:
            blocks = page.get_text('dict')
            sorted_blocks = sorted(blocks["blocks"], key=lambda b: (b["bbox"][1], b["bbox"][0]))
            parser = PDFParser(sorted_blocks)
            all_blocks += sorted_blocks
            all_styles += parser.getStyleTuples(blocks=sorted_blocks)
            
        parser = PDFParser(all_blocks)
        parser.getCommonStyleTuple(all_styles=all_styles)
        larger, same, smaller = parser.sortAndArrangeDistinctStyles(all_styles=all_styles)
        parser.assignTagsToStyles(larger=larger, same=same, smaller=smaller)
        #assigning complete. Now next level of checking where we check for sub-heading

    except FileNotFoundError:
        print("File not found!")
    except Exception as e:
        print(f"The following Exception Occured: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()