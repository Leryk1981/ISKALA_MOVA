
/**
 * Ukrainian Embroidery Pictogram Generator
 * Creates small embroidery patterns for tree nodes
 * Based on traditional Ukrainian vyshyvanka patterns
 */

class UkrainianEmbroideryGenerator {
    constructor() {
        this.colors = {
            red: '#bd1136',      // любов, захист
            black: '#1a0709',    // мудрість, земля
            white: '#ffffff',    // чистота, світло
            green: '#58a34a',    // природа, життя
            blue: '#2fa6c7',     // небо, вода
            yellow: '#feca32',   // сонце, тепло
            orange: '#ff6b35'    // енергія, радість
        };

        this.patterns = {
            // Traditional Ukrainian symbols
            'мова': [
                [0,1,1,1,0],
                [1,0,1,0,1],
                [1,1,1,1,1],
                [1,0,1,0,1],
                [0,1,1,1,0]
            ],
            'дім': [
                [0,1,1,1,0],
                [1,1,0,1,1],
                [1,0,0,0,1],
                [1,1,1,1,1],
                [1,0,0,0,1]
            ],
            'любов': [
                [0,1,0,1,0],
                [1,1,1,1,1],
                [1,1,1,1,1],
                [0,1,1,1,0],
                [0,0,1,0,0]
            ],
            'захист': [
                [1,0,1,0,1],
                [0,1,1,1,0],
                [1,1,1,1,1],
                [0,1,1,1,0],
                [1,0,1,0,1]
            ],
            'мудрість': [
                [1,1,1,1,1],
                [1,0,0,0,1],
                [1,0,1,0,1],
                [1,0,0,0,1],
                [1,1,1,1,1]
            ],
            'ріст': [
                [0,0,1,0,0],
                [0,1,1,1,0],
                [1,1,1,1,1],
                [0,1,1,1,0],
                [1,1,1,1,1]
            ],
            'гармонія': [
                [1,0,1,0,1],
                [0,1,0,1,0],
                [1,0,1,0,1],
                [0,1,0,1,0],
                [1,0,1,0,1]
            ],
            'сила': [
                [1,1,0,1,1],
                [1,0,1,0,1],
                [0,1,1,1,0],
                [1,0,1,0,1],
                [1,1,0,1,1]
            ]
        };
    }

    generatePictogram(text, colorScheme = 'traditional', size = 32) {
        const pattern = this.getPatternForText(text);
        const colors = this.getColorScheme(colorScheme);

        return {
            pattern: pattern,
            colors: colors,
            size: size,
            svg: this.createSVG(pattern, colors, size),
            dataURL: this.createDataURL(pattern, colors, size)
        };
    }

    getPatternForText(text) {
        // Simple mapping of text to patterns
        const textLower = text.toLowerCase();

        for (const [key, pattern] of Object.entries(this.patterns)) {
            if (textLower.includes(key)) {
                return pattern;
            }
        }

        // Generate unique pattern based on text hash
        return this.generatePatternFromText(text);
    }

    generatePatternFromText(text) {
        const hash = this.simpleHash(text);
        const size = 5;
        const pattern = [];

        for (let i = 0; i < size; i++) {
            pattern[i] = [];
            for (let j = 0; j < size; j++) {
                pattern[i][j] = (hash >> (i * size + j)) & 1;
            }
        }

        return pattern;
    }

    simpleHash(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32-bit integer
        }
        return Math.abs(hash);
    }

    getColorScheme(scheme) {
        const schemes = {
            traditional: [this.colors.red, this.colors.black, this.colors.white],
            nature: [this.colors.green, this.colors.blue, this.colors.yellow],
            warm: [this.colors.red, this.colors.orange, this.colors.yellow],
            cool: [this.colors.blue, this.colors.green, this.colors.white],
            monochrome: [this.colors.black, '#666666', '#cccccc']
        };

        return schemes[scheme] || schemes.traditional;
    }

    createSVG(pattern, colors, size) {
        const cellSize = Math.floor(size / pattern.length);
        const svgSize = cellSize * pattern.length;

        let svg = `<svg width="${svgSize}" height="${svgSize}" xmlns="http://www.w3.org/2000/svg">`;
        svg += `<rect width="100%" height="100%" fill="white"/>`;

        for (let i = 0; i < pattern.length; i++) {
            for (let j = 0; j < pattern[i].length; j++) {
                if (pattern[i][j] === 1) {
                    const color = colors[(i + j) % colors.length];
                    svg += `<rect x="${j * cellSize}" y="${i * cellSize}" `;
                    svg += `width="${cellSize}" height="${cellSize}" fill="${color}"/>`;
                }
            }
        }

        svg += '</svg>';
        return svg;
    }

    createDataURL(pattern, colors, size) {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');

        canvas.width = size;
        canvas.height = size;

        const cellSize = Math.floor(size / pattern.length);

        // White background
        ctx.fillStyle = 'white';
        ctx.fillRect(0, 0, size, size);

        // Draw pattern
        for (let i = 0; i < pattern.length; i++) {
            for (let j = 0; j < pattern[i].length; j++) {
                if (pattern[i][j] === 1) {
                    const color = colors[(i + j) % colors.length];
                    ctx.fillStyle = color;
                    ctx.fillRect(j * cellSize, i * cellSize, cellSize, cellSize);
                }
            }
        }

        return canvas.toDataURL();
    }

    // Integration with tree system
    createTreeNodePictogram(nodeData) {
        const { intention, context, color } = nodeData;

        return this.generatePictogram(
            intention || context || 'default',
            color || 'traditional',
            64
        );
    }

    // API for tree system
    getAvailablePatterns() {
        return Object.keys(this.patterns);
    }

    getAvailableColorSchemes() {
        return ['traditional', 'nature', 'warm', 'cool', 'monochrome'];
    }
}

// Export for use in tree system
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UkrainianEmbroideryGenerator;
}

// Browser global
if (typeof window !== 'undefined') {
    window.UkrainianEmbroideryGenerator = UkrainianEmbroideryGenerator;
}
