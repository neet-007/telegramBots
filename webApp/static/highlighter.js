export class Highlighter {
	/**
	 *@param {HTMLButtonElement} elem 
	 *@param {HTMLCanvasElement} canvas
	 *@param {CanvasRenderingContext2D} canvasContext 
	 */
	constructor(elem, canvas, canvasContext) {
		console.log(elem)
		console.log(canvas)
		console.log(canvasContext)
		this.elem = elem;
		this.canvas = canvas;
		this.canvasRect = canvas.getBoundingClientRect();
		this.canvasContext = canvasContext;
		this.startCoordinates = { x: 0, y: 0 };
		this.prevRectCoords = { x1: 0, y1: 0, x2: 0, y2: 0 };
		this.rectsList = [];

		this.handleCanvasMouseMove = this.handleCanvasMouseMove.bind(this);
		this.handleCanvasMouseDown = this.handleCanvasMouseDown.bind(this);
		this.handleCanvasMouseDownEnd = this.handleCanvasMouseDownEnd.bind(this);
	}


	handleCanvasMouseMove(e) {
		this.canvasContext.globalAlpha = 0.2;
		this.canvasContext.clearRect(this.prevRectCoords.x1, this.prevRectCoords.y1, this.prevRectCoords.x2, this.prevRectCoords.y2);
		this.prevRectCoords = {
			x1: this.startCoordinates.x, y1: this.startCoordinates.y,
			x2: e.clientX - this.canvasRect.left - this.startCoordinates.x, y2: e.clientY - this.canvasRect.top - this.startCoordinates.y
		};
		this.canvasContext.fillRect(this.prevRectCoords.x1, this.prevRectCoords.y1,
			this.prevRectCoords.x2, this.prevRectCoords.y2);
		this.canvasContext.globalAlpha = 1.0;
	}

	handleCanvasMouseDown(e) {
		console.log(this.canvas)
		this.startCoordinates.x = e.clientX - this.canvasRect.left;
		this.startCoordinates.y = e.clientY - this.canvasRect.top;
		this.canvas.removeEventListener("mousedown", this.handleCanvasMouseDown);
		this.canvas.addEventListener("mousemove", this.handleCanvasMouseMove);
		this.canvas.addEventListener("mousedown", this.handleCanvasMouseDownEnd);
	}

	handleCanvasMouseDownEnd(_) {
		this.rectsList.push({
			x1: this.prevRectCoords.x1, y1: this.prevRectCoords.y1,
			x2: this.prevRectCoords.x2, y2: this.prevRectCoords.y2
		});
		this.canvas.removeEventListener("mousedown", this.handleCanvasMouseDownEnd);
		this.canvas.removeEventListener("mousemove", this.handleCanvasMouseMove);
		this.canvas.addEventListener("mousedown", this.handleCanvasMouseDown);
		this.prevRectCoords = { x1: 0, y1: 0, x2: 0, y2: 0 };
	}

}
