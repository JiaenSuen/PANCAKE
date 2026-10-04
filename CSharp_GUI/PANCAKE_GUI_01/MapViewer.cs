using PANCAKE_DSLib;
using PANCAKE_Params;
using PANCAKE_Solution;
using System.Drawing.Drawing2D;

namespace PANCAKE_GUI_01
{
    public class MapViewer : UserControl
    {
        private List<Node> nodes = new();
        private float zoom = 1.0f;
        private float offsetX = 0;
        private float offsetY = 0;
        private bool isDragging = false;
        private Point lastMouse;
        private Recommend_Aquire_Commodities_Path currentPath = new()
        {
            Start_Node = Params.pStart_Node,
            UnitMoveCost = Params.pUnit_Cost
        };

        public MapViewer()
        {
            DoubleBuffered = true;
            BackColor = Color.White;
            MouseWheel += MapViewer_MouseWheel;
            MouseDown += MapViewer_MouseDown;
            MouseMove += MapViewer_MouseMove;
            MouseUp += MapViewer_MouseUp;
            Resize += (_, _) => FitToNodes();
        }

        public void LoadNodes(IEnumerable<Node> mapNodes)
        {
            nodes = new List<Node>(mapNodes);
            Invalidate();
        }

        public void LoadPath(Recommend_Aquire_Commodities_Path path)
        {
            currentPath = path;
            Invalidate();
        }

        public void ClearPath()
        {
            currentPath = new Recommend_Aquire_Commodities_Path
            {
                Start_Node = Params.pStart_Node,
                UnitMoveCost = Params.pUnit_Cost
            };
            Invalidate();
        }

        public float Zoom
        {
            get => zoom;
            set
            {
                zoom = Math.Max(0.05f, Math.Min(40f, value));
                Invalidate();
            }
        }

        public void ResetPan()
        {
            offsetX = 0;
            offsetY = 0;
            Invalidate();
        }

        /// <summary>
        /// Fits both legacy small-coordinate maps and the new research maps into the panel.
        /// </summary>
        public void FitToNodes()
        {
            if (nodes.Count == 0 || ClientSize.Width <= 20 || ClientSize.Height <= 20)
                return;

            float minX = Math.Min(0f, nodes.Min(n => (float)n.Location_X));
            float maxX = Math.Max(0f, nodes.Max(n => (float)n.Location_X));
            float minY = Math.Min(0f, nodes.Min(n => (float)n.Location_Y));
            float maxY = Math.Max(0f, nodes.Max(n => (float)n.Location_Y));

            float rangeX = Math.Max(1f, maxX - minX);
            float rangeY = Math.Max(1f, maxY - minY);
            float usableW = Math.Max(20f, ClientSize.Width - 70f);
            float usableH = Math.Max(20f, ClientSize.Height - 70f);

            zoom = Math.Clamp(Math.Min(usableW / rangeX, usableH / rangeY), 0.05f, 40f);

            float centerX = (minX + maxX) / 2f;
            float centerY = (minY + maxY) / 2f;
            offsetX = -centerX * zoom;
            offsetY = -centerY * zoom;
            Invalidate();
        }

        private void MapViewer_MouseWheel(object? sender, MouseEventArgs e)
        {
            float oldZoom = zoom;
            Zoom = e.Delta > 0 ? zoom * 1.1f : zoom / 1.1f;

            if (Math.Abs(oldZoom) > 1e-6f)
            {
                offsetX = e.X - ClientSize.Width / 2f -
                          (e.X - ClientSize.Width / 2f - offsetX) * (zoom / oldZoom);
                offsetY = e.Y - ClientSize.Height / 2f -
                          (e.Y - ClientSize.Height / 2f - offsetY) * (zoom / oldZoom);
            }
        }

        private void MapViewer_MouseDown(object? sender, MouseEventArgs e)
        {
            if (e.Button != MouseButtons.Left) return;
            isDragging = true;
            lastMouse = e.Location;
            Cursor = Cursors.Hand;
        }

        private void MapViewer_MouseMove(object? sender, MouseEventArgs e)
        {
            if (!isDragging) return;
            offsetX += e.X - lastMouse.X;
            offsetY += e.Y - lastMouse.Y;
            lastMouse = e.Location;
            Invalidate();
        }

        private void MapViewer_MouseUp(object? sender, MouseEventArgs e)
        {
            if (e.Button != MouseButtons.Left) return;
            isDragging = false;
            Cursor = Cursors.Default;
        }

        protected override void OnPaint(PaintEventArgs e)
        {
            base.OnPaint(e);
            if (nodes.Count == 0) return;

            var g = e.Graphics;
            g.SmoothingMode = SmoothingMode.AntiAlias;
            g.TranslateTransform(ClientSize.Width / 2f + offsetX, ClientSize.Height / 2f + offsetY);
            g.ScaleTransform(zoom, zoom);

            // Draw the optimized path. The objective does not include a return-to-origin leg,
            // so the visualization intentionally stays open as well.
            if (currentPath.Path.Count > 0 && currentPath.Start_Node is not null)
            {
                var points = new List<PointF>
                {
                    new(currentPath.Start_Node.Location_X, currentPath.Start_Node.Location_Y)
                };
                points.AddRange(currentPath.Path.Select(step =>
                    new PointF(step.Node.Location_X, step.Node.Location_Y)));

                float pathWidth = Math.Max(0.35f, 2.0f / zoom);
                using var pathPen = new Pen(Color.Firebrick, pathWidth);
                using var cap = new AdjustableArrowCap(Math.Max(1.5f, 4f / zoom), Math.Max(2f, 5f / zoom));
                pathPen.CustomEndCap = cap;

                for (int i = 0; i < points.Count - 1; i++)
                    g.DrawLine(pathPen, points[i], points[i + 1]);
            }

            float nodeRadius = Math.Max(0.8f, 4.0f / zoom);
            float penWidth = Math.Max(0.25f, 1.2f / zoom);
            float fontSize = Math.Max(1.2f, 8.0f / zoom);

            // Origin
            using (var startBrush = new SolidBrush(Color.SeaGreen))
            using (var startPen = new Pen(Color.DarkGreen, penWidth))
            using (var startFont = new Font("Segoe UI", fontSize))
            using (var startText = new SolidBrush(Color.DarkGreen))
            {
                var origin = Params.pStart_Node;
                g.FillEllipse(startBrush, origin.Location_X - nodeRadius, origin.Location_Y - nodeRadius,
                    nodeRadius * 2, nodeRadius * 2);
                g.DrawEllipse(startPen, origin.Location_X - nodeRadius, origin.Location_Y - nodeRadius,
                    nodeRadius * 2, nodeRadius * 2);
                g.DrawString("Origin", startFont, startText,
                    origin.Location_X + nodeRadius, origin.Location_Y - nodeRadius);
            }

            using var nodePen = new Pen(Color.RoyalBlue, penWidth);
            using var nodeBrush = new SolidBrush(Color.LightSkyBlue);
            using var font = new Font("Segoe UI", fontSize);
            using var textBrush = new SolidBrush(Color.Black);

            foreach (var node in nodes)
            {
                float x = node.Location_X;
                float y = node.Location_Y;
                g.FillEllipse(nodeBrush, x - nodeRadius, y - nodeRadius, nodeRadius * 2, nodeRadius * 2);
                g.DrawEllipse(nodePen, x - nodeRadius, y - nodeRadius, nodeRadius * 2, nodeRadius * 2);
                g.DrawString(node.Name, font, textBrush, x + nodeRadius, y);
            }
        }
    }
}
