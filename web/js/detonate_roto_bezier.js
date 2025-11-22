/**
 * ComfyUI_Detonate - RotoBezier Interactive Spline Drawing Widget
 *
 * Interactive Bezier curve drawing widget for creating masks.
 * Based on Natron's Roto implementation with modern web technologies.
 */

import { app } from "../../scripts/app.js";
import { ComfyWidgets } from "../../scripts/widgets.js";

/**
 * Bezier curve point structure
 */
class BezierPoint {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.handleIn = { x: 0, y: 0 };   // Left tangent handle (offset from point)
        this.handleOut = { x: 0, y: 0 };  // Right tangent handle (offset from point)
        this.smooth = true;  // Auto-align handles for smooth curves
    }

    clone() {
        const p = new BezierPoint(this.x, this.y);
        p.handleIn = { ...this.handleIn };
        p.handleOut = { ...this.handleOut };
        p.smooth = this.smooth;
        return p;
    }
}

/**
 * Bezier spline (collection of connected Bezier curves)
 */
class BezierSpline {
    constructor() {
        this.points = [];
        this.closed = false;
        this.feather = 2.0;  // Default feather in pixels
        this.operation = 'add';  // Shape operation: 'add', 'subtract', 'intersect'
        this.invert = false;  // Invert this spline's mask
    }

    addPoint(x, y) {
        this.points.push(new BezierPoint(x, y));
    }

    clone() {
        const spline = new BezierSpline();
        spline.points = this.points.map(p => p.clone());
        spline.closed = this.closed;
        spline.feather = this.feather;
        spline.operation = this.operation;
        spline.invert = this.invert;
        return spline;
    }

    toJSON() {
        return {
            points: this.points.map(p => ({
                x: p.x,
                y: p.y,
                handleIn: p.handleIn,
                handleOut: p.handleOut,
                smooth: p.smooth
            })),
            closed: this.closed,
            feather: this.feather,
            operation: this.operation,
            invert: this.invert
        };
    }

    static fromJSON(data) {
        const spline = new BezierSpline();
        spline.closed = data.closed || false;
        spline.feather = data.feather || 2.0;
        spline.operation = data.operation || 'add';
        spline.invert = data.invert || false;
        spline.points = (data.points || []).map(p => {
            const point = new BezierPoint(p.x, p.y);
            point.handleIn = p.handleIn || { x: 0, y: 0 };
            point.handleOut = p.handleOut || { x: 0, y: 0 };
            point.smooth = p.smooth !== undefined ? p.smooth : true;
            return point;
        });
        return spline;
    }

    /**
     * Generate a circle spline (Phase 1.5 preset)
     */
    static createCircle(cx, cy, radius) {
        const spline = new BezierSpline();
        spline.closed = true;

        // Circle approximated with 4 Bezier curves
        // Magic constant for circle approximation: 0.5522847498 ≈ 4/3 * tan(π/8)
        const kappa = 0.5522847498;
        const offset = radius * kappa;

        // Top point
        const p1 = new BezierPoint(cx, cy - radius);
        p1.handleIn = { x: -offset, y: 0 };
        p1.handleOut = { x: offset, y: 0 };

        // Right point
        const p2 = new BezierPoint(cx + radius, cy);
        p2.handleIn = { x: 0, y: -offset };
        p2.handleOut = { x: 0, y: offset };

        // Bottom point
        const p3 = new BezierPoint(cx, cy + radius);
        p3.handleIn = { x: offset, y: 0 };
        p3.handleOut = { x: -offset, y: 0 };

        // Left point
        const p4 = new BezierPoint(cx - radius, cy);
        p4.handleIn = { x: 0, y: offset };
        p4.handleOut = { x: 0, y: -offset };

        spline.points = [p1, p2, p3, p4];
        return spline;
    }

    /**
     * Generate a rectangle spline (Phase 1.5 preset)
     */
    static createRectangle(cx, cy, width, height) {
        const spline = new BezierSpline();
        spline.closed = true;

        const hw = width / 2;
        const hh = height / 2;

        // Four corners (no handles for sharp corners)
        spline.addPoint(cx - hw, cy - hh);  // Top-left
        spline.addPoint(cx + hw, cy - hh);  // Top-right
        spline.addPoint(cx + hw, cy + hh);  // Bottom-right
        spline.addPoint(cx - hw, cy + hh);  // Bottom-left

        return spline;
    }

    /**
     * Generate a star spline (Phase 1.5 preset)
     */
    static createStar(cx, cy, outerRadius, innerRadius, points = 5) {
        const spline = new BezierSpline();
        spline.closed = true;

        const angleStep = Math.PI / points;

        for (let i = 0; i < points * 2; i++) {
            const angle = i * angleStep - Math.PI / 2;  // Start at top
            const radius = i % 2 === 0 ? outerRadius : innerRadius;
            const x = cx + radius * Math.cos(angle);
            const y = cy + radius * Math.sin(angle);
            spline.addPoint(x, y);
        }

        return spline;
    }
}

/**
 * Interactive Bezier drawing widget
 */
class BezierDrawingWidget {
    constructor(node, name, value) {
        this.node = node;
        this.name = name;
        this.splines = [];  // Array of BezierSpline objects
        this.currentSpline = null;  // Spline being drawn
        this.selectedPoint = null;  // { splineIdx, pointIdx }
        this.selectedHandle = null;  // { splineIdx, pointIdx, handle: 'in'|'out' }
        this.dragging = false;
        this.dragStart = null;

        // Drawing state
        this.drawMode = false;  // Are we currently drawing a new spline?
        this.hoveredPoint = null;

        // Canvas for drawing (created on first draw)
        this.canvas = null;
        this.ctx = null;

        // Parse initial value
        if (value) {
            try {
                const data = JSON.parse(value);
                this.splines = (data.splines || []).map(s => BezierSpline.fromJSON(s));
            } catch (e) {
                console.warn("Failed to parse spline data:", e);
            }
        }

        // Widget properties for ComfyUI
        this.type = "BEZIER_DRAWING";
        this.value = this.serializeSplines();
        this.options = {};
        this.serialize = true;
    }

    serializeSplines() {
        return JSON.stringify({
            splines: this.splines.map(s => s.toJSON())
        });
    }

    updateValue() {
        this.value = this.serializeSplines();
        if (this.callback) {
            this.callback(this.value);
        }
    }

    // Convert widget coords to canvas coords
    widgetToCanvas(x, y) {
        const rect = this.canvas.getBoundingClientRect();
        return {
            x: x - rect.left,
            y: y - rect.top
        };
    }

    // Find point near cursor (for selection)
    findNearPoint(x, y, threshold = 10) {
        for (let i = 0; i < this.splines.length; i++) {
            const spline = this.splines[i];
            for (let j = 0; j < spline.points.length; j++) {
                const p = spline.points[j];
                const dist = Math.sqrt((p.x - x) ** 2 + (p.y - y) ** 2);
                if (dist < threshold) {
                    return { splineIdx: i, pointIdx: j, type: 'point' };
                }

                // Check handles
                const handleInX = p.x + p.handleIn.x;
                const handleInY = p.y + p.handleIn.y;
                const distIn = Math.sqrt((handleInX - x) ** 2 + (handleInY - y) ** 2);
                if (distIn < threshold) {
                    return { splineIdx: i, pointIdx: j, type: 'handleIn' };
                }

                const handleOutX = p.x + p.handleOut.x;
                const handleOutY = p.y + p.handleOut.y;
                const distOut = Math.sqrt((handleOutX - x) ** 2 + (handleOutY - y) ** 2);
                if (distOut < threshold) {
                    return { splineIdx: i, pointIdx: j, type: 'handleOut' };
                }
            }
        }
        return null;
    }

    onMouseDown(e) {
        if (!this.canvas) return;

        const pos = this.widgetToCanvas(e.clientX, e.clientY);

        // Check if clicking on existing point or handle
        const near = this.findNearPoint(pos.x, pos.y);

        if (near) {
            // Start dragging existing point/handle
            if (near.type === 'point') {
                this.selectedPoint = { splineIdx: near.splineIdx, pointIdx: near.pointIdx };
                this.selectedHandle = null;
            } else if (near.type === 'handleIn' || near.type === 'handleOut') {
                this.selectedHandle = {
                    splineIdx: near.splineIdx,
                    pointIdx: near.pointIdx,
                    handle: near.type === 'handleIn' ? 'in' : 'out'
                };
                this.selectedPoint = null;
            }
            this.dragging = true;
            this.dragStart = pos;
        } else if (this.drawMode) {
            // Add new point to current spline
            if (!this.currentSpline) {
                this.currentSpline = new BezierSpline();
            }
            this.currentSpline.addPoint(pos.x, pos.y);
            this.render();
        }
    }

    onMouseMove(e) {
        if (!this.canvas) return;

        const pos = this.widgetToCanvas(e.clientX, e.clientY);

        if (this.dragging && this.dragStart) {
            const dx = pos.x - this.dragStart.x;
            const dy = pos.y - this.dragStart.y;

            if (this.selectedPoint) {
                // Move point
                const spline = this.splines[this.selectedPoint.splineIdx];
                const point = spline.points[this.selectedPoint.pointIdx];
                point.x += dx;
                point.y += dy;
            } else if (this.selectedHandle) {
                // Move handle
                const spline = this.splines[this.selectedHandle.splineIdx];
                const point = spline.points[this.selectedHandle.pointIdx];

                if (this.selectedHandle.handle === 'in') {
                    point.handleIn.x += dx;
                    point.handleIn.y += dy;

                    // If smooth, mirror to out handle
                    if (point.smooth) {
                        point.handleOut.x = -point.handleIn.x;
                        point.handleOut.y = -point.handleIn.y;
                    }
                } else {
                    point.handleOut.x += dx;
                    point.handleOut.y += dy;

                    // If smooth, mirror to in handle
                    if (point.smooth) {
                        point.handleIn.x = -point.handleOut.x;
                        point.handleIn.y = -point.handleOut.y;
                    }
                }
            }

            this.dragStart = pos;
            this.render();
            this.updateValue();
        } else {
            // Update hover state
            this.hoveredPoint = this.findNearPoint(pos.x, pos.y);
            this.render();
        }
    }

    onMouseUp(e) {
        this.dragging = false;
        this.dragStart = null;
    }

    onKeyDown(e) {
        // Enter or clicking first point again = close spline
        if (e.key === 'Enter' && this.currentSpline && this.currentSpline.points.length > 0) {
            this.currentSpline.closed = true;
            this.splines.push(this.currentSpline);
            this.currentSpline = null;
            this.drawMode = false;
            this.updateValue();
            this.render();
        }

        // Escape = cancel current spline
        if (e.key === 'Escape' && this.drawMode) {
            this.currentSpline = null;
            this.drawMode = false;
            this.render();
        }

        // Delete = remove selected point
        if (e.key === 'Delete' && this.selectedPoint) {
            const spline = this.splines[this.selectedPoint.splineIdx];
            spline.points.splice(this.selectedPoint.pointIdx, 1);
            this.selectedPoint = null;
            this.updateValue();
            this.render();
        }
    }

    render() {
        if (!this.ctx) return;

        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw all splines
        this.splines.forEach((spline, idx) => {
            this.drawSpline(spline, idx);
        });

        // Draw current spline being drawn
        if (this.currentSpline) {
            this.ctx.strokeStyle = '#00ff00';
            this.ctx.lineWidth = 2;
            this.drawSpline(this.currentSpline, -1);
        }
    }

    drawSpline(spline, splineIdx) {
        if (spline.points.length === 0) return;

        const ctx = this.ctx;
        const isSelected = this.selectedPoint && this.selectedPoint.splineIdx === splineIdx;

        // Draw Bezier curve
        ctx.beginPath();
        ctx.strokeStyle = isSelected ? '#00aaff' : '#ffffff';
        ctx.lineWidth = 2;

        const firstPoint = spline.points[0];
        ctx.moveTo(firstPoint.x, firstPoint.y);

        for (let i = 0; i < spline.points.length - 1; i++) {
            const p0 = spline.points[i];
            const p1 = spline.points[i + 1];

            const cp1x = p0.x + p0.handleOut.x;
            const cp1y = p0.y + p0.handleOut.y;
            const cp2x = p1.x + p1.handleIn.x;
            const cp2y = p1.y + p1.handleIn.y;

            ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, p1.x, p1.y);
        }

        // Close path if closed
        if (spline.closed && spline.points.length > 2) {
            const lastPoint = spline.points[spline.points.length - 1];
            const cp1x = lastPoint.x + lastPoint.handleOut.x;
            const cp1y = lastPoint.y + lastPoint.handleOut.y;
            const cp2x = firstPoint.x + firstPoint.handleIn.x;
            const cp2y = firstPoint.y + firstPoint.handleIn.y;

            ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, firstPoint.x, firstPoint.y);
            ctx.closePath();
        }

        ctx.stroke();

        // Draw control points and handles
        spline.points.forEach((p, idx) => {
            const isPointSelected = isSelected && this.selectedPoint.pointIdx === idx;
            const isHovered = this.hoveredPoint &&
                             this.hoveredPoint.splineIdx === splineIdx &&
                             this.hoveredPoint.pointIdx === idx;

            // Draw handles
            if (isPointSelected || isHovered) {
                // Handle lines
                ctx.beginPath();
                ctx.strokeStyle = '#888888';
                ctx.lineWidth = 1;
                ctx.moveTo(p.x + p.handleIn.x, p.y + p.handleIn.y);
                ctx.lineTo(p.x, p.y);
                ctx.lineTo(p.x + p.handleOut.x, p.y + p.handleOut.y);
                ctx.stroke();

                // Handle points
                ctx.fillStyle = '#00ff00';
                ctx.fillRect(p.x + p.handleIn.x - 3, p.y + p.handleIn.y - 3, 6, 6);
                ctx.fillRect(p.x + p.handleOut.x - 3, p.y + p.handleOut.y - 3, 6, 6);
            }

            // Draw control point
            ctx.fillStyle = isPointSelected ? '#00aaff' : (isHovered ? '#ffff00' : '#ffffff');
            ctx.fillRect(p.x - 4, p.y - 4, 8, 8);
        });
    }

    draw(ctx, node, widgetWidth, y, widgetHeight) {
        // Create canvas if needed
        if (!this.canvas) {
            this.canvas = document.createElement('canvas');
            this.canvas.width = widgetWidth - 30;
            this.canvas.height = 300;
            this.canvas.style.border = '1px solid #444';
            this.canvas.style.backgroundColor = '#222';
            this.ctx = this.canvas.getContext('2d');

            // Event listeners
            this.canvas.addEventListener('mousedown', this.onMouseDown.bind(this));
            this.canvas.addEventListener('mousemove', this.onMouseMove.bind(this));
            this.canvas.addEventListener('mouseup', this.onMouseUp.bind(this));
            document.addEventListener('keydown', this.onKeyDown.bind(this));

            // Add to DOM (will be positioned by LiteGraph)
            document.body.appendChild(this.canvas);
        }

        // Position canvas (LiteGraph handles this)
        const canvasY = y + 20;
        this.canvas.style.position = 'absolute';
        this.canvas.style.left = `${node.pos[0] + 15}px`;
        this.canvas.style.top = `${node.pos[1] + canvasY}px`;

        // Render current splines
        this.render();

        return y + 320;  // Return new Y position (widget height)
    }
}

// Register the widget with ComfyUI
app.registerExtension({
    name: "Detonate.RotoBezier",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "DetonateRotoBezier") {
            // Add custom widget for spline drawing
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;

                // Replace string widget with custom drawing widget
                const splineWidget = this.widgets.find(w => w.name === "spline_data");
                if (splineWidget) {
                    const bezierWidget = new BezierDrawingWidget(this, "spline_data", splineWidget.value);
                    const widgetIndex = this.widgets.indexOf(splineWidget);
                    this.widgets[widgetIndex] = bezierWidget;

                    // Add toolbar buttons
                    this.addWidget("button", "Start Drawing", null, () => {
                        bezierWidget.drawMode = true;
                        bezierWidget.currentSpline = new BezierSpline();
                    });

                    this.addWidget("button", "Clear All", null, () => {
                        bezierWidget.splines = [];
                        bezierWidget.currentSpline = null;
                        bezierWidget.updateValue();
                        bezierWidget.render();
                    });

                    // Phase 1.5: Preset shape generators
                    this.addWidget("button", "Add Circle", null, () => {
                        const cx = bezierWidget.canvas.width / 2;
                        const cy = bezierWidget.canvas.height / 2;
                        const radius = Math.min(cx, cy) * 0.5;
                        const circle = BezierSpline.createCircle(cx, cy, radius);
                        bezierWidget.splines.push(circle);
                        bezierWidget.updateValue();
                        bezierWidget.render();
                    });

                    this.addWidget("button", "Add Rectangle", null, () => {
                        const cx = bezierWidget.canvas.width / 2;
                        const cy = bezierWidget.canvas.height / 2;
                        const width = bezierWidget.canvas.width * 0.6;
                        const height = bezierWidget.canvas.height * 0.5;
                        const rect = BezierSpline.createRectangle(cx, cy, width, height);
                        bezierWidget.splines.push(rect);
                        bezierWidget.updateValue();
                        bezierWidget.render();
                    });

                    this.addWidget("button", "Add Star", null, () => {
                        const cx = bezierWidget.canvas.width / 2;
                        const cy = bezierWidget.canvas.height / 2;
                        const outerRadius = Math.min(cx, cy) * 0.6;
                        const innerRadius = outerRadius * 0.4;
                        const star = BezierSpline.createStar(cx, cy, outerRadius, innerRadius, 5);
                        bezierWidget.splines.push(star);
                        bezierWidget.updateValue();
                        bezierWidget.render();
                    });
                }

                return r;
            };
        }
    }
});

console.log("✅ Detonate RotoBezier widget loaded");
