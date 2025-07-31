# 🌺 Ukrainian Embroidery Tree System

## Overview
Complete system for adding Ukrainian embroidery signatures to tree nodes in ISKALA. Users can create custom vyshyvanka patterns for their intentions and meanings.

## Components

### 1. Embroidery Generator (`embroidery_generator.js`)
- Creates traditional Ukrainian embroidery patterns
- Supports multiple color schemes with cultural significance
- Generates SVG and Canvas patterns
- Custom pattern generation from text

### 2. Integration System (`integration.js`)
- Connects embroidery with tree nodes
- Manages user signatures
- Provides API for frontend
- Handles data persistence

### 3. User Interface (`index.html`)
- Interactive web interface
- Real-time preview
- Pattern selection
- Color scheme options
- Statistics and export

### 4. Python Wrapper (`embroidery_wrapper.py`)
- Backend integration
- Data management
- Export/import functionality

## Usage

### Web Interface
1. Open `index.html` in browser
2. Select tree node ID
3. Enter intention text
4. Choose color scheme and pattern
5. Preview and save

### API Usage
```javascript
// Create embroidery signature
const signature = {
    text: 'створити гармонію',
    colorScheme: 'traditional',
    patternType: 'гармонія'
};

const result = integration.addEmbroiderySignature('node-001', signature);
```

### Color Schemes
- **Traditional**: Red, black, white (love, protection, purity)
- **Nature**: Green, blue, yellow (nature, sky, sun)
- **Warm**: Red, orange, yellow (energy, joy, warmth)
- **Cool**: Blue, green, white (calm, peace, clarity)
- **Monochrome**: Black, gray, white (simplicity, elegance)

### Available Patterns
- мова (language/communication)
- дім (home/security)
- любов (love)
- захист (protection)
- мудрість (wisdom)
- ріст (growth)
- гармонія (harmony)
- сила (strength)

## Integration with Tree System

### Adding to Tree Node
```python
from embroidery_wrapper import EmbroideryTreeWrapper

wrapper = EmbroideryTreeWrapper()
signature = wrapper.add_signature("tree-node-123", {
    'text': 'моя мета',
    'color_scheme': 'traditional',
    'pattern_type': 'мова'
})
```

### Getting Node Embroidery
```python
embroidery = wrapper.get_signature("tree-node-123")
```

## Files Structure
```
embroidery_system/
├── embroidery_generator.js    # Core pattern generator
├── integration.js            # Tree integration
├── api.js                    # REST API endpoints
├── index.html                # User interface
├── embroidery_wrapper.py     # Python backend
└── README.md                 # This file
```

## Quick Start
1. Open `index.html` in browser
2. Select a tree node
3. Create your embroidery signature
4. Save to integrate with tree

## Cultural Significance
Each pattern and color carries deep Ukrainian cultural meaning, making each tree node a living piece of cultural heritage.
