from langchain_text_splitters import RecursiveCharacterTextSplitter
# SPLIT RESUME INTO CHUNK
def split_document(text):
    if not text:
        return []
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_text(text)
    return chunks