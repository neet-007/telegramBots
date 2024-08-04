export class Pen {
	/**
	 *@param {HTMLButtonElement} elem 
	 *@param {HTMLCanvasElement} canvas
	 *@param {CanvasRenderingContext2D} canvasContext 
	 */
	constructor(elem, canvas, canvasContext) {
		this.elem = elem;
		this.canvas = canvas;
		this.canvasRect = canvas.getBoundingClientRect();
		this.canvasContext = canvasContext;

		this.mousedown = this.mousedown.bind(this);
		this.mousemove = this.mousemove.bind(this);
		this.mouseup = this.mouseup.bind(this);
	}


	mousedown(e) {
		this.canvasContext.beginPath();
		this.canvasContext.moveTo(e.clientX - this.canvasRect.left, e.clientY - this.canvasRect.top);
		this.canvas.removeEventListener("mousedown", this.mousedown);
		this.canvas.addEventListener("mousemove", this.mousemove);
		this.canvas.addEventListener("mouseup", this.mouseup);
	}
	mousemove(e) {
		this.canvasContext.lineTo(e.clientX - this.canvasRect.left, e.clientY - this.canvasRect.top);
		this.canvasContext.stroke();
	}
	mouseup(_) {
		this.canvas.removeEventListener("mouseup", this.mouseup);
		this.canvas.removeEventListener("mousemove", this.mousemove);
		this.canvas.addEventListener("mousedown", this.mousedown);
	}
}
