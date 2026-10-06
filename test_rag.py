# import chromadb
# from pypdf import PdfReader

# def chunk_text(text, chunk_size=500, overlap=50):
#     chunks = []
#     start = 0
#     while start < len(text):
#         end = start + chunk_size
#         chunks.append(text[start:end])
#         start += chunk_size - overlap
#     return chunks

# # Step 1: Read PDF and create chunks
# reader = PdfReader("test.pdf")
# full_text = ""
# for page in reader.pages:
#     full_text += page.extract_text() + "\n"

# chunks = chunk_text(full_text, chunk_size=500, overlap=50)
# print(f"Created {len(chunks)} chunks from the PDF")

# # Step 2: Set up ChromaDB (local, file-based vector database)
# chroma_client = chromadb.PersistentClient(path="./chroma_db")

# # Create (or get existing) a collection — like a "table" for vectors
# collection = chroma_client.get_or_create_collection(name="handbook")

# # Step 3: Add chunks to the collection
# # ChromaDB automatically creates embeddings for us using a default model
# collection.add(
#     documents=chunks,
#     ids=[f"chunk_{i}" for i in range(len(chunks))]
# )
# print("All chunks saved to ChromaDB")

# # Step 4: Test with a question
# query = "What is the warranty policy?"
# results = collection.query(
#     query_texts=[query],
#     n_results=2  # get the top 2 most relevant chunks
# )

# print(f"\nQuery: {query}")
# print("\nMost relevant chunks found:")
# for i, doc in enumerate(results['documents'][0]):
#     print(f"\n--- Match {i+1} ---")
#     print(doc)



# step:2



import os
from dotenv import load_dotenv
from groq import Groq
import chromadb
from pypdf import PdfReader

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

# Step 1: Read PDF and create chunks
reader = PdfReader("test.pdf")
full_text = ""
for page in reader.pages:
    full_text += page.extract_text() + "\n"

chunks = chunk_text(full_text, chunk_size=500, overlap=50)
print(f"Created {len(chunks)} chunks from the PDF")

# Step 2: Set up ChromaDB (local, file-based vector database)
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="handbook")

# Step 3: Add chunks to the collection
collection.add(
    documents=chunks,
    ids=[f"chunk_{i}" for i in range(len(chunks))]
)
print("All chunks saved to ChromaDB")

# Step 4: Query for the most relevant chunks
query = "What is the warranty policy?"
results = collection.query(
    query_texts=[query],
    n_results=2
)

print(f"\nQuery: {query}")
print("\nMost relevant chunks found:")
for i, doc in enumerate(results['documents'][0]):
    print(f"\n--- Match {i+1} ---")
    print(doc)

# Step 5: Generate a natural-language answer using the retrieved context
context = "\n\n".join(results['documents'][0])

prompt = f"""Answer the question based only on the context below. If the answer is not in the context, say "I don't have that information."

Context:
{context}

Question: {query}

Answer:"""

response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.3
)

print("\n--- AI Answer (based on document) ---")
print(response.choices[0].message.content)