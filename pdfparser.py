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
    
    @staticmethod
    def getCommonStyleTuple(style_tuples: list[tuple]):
        return collections.Counter(style_tuples).most_common(1)[0][0]
    
    def getMostCommonStyleTuple(self, all_styles:list[tuple]):
        self.most_common = self.getCommonStyleTuple(style_tuples=all_styles) # do something for heading and sub-headings (quick-thought: count-based?)

    
    def sortAndArrangeDistinctStyles(self, all_styles) -> tuple:
        distinct_styles = list(set(all_styles))
        #check for same font over all fonts if it is same fonts then a different logic has to be font. 
        self.sorted_styles_on_size = sorted(distinct_styles, key= lambda item: (item[0], item[1]), reverse=True)
        #Even after sorting if it is the same size then we should look for other ways to find semantics.
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

        self.larger, self.same, self.smaller = larger, same, smaller

        return larger, same, smaller
        
    def getCountsOfStyles(self, all_styles):
        counts = collections.Counter(all_styles)
        style_to_count = [(style, counts[style]) for style in self.sorted_styles_on_size]
        print(sorted(style_to_count, key=lambda item: item[1], reverse=True))

        #try with manual method, if its not that good, might have to resort to LLM-based semantic analysis. The key is not to overload the LLM, but ask it why the style tuples are used. 
    def assignTagsToStyles(self): # check if the larger list or the smaller list is empty, based on that we need to decide whether to assign subheadings. 
        tag_map = {}
        if self.larger:
            for i, tuple in enumerate(self.larger, 1):
                tag_map[tuple] = f"h{i}"
        
            for i, tuple in enumerate(self.same, 1):
                if tuple == self.most_common:
                    tag_map[tuple] = "p"
                else:
                    tag_map[tuple] = f"sh{i}"
            
            for i, tuple in enumerate(self.smaller, 1):
                tag_map[tuple] = "p"
        else:
            for i, tuple in enumerate(self.same, 1):
                if tuple == self.most_common:
                    tag_map[tuple] = "p"
                else:
                    tag_map[tuple] = f"h{i}"
            
            for i, tuple in enumerate(self.smaller, 1):
                tag_map[tuple] = "p"
        
        print(tag_map)

        self.tag_map = tag_map

    @staticmethod
    def check_for_subheading(text: str) -> bool:

        #regular expression for most common starting characters
        pattern = re.compile(r"^\s*((\d+(?:\.\d+)*)|[A-Za-z])[\.\)]")
        if pattern.match(text):
            return True
        elif not pattern.match(text) and text.endswith("."):
            return True
        else: 
            return False


    def tagLines(self, all_blocks):

        tagged_lines = []
        for block in all_blocks:
            if "lines" in block:
                for line in block["lines"]:
                    tuples = []
                    line_content = []
                    for span in line["spans"]:
                        size = span["size"]
                        color = span["color"]
                        font = span["font"]
                        text = span["text"]
                        style_tuple = (size, color, font)
                        tag = self.tag_map[style_tuple]
                        if tag[:2] == "sh":
                            if not self.check_for_subheading(text=text):
                                tag = "p"
                        #Tryning to get one complete line in an object. Basically, what we did is instead of assigning tags to individul spans, we generalized it and made it into a single line logic. 
                        #For bold and italics a different logic is needed. Like wraping the text in '*' or something
                        tuples.append(style_tuple)
                        line_content.append(text)
                    content = ' '.join(line_content)
                    content += '\n'
                    common_tuple = self.getCommonStyleTuple(style_tuples=tuples)
                    common_tag = self.tag_map[common_tuple]
                    line_object = {
                        "tag" : common_tag,
                        "content": content,
                        "style_tuple": common_tuple
                    }
                    tagged_lines.append(line_object)
        self.tagged_lines = tagged_lines
        return tagged_lines
                        
                        
    def createTaggedChunks(self):
        paragraph = ""
        chunks = {}
        chunk_no = 0
        for span_object in self.tagged_lines:
            current_tag = span_object["tag"]
            if current_tag[0] == 'h' or current_tag[:2] == 'sh':
                if paragraph:
                    chunk_name = f'chunk {chunk_no}'
                    chunks[chunk_name] = {
                        'tag' : 'p',
                        'content' : paragraph
                        }
                    chunk_no += 1
                    paragraph = ""

                chunk_name = f'chunk {chunk_no}'
                chunks[chunk_name] = {
                    'tag' : current_tag,
                    'content': span_object["content"]
                }
                chunk_no +=1
                paragraph = ""
            else:
                paragraph += span_object["content"]
        chunk_name = f'chunk {chunk_no}'
        chunks[chunk_name] = {
            'tag' : current_tag,
            'content' : paragraph
            }
        self.chunks = chunks
        return chunks

    def createSemanticChunks(self):
        anchor_tuple = self.larger + self.same + self.smaller
        anchor_tag = self.tag_map[anchor_tuple[0]]
        reversed_list = list(self.chunks.keys())[::-1]
        all_semantic_chunks = {}
        semantic_chunks_no = 0
        same_topic = []
        current_semantic_chunk = {}
        for key in reversed_list:
            chunk = self.chunks[key]
            tag = chunk['tag']
            content = chunk['content']
            if tag == 'p':
                if current_semantic_chunk:
                    same_topic.append(current_semantic_chunk)
                    current_semantic_chunk = {}
                    current_semantic_chunk[tag] = content
                else:
                    current_semantic_chunk[tag] = content
            elif tag[:2] == 'sh':
                if not current_semantic_chunk:
                    current_semantic_chunk[tag] = content
                else:
                    current_semantic_chunk[tag] = content
            elif tag == anchor_tag:
                # for previous chunks
                if same_topic:
                    for chunk in same_topic:
                        chunk[tag] = content
                    for chunk in same_topic:
                        key = f"Chunk {semantic_chunks_no}"
                        all_semantic_chunks[key] = chunk
                        same_topic = []
                        semantic_chunks_no += 1
                    # for current chunk
                    key = f"Chunk {semantic_chunks_no}" 
                    current_semantic_chunk[tag] = content
                    all_semantic_chunks[key] = current_semantic_chunk
                    current_semantic_chunk = {}
                    semantic_chunks_no +=1
                else: 
                    if current_semantic_chunk:
                        current_semantic_chunk[tag] = content
                        key = f"Chunk {semantic_chunks_no}"
                        all_semantic_chunks[key] = current_semantic_chunk
                        current_semantic_chunk = {}
                        semantic_chunks_no += 1
                    else:
                        current_semantic_chunk[tag] = content

            elif tag[:1] == 'h':
                if not current_semantic_chunk:
                    current_semantic_chunk[tag] = content
                else:
                    current_semantic_chunk[tag] = content
        
        if same_topic:
            print("same topic exists")
            for chunk in same_topic:
                key = f"Chunk {semantic_chunks_no}"
                all_semantic_chunks[key] = chunk
                current_semantic_chunk = {}
                same_topic = []
                semantic_chunks_no += 1
        if current_semantic_chunk:
            print('last chunk')
            key = f"Chunk {semantic_chunks_no}"
            all_semantic_chunks[key] = current_semantic_chunk
        
        self.all_semantic_chunks = all_semantic_chunks
        return all_semantic_chunks