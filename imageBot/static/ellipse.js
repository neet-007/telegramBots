export class Eliipse {

	/**
	 *@param {HTMLCanvasElement} canvas 
	 *@param {CanvasRenderingContext2D} canvasCtx 
	 *@param {DOMRect} canvasRect 
	 * */
	constructor(canvas, canvasCtx, canvasRect, shapes, deleteShapes, addShape, mode) {
		this.canvas = canvas;
		this.canvasCtx = canvasCtx;
		this.canvasRect = canvasRect;
		this.start = { x: 0, y: 0 };
		this.index = -1;
		this.angle360 = (Math.PI + Math.PI) * (180 / Math.PI);
		this.shapes = shapes;
		this.deleteShapes = deleteShapes;
		this.addShape = addShape;
		this.mode = mode;
		this.lastCenter = { x: 0, y: 0 };
		this.lastRadiusX = 0;
		this.lastRadiusY = 0;

		this.pointerup = this.pointerup.bind(this);
		this.pointerdown = this.pointerdown.bind(this);
		this.pointermove = this.pointermove.bind(this);
	}

	/**
	 *@param {PointerEvent} e 
	 * */
	pointerdown(e) {
		e.preventDefault();
		this.canvas.removeEventListener("pointerdown", this.pointerdown);
		this.canvas.addEventListener("pointermove", this.pointermove);
		this.canvas.addEventListener("pointerup", this.pointerup)
		this.start = { x: e.clientX - this.canvasRect.left, y: e.clientY - this.canvasRect.top };
	}
	/**
	 *@param {PointerEvent} e 
	 * */
	pointermove(e) {
		e.preventDefault();
		if (this.index > -1) {
			this.deleteShapes("ellipse", this.index);
		}
		this.index = this.shapes.ellipse[0].length;

		this.canvasCtx.fillStyle = this.mode[2];
		this.canvasCtx.globalAlpha = 0.2;
		const ellipse = new Path2D();
		this.center = { x: (this.start.x + e.clientX - this.canvasRect.left) / 2, y: (this.start.y + e.clientY - this.canvasRect.top) / 2 };
		this.radiusX = Math.abs(this.start.x - e.clientX - this.canvasRect.left) / 2;
		this.radiusY = Math.abs(this.start.y - e.clientY - this.canvasRect.top) / 2;
		ellipse.ellipse(this.center.x, this.center.y, this.radiusX, this.radiusY, 0, 0, this.angle360);
		this.canvasCtx.fill(ellipse);
		this.canvasCtx.fillStyle = "black";
		this.canvasCtx.globalAlpha = 1.0;
		this.shapes.ellipse[0].push(ellipse);
	}
	/**
	 *@param {PointerEvent} e 
	 * */
	pointerup(e) {
		e.preventDefault();
		this.canvas.removeEventListener("pointerup", this.pointerup);
		this.canvas.removeEventListener("pointermove", this.pointermove);
		this.canvas.addEventListener("pointerdown", this.pointerdown);
		this.addShape("ellipse", { center: this.center, radiusX: this.radiusX, radiusY: this.radiusY });
		this.index = -1;
		console.log(this.shapes)
	}
}
