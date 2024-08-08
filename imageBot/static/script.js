import { Ellipse } from "./ellipse.js";
import { Eraser } from "./eraser.js";
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

let command = undefined;
let mode = undefined;

const SHAPES = {
	rect: [[], []],
	ellipse: [[], []]
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
	eraser: new Eraser(canvas, canvasCtx, canvasRect, SHAPES, deleteShapes)
};

function removerCurrentEventListners(newCommand) {
	if (command !== undefined) {
		Object.getOwnPropertyNames(Object.getPrototypeOf(COMMANDS[command]))
			.filter(prop => typeof (COMMANDS[command][prop] === "function"))
			.forEach(method => {
				if (method !== 'constructor') {
					canvas.removeEventListener(method, COMMANDS[command][method])
				}
			})
	}
	if (newCommand !== "cursor") {
		command = newCommand;
	}
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
			removerCurrentEventListners(menuContainer.children[i].id);
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
			if (mode === undefined) {
				for (let i = 0; i < menuContainer.children.length; i++) {
					menuContainer.children[i].disabled = false;
				}
			}
			mode = modesContainer.children[i].id;
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

