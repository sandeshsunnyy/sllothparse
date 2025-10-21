import collections
import re

class PDFParser:

    def __init__(self, page_data: list[dict]):
        self.page_data = page_data

    
    def getStyleTuples(self, blocks: list[dir]):
        list_of_styles = []
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        size = span["size"]
                        color = span["color"]
                        font = span["font"]
                        list_of_styles.append((size, color, font))
        return list_of_styles
    
    def getCommonStyleTuple(self, all_styles:list[tuple]):
        self.most_common = collections.Counter(all_styles).most_common(1)[0][0]# do something for heading and sub-headings (quick-thought: count-based?)
    

    def sortAndArrangeDistinctStyles(self, all_styles) -> tuple:
        distinct_styles = list(set(all_styles))
        print(distinct_styles) # we got distinct styles

        #check for same font over all fonts if it is same fonts then a different logic has to be font. 
        self.sorted_styles_on_size = sorted(distinct_styles, key= lambda item: (item[0], item[1]), reverse=True)
        #Even after sorting if it is the same size then we should look for other ways to find semantics.
        print(self.sorted_styles_on_size)

        #divide the tuples into different groups based on whether it is in the same level as common text. In the group having the common tuple, place it at the very end. Anything below the common font should be handled carefully.
        ix = self.sorted_styles_on_size.index(self.most_common)
        larger, same, smaller = [], [], []
        for index, style_tuple in enumerate(self.sorted_styles_on_size):
            if index == ix:
                continue
            if style_tuple[0] == self.most_common[0]:
                same.append(style_tuple)
            elif style_tuple[0] > self.most_common[0]:
                larger.append(style_tuple)
            else:
                smaller.append(style_tuple)
        same.append(self.most_common)

        return larger, same, smaller
        
    def getCountsOfStyles(self, all_styles):
        counts = collections.Counter(all_styles)
        style_to_count = [(style, counts[style]) for style in self.sorted_styles_on_size]
        print(sorted(style_to_count, key=lambda item: item[1], reverse=True))

        #try with manual method, if its not that good, might have to resort to LLM-based semantic analysis. The key is not to overload the LLM, but ask it why the style tuples are used. 
    def assignTagsToStyles(self, larger: list[tuple], same: list[tuple], smaller: list[tuple]):
        tag_map = {}
        for i, tuple in enumerate(larger, 1):
            tag_map[tuple] = f"h{i}"
    
        for i, tuple in enumerate(same, 1):
            if tuple == self.most_common:
                tag_map[tuple] = "p"
            else:
                tag_map[tuple] = f"sh{i}"
        
        for i, tuple in enumerate(smaller, 1):
            tag_map[tuple] = "p"

        self.tag_map = tag_map

    @staticmethod
    def check_for_subheading(text: str) -> bool:
        pattern = re.compile(r"^\s*((\d+(?:\.\d+)*)|[A-Za-z])[\.\)]")

        return True if pattern.match(text) else False
    
    def showSpans(self, all_blocks):
        for block in all_blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        size = span["size"]
                        color = span["color"]
                        font = span["font"]
                        style_tuple = (size, color, font)
                        tag = self.tag_map[style_tuple]
                        if tag[:2] == "sh":
                            if not self.check_for_subheading(span["text"]):
                                tag = "p"
                        final_text = f"<{tag}> {span["text"]} </{tag}>\n"
                        print(final_text)

    def tagPages(self, common_font_size: int, blocks: list[dict]) -> list[dict]:
        """
        Tagging will be done in a simple manner for now. We will consider each block, and take the first span. The font_size of the
        first span will be taken as the size for the entire block. After that we'll combine the data from every line and make new dictionary with the
        tags and its text.
        """

        tagged_spans = []

        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    span_text = ""
                    for span in line["spans"]:
                        span_font_size = span["size"]
                        span_text += span["text"]
                        span_font = "normal"
                        if "bold" in span["font"].lower():
                            span_font = "bold"
                        elif "italics" in span["font"].lower():
                            span_font = "italics"

                        if span_font_size > common_font_size:
                            tagged_spans.append(
                                {
                                    "tag" : "heading",
                                    "text": span_text,
                                    "font_type" : span_font
                                
                                }
                            )
                        elif span_font_size <= common_font_size:
                            tagged_spans.append(
                                {
                                    "tag" : "paragraph",
                                    "text": span_text,
                                    "font_type" : span_font
                                
                                }
                            )
                        else:
                            tagged_spans.append(
                                {
                                    "tag" : "paragraph",
                                    "text": span_text,
                                    "font_type" : span_font
                                
                                }
                            )
        print(tagged_spans[-1])
        return tagged_spans
    
    @staticmethod
    def wrapFont(text: str, type: str) -> str:
        
        if type == "bold":
            return f"**{text}**"
        elif type == "italic":
            return f"*{text}*"
        else:
            return text
    
    def createMarkdown(self, tagged_spans: list[dict]) -> str:
    
        whole_text = ""
        for span in tagged_spans:
            if span["tag"] == "heading":
                whole_text += f"\n\n##{self.wrapFont(text=span["text"], type=span["font_type"])}\n\n"
            elif span["tag"] == "paragraph":
                whole_text += f"{self.wrapFont(text=span["text"], type=span["font_type"])}"
        print(whole_text)
        return whole_text
    
    @staticmethod
    def createDict(previous_dict: dict, previous_chunk_no: int, tagged_spans: list[dict]) -> tuple:
        if not previous_chunk_no:
            previous_chunk_no = 1

        if not previous_dict:
            previous_dict = {}

        isParagraph = False
        span_text = ""

        for span in tagged_spans:
            
            if span["tag"] == "heading":
                isParagraph = False
            elif span["tag"] == "paragraph":
                isParagraph = True
            
            if isParagraph:
                span_text += span["text"]
            else:
                if span_text:
                    previous_dict[f"chunk_{previous_chunk_no}"] = {
                        "paragraph": span_text,
                    }
                    span_text = ""
                    previous_chunk_no +=1
                previous_dict[f"chunk_{previous_chunk_no}"] = {
                    "heading": span["text"],
                }
                previous_chunk_no += 1

        return previous_dict, previous_chunk_no


    #TODO: Process chunks, add line breaks as necessary. 
    #TODO: Check. if there are any methods to derive the breaklines from PyMuPDF itself.
    #TODO: Convert the text to pdfs
                    
                
    '''@staticmethod
    def createDict(previous_dict: dict, previous_chunk_no: int, tagged_spans: list[dict]) -> tuple:

        if not previous_chunk_no:
            previous_chunk_no = 1

        if not previous_dict:
            previous_dict = {}

        isParagraph = False
        span_text = ""
        for span in tagged_spans:
            if "text" in span:
                if span["tag"] == "heading":
                    isParagraph = False
                    if span_text:
                        previous_dict[f"chunk_{previous_chunk_no}"] = {
                            "paragraph" : span_text,
                        }
                        previous_chunk_no += 1
                        span_text = ""
                    previous_dict[f"chunk_{previous_chunk_no}"] = {
                            "heading": span["text"],
                        }
                    previous_chunk_no += 1
                    
                elif span["tag"] == "paragraph":
                    isParagraph = True
                    span_text += span["text"]

        return previous_dict, previous_chunk_no'''
    


'''
def findCommonFontSize(self, blocks: list[dict]) -> int:

        font_sizes = []
        
        
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        font_sizes.append(round(span["size"]))

        if not font_sizes:
            return 0
        
        common_font_size = collections.Counter(font_sizes).most_common(1)[0][0]
        return common_font_size
    
    def findCommonFontColor(self, blocks: list[dict]) -> str:

        font_colours = []

        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        font_colours.append(span["color"])

        if not font_colours:
            return ""
        
        print(font_colours)
        
        common_font_color = collections.Counter(font_colours).most_common(1)[0][0]
        

    def firstSpanSize(self, blocks: list[dir]) -> float:

        #IMPORTANT: only after sorting
        first_span_size = round(blocks["blocks"][0]["lines"][0]["spans"][0]["size"])

        return first_span_size

    def firstSpanColor(self, blocks: list[dir]) -> str:

        #IMPORTANT: only after sorting
        first_span_color = blocks["blocks"][0]["lines"][0]["spans"][0]["color"]

        return first_span_color
    
    def getLargestSize(self, blocks: list[dir]):

        list_of_font_sizes= []

        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        list_of_font_sizes.append(round(span["size"]))

        if not list_of_font_sizes:
            return 0
    
        fontList = collections.Counter(list_of_font_sizes).most_common()
        largestFontSize = sorted(fontList, key= lambda item: item[0], reverse= False)[-1][0]
        return largestFontSize
'''