export class Pen {

	/**
	 *@param {HTMLCanvasElement} canvas 
	 *@param {CanvasRenderingContext2D} canvasCtx 
	 *@param {DOMRect} canvasRect 
	 * */
	constructor(canvas, canvasCtx, canvasRect, shapes, deleteShapes, addShape) {
		this.canvas = canvas;
		this.canvasCtx = canvasCtx;
		this.canvasRect = canvasRect;
		this.shapes = shapes;
		this.deleteShapes = deleteShapes;
		this.addShape = addShape;
		this.index = -1;
		this.path = undefined;
		this.start = { x: 0, y: 0 };
		this.stackTrace = [];

		this.pointerdown = this.pointerdown.bind(this);
		this.pointermove = this.pointermove.bind(this);
		this.pointerup = this.pointerup.bind(this);
	}

	/**
	 *@param {PointerEvent} e 
	 * */
	pointerdown(e) {
		this.canvas.removeEventListener("pointerdown", this.pointerdown);
		this.canvas.addEventListener("pointermove", this.pointermove);
		this.canvas.addEventListener("pointerup", this.pointerup);

		this.path = new Path2D();
		this.start = { x: e.clientX - this.canvas.left, y: e.clientY - this.canvasRect.top };
		this.path.moveTo(this.start.x, this.start.y);
	}

	/**
	 *@param {PointerEvent} e 
	 * */
	pointermove(e) {
		const coords = { x: e.clientX - this.canvasRect.left, y: e.clientY - this.canvasRect.top }
		this.path.lineTo(coords.x, coords.y);
		this.stackTrace.push(coords);
		this.canvasCtx.stroke(this.path);
	}

	/**
	 *@param {PointerEvent} e 
	 * */
	pointerup(_) {
		this.canvas.removeEventListener("pointerup", this.pointerup);
		this.canvas.removeEventListener("pointermove", this.pointermove);
		this.canvas.addEventListener("pointerdown", this.pointerdown);
		const newPath = new Path2D();
		newPath.moveTo(this.start.x, this.start.y);
		let condition = false;
		for (let i = 0; i < this.stackTrace.length; i++) {
			if (i === this.stackTrace.length - 1) {
				if (this.canvasCtx.isPointInStroke(newPath, this.stackTrace[i].x, this.stackTrace[i].y)) {
					condition = true;
					break;
				}
				else {
					alert("must close shape")
				}
			}
			newPath.lineTo(this.stackTrace[i].x, this.stackTrace[i].y);
			this.canvasCtx.stroke(newPath);
		}
		if (condition) {
			this.shapes.pen[0].push(newPath);
			this.addShape("pen", { a: newPath });
		}

		this.deleteShapes("pen", -1);
		this.start = { x: 0, y: 0 };
		this.stackTrace = [];
		this.path = undefined;
	}
}
