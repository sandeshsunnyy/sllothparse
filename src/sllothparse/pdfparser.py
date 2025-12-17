import collections
import re
from sllothparse.utilities import partition_data_based_on_item_idx

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

    @staticmethod
    def return_unique_styles(all_styles) -> list:
        return list(set(all_styles))
    
    def sortAndArrangeDistinctStyles(self, all_styles) -> tuple:
        distinct_styles = self.return_unique_styles(all_styles=all_styles)
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
        
        self.tag_map = tag_map
        self.redefine_tags(all_blocks=self.page_data)

    def create_single_tags(self, tuples: list[tuple], atr_idx: int):
        """
        Docstring for create_single_tags
        
        :param tuples: Description
        :type tuples: list[tuple]
        :param atr_idx: Description
        :type atr_idx: int (Give 0, 1 or 2 for sorting and partitioning with size, color and font respectively.)
        """
        partitions = partition_data_based_on_item_idx(data=tuples, item_idx=atr_idx)
        unique_among_partitions = []
        for i in range(len(partitions)):
            unique = list(set(partitions[i]))
            unique_among_partitions.append(unique)
        
        headings = {}
        for idx, unique in enumerate(unique_among_partitions, 1):
            tag = f'h{idx}'
            headings[tag] = unique
        
        headings_removed = dict([(value, key) for key, value in self.tag_map.items() if value[:1] != 'h'])
        list_transformed = dict([(key, [value]) for key, value in headings_removed.items()])
        new_tag_map = {**headings, **list_transformed}
        self.tag_map = new_tag_map


    def redefine_tags(self, all_blocks):
        headings = []
        for block in all_blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        size = span["size"]
                        color = span["color"]
                        font = span["font"]
            
                        style_tuple = (size, color, font)  
                        tag = self.tag_map[style_tuple] 
                        if tag[:1] == 'h':
                            headings.append(style_tuple)
                        else:
                            continue
        # We sort the styles according to key, then make partitions according to key. This would allow us to find common tuple in each size category and then assign values accordingly.
        self.create_single_tags(tuples=headings, atr_idx=0)
        

    @staticmethod
    def check_for_subheading(text: str, font_style: str = None) -> bool:

        delimiters = ('.', '?', '!', ';', ':')
        #regular expression for most common starting characters
        pattern = re.compile(r"^\s*((\d+(?:\.\d+)*)|[A-Za-z])[\.\)]")
        if pattern.match(text) and not text.strip().endswith(delimiters):
            return True
        elif not pattern.match(text):
            if font_style.__contains__("Bold") and not text.strip().endswith(delimiters):
                return True
            else:
                return False
        else: 
            return False
        
    def fetch_tag(self, style_tuple: tuple):

        for tag, tuples in self.tag_map.items():
            if style_tuple in tuples:
                return tag
            else:
                continue
        
        print("No style tuple entry found.")
        return None

    def tagLines(self, all_blocks):

        tagged_lines = []
        for block in all_blocks:
            if "lines" in block:
                for line in block["lines"]:
                    tuples = []
                    line_content = []
                    tags = []
                    for span in line["spans"]:
                        size = span["size"]
                        color = span["color"]
                        font = span["font"]
                        text = span["text"]
                        style_tuple = (size, color, font)                    
                        #Trying to get one complete line in an object. Basically, what we did is instead of assigning tags to individul spans, we generalized it and made it into a single line logic. 
                        #For bold and italics a different logic is needed. Like wraping the text in '*' or something
                        tag = self.fetch_tag(style_tuple=style_tuple)
                        if tag[:2] == "sh":
                            if not self.check_for_subheading(text=content, font_style=common_tuple[2]):
                                tag = "p"
                        tags.append(tag)
                        tuples.append(style_tuple)
                        line_content.append(text)
                    content = ' '.join(line_content)
                    #content += '\n'
                    common_tuple = self.getCommonStyleTuple(style_tuples=tuples)
                    common_tag = collections.Counter(tags).most_common(1)[0][0]
                    if common_tag[:2] == "sh":
                            if not self.check_for_subheading(text=content, font_style=common_tuple[2]):
                                common_tag = "p"
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
        '''for chunk in chunks.values():
            if chunk["content"].strip() and chunk["tag"][:2] == 'sh':
                print("start")
                print(f"\n{chunk["content"]}\n")
                print("end")'''
        return chunks

    def createSemanticChunks(self):
        anchor_tuple = self.larger + self.same + self.smaller
        anchor_tag = self.fetch_tag(style_tuple=anchor_tuple[0])
        reversed_list = list(self.chunks.keys())[::-1]
        all_semantic_chunks = {}
        semantic_chunks_no = 0
        same_topic = []
        current_semantic_chunk = {}
        for key in reversed_list:
            chunk = self.chunks[key]
            tag = chunk['tag']
            content = chunk['content']
            if not content.strip():
                continue
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
    
    def view_chunks(self):
        for chunk in self.all_semantic_chunks:
            print(f"\n{chunk}\n")
            print(self.all_semantic_chunks[chunk])
            print("\n")
    
    def get_only_paragraphs(self):

        all_paragraphs = ""
        for chunk_key in self.all_semantic_chunks:
            chunk = self.all_semantic_chunks[chunk_key]
        
            chunk_paragraph = chunk.get('p')
            all_paragraphs += chunk_paragraph

        return all_paragraphs