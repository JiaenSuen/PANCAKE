using PANCAKE_DSLib;
using PANCAKE_Read_Map;
using PANCAKE_Solution;
using Basic_Algorithms_PANCAKE;


namespace PANCAKE_GUI_01
{
    internal static class Program
    {
        /// <summary>
        ///  The main entry point for the application.
        /// </summary>
        [STAThread]
        static void Main()
        {
            // To customize application configuration such as set high DPI settings or default font,
            // see https://aka.ms/applicationconfiguration.
            ApplicationConfiguration.Initialize();
            Application.Run(new PANCAKE_GUI_Form_1());
            




            
        }
    }
}