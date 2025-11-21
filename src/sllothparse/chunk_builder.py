from sllothparse.pdfparser import PDFParser
import fitz
import traceback
from sllothparse.utilities import get_arranged_keys

class DocumentHandler:
    def __init__(self, pdf_path) -> None:
        try: 
            self.pages = fitz.open(pdf_path)
        except Exception as e:
            print(f"Error: While opening pdf with PyMuPDF: {e}")

    def get_all_blocks_and_style_info(self) -> tuple:
        """
        Gets all the blocks in the PDF and also their associated style tuples. 
        """
        try:
            all_styles = []
            all_blocks = []
            for page in self.pages:
                blocks = page.get_text('dict')
                sorted_blocks = sorted(blocks["blocks"], key=lambda b: (b["bbox"][1], b["bbox"][0]))
                parser = PDFParser(sorted_blocks)
                all_blocks += sorted_blocks
                all_styles += parser.getStyleTuples(blocks=sorted_blocks)

            return all_blocks, all_styles
        except Exception as e:
            print(f"Error: While trying to collect all blocks and their corresponding style tuples, {e}")
            return None
        
    def tag_parts(self, all_blocks, all_styles) -> None:
        """
        Based on results from get_all_blocks_and_style_info() method, tag the different parts of the PDF as headings of different types, subheadings of different types and paragraphs.
        """
        try:
            self.parser = PDFParser(all_blocks)
            self.parser.getMostCommonStyleTuple(all_styles=all_styles)
            self.parser.sortAndArrangeDistinctStyles(all_styles=all_styles) #Even though it returns the results i don't need it here.
            self.parser.assignTagsToStyles() 
            #assigning complete. Now next level of checking where we check for sub-heading
            self.parser.tagLines(all_blocks=all_blocks)

        except Exception as e:
            print(f"Error: While tagging parts of the documents, {e}")
            traceback.print_exc()

    def get_parsed_chunks(self) -> dict:
        """
        Based on the result from tag_parts() method, create semantic chunks
        """
        try:
            self.parser.createTaggedChunks()
            self.parser.createSemanticChunks()
            return self.parser.all_semantic_chunks
        except Exception as e:
            print(f"Error: While creating semantic chunks: {e}")
            return None
        
    def get_semantic_chunks(self):
        """
        Handles all operations by itself
        """
        all_blocks, all_styles = self.get_all_blocks_and_style_info()
        self.tag_parts(all_blocks=all_blocks, all_styles=all_styles)
        all_semantic_chunks = self.get_parsed_chunks()
        return all_semantic_chunks
    
def parse_pdf(pdf_path: str) -> dict:
    doc_handler = DocumentHandler(pdf_path=pdf_path)
    all_semantic_chunks = doc_handler.get_semantic_chunks()

    return all_semantic_chunks
    

#-------------------------------------------------------------------
#                       Example usage
#-------------------------------------------------------------------

if __name__ == '__main__':
    pdf_path = '/Users/sandeshsunny/Documents/Developement/GitHub/sllothparse/src/sllothparse/12 SEPTEMBER 2025.pdf'
    semantic_chunks = parse_pdf(pdf_path=pdf_path)
    for ix, chunk in semantic_chunks.items():
        keys = get_arranged_keys(chunk=chunk)
        for key in keys:
            print(f"{key} : {chunk[key]}")
        print("\n")