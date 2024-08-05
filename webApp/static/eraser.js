export class Eraser {
	/**
		 * @param {HTMLButtonElement} button - The button element.
		 * @param {HTMLCanvasElement} canvas - The canvas element.
		 * @param {CanvasRenderingContext2D} context - The canvas rendering context.
		 * @param {Object<string, [Path2D[], boolean]>} shapes - The shapes object.
	 */
	constructor(elem, canvas, canvasContext, shapes, canvasRect) {
		this.elem = elem;
		this.canvas = canvas;
		this.canvasRect = canvasRect;
		this.canvasContext = canvasContext;
		this.shapes = shapes;
		this.index = -1;
		this.path = undefined;

		this.mousedown = this.mousedown.bind(this);
		this.mousemove = this.mousemove.bind(this);
		this.mouseup = this.mouseup.bind(this);
	}


	mousedown(e) {
		this.canvasContext.lineWidth = 50;
		this.path = new Path2D();
		this.path.moveTo(e.clientX - this.canvasRect.left, e.clientY - this.canvasRect.top);
		this.canvasContext.globalCompositeOperation = "destination-out";
		//this.canvasContext.clearRect(rect.x1, rect.y1, rect.x2, rect.y2);
		this.path.lineTo(e.clientX - this.canvasRect.left, e.clientY - this.canvasRect.top);
		this.canvasContext.fill(this.path);
		//this.shapes["erase"][0].push(rect);
		this.canvas.removeEventListener("mousedown", this.mousedown);
		this.canvas.addEventListener("mousemove", this.mousemove);
		this.canvas.addEventListener("mouseup", this.mouseup);
	}
	mousemove(e) {
		//this.canvasContext.clearRect(rect.x1, rect.y1, rect.x2, rect.y2);
		this.path.lineTo(e.clientX - this.canvasRect.left, e.clientY - this.canvasRect.top);
		this.canvasContext.fill(this.path);
	}
	mouseup(_) {
		this.shapes["erase"][0].push(this.path);
		this.index = this.shapes["erase"].length;
		this.path = undefined;
		this.canvas.removeEventListener("mouseup", this.mouseup);
		this.canvas.removeEventListener("mousemove", this.mousemove);
		this.canvas.addEventListener("mousedown", this.mousedown);
		this.canvasContext.globalCompositeOperation = "source-over";
		this.canvasContext.lineWidth = 1;
	}
}
