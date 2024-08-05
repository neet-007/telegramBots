export class Pen {
	/**
	 *@param {HTMLButtonElement} elem 
	 *@param {HTMLCanvasElement} canvas
	 *@param {CanvasRenderingContext2D} canvasContext 
	 * @param {Object<string, [Path2D[], boolean]>} shapes - The shapes object.
	 */
	constructor(elem, canvas, canvasContext, shapes, canvasRect) {
		this.elem = elem;
		this.canvas = canvas;
		this.canvasRect = canvasRect;
		this.canvasContext = canvasContext;
		this.shapes = shapes;
		this.index = -1;
		this.line = undefined;

		this.mousedown = this.mousedown.bind(this);
		this.mousemove = this.mousemove.bind(this);
		this.mouseup = this.mouseup.bind(this);
	}


	mousedown(e) {
		this.canvasContext.beginPath();
		this.line = new Path2D();
		this.line.moveTo(e.clientX - this.canvasRect.left, e.clientY - this.canvasRect.top);
		this.canvas.removeEventListener("mousedown", this.mousedown);
		this.canvas.addEventListener("mousemove", this.mousemove);
		this.canvas.addEventListener("mouseup", this.mouseup);
	}
	mousemove(e) {
		this.line.lineTo(e.clientX - this.canvasRect.left, e.clientY - this.canvasRect.top);
		this.canvasContext.stroke(this.line);
	}
	mouseup(_) {
		this.shapes["pen"][0].push(this.line);
		this.index = this.shapes["pen"].length;
		this.line = undefined;
		this.canvas.removeEventListener("mouseup", this.mouseup);
		this.canvas.removeEventListener("mousemove", this.mousemove);
		this.canvas.addEventListener("mousedown", this.mousedown);
	}
}
