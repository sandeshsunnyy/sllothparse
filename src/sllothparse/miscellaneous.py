'''
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

    return previous_dict, previous_chunk_no'''


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