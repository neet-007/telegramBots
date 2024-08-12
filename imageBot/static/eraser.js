export class Eraser {

	/**
	 *@param {HTMLCanvasElement} canvas 
	 *@param {CanvasRenderingContext2D} canvasCtx 
	 *@param {DOMRect} canvasRect 
	 * */
	constructor(canvas, canvasCtx, canvasRect, shapes, deleteShapes) {
		this.canvas = canvas;
		this.canvasCtx = canvasCtx;
		this.canvasRect = canvasRect;
		this.shapes = shapes;
		this.deleteShapes = deleteShapes;

		this.pointerdown = this.pointerdown.bind(this);
	}

	/**
	 *@param {PointerEvent} e 
	 * */
	pointerdown(e) {
		const shapesArr = Object.values(this.shapes);
		for (let i = 0; i < shapesArr.length; i++) {
			let swap = false;
			const pathsArr = shapesArr[i][0];
			for (let j = 0; j < pathsArr.length; j++) {
				if (this.canvasCtx.isPointInPath(pathsArr[j], e.clientX - this.canvasRect.left, e.clientY - this.canvasRect.top)) {
					pathsArr.splice(j, 1);
					shapesArr[i][1].splice(j, 1);
					swap = true;
					this.deleteShapes("eraser", -1);
					break;
				}
			}
			if (swap) {
				break;
			}
		}

	}
}
