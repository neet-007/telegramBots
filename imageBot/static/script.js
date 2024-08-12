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
let mode = [undefined, -1, "black"];
let shapesNum = 0;
let cropRect = [undefined, undefined];

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
				shape_[0].forEach((path, index) => {
					console.log(shape_[1][index])
					canvasCtx.fillStyle = shape_[1][index] !== undefined ? shape_[1][index].fill : mode[2];
					canvasCtx.globalAlpha = 0.2;
					canvasCtx.fill(path);
					canvasCtx.globalAlpha = 1.0;
				})
			}
		})
}


function addShape(shape, coords) {
	SHAPES[shape][1].push({ ...coords, mode: mode[0], fill: mode[2] });
	shapesNum += 1;
	console.log(shapesNum);
	if (mode[0] === "crop") {
		cropRect[0] = SHAPES[shape][0][SHAPES[shape][0].length - 1];
		cropRect[1] = { ...coords };
	}
}

const COMMANDS = {
	rect: new Rect(canvas, canvasCtx, canvasRect, SHAPES, deleteShapes, addShape, mode),
	circle: new Circle(canvas, canvasCtx, canvasRect, SHAPES, deleteShapes, addShape, mode),
	ellipse: new Eliipse(canvas, canvasCtx, canvasRect, SHAPES, deleteShapes, addShape, mode),
	pen: new Pen(canvas, canvasCtx, canvasRect, SHAPES, deleteShapes, addShape),
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
			mode[2] = modesContainer.children[i].getAttribute("data-color", "black");
			canvasCtx.fillStyle = mode[2];
			console.log(mode)
			console.log(SHAPES)
		}
	}

	tele.ready();
	tele.expand();
	tele.MainButton.setText('make changes').show().onClick(function() {

		const data = { rect: [], circle: [], ellipse: [], pen: [], crop: { rect: [], circle: [], ellipse: [], pen: [] } };
		for (const key in SHAPES) {
			let deleteCount = 0;
			const len = SHAPES[key][1].length
			for (let i = 0; i < len; i++) {
				const { fill, ...val } = SHAPES[key][1][i - deleteCount];
				SHAPES[key][1][i - deleteCount] = val;
				if (val.mode === "crop") {
					data.crop[key].push(val);
					SHAPES[key][1].splice(i - deleteCount, 1);
					console.log(SHAPES[key][1])
					deleteCount++;
				}
			}
			console.log(SHAPES[key][1])
			data[key] = [...SHAPES[key][1]];
		}
		console.log(data);
		tele.sendData(JSON.stringify(data));
		tele.close();
	});
};

