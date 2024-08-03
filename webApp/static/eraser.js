export class Eraser {
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

		this.handleCanvasMouseDownErase = this.handleCanvasMouseDownErase.bind(this);
		this.handleCanvasMouseMoveErase = this.handleCanvasMouseMoveErase.bind(this);
		this.handleCanvasMouseUpErase = this.handleCanvasMouseUpErase.bind(this);
	}


	handleCanvasMouseDownErase(e) {
		this.canvasContext.clearRect(e.clientX - this.canvasRect.left, e.clientY - this.canvasRect.top, 50, 50);
		this.canvas.removeEventListener("mousedown", this.handleCanvasMouseDownErase);
		this.canvas.addEventListener("mousemove", this.handleCanvasMouseMoveErase);
		this.canvas.addEventListener("mouseup", this.handleCanvasMouseUpErase);
	}
	handleCanvasMouseMoveErase(e) {
		this.canvasContext.clearRect(e.clientX - this.canvasRect.left, e.clientY - this.canvasRect.top, 50, 50);
	}
	handleCanvasMouseUpErase(_) {
		this.canvas.removeEventListener("mouseup", this.handleCanvasMouseUpErase);
		this.canvas.removeEventListener("mousemove", this.handleCanvasMouseMoveErase);
		this.canvas.addEventListener("mousedown", this.handleCanvasMouseDownErase);
	}
}
