
/**
 * Embroidery-Tree Integration System
 * Connects Ukrainian embroidery patterns with tree nodes
 */

class EmbroideryTreeIntegration {
    constructor(embroideryGenerator, treeSystem) {
        this.embroidery = embroideryGenerator;
        this.tree = treeSystem;
        this.nodeEmbroideryMap = new Map();
    }

    // Add embroidery signature to tree node
    addEmbroiderySignature(nodeId, signatureData) {
        const {
            text,
            colorScheme,
            patternType,
            customPattern
        } = signatureData;

        const pictogram = this.embroidery.generatePictogram(
            text,
            colorScheme,
            64
        );

        const embroideryData = {
            nodeId: nodeId,
            signature: signatureData,
            pictogram: pictogram,
            created: new Date().toISOString(),
            updated: new Date().toISOString()
        };

        this.nodeEmbroideryMap.set(nodeId, embroideryData);

        // Update tree node with embroidery data
        this.updateTreeNode(nodeId, {
            embroidery: embroideryData
        });

        return embroideryData;
    }

    // Get embroidery for specific node
    getNodeEmbroidery(nodeId) {
        return this.nodeEmbroideryMap.get(nodeId);
    }

    // List available embroidery options
    getEmbroideryOptions() {
        return {
            patterns: this.embroidery.getAvailablePatterns(),
            colorSchemes: this.embroidery.getAvailableColorSchemes(),
            customPatterns: this.getCustomPatterns()
        };
    }

    // Create custom pattern from user input
    createCustomPattern(userInput) {
        return this.embroidery.generatePatternFromText(userInput);
    }

    // Generate preview for user selection
    generatePreview(text, colorScheme, patternType) {
        return this.embroidery.generatePictogram(text, colorScheme, 128);
    }

    // Batch update multiple nodes
    batchUpdateEmbroidery(updates) {
        const results = [];

        for (const update of updates) {
            try {
                const result = this.addEmbroiderySignature(
                    update.nodeId,
                    update.signature
                );
                results.push({ success: true, data: result });
            } catch (error) {
                results.push({ 
                    success: false, 
                    error: error.message,
                    nodeId: update.nodeId 
                });
            }
        }

        return results;
    }

    // Export embroidery data
    exportEmbroideryData() {
        const data = {
            version: '1.0',
            created: new Date().toISOString(),
            nodeEmbroideryMap: Object.fromEntries(this.nodeEmbroideryMap),
            totalNodes: this.nodeEmbroideryMap.size
        };

        return JSON.stringify(data, null, 2);
    }

    // Import embroidery data
    importEmbroideryData(jsonData) {
        const data = JSON.parse(jsonData);

        for (const [nodeId, embroideryData] of Object.entries(data.nodeEmbroideryMap)) {
            this.nodeEmbroideryMap.set(nodeId, embroideryData);
        }

        return {
            imported: Object.keys(data.nodeEmbroideryMap).length,
            total: this.nodeEmbroideryMap.size
        };
    }

    // Get statistics
    getStatistics() {
        const stats = {
            totalNodes: this.nodeEmbroideryMap.size,
            colorSchemes: {},
            patterns: {},
            recentUpdates: []
        };

        for (const [nodeId, data] of this.nodeEmbroideryMap) {
            const { signature } = data;

            stats.colorSchemes[signature.colorScheme] = 
                (stats.colorSchemes[signature.colorScheme] || 0) + 1;

            stats.patterns[signature.patternType] = 
                (stats.patterns[signature.patternType] || 0) + 1;
        }

        // Get recent updates
        const sorted = Array.from(this.nodeEmbroideryMap.values())
            .sort((a, b) => new Date(b.updated) - new Date(a.updated))
            .slice(0, 10);

        stats.recentUpdates = sorted;

        return stats;
    }

    // Helper methods
    updateTreeNode(nodeId, data) {
        // This would integrate with your tree system
        console.log(`Updating tree node ${nodeId} with embroidery data:`, data);
    }

    getCustomPatterns() {
        return [
            'geometric',
            'floral',
            'symbolic',
            'abstract'
        ];
    }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EmbroideryTreeIntegration;
}

if (typeof window !== 'undefined') {
    window.EmbroideryTreeIntegration = EmbroideryTreeIntegration;
}
