import { Circle } from "./circle.js";
import { Eliipse } from "./ellipse.js";
import { Eraser } from "./eraser.js";
import { Pen } from "./pen.js";
import { Rect } from "./rect.js";

const loader = document.createElement("h1");
loader.innerHTML = "loading";
document.body.appendChild(loader);

const tele = window.Telegram.WebApp
/**
 * @type {HTMLCanvasElement}
 */
const canvas = document.getElementById("main-canvas");
/**
 *@type {CanvasRenderingContext2D} 
 */
const canvasCtx = canvas.getContext("2d");
/**
 *@type {DOMRect}
 * */
const canvasRect = canvas.getBoundingClientRect();
/**
 *@type {HTMLDivElement}
*/
const canvasBg = document.getElementById("canvas-bg");
/**
 * @type {HTMLDivElement}
*/
const menuContainer = document.getElementById("menu-container");
/**
 * @type {HTMLDivElement}
*/
const modesContainer = document.getElementById("modes-container");
/**
 * @type {HTMLButtonElement}
 * */
const cropButton = document.getElementById("crop");


let command = [undefined, -1];
let mode = [undefined, -1];
let shapesNum = 0;
let cropRect = [undefined, undefined];
let scale = [1, 1];

const SHAPES = {
	rect: [[], [], false],
	circle: [[], [], false],
	pen: [[], [], true],
	ellipse: [[], [], false]
}

function deleteShapes(shape, index) {
	canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
	if (index > -1) {
		SHAPES[shape][0].splice(index);
	}
	if (shape === "eraser") {
		if (shapesNum === 1) {
			for (let i = 0; i < menuContainer.children.length; i++) {
				menuContainer.children[i].disabled = false;
			}
			for (let i = 0; i < modesContainer.children.length; i++) {
				modesContainer.children[i].disabled = false;
			}
		}
		shapesNum -= 1;
		console.log(shapesNum);
	}
	Object.values(SHAPES)
		.forEach(shape_ => {
			if (shape_[2]) {
				shape_[0].forEach(path => {
					canvasCtx.stroke(path);
				})

			} else {
				shape_[0].forEach(path => {
					canvasCtx.globalAlpha = 0.2;
					canvasCtx.fill(path);
					canvasCtx.globalAlpha = 1.0;
				})
			}
		})
}


function addShape(shape, coords) {
	if (mode[0] === "crop") {
		cropRect[0] = SHAPES[shape][0][SHAPES[shape][0].length - 1];
		cropRect[1] = { ...coords };
		SHAPES[shape][0].splice(SHAPES[shape][0].length - 1);

		if (command[0] === "rect") {
			const width = Math.abs(coords.x2 - coords.x1);
			const height = Math.abs(coords.y2 - coords.y1);
			scale[0] = canvas.width / width;
			scale[1] = canvas.height / height;

			canvasBg.style.backgroundPosition = `-${coords.x1}px -${coords.y1}px`;
			canvasBg.style.backgroundSize = `${scale[0] * 100}% ${scale[1] * 100}%`;

			canvasBg.style.width = `${width}px`;
			canvasBg.style.height = `${height}px`;
			canvas.width = `${width}`;
			canvas.height = `${height}`;
			canvasCtx.scale(scale[0], scale[1]);
		} else if (command[0] === "circle") {
			const radius = coords.radius;
			const center = coords.center;

			scale[0] = canvas.height / radius;
			scale[1] = canvas.height / radius;

			canvasBg.style.backgroundPosition = `-${center.x - radius}px -${center.y - radius}px`;
			canvasBg.style.backgroundSize = `${scale[0] * 100}% ${scale[1] * 100}%`;

			canvasBg.style.width = `${radius}px`;
			canvasBg.style.height = `${radius}px`;
			canvasBg.style.borderRadius = "50%";
			canvas.width = `${radius}`;
			canvas.height = `${radius}`;
			canvas.style.borderRadius = "50%"
			canvasCtx.scale(scale[0], scale[1]);
		}

		removerCurrentEventListners("cursor", command[1]);
		command[0] = undefined;
		mode[0] = undefined;
		cropButton.disabled = true;
		cropButton.setAttribute("data-state", "not");
	} else {
		SHAPES[shape][1].push({ ...coords, mode: mode[0] });
		shapesNum += 1;
		console.log(shapesNum);
	}
}

const COMMANDS = {
	rect: new Rect(canvas, canvasCtx, canvasRect, SHAPES, deleteShapes, addShape, scale),
	circle: new Circle(canvas, canvasCtx, canvasRect, SHAPES, deleteShapes, addShape, scale),
	ellipse: new Eliipse(canvas, canvasCtx, canvasRect, SHAPES, deleteShapes, addShape, scale),
	pen: new Pen(canvas, canvasCtx, canvasRect, SHAPES, deleteShapes, addShape, scale),
	eraser: new Eraser(canvas, canvasCtx, canvasRect, SHAPES, deleteShapes)
};

function removerCurrentEventListners(newCommand, index) {
	if (command[0] !== undefined) {
		Object.getOwnPropertyNames(Object.getPrototypeOf(COMMANDS[command[0]]))
			.filter(prop => typeof (COMMANDS[command[0]][prop] === "function"))
			.forEach(method => {
				if (method !== 'constructor') {
					canvas.removeEventListener(method, COMMANDS[command[0]][method])
				}
			})
	}
	if (newCommand !== "cursor") {
		command[0] = newCommand;
	}
	command[1] = index;
}

const image = new Image()
image.src = "static/uploads/uploaded_img.jpeg";

image.onload = () => {
	document.body.removeChild(loader);
	canvas.width = image.width;
	canvas.height = image.height;
	canvasBg.style.width = `${image.width}px`;
	canvasBg.style.height = `${image.height}px`;
	canvasBg.style.backgroundImage = `url(static/uploads/uploaded_img.jpeg)`;
	menuContainer.style.marginTop = `${canvas.height}px`;

	for (let i = 0; i < menuContainer.children.length; i++) {
		menuContainer.children[i].disabled = true;
		menuContainer.children[i].onclick = () => {
			if (menuContainer.children[i].disabled) {
				return
			}
			if (command[1] > -1) {
				menuContainer.children[command[1]].setAttribute("data-state", "not");
			}
			menuContainer.children[i].setAttribute("data-state", "active");

			removerCurrentEventListners(menuContainer.children[i].id, i);
			if (menuContainer.children[i].id === "eraser") {
				canvas.style.cursor = "pointer";
			} else if (menuContainer.children[i].id === "cursor") {
				canvas.style.cursor = "default";
				return
			} else {
				canvas.style.cursor = "crosshair";
			}
			canvas.addEventListener("pointerdown", COMMANDS[menuContainer.children[i].id].pointerdown);
		}
	}
	for (let i = 0; i < modesContainer.children.length; i++) {
		modesContainer.children[i].onclick = () => {
			if (mode[0] === undefined) {
				for (let i = 0; i < menuContainer.children.length; i++) {
					menuContainer.children[i].disabled = false;
				}
			}

			if (mode[1] > -1) {
				modesContainer.children[mode[1]].setAttribute("data-state", "not");
			}
			modesContainer.children[i].setAttribute("data-state", "active");

			mode[0] = modesContainer.children[i].id;
			mode[1] = i;
			console.log(mode)
			console.log(SHAPES)
		}
	}

	tele.ready();
	tele.expand();
	tele.MainButton.setText('make changes').show().onClick(function() {

		const data = {};
		for (const key in SHAPES) {
			data[key] = SHAPES[key][1];
		}
		console.log(data);
		tele.sendData(JSON.stringify(data));
		tele.close();
	});
};

