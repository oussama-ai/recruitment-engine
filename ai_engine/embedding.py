from sentence_transformers import SentenceTransformer

class Embedder:
    def __init__(self):
        # Multilingual model is mandatory for Moroccan job markets (French/English)
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

    def encode(self, text):
        return self.model.encode(text).tolist()