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

		this.handleCanvasMouseDownPen = this.handleCanvasMouseDownPen.bind(this);
		this.handleCanvasMouseMovePen = this.handleCanvasMouseMovePen.bind(this);
		this.handleCanvasMouseUpPen = this.handleCanvasMouseUpPen.bind(this);
	}


	handleCanvasMouseDownPen(e) {
		this.canvasContext.beginPath();
		this.canvasContext.moveTo(e.clientX - this.canvasRect.left, e.clientY - this.canvasRect.top);
		this.canvas.removeEventListener("mousedown", this.handleCanvasMouseDownPen);
		this.canvas.addEventListener("mousemove", this.handleCanvasMouseMovePen);
		this.canvas.addEventListener("mouseup", this.handleCanvasMouseUpPen);
	}
	handleCanvasMouseMovePen(e) {
		this.canvasContext.lineTo(e.clientX - this.canvasRect.left, e.clientY - this.canvasRect.top);
		this.canvasContext.stroke();
	}
	handleCanvasMouseUpPen(_) {
		this.canvas.removeEventListener("mouseup", this.handleCanvasMouseUpPen);
		this.canvas.removeEventListener("mousemove", this.handleCanvasMouseMovePen);
		this.canvas.addEventListener("mousedown", this.handleCanvasMouseDownPen);
	}
}
