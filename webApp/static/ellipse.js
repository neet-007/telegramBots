export class Ellipse {
	/**
	 *@param {HTMLButtonElement} elem 
	 *@param {HTMLCanvasElement} canvas 
	 *@param {CanvasRenderingContext2D} canvasContext 
	 * */
	constructor(elem, canvas, canvasContext) {
		this.elem = elem;
		this.canvas = canvas;
		this.canvasRect = canvas.getBoundingClientRect();
		this.canvasContext = canvasContext;
		this.center = { x: 0, y: 0 };

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
		const radius = Math.sqrt(Math.pow(e.clientX - this.center.x - this.canvasRect.left, 2) +
			Math.pow(e.clientY - this.center.y - this.canvasRect.top, 2));
		this.canvasContext.globalAlpha = 0.2;
		this.canvasContext.arc(this.center.x, this.center.y, radius, 0, Math.PI + Math.PI);
		this.canvasContext.fill();
		this.canvasContext.globalAlpha = 1.0;
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
	}
}
