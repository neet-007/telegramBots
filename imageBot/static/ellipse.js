export class Ellipse {

	/**
	 *@param {HTMLCanvasElement} canvas 
	 *@param {CanvasRenderingContext2D} canvasCtx 
	 *@param {DOMRect} canvasRect 
	 * */
	constructor(canvas, canvasCtx, canvasRect) {
		this.canvas = canvas;
		this.canvasCtx = canvasCtx;
		this.canvasRect = canvasRect;
		this.center = { x: 0, y: 0 };
		this.index = -1;
		this.angle360 = (Math.PI + Math.PI) * (180 / Math.PI);

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
		this.center = { x: e.clientX - this.canvasRect.left, y: e.clientY - this.canvasRect.top };
	}
	/**
	 *@param {PointerEvent} e 
	 * */
	pointermove(e) {
		e.preventDefault();
		this.canvasCtx.globalAlpha = 0.2;
		const ellipse = new Path2D();
		const radius = Math.sqrt(Math.pow(e.clientX - this.canvasRect.left - this.center.x, 2)
			+ Math.pow(e.clientY - this.canvasRect.top - this.center.y, 2));
		ellipse.arc(this.center.x, this.center.y, radius, 0, this.angle360);
		this.canvasCtx.fill(ellipse);
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
