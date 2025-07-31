
/**
 * Embroidery API Endpoints
 * REST API for managing embroidery signatures
 */

const express = require('express');
const router = express.Router();

class EmbroideryAPI {
    constructor(integration) {
        this.integration = integration;
    }

    setupRoutes() {
        // Get embroidery options
        router.get('/options', (req, res) => {
            try {
                const options = this.integration.getEmbroideryOptions();
                res.json({ success: true, data: options });
            } catch (error) {
                res.status(500).json({ success: false, error: error.message });
            }
        });

        // Get node embroidery
        router.get('/node/:nodeId', (req, res) => {
            try {
                const { nodeId } = req.params;
                const embroidery = this.integration.getNodeEmbroidery(nodeId);

                if (!embroidery) {
                    return res.status(404).json({ 
                        success: false, 
                        error: 'Embroidery not found' 
                    });
                }

                res.json({ success: true, data: embroidery });
            } catch (error) {
                res.status(500).json({ success: false, error: error.message });
            }
        });

        // Add embroidery to node
        router.post('/node/:nodeId', (req, res) => {
            try {
                const { nodeId } = req.params;
                const signatureData = req.body;

                const result = this.integration.addEmbroiderySignature(
                    nodeId, 
                    signatureData
                );

                res.json({ success: true, data: result });
            } catch (error) {
                res.status(500).json({ success: false, error: error.message });
            }
        });

        // Generate preview
        router.post('/preview', (req, res) => {
            try {
                const { text, colorScheme, patternType } = req.body;

                const preview = this.integration.generatePreview(
                    text, 
                    colorScheme, 
                    patternType
                );

                res.json({ success: true, data: preview });
            } catch (error) {
                res.status(500).json({ success: false, error: error.message });
            }
        });

        // Get statistics
        router.get('/stats', (req, res) => {
            try {
                const stats = this.integration.getStatistics();
                res.json({ success: true, data: stats });
            } catch (error) {
                res.status(500).json({ success: false, error: error.message });
            }
        });

        // Export data
        router.get('/export', (req, res) => {
            try {
                const data = this.integration.exportEmbroideryData();
                res.setHeader('Content-Type', 'application/json');
                res.setHeader('Content-Disposition', 'attachment; filename="embroidery-data.json"');
                res.send(data);
            } catch (error) {
                res.status(500).json({ success: false, error: error.message });
            }
        });

        // Import data
        router.post('/import', (req, res) => {
            try {
                const jsonData = req.body.data;
                const result = this.integration.importEmbroideryData(jsonData);
                res.json({ success: true, data: result });
            } catch (error) {
                res.status(500).json({ success: false, error: error.message });
            }
        });

        return router;
    }
}

module.exports = EmbroideryAPI;
