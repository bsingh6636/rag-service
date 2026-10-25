import tiktoken
from markdown_it import MarkdownIt

tokenizer = tiktoken.get_encoding("cl100k_base")

def split_sections ( text : str) -> list[str] :
    lines = text.splitlines ( keepends = True )
    tokens = MarkdownIt().parse(text)

    boundaries = [0]

    for token in tokens :
        if token.type == 'heading_open' and token.map is not None :
            boundaries.append(token.map[0])
    
    boundaries.append(len(lines))
    boundaries = sorted(set(boundaries))

    sections = []

    for start, end in zip(boundaries , boundaries[1:]):
        section = "".join(lines[start:end]).strip()

        if section :
            sections.append(section)

    return sections

def count_tokens ( text : str ) -> int : 
    return len(tokenizer.encode_ordinary(text))  

def chunk_text ( text : str , max_tokens : int = 800 , overlap : int = 100 ) -> list[str] :
    if max_tokens <= 0 or not 0 <= overlap < max_tokens :
        raise ValueError("Require max_tokens > 0 and 0 <= overlap < max_tokens")

    chunks = []

    for section in split_sections(text) :
        token_ids = tokenizer.encode_ordinary(section)
        start = 0

        while start < len(token_ids) :
            end = min ( start + max_tokens , len ( token_ids ))
            chunk = tokenizer.decode(token_ids[start:end])
            chunks.append(chunk)

            if end == len(token_ids):
                break
            
            start = end - overlap

    return chunks