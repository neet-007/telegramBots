export class Highlighter {
	/**
		 * @param {HTMLButtonElement} button - The button element.
		 * @param {HTMLCanvasElement} canvas - The canvas element.
		 * @param {CanvasRenderingContext2D} context - The canvas rendering context.
		 * @param {function(string, number): void} deleteShapes - The function to delete a shape.
		 * @param {Object<string, [Path2D[], boolean]>} shapes - The shapes object.
	 */
	constructor(elem, canvas, canvasContext, deleteShapes, shapes, canvasRect) {
		this.elem = elem;
		this.canvas = canvas;
		this.canvasRect = canvasRect;
		this.canvasContext = canvasContext;
		this.startCoordinates = { x: 0, y: 0 };
		this.prevRectCoords = { x1: 0, y1: 0, x2: 0, y2: 0 };
		this.shaps = shapes;
		this.deleteShapes = deleteShapes;
		this.index = -1;

		this.mousemove = this.mousemove.bind(this);
		this.mousedown = this.mousedown.bind(this);
		this.mousedup = this.mousedup.bind(this);
	}


	mousemove(e) {
		if (this.index > -1) {
			this.deleteShapes("highlight", this.index);
		}
		this.index = this.shaps["highlight"][0].length;

		this.canvasContext.globalAlpha = 0.2;
		this.prevRectCoords = {
			x1: this.startCoordinates.x, y1: this.startCoordinates.y,
			x2: e.clientX - this.canvasRect.left - this.startCoordinates.x, y2: e.clientY - this.canvasRect.top - this.startCoordinates.y
		};
		const rect = new Path2D();
		rect.rect(this.prevRectCoords.x1, this.prevRectCoords.y1,
			this.prevRectCoords.x2, this.prevRectCoords.y2);
		this.canvasContext.fill(rect);
		this.shaps["highlight"][0].push(rect);
		this.canvasContext.globalAlpha = 1.0;
	}

	mousedown(e) {
		this.startCoordinates.x = e.clientX - this.canvasRect.left;
		this.startCoordinates.y = e.clientY - this.canvasRect.top;
		this.canvas.removeEventListener("mousedown", this.mousedown);
		this.canvas.addEventListener("mousemove", this.mousemove);
		this.canvas.addEventListener("mouseup", this.mousedup);
	}

	mousedup(_) {
		this.canvas.removeEventListener("mouseup", this.mousedup);
		this.canvas.removeEventListener("mousemove", this.mousemove);
		this.canvas.addEventListener("mousedown", this.mousedown);
		this.prevRectCoords = { x1: 0, y1: 0, x2: 0, y2: 0 };
		this.index = -1
	}

}
