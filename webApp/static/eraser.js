export class Eraser {
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

		this.mousedown = this.mousedown.bind(this);
		this.mousemove = this.mousemove.bind(this);
		this.mouseup = this.mouseup.bind(this);
	}


	mousedown(e) {
		const rect = { x1: e.clientX - this.canvasRect.left, y1: e.clientY - this.canvasRect.top, x2: 50, y2: 50 };
		this.canvasContext.clearRect(rect.x1, rect.y1, rect.x2, rect.y2);
		this.shapes["erase"][0].push(rect);
		this.canvas.removeEventListener("mousedown", this.mousedown);
		this.canvas.addEventListener("mousemove", this.mousemove);
		this.canvas.addEventListener("mouseup", this.mouseup);
	}
	mousemove(e) {
		const rect = { x1: e.clientX - this.canvasRect.left, y1: e.clientY - this.canvasRect.top, x2: 50, y2: 50 };
		this.canvasContext.clearRect(rect.x1, rect.y1, rect.x2, rect.y2);
		this.shapes["erase"][0].push(rect);
	}
	mouseup(_) {
		this.canvas.removeEventListener("mouseup", this.mouseup);
		this.canvas.removeEventListener("mousemove", this.mousemove);
		this.canvas.addEventListener("mousedown", this.mousedown);
	}
}
