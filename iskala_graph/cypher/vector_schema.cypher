-- 🌍 ISKALA MOVA Neo4j Vector Schema
-- Enterprise-grade vector search infrastructure with multilingual support
-- ====================================================================

-- Drop existing indexes if they exist (for development)
DROP VECTOR INDEX chunk_embedding_idx IF EXISTS;
DROP INDEX chunk_hash_idx IF EXISTS;
DROP INDEX chunk_lang_idx IF EXISTS;
DROP FULLTEXT INDEX chunk_content_idx IF EXISTS;
DROP INDEX intent_name_idx IF EXISTS;
DROP INDEX phase_name_idx IF EXISTS;

-- ==============================
-- 🧠 VECTOR INDEXES FOR SEMANTIC SEARCH
-- ==============================

-- Primary vector index for 384-dimensional embeddings (sentence-transformers all-MiniLM-L6-v2)
CREATE VECTOR INDEX chunk_embedding_idx IF NOT EXISTS
FOR (c:ContextChunk) ON (c.embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 384,
    `vector.similarity_function`: 'cosine'
  }
};

-- ==============================
-- 📊 PERFORMANCE INDEXES
-- ==============================

-- Hash-based unique identifier index  
CREATE INDEX chunk_hash_idx IF NOT EXISTS
FOR (c:ContextChunk) ON (c.chunk_hash);

-- Language filtering index (critical for multilingual search)
CREATE INDEX chunk_lang_idx IF NOT EXISTS  
FOR (c:ContextChunk) ON (c.language);

-- Source document index
CREATE INDEX chunk_source_idx IF NOT EXISTS
FOR (c:ContextChunk) ON (c.source_doc);

-- Position index for chunk ordering
CREATE INDEX chunk_position_idx IF NOT EXISTS
FOR (c:ContextChunk) ON (c.position);

-- Confidence score index for quality filtering
CREATE INDEX chunk_confidence_idx IF NOT EXISTS
FOR (c:ContextChunk) ON (c.confidence);

-- ==============================
-- 🔍 FULL-TEXT SEARCH INDEXES
-- ==============================

-- Full-text search for content (backup search method)
CREATE FULLTEXT INDEX chunk_content_idx IF NOT EXISTS
FOR (c:ContextChunk) ON EACH [c.content]
OPTIONS {
  indexConfig: {
    `fulltext.analyzer`: 'standard',
    `fulltext.eventually_consistent`: true
  }
};

-- ==============================
-- 🎯 INTENT & PHASE INDEXES
-- ==============================

-- Intent name index for graph traversal
CREATE INDEX intent_name_idx IF NOT EXISTS
FOR (i:Intent) ON (i.name);

-- Intent confidence index
CREATE INDEX intent_confidence_idx IF NOT EXISTS
FOR (i:Intent) ON (i.confidence);

-- Phase name index
CREATE INDEX phase_name_idx IF NOT EXISTS
FOR (p:Phase) ON (p.name);

-- ==============================
-- 👤 USER & SESSION INDEXES
-- ==============================

-- User ID index for personalization
CREATE INDEX user_id_idx IF NOT EXISTS
FOR (u:User) ON (u.user_id);

-- Session timestamp index
CREATE INDEX session_timestamp_idx IF NOT EXISTS
FOR (s:Session) ON (s.created_at);

-- ==============================
-- 🔗 RELATIONSHIP INDEXES
-- ==============================

-- Relationship type index for graph traversal optimization
CREATE INDEX rel_type_idx IF NOT EXISTS
FOR ()-[r]-() ON (type(r));

-- ==============================
-- 📈 CONSTRAINTS FOR DATA INTEGRITY
-- ==============================

-- Unique constraint on chunk hash
CREATE CONSTRAINT chunk_hash_unique IF NOT EXISTS
FOR (c:ContextChunk) REQUIRE c.chunk_hash IS UNIQUE;

-- Unique constraint on intent name
CREATE CONSTRAINT intent_name_unique IF NOT EXISTS
FOR (i:Intent) REQUIRE i.name IS UNIQUE;

-- Unique constraint on user ID
CREATE CONSTRAINT user_id_unique IF NOT EXISTS
FOR (u:User) REQUIRE u.user_id IS UNIQUE;

-- ==============================
-- ✅ VERIFICATION QUERIES
-- ==============================

-- Query to verify vector index creation
-- CALL db.indexes() YIELD name, type, labelsOrTypes, properties, state
-- WHERE name = 'chunk_embedding_idx' RETURN *;

-- Query to check vector index configuration
-- CALL db.index.vector.queryNodes('chunk_embedding_idx', 1, [0.1, 0.2, 0.3]) YIELD node, score;

-- Sample data insertion for testing:
/*
MERGE (c:ContextChunk {
  chunk_hash: 'test_chunk_001',
  content: 'Test Ukrainian content: Україна розвиває штучний інтелект',
  language: 'uk',
  source_doc: 'test.txt',
  position: 0,
  confidence: 0.95,
  embedding: [0.1, 0.2, 0.3, ..., 0.384],  // 384-dimensional vector
  metadata: {
    word_count: 7,
    sentence_count: 1,
    processing_method: 'multilingual_enhanced'
  },
  created_at: datetime(),
  updated_at: datetime()
});

MERGE (i:Intent {
  name: 'ai_development',
  description: 'Artificial Intelligence Development',
  confidence: 0.8,
  lang: 'uk',
  created_at: datetime()
});

MERGE (c)-[:DETAILS]->(i);
*/

-- ==============================
-- 📊 PERFORMANCE MONITORING QUERIES
-- ==============================

-- Index usage statistics
-- CALL db.stats.retrieve('INDEX_USAGE');

-- Vector search performance test
-- CALL db.index.vector.queryNodes('chunk_embedding_idx', 10, $query_vector) 
-- YIELD node, score
-- RETURN node.content, node.language, score
-- ORDER BY score DESC;

-- Language distribution analysis
-- MATCH (c:ContextChunk)
-- RETURN c.language, count(*) as chunk_count
-- ORDER BY chunk_count DESC;

-- ==============================
-- 🔧 MAINTENANCE QUERIES
-- ==============================

-- Rebuild vector index if needed
-- CALL db.index.vector.drop('chunk_embedding_idx');
-- CREATE VECTOR INDEX chunk_embedding_idx FOR (c:ContextChunk) ON (c.embedding) 
-- OPTIONS {indexConfig: {`vector.dimensions`: 384, `vector.similarity_function`: 'cosine'}};

-- Clear test data
-- MATCH (c:ContextChunk {chunk_hash: 'test_chunk_001'}) DETACH DELETE c;

-- ==============================
-- ✅ SCHEMA VALIDATION
-- ==============================

-- Verify all indexes are created
CALL db.indexes() YIELD name, type, state
WHERE state = 'ONLINE'
RETURN name, type, state
ORDER BY name; 