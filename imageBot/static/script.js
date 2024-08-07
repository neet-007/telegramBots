import { Ellipse } from "./ellipse.js";
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
/**
 * @type {HTMLButtonElement}
 */
const eraserButton = document.getElementById("eraser");

let command = undefined;
let mode = undefined;

const SHAPES = {
	rect: [[], []],
	ellipse: [[], []]
}

function deleteShapes(shape, index) {
	canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
	SHAPES[shape][0].splice(index);
	Object.values(SHAPES)
		.forEach(shape => {
			shape[0].forEach(path => {
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
	ellipse: new Ellipse(canvas, canvasCtx, canvasRect, SHAPES, deleteShapes, addShape)
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
	command = newCommand;
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
	/*
	rectButton.onpointerdown = () => {
		removerCurrentEventListners("rect")
		canvas.addEventListener("pointerdown", COMMANDS.rect.pointerdown)
	};
	ellipseButton.onpointerdown = () => {
		removerCurrentEventListners("ellipse")
		canvas.addEventListener("pointerdown", COMMANDS.ellipse.pointerdown)
	};
	*/
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

