// Створення або оновлення наміру в ISKALA MOVA
// Параметри: name, description, confidence, lang, category

MERGE (i:Intent {name: $name, lang: $lang})
ON CREATE SET 
    i.id = randomUUID(),
    i.description = $description,
    i.confidence = $confidence,
    i.category = $category,
    i.frequency = 1,
    i.success_rate = 0.0,
    i.created_at = datetime(),
    i.updated_at = datetime()
ON MATCH SET 
    i.description = coalesce($description, i.description),
    i.confidence = coalesce($confidence, i.confidence),
    i.category = coalesce($category, i.category),
    i.frequency = i.frequency + 1,
    i.updated_at = datetime()

RETURN i.id as intent_id, 
       i.name as name,
       i.frequency as frequency,
       i.created_at as created_at 