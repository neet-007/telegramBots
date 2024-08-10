export class Rect {

	/**
	 *@param {HTMLCanvasElement} canvas 
	 *@param {CanvasRenderingContext2D} canvasCtx 
	 *@param {DOMRect} canvasRect 
	 * */
	constructor(canvas, canvasCtx, canvasRect, shapes, deleteShapes, addShape, scale) {
		this.canvas = canvas;
		this.canvasCtx = canvasCtx;
		this.canvasRect = canvasRect;
		this.start = { x: 0, y: 0 };
		this.index = -1;
		this.shapes = shapes;
		this.deleteShapes = deleteShapes;
		this.addShape = addShape;
		this.lastCoords = { x: 0, y: 0 };
		this.scale = scale;

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
		this.start = { x: (e.clientX - this.canvasRect.left) / this.scale[0], y: (e.clientY - this.canvasRect.top) / this.scale[1] };
	}
	/**
	 *@param {PointerEvent} e 
	 * */
	pointermove(e) {
		e.preventDefault();
		if (this.index > -1) {
			this.deleteShapes("rect", this.index);
		}
		this.index = this.shapes.rect[0].length;

		this.canvasCtx.globalAlpha = 0.2;
		const rect = new Path2D();
		this.lastCoords = { x: (e.clientX - this.canvasRect.left) / this.scale[0], y: (e.clientY - this.canvasRect.top) / this.scale[1] };
		rect.rect(this.start.x, this.start.y, this.lastCoords.x - this.start.x, this.lastCoords.y - this.start.y);
		this.canvasCtx.fill(rect);
		this.canvasCtx.globalAlpha = 1.0;
		this.shapes.rect[0].push(rect);
	}
	/**
	 *@param {PointerEvent} e 
	 * */
	pointerup(e) {
		e.preventDefault();
		this.canvas.removeEventListener("pointerup", this.pointerup);
		this.canvas.removeEventListener("pointermove", this.pointermove);
		this.canvas.addEventListener("pointerdown", this.pointerdown);
		this.addShape("rect", { x1: this.start.x, y1: this.start.y, x2: this.lastCoords.x, y2: this.lastCoords.y });
		this.index = -1;
		console.log(this.shapes)
	}
}
