from pdfparser import PDFParser
import fitz
import traceback

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

        for page in pages:
            blocks = page.get_text('dict')
            sorted_blocks = sorted(blocks["blocks"], key=lambda b: (b["bbox"][1], b["bbox"][0]))
            parser = PDFParser(sorted_blocks)
            style_tuples = parser.getStyleTuples(blocks=sorted_blocks)
            print(style_tuples)
            '''tagged_spans = parser.tagPages(common_font_size=common_font_size, blocks=sorted_blocks)
            current_dict, current_chunk_no = parser.createDict(previous_dict=previous_dict, previous_chunk_no=previous_chunk_no, tagged_spans=tagged_spans)
            previous_dict, previous_chunk_no = current_dict, current_chunk_no'''

        'print(previous_dict)'
                  


    except FileNotFoundError:
        print("File not found!")
    except Exception as e:
        print(f"The following Exception Occured: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()