using System;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using Autodesk.Revit.UI;
using Autodesk.Revit.DB;
using Autodesk.Revit.Attributes;
using Newtonsoft.Json;

namespace RevitAssist.Commands
{
    /// <summary>
    /// Command to process drawing with AI backend
    /// </summary>
    [Transaction(TransactionMode.Manual)]
    public class ProcessDrawingCommand : IExternalCommand
    {
        private const string API_URL = "http://localhost:8000/api/process";
        
        public Result Execute(
            ExternalCommandData commandData, 
            ref string message, 
            ElementSet elements)
        {
            UIApplication uiApp = commandData.Application;
            
            try
            {
                // Check if drawing is loaded
                if (App.CurrentDrawing == null)
                {
                    TaskDialog.Show(
                        "RevitAssist", 
                        "Please import a drawing first using 'Import Drawing' button."
                    );
                    return Result.Cancelled;
                }
                
                // Show processing dialog
                var progressDialog = new UI.ProcessingDialog();
                progressDialog.Show();
                
                // Process drawing asynchronously
                Task.Run(async () =>
                {
                    try
                    {
                        var result = await ProcessDrawingAsync(
                            App.CurrentDrawing,
                            progressDialog
                        );
                        
                        // Store results
                        App.ProcessingResult = result;
                        
                        // Update UI on main thread
                        progressDialog.Dispatcher.Invoke(() =>
                        {
                            progressDialog.Close();
                            
                            TaskDialog.Show(
                                "Processing Complete",
                                $"Successfully detected {result.Components.Count} components!\n\n" +
                                $"Average confidence: {result.AverageConfidence:P0}\n" +
                                $"Processing time: {result.ProcessingTime:F1}s\n\n" +
                                $"Click 'Review & Edit' to inspect results."
                            );
                        });
                    }
                    catch (Exception ex)
                    {
                        progressDialog.Dispatcher.Invoke(() =>
                        {
                            progressDialog.Close();
                            TaskDialog.Show("Error", $"Processing failed:\n{ex.Message}");
                        });
                    }
                });
                
                return Result.Succeeded;
            }
            catch (Exception ex)
            {
                message = ex.Message;
                TaskDialog.Show("Error", $"Failed to process drawing:\n{ex.Message}");
                return Result.Failed;
            }
        }
        
        private async Task<ProcessingResult> ProcessDrawingAsync(
            DrawingData drawing,
            UI.ProcessingDialog progressDialog)
        {
            using (HttpClient client = new HttpClient())
            {
                // Prepare request
                var request = new ProcessingRequest
                {
                    FilePath = drawing.FilePath,
                    DrawingType = drawing.DrawingType,
                    Level = drawing.TargetLevel?.Name,
                    Scale = drawing.Scale,
                    ProcessingMode = "standard" // or "high_accuracy", "fast_preview"
                };
                
                string jsonContent = JsonConvert.SerializeObject(request);
                var content = new StringContent(
                    jsonContent, 
                    Encoding.UTF8, 
                    "application/json"
                );
                
                // Update progress
                UpdateProgress(progressDialog, "Uploading drawing...", 10);
                
                // Send request
                HttpResponseMessage response = await client.PostAsync(
                    API_URL, 
                    content
                );
                
                response.EnsureSuccessStatusCode();
                
                // Read response
                string responseJson = await response.Content.ReadAsStringAsync();
                var result = JsonConvert.DeserializeObject<ProcessingResult>(responseJson);
                
                // Simulate progress updates (in real impl, use websockets)
                UpdateProgress(progressDialog, "Analyzing layout...", 30);
                await Task.Delay(500);
                
                UpdateProgress(progressDialog, "Detecting components...", 50);
                await Task.Delay(500);
                
                UpdateProgress(progressDialog, "Extracting connections...", 70);
                await Task.Delay(500);
                
                UpdateProgress(progressDialog, "Validating HVAC logic...", 90);
                await Task.Delay(500);
                
                UpdateProgress(progressDialog, "Complete!", 100);
                
                return result;
            }
        }
        
        private void UpdateProgress(
            UI.ProcessingDialog dialog, 
            string message, 
            int percentage)
        {
            dialog.Dispatcher.Invoke(() =>
            {
                dialog.UpdateProgress(message, percentage);
            });
        }
    }
    
    /// <summary>
    /// Request object for AI processing
    /// </summary>
    public class ProcessingRequest
    {
        public string FilePath { get; set; }
        public string DrawingType { get; set; }
        public string Level { get; set; }
        public string Scale { get; set; }
        public string ProcessingMode { get; set; }
    }
    
    /// <summary>
    /// Result from AI processing
    /// </summary>
    public class ProcessingResult
    {
        public List<HVACComponent> Components { get; set; }
        public List<Connection> Connections { get; set; }
        public List<ValidationIssue> Issues { get; set; }
        public double AverageConfidence { get; set; }
        public double ProcessingTime { get; set; }
        public string DetectedScale { get; set; }
    }
    
    public class HVACComponent
    {
        public string Id { get; set; }
        public string Type { get; set; }
        public string SubType { get; set; }
        public double[] BoundingBox { get; set; } // [x, y, width, height]
        public double Confidence { get; set; }
        public Dictionary<string, string> Properties { get; set; }
        public string RevitFamily { get; set; }
    }
    
    public class Connection
    {
        public string FromComponent { get; set; }
        public string ToComponent { get; set; }
        public string ConnectionType { get; set; }
        public double Confidence { get; set; }
    }
    
    public class ValidationIssue
    {
        public string Severity { get; set; } // "ERROR", "WARNING", "INFO"
        public string Message { get; set; }
        public string ComponentId { get; set; }
    }
}
