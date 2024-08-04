export class Ellipse {
	/**
		 * @param {HTMLButtonElement} button - The button element.
		 * @param {HTMLCanvasElement} canvas - The canvas element.
		 * @param {CanvasRenderingContext2D} canvasContext - The canvas rendering context.
		 * @param {function(string, number): void} deleteShapes - The function to delete a shape.
		 * @param {Object<string, [Path2D[], boolean]>} shapes - The shapes object.
	 */
	constructor(elem, canvas, canvasContext, deleteShapes, shapes) {
		this.elem = elem;
		this.canvas = canvas;
		this.canvasRect = canvas.getBoundingClientRect();
		this.canvasContext = canvasContext;
		this.deleteShapes = deleteShapes;
		this.shapes = shapes;
		this.center = { x: 0, y: 0 };
		this.index = -1;

		this.mousedown = this.mousedown.bind(this);
		this.mousemove = this.mousemove.bind(this);
		this.mouseup = this.mouseup.bind(this);
	}

	/**
	 *@param {MouseEvent} e 
	 * */
	mousedown(e) {
		this.center = { x: e.clientX - this.canvasRect.left, y: e.clientY - this.canvasRect.top };
		this.canvas.removeEventListener("mousedown", this.mousedown);
		this.canvas.addEventListener("mousemove", this.mousemove);
		this.canvas.addEventListener("mouseup", this.mouseup);
		this.canvasContext.beginPath();
	}

	/**
	 *@param {MouseEvent} e 
	 * */
	mousemove(e) {
		if (this.index > -1) {
			this.deleteShapes("ellipse", this.index);
		}
		this.index = this.shapes["ellipse"][0].length;

		const arc = new Path2D();
		const radius = Math.sqrt(Math.pow(e.clientX - this.center.x - this.canvasRect.left, 2) +
			Math.pow(e.clientY - this.center.y - this.canvasRect.top, 2));

		this.canvasContext.globalAlpha = 0.2;

		arc.arc(this.center.x, this.center.y, radius, 0, Math.PI + Math.PI);
		this.canvasContext.fill(arc);
		this.canvasContext.globalAlpha = 1.0;
		this.shapes["ellipse"][0].push(arc);
	}

	/**
	 *@param {MouseEvent} e 
	 * */
	mouseup(_) {
		this.canvas.removeEventListener("mouseup", this.mouseup);
		this.canvas.removeEventListener("mousemove", this.mousemove);
		this.canvas.addEventListener("mousedown", this.mousedown);
		this.center = { x: 0, y: 0 };
		this.canvasContext.closePath();
		this.index = -1;
	}
}
