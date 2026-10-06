
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

model = SentenceTransformer('all-MiniLM-L6-v2')

sentences = [
    "The cat sits on the mat",       # 0
    "A kitten is sitting on a rug",  # 1
    "I love programming in Python"   # 2
]

embeddings = model.encode(sentences)

similarity_matrix = cos_sim(embeddings, embeddings)

print("Similarity Matrix:")
print(similarity_matrix)

print("\n--- Results ---")
print(f"Sentence 0 vs 1 similarity (cat/kitten): {similarity_matrix[0][1]:.4f}")
print(f"Sentence 0 vs 2 similarity (cat vs Python): {similarity_matrix[0][2]:.4f}")