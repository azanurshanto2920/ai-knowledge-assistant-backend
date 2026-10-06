

from pypdf import PdfReader

def chunk_text(text, chunk_size=500, overlap=50):
    """
    Splits a long text into overlapping chunks.
    chunk_size: how many characters per chunk
    overlap: how many characters repeat between chunks (keeps context connected)
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

# Read the PDF
reader = PdfReader("test.pdf")

full_text = ""
for page in reader.pages:
    full_text += page.extract_text() + "\n"

# Split into chunks
chunks = chunk_text(full_text, chunk_size=500, overlap=50)

print(f"Total chunks created: {len(chunks)}")
print("\n--- Chunk 1 ---")
print(chunks[0])
print("\n--- Chunk 2 ---")
print(chunks[1])