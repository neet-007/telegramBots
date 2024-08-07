export class Rect {

	/**
	 *@param {HTMLCanvasElement} canvas 
	 *@param {CanvasRenderingContext2D} canvasCtx 
	 *@param {DOMRect} canvasRect 
	 * */
	constructor(canvas, canvasCtx, canvasRect) {
		this.canvas = canvas;
		this.canvasCtx = canvasCtx;
		this.canvasRect = canvasRect;
		this.start = { x: 0, y: 0 };
		this.index = -1;

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
		this.canvasCtx.globalAlpha = 0.2;
		const rect = new Path2D();
		rect.rect(this.start.x, this.start.y, e.clientX - this.canvasRect.left - this.start.x, e.clientY - this.canvasRect.top - this.start.y);
		this.canvasCtx.fill(rect);
		this.canvasCtx.globalAlpha = 1.0;
	}
	/**
	 *@param {PointerEvent} e 
	 * */
	pointerup(e) {
		e.preventDefault();
		this.canvas.removeEventListener("pointerup", this.pointerup);
		this.canvas.removeEventListener("pointermove", this.pointermove);
		this.canvas.addEventListener("pointerdown", this.pointerdown);
	}
}
