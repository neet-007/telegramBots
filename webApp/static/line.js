export class Line {
	/**
		 * @param {HTMLButtonElement} button - The button element.
		 * @param {HTMLCanvasElement} canvas - The canvas element.
		 * @param {CanvasRenderingContext2D} canvasContext - The canvas rendering context.
		 * @param {function(string, number): void} deleteShapes - The function to delete a shape.
		 * @param {Object<string, [Path2D[], boolean]>} shapes - The shapes object.
	 */
	constructor(elem, canvas, canvasContext, deleteShapes, shapes, canvasRect) {
		this.elem = elem;
		this.canvas = canvas;
		this.canvasRect = canvasRect;
		this.canvasContext = canvasContext;
		this.deleteShapes = deleteShapes;
		this.shapes = shapes;
		this.startPoint = { x: 0, y: 0 };
		this.index = -1;

		this.mousedown = this.mousedown.bind(this);
		this.mousemove = this.mousemove.bind(this);
		this.mousedown_ = this.mousedown_.bind(this);
	}


	mousedown(e) {
		this.startPoint = { x: e.clientX - this.canvasRect.left, y: e.clientY - this.canvasRect.top };
		this.canvas.removeEventListener("mousedown", this.mousedown);
		this.canvas.addEventListener("mousemove", this.mousemove);
		this.canvas.addEventListener("mousedown", this.mousedown_);
	}
	mousemove(e) {
		const line = new Path2D();
		if (this.index > -1) {
			this.deleteShapes("line", this.index);
			this.canvasContext.closePath();
		}
		this.index = this.shapes["line"][0].length;

		this.canvasContext.beginPath();
		line.moveTo(this.startPoint.x, this.startPoint.y);
		this.canvasContext.lineWidth = 0.4;
		this.canvasContext.globalAlpha = 0.5;
		line.lineTo(e.clientX - this.canvasRect.left, e.clientY - this.canvasRect.top);
		this.shapes["line"][0].push(line);
		this.canvasContext.stroke(line);
		this.canvasContext.globalAlpha = 1.0;
	}
	mousedown_(e) {
		if (this.index > -1) {
			this.deleteShapes("line", this.index);
		}
		this.index = this.shapes["line"][0].length;

		const line = new Path2D();
		this.canvasContext.beginPath();
		line.moveTo(this.startPoint.x, this.startPoint.y);
		line.lineTo(e.clientX - this.canvasRect.left, e.clientY - this.canvasRect.top);
		this.shapes["line"][0].push(line);
		this.canvasContext.stroke(line);
		this.canvasContext.moveTo(e.clientX - this.canvasRect.left, e.clientY - this.canvasRect.top);
		this.canvas.removeEventListener("mousemove", this.mousemove);
		this.canvas.removeEventListener("mousedown", this.mousedown_);
		this.canvas.addEventListener("mousedown", this.mousedown);
		this.index = -1;
	}
}
