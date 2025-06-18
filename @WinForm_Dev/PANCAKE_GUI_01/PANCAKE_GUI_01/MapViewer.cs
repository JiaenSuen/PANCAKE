using System;
using System.Collections.Generic;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Windows.Forms;
using PANCAKE_DSLib;
using PANCAKE_Solution;

namespace PANCAKE_GUI_01
{
    public class MapViewer : UserControl
    {
        private List<Node> nodes = new List<Node>();
        private float zoom = 10.0f;
        private float offsetX = 0, offsetY = 0;
        private bool isDragging = false;
        private Point lastMouse;

        private Recommend_Aquire_Commodities_Path currentPath = new Recommend_Aquire_Commodities_Path();

        public MapViewer()
        {
            this.DoubleBuffered = true;
            this.BackColor = Color.White;
            this.MouseWheel += MapViewer_MouseWheel;
            this.MouseDown += MapViewer_MouseDown;
            this.MouseMove += MapViewer_MouseMove;
            this.MouseUp += MapViewer_MouseUp;
        }

      
        /// 載入要繪製的節點
        public void LoadNodes(IEnumerable<Node> nodes)
        {
            this.nodes = new List<Node>(nodes);
            this.Invalidate();
        }

        /// 設定、取得縮放比例
        public float Zoom
        {
            get => zoom;
            set
            {
                zoom = Math.Max(0.1f, Math.Min(10f, value));
                this.Invalidate();
            }
        }

     
        /// 清除平移偏移量
        public void ResetPan()
        {
            offsetX = offsetY = 0;
            this.Invalidate();
        }

        

        private void MapViewer_MouseWheel(object? sender, MouseEventArgs e)
        {
            float oldZoom = zoom;
            if (e.Delta > 0) Zoom *= 1.1f;
            else Zoom /= 1.1f;

            // 如果要保持滑鼠位置當縮放中心，可調整 offsetX/Y
            offsetX = e.X - (e.X - offsetX) * (zoom / oldZoom);
            offsetY = e.Y - (e.Y - offsetY) * (zoom / oldZoom);
        }

        private void MapViewer_MouseDown(object? sender, MouseEventArgs e)
        {
            if (e.Button == MouseButtons.Left)
            {
                isDragging = true;
                lastMouse = e.Location;
            }
        }

        private void MapViewer_MouseMove(object? sender, MouseEventArgs e)
        {
            if (!isDragging) return;
            offsetX += e.X - lastMouse.X;
            offsetY += e.Y - lastMouse.Y;
            lastMouse = e.Location;
            this.Invalidate();
        }

        private void MapViewer_MouseUp(object? sender, MouseEventArgs e)
        {
            if (e.Button == MouseButtons.Left)
                isDragging = false;
        }



        
        public void LoadPath(Recommend_Aquire_Commodities_Path path) {
            currentPath = path;
            this.Invalidate();
        }


        protected override void OnPaint(PaintEventArgs e)
        {
            base.OnPaint(e);
            if (nodes == null || nodes.Count == 0) return;
            var g = e.Graphics;
            g.SmoothingMode = SmoothingMode.AntiAlias;

            // 平移到中心 + 使用者平移 + 縮放
            g.TranslateTransform(this.ClientSize.Width / 2f + offsetX,
                                 this.ClientSize.Height / 2f + offsetY);
            g.ScaleTransform(zoom, zoom);

            // 先畫路徑線（含最後回到出發點）
            if (currentPath?.Path?.Count > 0)
            {
                //  收集所有點：起點→每個取貨點→回到起點
                var pts = new List<PointF>();
                pts.Add(new PointF(currentPath.Start_Node.Location_X,
                                    currentPath.Start_Node.Location_Y));
                foreach (var step in currentPath.Path)
                    pts.Add(new PointF(step.Node.Location_X, step.Node.Location_Y));
                // 加上最後回到出發點
                pts.Add(new PointF(currentPath.Start_Node.Location_X,
                                    currentPath.Start_Node.Location_Y));

                using (var pen = new Pen(Color.Red, 1f ))
                {
                    // 設定箭頭尾端
                    var cap = new AdjustableArrowCap(2f , 3f );
                    pen.CustomEndCap = cap;

                    // 一段段畫
                    for (int i = 0; i < pts.Count - 1; i++)
                        g.DrawLine(pen, pts[i], pts[i + 1]);
                }
            }

            // 在起點畫一個綠色圓圈標記
            {
                float sx = currentPath!.Start_Node.Location_X;
                float sy = currentPath.Start_Node.Location_Y;
                float sr = 1f;  // 起點半徑
                using (var startBrush = new SolidBrush(Color.Green))
                using (var startPen = new Pen(Color.DarkGreen, 1f))
                {
                    g.FillEllipse(startBrush, sx - sr, sy - sr, sr * 2, sr * 2);
                    g.DrawEllipse(startPen, sx - sr, sy - sr, sr * 2, sr * 2);
                }
                // 可加上「Origin」文字
                using (var font = new Font("Arial", 1f))
                using (var textBrush = new SolidBrush(Color.DarkGreen))
                {
                    g.DrawString("Origin", font, textBrush, sx + sr , sy - sr );
                }
            }

            // 最後再畫所有節點
            int baseRadius = 1;
            using (var pen = new Pen(Color.Blue, 1f ))
            using (var brush = new SolidBrush(Color.LightBlue))
            using (var font = new Font("Arial", 1f))
            using (var textBrush = new SolidBrush(Color.Black))
            {
                foreach (var node in nodes)
                {
                    float x = node.Location_X;
                    float y = node.Location_Y;
                    float r = baseRadius;

                    g.FillEllipse(brush, x - r, y - r, r * 2, r * 2);
                    g.DrawEllipse(pen, x - r, y - r, r * 2, r * 2);
                    g.DrawString(node.Name, font, textBrush, x  , y   );
                }
            }
        }










    }





}
