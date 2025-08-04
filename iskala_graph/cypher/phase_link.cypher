// Створення зв'язку між фазами мислення
// Параметри: from_phase, to_phase, relation_type, weight

MATCH (from:Phase {name: $from_phase})
MATCH (to:Phase {name: $to_phase})

MERGE (from)-[r:LEADS_TO]->(to)
ON CREATE SET 
    r.relation_type = coalesce($relation_type, 'LEADS_TO'),
    r.weight = coalesce($weight, 1.0),
    r.created_at = datetime(),
    r.usage_count = 1
ON MATCH SET 
    r.weight = coalesce($weight, r.weight),
    r.usage_count = r.usage_count + 1,
    r.updated_at = datetime()

RETURN from.name as from_phase, 
       to.name as to_phase,
       r.weight as weight,
       r.usage_count as usage_count 