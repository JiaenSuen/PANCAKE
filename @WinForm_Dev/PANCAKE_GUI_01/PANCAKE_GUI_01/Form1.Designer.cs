namespace PANCAKE_GUI_01
{
    partial class PANCAKE_GUI_Form_1
    {
        /// <summary>
        ///  Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        ///  Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        ///  Required method for Designer support - do not modify
        ///  the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            MapFrame = new Panel();
            btnZoomIn = new Button();
            btnZoomOut = new Button();
            RAC_Path_Box = new TextBox();
            Algorithm_Selection = new ComboBox();
            txtDemandInput = new TextBox();
            Test_Cases = new ComboBox();
            SuspendLayout();
            // 
            // MapFrame
            // 
            MapFrame.AutoScroll = true;
            MapFrame.Location = new Point(200, 40);
            MapFrame.Name = "MapFrame";
            MapFrame.Size = new Size(500, 500);
            MapFrame.TabIndex = 0;
            // 
            // btnZoomIn
            // 
            btnZoomIn.Location = new Point(195, 555);
            btnZoomIn.Name = "btnZoomIn";
            btnZoomIn.Size = new Size(138, 42);
            btnZoomIn.TabIndex = 1;
            btnZoomIn.Text = "放大";
            btnZoomIn.UseVisualStyleBackColor = true;
            btnZoomIn.Click += btnZoomIn_Click;
            // 
            // btnZoomOut
            // 
            btnZoomOut.Location = new Point(369, 555);
            btnZoomOut.Name = "btnZoomOut";
            btnZoomOut.Size = new Size(138, 42);
            btnZoomOut.TabIndex = 2;
            btnZoomOut.Text = "縮小";
            btnZoomOut.UseVisualStyleBackColor = true;
            btnZoomOut.Click += btnZoomOut_Click;
            // 
            // RAC_Path_Box
            // 
            RAC_Path_Box.BackColor = SystemColors.Window;
            RAC_Path_Box.Location = new Point(788, 54);
            RAC_Path_Box.Multiline = true;
            RAC_Path_Box.Name = "RAC_Path_Box";
            RAC_Path_Box.ReadOnly = true;
            RAC_Path_Box.ScrollBars = ScrollBars.Vertical;
            RAC_Path_Box.Size = new Size(300, 400);
            RAC_Path_Box.TabIndex = 3;
            // 
            // Algorithm_Selection
            // 
            Algorithm_Selection.FormattingEnabled = true;
            Algorithm_Selection.Items.AddRange(new object[] { "Greedy Strategy", "Genetic Algorithm", "Tabu Search", "" });
            Algorithm_Selection.Location = new Point(788, 488);
            Algorithm_Selection.Name = "Algorithm_Selection";
            Algorithm_Selection.Size = new Size(300, 27);
            Algorithm_Selection.TabIndex = 4;
            Algorithm_Selection.SelectedIndexChanged += comboBox1_SelectedIndexChanged;
            // 
            // txtDemandInput
            // 
            txtDemandInput.Location = new Point(1191, 54);
            txtDemandInput.Multiline = true;
            txtDemandInput.Name = "txtDemandInput";
            txtDemandInput.ScrollBars = ScrollBars.Vertical;
            txtDemandInput.Size = new Size(200, 400);
            txtDemandInput.TabIndex = 5;
            // 
            // Test_Cases
            // 
            Test_Cases.FormattingEnabled = true;
            Test_Cases.Items.AddRange(new object[] { "Not Use", "Test Case 01", "Test Case 02", "Test Case 03" });
            Test_Cases.Location = new Point(1191, 488);
            Test_Cases.Name = "Test_Cases";
            Test_Cases.Size = new Size(200, 27);
            Test_Cases.TabIndex = 6;
            // 
            // PANCAKE_GUI_Form_1
            // 
            AutoScaleDimensions = new SizeF(9F, 19F);
            AutoScaleMode = AutoScaleMode.Font;
            ClientSize = new Size(1782, 953);
            Controls.Add(Test_Cases);
            Controls.Add(txtDemandInput);
            Controls.Add(Algorithm_Selection);
            Controls.Add(RAC_Path_Box);
            Controls.Add(btnZoomOut);
            Controls.Add(btnZoomIn);
            Controls.Add(MapFrame);
            Name = "PANCAKE_GUI_Form_1";
            Text = "PANCAKE_GUI";
            Load += PANCAKE_GUI_Form_1_Load;
            ResumeLayout(false);
            PerformLayout();
        }

        #endregion

        private Panel MapFrame;
        private Button btnZoomIn;
        private Button btnZoomOut;
        private TextBox RAC_Path_Box;
        private ComboBox Algorithm_Selection;
        private TextBox txtDemandInput;
        private ComboBox Test_Cases;
    }
}
