export class Pen {

	/**
	 *@param {HTMLCanvasElement} canvas 
	 *@param {CanvasRenderingContext2D} canvasCtx 
	 *@param {DOMRect} canvasRect 
	 * */
	constructor(canvas, canvasCtx, canvasRect) {
		this.canvas = canvas;
		this.canvasCtx = canvasCtx;
		this.canvasRect = canvasRect;

		this.mousedown = this.mousedown.bind(this);
		this.mousemove = this.mousemove.bind(this);
		this.mouseup = this.mouseup.bind(this);
	}
}
