import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

/**
 * Extension to add CSV reload button to AnimaginePrompt node
 */
app.registerExtension({
    name: "AnimaginePrompt.ReloadCSV",
    
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        // Only apply to our AnimaginePrompt node
        if (nodeData.name === "AnimaginePrompt") {
            
            // Function to reload CSV
            const reloadCSV = async (node) => {
                try {
                    // Get current csv_path value
                    const csvPathWidget = node.widgets.find(w => w.name === "csv_path");
                    if (!csvPathWidget || !csvPathWidget.value) {
                        alert("No CSV path specified");
                        return;
                    }
                    
                    // Get reload button to update its text
                    const reloadButton = node.widgets.find(w => w.name === "🔄 Reload CSV" || w.name.startsWith("🔄 Reload CSV"));
                    
                    // Call reload endpoint
                    const response = await api.fetchApi("/animagine/reload_csv", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify({
                            csv_path: csvPathWidget.value
                        })
                    });
                    
                    if (response.ok) {
                        const result = await response.json();
                        if (result.success) {
                            console.log(`CSV reloaded successfully. Rows: ${result.rows}`);
                            // Update button text with row count
                            if (reloadButton) {
                                reloadButton.name = `🔄 Reload CSV (${result.rows})`;
                            }
                            node.setDirtyCanvas(true, true);
                        } else {
                            alert(`Error reloading CSV: ${result.error}`);
                        }
                    } else {
                        alert("Connection error while reloading CSV");
                    }
                    
                } catch (error) {
                    console.error("Error reloading CSV:", error);
                    alert("Error reloading CSV: " + error.message);
                }
            };
            
            // Function executed when node is created
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                const result = onNodeCreated?.apply(this, arguments);
                
                // Add reload button
                const reloadButton = this.addWidget(
                    "button",
                    "🔄 Reload CSV",
                    null,
                    () => reloadCSV(this),
                    {
                        serialize: false
                    }
                );
                
                // Button styling
                reloadButton.computeSize = () => [120, 25];
                
                // Reorder widgets: move button after csv_path
                const csvPathIndex = this.widgets.findIndex(w => w.name === "csv_path");
                if (csvPathIndex !== -1) {
                    const buttonIndex = this.widgets.length - 1;
                    const button = this.widgets.splice(buttonIndex, 1)[0];
                    this.widgets.splice(csvPathIndex + 1, 0, button);
                }
                
                return result;
            };
        }
    }
});