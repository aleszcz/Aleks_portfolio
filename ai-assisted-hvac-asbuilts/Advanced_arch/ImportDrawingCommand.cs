using System;
using System.IO;
using Autodesk.Revit.UI;
using Autodesk.Revit.DB;
using Autodesk.Revit.Attributes;
using Microsoft.Win32;

namespace RevitAssist.Commands
{
    /// <summary>
    /// Command to import HVAC drawings (PDF/Image) into Revit
    /// </summary>
    [Transaction(TransactionMode.Manual)]
    [Regeneration(RegenerationOption.Manual)]
    public class ImportDrawingCommand : IExternalCommand
    {
        public Result Execute(
            ExternalCommandData commandData, 
            ref string message, 
            ElementSet elements)
        {
            UIApplication uiApp = commandData.Application;
            UIDocument uiDoc = uiApp.ActiveUIDocument;
            Document doc = uiDoc.Document;
            
            try
            {
                // Show file selection dialog
                string filePath = SelectDrawingFile();
                
                if (string.IsNullOrEmpty(filePath))
                {
                    return Result.Cancelled;
                }
                
                // Show import configuration dialog
                var importDialog = new UI.ImportDialog(doc);
                importDialog.FilePath = filePath;
                
                if (importDialog.ShowDialog() != true)
                {
                    return Result.Cancelled;
                }
                
                // Store drawing information for processing
                DrawingData drawingData = new DrawingData
                {
                    FilePath = filePath,
                    DrawingType = importDialog.SelectedDrawingType,
                    TargetLevel = importDialog.SelectedLevel,
                    Scale = importDialog.DetectedScale,
                    AutoDetectScale = importDialog.AutoDetectScale
                };
                
                // Store in application-level data for next command
                App.CurrentDrawing = drawingData;
                
                // Import as underlay for reference
                if (importDialog.ShowAsUnderlay)
                {
                    ImportAsUnderlay(doc, filePath, importDialog.SelectedLevel);
                }
                
                TaskDialog.Show(
                    "RevitAssist", 
                    $"Drawing imported successfully!\n\n" +
                    $"Click 'Process with AI' to detect HVAC components."
                );
                
                return Result.Succeeded;
            }
            catch (Exception ex)
            {
                message = ex.Message;
                TaskDialog.Show("Error", $"Failed to import drawing:\n{ex.Message}");
                return Result.Failed;
            }
        }
        
        private string SelectDrawingFile()
        {
            OpenFileDialog dialog = new OpenFileDialog
            {
                Title = "Select HVAC Drawing",
                Filter = "All Supported Files|*.pdf;*.png;*.jpg;*.jpeg;*.tif;*.tiff|" +
                         "PDF Files|*.pdf|" +
                         "Image Files|*.png;*.jpg;*.jpeg;*.tif;*.tiff|" +
                         "All Files|*.*",
                FilterIndex = 1
            };
            
            if (dialog.ShowDialog() == true)
            {
                return dialog.FileName;
            }
            
            return null;
        }
        
        private void ImportAsUnderlay(Document doc, string filePath, Level level)
        {
            using (Transaction trans = new Transaction(doc, "Import Drawing Underlay"))
            {
                trans.Start();
                
                try
                {
                    // Create image instance as reference
                    ImageType imageType = null;
                    
                    // Check if image type already exists
                    FilteredElementCollector collector = 
                        new FilteredElementCollector(doc)
                            .OfClass(typeof(ImageType));
                    
                    foreach (ImageType type in collector)
                    {
                        if (type.Path == filePath)
                        {
                            imageType = type;
                            break;
                        }
                    }
                    
                    // Create new image type if not found
                    if (imageType == null)
                    {
                        ImageTypeOptions options = new ImageTypeOptions(
                            filePath, 
                            false, 
                            ImageTypeSource.Link
                        );
                        imageType = ImageType.Create(doc, options);
                    }
                    
                    // Get active view
                    View activeView = doc.ActiveView;
                    
                    // Create image instance
                    if (activeView.ViewType == ViewType.FloorPlan ||
                        activeView.ViewType == ViewType.CeilingPlan)
                    {
                        ImageInstance.Create(
                            doc, 
                            activeView, 
                            imageType.Id
                        );
                    }
                    
                    trans.Commit();
                }
                catch
                {
                    trans.RollBack();
                    throw;
                }
            }
        }
    }
    
    /// <summary>
    /// Data class to store drawing information
    /// </summary>
    public class DrawingData
    {
        public string FilePath { get; set; }
        public string DrawingType { get; set; }
        public Level TargetLevel { get; set; }
        public string Scale { get; set; }
        public bool AutoDetectScale { get; set; }
    }
}
