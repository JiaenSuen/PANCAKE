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
            MinCost_label = new Label();
            label1 = new Label();
            MapSelector = new ComboBox();
            label2 = new Label();
            label3 = new Label();
            label4 = new Label();
            label5 = new Label();
            label6 = new Label();
            ShowCommodities = new TextBox();
            label7 = new Label();
            Demands_Show = new TextBox();
            NoteSpace = new TextBox();
            label8 = new Label();
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
            Algorithm_Selection.Items.AddRange(new object[] { "Greedy Strategy", "SetCover Strategy", "Dynamic Programming", "Genetic Algorithm", "Tabu Search", "Genetic Mix TS", "Ant Colony", "Whale Optimization", "Whale Optimization Mix TS", "Particle Swarm" });
            Algorithm_Selection.Location = new Point(788, 500);
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
            Test_Cases.Items.AddRange(new object[] { "Customized Input", "Test Case Map6-2", "Test Case Map6-1", "Test Case Map7-1", "Test Case Map7-2" });
            Test_Cases.Location = new Point(1191, 490);
            Test_Cases.Name = "Test_Cases";
            Test_Cases.Size = new Size(200, 27);
            Test_Cases.TabIndex = 6;
            Test_Cases.SelectedIndexChanged += Test_Cases_SelectedIndexChanged;
            // 
            // MinCost_label
            // 
            MinCost_label.AutoSize = true;
            MinCost_label.Font = new Font("Microsoft JhengHei UI", 12F);
            MinCost_label.Location = new Point(930, 567);
            MinCost_label.Name = "MinCost_label";
            MinCost_label.Size = new Size(0, 25);
            MinCost_label.TabIndex = 8;
            // 
            // label1
            // 
            label1.AutoSize = true;
            label1.Font = new Font("Microsoft JhengHei UI", 12F);
            label1.Location = new Point(790, 565);
            label1.Name = "label1";
            label1.Size = new Size(110, 25);
            label1.TabIndex = 9;
            label1.Text = "Min Cost : ";
            // 
            // MapSelector
            // 
            MapSelector.FormattingEnabled = true;
            MapSelector.Items.AddRange(new object[] { "map", "map2", "map3", "map4", "map5", "map6", "map7", "map8", "map9" });
            MapSelector.Location = new Point(1191, 555);
            MapSelector.Name = "MapSelector";
            MapSelector.Size = new Size(200, 27);
            MapSelector.TabIndex = 10;
            MapSelector.SelectedIndexChanged += MapSelector_SelectedIndexChanged;
            // 
            // label2
            // 
            label2.AutoSize = true;
            label2.Font = new Font("Microsoft JhengHei UI", 12F);
            label2.Location = new Point(790, 464);
            label2.Name = "label2";
            label2.Size = new Size(104, 25);
            label2.TabIndex = 11;
            label2.Text = "Strategy : ";
            // 
            // label3
            // 
            label3.AutoSize = true;
            label3.Font = new Font("Microsoft JhengHei UI", 12F);
            label3.Location = new Point(1191, 464);
            label3.Name = "label3";
            label3.Size = new Size(178, 25);
            label3.TabIndex = 12;
            label3.Text = "Requirements List";
            // 
            // label4
            // 
            label4.AutoSize = true;
            label4.Font = new Font("Microsoft JhengHei UI", 12F);
            label4.Location = new Point(1191, 527);
            label4.Name = "label4";
            label4.Size = new Size(115, 25);
            label4.TabIndex = 13;
            label4.Text = "Map Select";
            // 
            // label5
            // 
            label5.AutoSize = true;
            label5.Font = new Font("Microsoft JhengHei UI", 12F);
            label5.Location = new Point(785, 26);
            label5.Name = "label5";
            label5.Size = new Size(228, 25);
            label5.TabIndex = 14;
            label5.Text = "Recommendation Path";
            // 
            // label6
            // 
            label6.AutoSize = true;
            label6.Font = new Font("Microsoft JhengHei UI", 12F);
            label6.Location = new Point(1191, 26);
            label6.Name = "label6";
            label6.Size = new Size(102, 25);
            label6.TabIndex = 15;
            label6.Text = "Demands";
            // 
            // ShowCommodities
            // 
            ShowCommodities.BackColor = SystemColors.Window;
            ShowCommodities.Location = new Point(195, 673);
            ShowCommodities.Multiline = true;
            ShowCommodities.Name = "ShowCommodities";
            ShowCommodities.ReadOnly = true;
            ShowCommodities.ScrollBars = ScrollBars.Vertical;
            ShowCommodities.Size = new Size(253, 217);
            ShowCommodities.TabIndex = 16;
            // 
            // label7
            // 
            label7.AutoSize = true;
            label7.Font = new Font("Microsoft JhengHei UI", 12F);
            label7.Location = new Point(200, 632);
            label7.Name = "label7";
            label7.Size = new Size(154, 25);
            label7.TabIndex = 17;
            label7.Text = "Commodities : ";
            // 
            // Demands_Show
            // 
            Demands_Show.BackColor = SystemColors.ScrollBar;
            Demands_Show.Location = new Point(1191, 634);
            Demands_Show.Multiline = true;
            Demands_Show.Name = "Demands_Show";
            Demands_Show.ReadOnly = true;
            Demands_Show.ScrollBars = ScrollBars.Vertical;
            Demands_Show.Size = new Size(200, 250);
            Demands_Show.TabIndex = 18;
            // 
            // NoteSpace
            // 
            NoteSpace.BackColor = SystemColors.InactiveBorder;
            NoteSpace.Location = new Point(1500, 54);
            NoteSpace.Multiline = true;
            NoteSpace.Name = "NoteSpace";
            NoteSpace.ScrollBars = ScrollBars.Vertical;
            NoteSpace.Size = new Size(200, 400);
            NoteSpace.TabIndex = 19;
            // 
            // label8
            // 
            label8.AutoSize = true;
            label8.Font = new Font("Microsoft JhengHei UI", 12F);
            label8.Location = new Point(1500, 26);
            label8.Name = "label8";
            label8.Size = new Size(59, 25);
            label8.TabIndex = 20;
            label8.Text = "Note";
            // 
            // PANCAKE_GUI_Form_1
            // 
            AutoScaleDimensions = new SizeF(9F, 19F);
            AutoScaleMode = AutoScaleMode.Font;
            ClientSize = new Size(1782, 953);
            Controls.Add(label8);
            Controls.Add(NoteSpace);
            Controls.Add(Demands_Show);
            Controls.Add(label7);
            Controls.Add(ShowCommodities);
            Controls.Add(label6);
            Controls.Add(label5);
            Controls.Add(label4);
            Controls.Add(label3);
            Controls.Add(label2);
            Controls.Add(MapSelector);
            Controls.Add(label1);
            Controls.Add(MinCost_label);
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
        private Label MinCost_label;
        private Label label1;
        private ComboBox MapSelector;
        private Label label2;
        private Label label3;
        private Label label4;
        private Label label5;
        private Label label6;
        private TextBox ShowCommodities;
        private Label label7;
        private TextBox Demands_Show;
        private TextBox NoteSpace;
        private Label label8;
    }
}
