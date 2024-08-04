export class Highlighter {
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
		this.startCoordinates = { x: 0, y: 0 };
		this.prevRectCoords = { x1: 0, y1: 0, x2: 0, y2: 0 };
		this.rectsList = [];

		this.mousemove = this.mousemove.bind(this);
		this.mousedown = this.mousedown.bind(this);
		this.mousedown_ = this.mousedown_.bind(this);
	}


	mousemove(e) {
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

	mousedown(e) {
		this.startCoordinates.x = e.clientX - this.canvasRect.left;
		this.startCoordinates.y = e.clientY - this.canvasRect.top;
		this.canvas.removeEventListener("mousedown", this.mousedown);
		this.canvas.addEventListener("mousemove", this.mousemove);
		this.canvas.addEventListener("mousedown", this.mousedown_);
	}

	mousedown_(_) {
		this.rectsList.push({
			x1: this.prevRectCoords.x1, y1: this.prevRectCoords.y1,
			x2: this.prevRectCoords.x2, y2: this.prevRectCoords.y2
		});
		this.canvas.removeEventListener("mousedown", this.mousedown_);
		this.canvas.removeEventListener("mousemove", this.mousemove);
		this.canvas.addEventListener("mousedown", this.mousedown);
		this.prevRectCoords = { x1: 0, y1: 0, x2: 0, y2: 0 };
	}

}
