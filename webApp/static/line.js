export class Line {
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
		this.prevLineCoords = { x: 0, y: 0 };

		this.handleCanvasMouseDownLine = this.handleCanvasMouseDownLine.bind(this);
		this.handleCanvasMouseMoveLine = this.handleCanvasMouseMoveLine.bind(this);
		this.handleCanvasMouseDownLineAdd = this.handleCanvasMouseDownLineAdd.bind(this);
	}


	handleCanvasMouseDownLine(e) {
		this.canvasContext.beginPath();
		this.canvasContext.moveTo(e.clientX - this.canvasRect.left, e.clientY - this.canvasRect.top);
		this.canvasContext.lineWidth = 0.4;
		this.canvas.removeEventListener("mousedown", this.handleCanvasMouseDownLine);
		this.canvas.addEventListener("mousemove", this.handleCanvasMouseMoveLine);
		this.canvas.addEventListener("mousedown", this.handleCanvasMouseDownLineAdd);
	}
	handleCanvasMouseMoveLine(e) {
		this.canvasContext.clearRect(0, this.prevLineCoords.y - 1, this.canvas.width, 2);
		this.canvasContext.globalAlpha = 0.2;
		this.canvasContext.lineTo(e.clientX - this.canvasRect.left, e.clientY - this.canvasRect.top);
		this.canvasContext.globalAlpha = 1.0;
		this.canvasContext.stroke();
	}
	handleCanvasMouseDownLineAdd(e) {
		this.canvasContext.clearRect(0, this.prevLineCoords.y - 1, this.canvas.width, 2);
		this.prevLineCoords = { x: e.clientX - this.canvasRect.left, y: e.clientY - this.canvasRect.top };
		this.canvasContext.lineTo(this.prevLineCoords.x, this.prevLineCoords.y);
		this.canvasContext.stroke();
		this.canvasContext.moveTo(this.prevLineCoords.x, this.prevLineCoords.y);
		this.canvasContext.closePath();
		this.canvas.removeEventListener("mousemove", this.handleCanvasMouseMoveLine);
		this.canvas.removeEventListener("mousedown", this.handleCanvasMouseDownLineAdd);
		this.canvas.addEventListener("mousedown", this.handleCanvasMouseDownLine);
	}
}
