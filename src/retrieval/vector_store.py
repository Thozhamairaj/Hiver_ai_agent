import chromadb
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer

class SupportVectorStore:
    """
    RAG Vector Store using ChromaDB and Sentence Transformers.
    """
    def __init__(
        self,
        persist_dir: str = "chroma_db",
        collection_name: str = "apple_support_conversations",
        model_name: str = "all-MiniLM-L6-v2"
    ):
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.collection_name = collection_name
        self.model_name = model_name
        
        # Initialize embedding model
        self.encoder = SentenceTransformer(self.model_name)
        
        # Initialize ChromaDB persistent client
        self.client = chromadb.PersistentClient(path=str(self.persist_dir))
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def index_conversations(self, conversations: List[Dict[str, Any]], intent_classifier=None):
        """
        Embeds and indexes historical support conversations into ChromaDB.
        """
        if not conversations:
            print("No conversations provided for indexing.")
            return

        documents = []
        metadatas = []
        ids = []
        embeddings = []

        for conv in conversations:
            cid = str(conv["conversation_id"])
            cust_text = conv.get("initial_customer_message") or conv.get("all_customer_messages", "")
            brand_reply = conv.get("brand_reply", "")
            brand = conv.get("brand", "AppleSupport")
            created_at = conv.get("created_at", "")
            
            # Predict intent if classifier provided
            intent = conv.get("intent", "other")
            if intent_classifier and intent == "other":
                res = intent_classifier.predict(cust_text)
                intent = res["intent"]

            # Document text indexed for retrieval (Customer issue + context)
            doc_text = f"Customer Query: {cust_text}\nBrand Reply: {brand_reply}"
            
            documents.append(doc_text)
            metadatas.append({
                "conversation_id": cid,
                "brand": brand,
                "intent": intent,
                "customer_message": cust_text,
                "brand_reply": brand_reply,
                "created_at": created_at,
                "source": "twcs_historical"
            })
            ids.append(f"conv_{cid}")

        print(f"Generating embeddings for {len(documents)} conversations...")
        raw_embeddings = self.encoder.encode(documents, show_progress_bar=False, convert_to_numpy=True)

        # Normalize embeddings for cosine distance
        norms = np.linalg.norm(raw_embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        normalized_embeddings = (raw_embeddings / norms).tolist()

        # Add to ChromaDB
        self.collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=normalized_embeddings
        )
        print(f"Indexed {len(documents)} conversations in ChromaDB collection '{self.collection_name}'.")

    def search(
        self,
        query_text: str,
        top_k: int = 5,
        brand_filter: Optional[str] = "AppleSupport"
    ) -> List[Dict[str, Any]]:
        """
        Searches ChromaDB for top-K historical conversations relevant to query_text.
        """
        if self.collection.count() == 0:
            return []

        # Embed query
        query_emb = self.encoder.encode([query_text], convert_to_numpy=True)
        norm = np.linalg.norm(query_emb)
        if norm > 0:
            query_emb = query_emb / norm
        query_emb_list = query_emb.tolist()

        where_clause = None
        if brand_filter:
            where_clause = {"brand": brand_filter}

        results = self.collection.query(
            query_embeddings=query_emb_list,
            n_results=min(top_k, self.collection.count()),
            where=where_clause
        )

        retrieved = []
        if results and "metadatas" in results and results["metadatas"]:
            metas = results["metadatas"][0]
            distances = results.get("distances", [[]])[0]
            docs = results.get("documents", [[]])[0]

            for i in range(len(metas)):
                meta = metas[i]
                dist = distances[i] if i < len(distances) else 0.5
                # Convert cosine distance to similarity score
                similarity = max(0.0, min(1.0, float(1.0 - dist)))
                
                retrieved.append({
                    "conversation_id": meta.get("conversation_id"),
                    "brand": meta.get("brand"),
                    "intent": meta.get("intent"),
                    "customer_message": meta.get("customer_message"),
                    "brand_reply": meta.get("brand_reply"),
                    "similarity_score": round(similarity, 4),
                    "document_text": docs[i] if i < len(docs) else ""
                })

        return retrieved
