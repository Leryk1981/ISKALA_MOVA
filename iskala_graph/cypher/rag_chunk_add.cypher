// Додавання контекстного чанка для RAG
// Параметри: content, source, chunk_hash, embedding, keywords, language, metadata

MERGE (chunk:ContextChunk {chunk_hash: $chunk_hash})
ON CREATE SET 
    chunk.id = randomUUID(),
    chunk.content = $content,
    chunk.source = $source,
    chunk.embedding = $embedding,
    chunk.keywords = coalesce($keywords, []),
    chunk.language = coalesce($language, 'uk'),
    chunk.metadata = coalesce($metadata, {}),
    chunk.created_at = datetime(),
    chunk.updated_at = datetime(),
    chunk.usage_count = 0
ON MATCH SET 
    chunk.usage_count = chunk.usage_count + 1,
    chunk.updated_at = datetime()

// Зв'язуємо з відповідними намірами за ключовими словами
WITH chunk
OPTIONAL MATCH (i:Intent)
WHERE any(keyword IN chunk.keywords WHERE keyword IN i.keywords)

FOREACH(intent IN CASE WHEN i IS NOT NULL THEN [i] ELSE [] END | 
    MERGE (intent)-[:REFERENCES]->(chunk)
)

RETURN chunk.id as chunk_id,
       chunk.source as source,
       chunk.language as language,
       size(chunk.keywords) as keywords_count,
       chunk.usage_count as usage_count 