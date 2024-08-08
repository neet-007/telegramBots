import { Ellipse } from "./ellipse.js";
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
 */
const penButton = document.getElementById("pen");

let command = [undefined, -1];
let mode = [undefined, -1];

const SHAPES = {
	rect: [[], []],
	ellipse: [[], []],
	pen: [[], []]
}

function deleteShapes(shape, index) {
	canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
	if (index > -1) {
		SHAPES[shape][0].splice(index);
	}
	Object.values(SHAPES)
		.forEach(shape_ => {
			shape_[0].forEach(path => {
				canvasCtx.globalAlpha = 0.2;
				canvasCtx.fill(path);
				canvasCtx.globalAlpha = 1.0;
			})
		})
}

function addShape(shape, coords) {
	SHAPES[shape][1].push({ ...coords, mode });
}

const COMMANDS = {
	rect: new Rect(canvas, canvasCtx, canvasRect, SHAPES, deleteShapes, addShape),
	ellipse: new Ellipse(canvas, canvasCtx, canvasRect, SHAPES, deleteShapes, addShape),
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
		menuContainer.children[i].onpointerdown = () => {
			if (menuContainer.children[i].disabled) {
				return
			}
			menuContainer.children[i].setAttribute("data-state", "active");
			if (command[1] > -1) {
				menuContainer.children[command[1]].setAttribute("data-state", "not");
			}

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
		modesContainer.children[i].onpointerdown = () => {
			if (mode[0] === undefined) {
				for (let i = 0; i < menuContainer.children.length; i++) {
					menuContainer.children[i].disabled = false;
				}
			}

			modesContainer.children[i].setAttribute("data-state", "active");
			if (mode[1] > -1) {
				modesContainer.children[mode[1]].setAttribute("data-state", "not");
			}
			mode[0] = modesContainer.children[i].id;
			mode[1] = i;
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

