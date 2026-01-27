import hashlib
import os
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, text
from app.models import NoteEmbedding, BlindIndex, Note
from app.core.security import get_blind_index
import openai

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

class SearchService:
    def __init__(self, db: Session):
        self.db = db

    def _get_embedding(self, text: str) -> List[float]:
        """Generate embedding using OpenAI"""
        if not text:
            return []
        try:
            response = openai.embeddings.create(
                input=text,
                model="text-embedding-3-small"
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []

    def _tokenize_and_hash(self, text: str) -> List[str]:
        """Split text into words and hash them for Blind Index"""
        if not text:
            return []
        # Simple whitespace tokenization, cleaning punctuation
        words = set(text.lower().split()) # Unique words
        hashes = []
        for word in words:
            # Clean word
            clean_word = "".join(c for c in word if c.isalnum())
            if clean_word:
                # Reuse get_blind_index from security (SHA256)
                hashes.append(get_blind_index(clean_word))
        return hashes

    async def index_note(self, note_id: UUID, content: str):
        """Update Embeddings and Blind Index for a note"""
        # 1. Generate & Save Vector
        vector = self._get_embedding(content)
        if vector:
            # Check if exists
            existing_emb = await self.db.execute(select(NoteEmbedding).filter(NoteEmbedding.note_id == note_id))
            emb_obj = existing_emb.scalars().first()
            if emb_obj:
               emb_obj.vector = vector
            else:
               new_emb = NoteEmbedding(note_id=note_id, vector=vector)
               self.db.add(new_emb)
        
        # 2. Generate & Save Blind Indexes
        # Delete old indexes for this note
        await self.db.execute(text(f"DELETE FROM blind_indexes WHERE note_id = '{note_id}'"))
        
        term_hashes = self._tokenize_and_hash(content)
        for h in term_hashes:
            self.db.add(BlindIndex(note_id=note_id, term_hash=h))
            
        await self.db.commit()

    async def search_notes(self, query: str, limit: int = 10) -> List[UUID]:
        """
        Hybrid Search:
        1. Keyword Match (Blind Index)
        2. Semantic Match (Vector Cosine Similarity)
        Returns list of unique Note IDs.
        """
        note_ids = set()

        # 1. Keyword Search
        query_hashes = self._tokenize_and_hash(query)
        if query_hashes:
            # Find notes that contain ANY of the query terms
            # Note: This is a loose match. Ideally we want matches that overlap most.
            # For MVP, just finding presence is fine.
            stmt = select(BlindIndex.note_id).filter(BlindIndex.term_hash.in_(query_hashes))
            result = await self.db.execute(stmt)
            keyword_matches = result.scalars().all()
            for nid in keyword_matches:
                note_ids.add(nid)

        # 2. Semantic Search
        vector = self._get_embedding(query)
        if vector:
            # Using pgvector cosine distance definition (<-> is Euclidean, <=> is Cosine)
            # SQLAlchemy pgvector helper usage: NoteEmbedding.vector.l2_distance(vector) etc.
            # We want cosine distance usually for embeddings.
            # Note: 1 - cosine_similarity = cosine_distance. 
            # We want smallest distance.
            stmt = select(NoteEmbedding.note_id).order_by(NoteEmbedding.vector.cosine_distance(vector)).limit(limit)
            result = await self.db.execute(stmt)
            semantic_matches = result.scalars().all()
            for nid in semantic_matches:
                note_ids.add(nid)
        
        return list(note_ids)
