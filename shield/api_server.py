"""
ISKALA API Server
API endpoints for the Ukrainian embroidery interface
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mova_tree_creator import plant_mova_seed

app = FastAPI(
    title="ISKALA Tree Creation API",
    description="API для створення дерев сенсів у просторі ISKALA",
    version="1.0.0"
)

# Enable CORS for the web interface
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TreeRequest(BaseModel):
    intention: str
    context: Dict[str, Any]

@app.post("/api/create-tree")
async def create_tree(request: TreeRequest):
    """Create a new tree from intention"""
    try:
        tree_id = plant_mova_seed(
            intention=request.intention,
            context=request.context
        )

        return {
            "success": True,
            "tree_id": tree_id,
            "message": "Дерево успішно створено",
            "ceremony": "first_seed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ISKALA Tree API"}

@app.get("/api/trees")
async def list_trees():
    """List all trees"""
    from mova_tree_creator import tree_creator
    trees = tree_creator.list_trees()
    return {"trees": trees, "count": len(trees)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
