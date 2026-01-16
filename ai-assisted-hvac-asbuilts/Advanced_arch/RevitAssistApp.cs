using System;
using System.Windows.Media.Imaging;
using Autodesk.Revit.UI;
using Autodesk.Revit.Attributes;

namespace RevitAssist
{
    /// <summary>
    /// Main application entry point for RevitAssist plugin
    /// </summary>
    public class RevitAssistApp : IExternalApplication
    {
        // API endpoint for AI processing service
        private const string API_ENDPOINT = "http://localhost:8000";
        
        public Result OnStartup(UIControlledApplication application)
        {
            try
            {
                // Create ribbon tab
                application.CreateRibbonTab("RevitAssist");
                
                // Create ribbon panel
                RibbonPanel panel = application.CreateRibbonPanel(
                    "RevitAssist", 
                    "HVAC Tools"
                );
                
                // Add buttons
                AddImportButton(panel);
                AddProcessButton(panel);
                AddReviewButton(panel);
                AddSettingsButton(panel);
                
                return Result.Succeeded;
            }
            catch (Exception ex)
            {
                TaskDialog.Show("RevitAssist Error", 
                    $"Failed to load plugin: {ex.Message}");
                return Result.Failed;
            }
        }
        
        public Result OnShutdown(UIControlledApplication application)
        {
            // Cleanup resources
            return Result.Succeeded;
        }
        
        private void AddImportButton(RibbonPanel panel)
        {
            string assemblyPath = typeof(RevitAssistApp).Assembly.Location;
            
            PushButtonData buttonData = new PushButtonData(
                "ImportDrawing",
                "Import\nDrawing",
                assemblyPath,
                "RevitAssist.Commands.ImportDrawingCommand"
            );
            
            PushButton button = panel.AddItem(buttonData) as PushButton;
            button.ToolTip = "Import HVAC drawing from PDF or image";
            button.LargeImage = LoadImage("import_icon.png");
        }
        
        private void AddProcessButton(RibbonPanel panel)
        {
            string assemblyPath = typeof(RevitAssistApp).Assembly.Location;
            
            PushButtonData buttonData = new PushButtonData(
                "ProcessDrawing",
                "Process\nwith AI",
                assemblyPath,
                "RevitAssist.Commands.ProcessDrawingCommand"
            );
            
            PushButton button = panel.AddItem(buttonData) as PushButton;
            button.ToolTip = "Process drawing with AI to detect HVAC components";
            button.LargeImage = LoadImage("process_icon.png");
        }
        
        private void AddReviewButton(RibbonPanel panel)
        {
            string assemblyPath = typeof(RevitAssistApp).Assembly.Location;
            
            PushButtonData buttonData = new PushButtonData(
                "ReviewResults",
                "Review\n& Edit",
                assemblyPath,
                "RevitAssist.Commands.ReviewResultsCommand"
            );
            
            PushButton button = panel.AddItem(buttonData) as PushButton;
            button.ToolTip = "Review and edit detected components";
            button.LargeImage = LoadImage("review_icon.png");
        }
        
        private void AddSettingsButton(RibbonPanel panel)
        {
            string assemblyPath = typeof(RevitAssistApp).Assembly.Location;
            
            PushButtonData buttonData = new PushButtonData(
                "Settings",
                "Settings",
                assemblyPath,
                "RevitAssist.Commands.SettingsCommand"
            );
            
            PushButton button = panel.AddItem(buttonData) as PushButton;
            button.ToolTip = "Configure RevitAssist settings";
            button.LargeImage = LoadImage("settings_icon.png");
        }
        
        private BitmapImage LoadImage(string imageName)
        {
            try
            {
                string assemblyPath = typeof(RevitAssistApp).Assembly.Location;
                string imagePath = System.IO.Path.Combine(
                    System.IO.Path.GetDirectoryName(assemblyPath),
                    "Resources",
                    "Icons",
                    imageName
                );
                
                return new BitmapImage(new Uri(imagePath));
            }
            catch
            {
                return null;
            }
        }
    }
}
