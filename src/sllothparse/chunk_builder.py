from sllothparse.pdfparser import PDFParser
import fitz
import traceback
from sllothparse.utilities import get_arranged_keys
from pathlib import Path
from abc import ABC, abstractmethod
from typing import TypeVar, Generic

R = TypeVar("R")

class BaseParser(ABC, Generic[R]):
    @abstractmethod
    def parse(self) -> R:
        pass

    def __call__(self) -> R:
        return self.parse()

    def __invoke__(self) -> R:
        return self.parse()

class SimpleParser(BaseParser):
    def __init__(self, pdf_path):
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
        
    def show_style_metadata(self):
        all_blocks, all_styles = self.get_all_blocks_and_style_info()
        self.parser = PDFParser(all_blocks)
        self.parser.getMostCommonStyleTuple(all_styles=all_styles)
        larger, same, smaller = self.parser.sortAndArrangeDistinctStyles(all_styles=all_styles)
        
        unique_styles = self.parser.return_unique_styles(all_styles=all_styles)

        print("\n-------------------------------------------------\n")
        print("Unique styles are:")
        for style_tuple in unique_styles:
            print(f'\n{style_tuple}')
        print("\n-------------------------------------------------\n")

        print(f"Styles larger than common font {self.parser.most_common}")
        if larger:
            for style_tuple in larger:
                print(f'\n{style_tuple}')
            print("\n-------------------------------------------------\n")

        print(f"Styles of same size in juxtaposition with common font {self.parser.most_common}")
        for style_tuple in same:
            print(f'\n{style_tuple}')
        print("\n-------------------------------------------------\n")
        
        print(f"Styles smaller than common font {self.parser.most_common}")
        if smaller:
            for style_tuple in smaller:
                print(f'\n{style_tuple}')
            print("\n-------------------------------------------------\n")
                
    def parse(self):
        """
        Handles all operations by itself
        """
        all_blocks, all_styles = self.get_all_blocks_and_style_info()
        self.tag_parts(all_blocks=all_blocks, all_styles=all_styles)
        all_semantic_chunks = self.get_parsed_chunks()
        return all_semantic_chunks
    

#-------------------------------------------------------------------
#                       Example usage
#-------------------------------------------------------------------

if __name__ == '__main__':
    pdf_path = '/Users/sandeshsunny/Documents/Developement/GitHub/sllothparse/src/sllothparse/12 SEPTEMBER 2025.pdf'
    parser = SimpleParser(pdf_path=pdf_path)
    semantic_chunks = parser()
    parser.show_style_metadata()
    for ix, chunk in semantic_chunks.items():
        keys = get_arranged_keys(chunk=chunk)
        for key in keys:
            print(f"{key} : {chunk[key]}")
        print("\n")