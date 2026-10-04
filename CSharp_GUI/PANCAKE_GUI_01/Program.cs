namespace PANCAKE_GUI_01
{
    internal static class Program
    {
        [STAThread]
        static void Main(string[] args)
        {
            if (args.Any(arg => arg.Equals("--self-test", StringComparison.OrdinalIgnoreCase)))
            {
                Environment.ExitCode = GuiSelfTest.Run();
                return;
            }

            ApplicationConfiguration.Initialize();
            Application.Run(new PANCAKE_GUI_Form_1());
        }
    }
}
