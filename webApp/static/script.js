import { Highlighter } from "./highlighter.js";
import { Eraser } from "./eraser.js";
import { Line } from "./line.js";
import { Pen } from "./pen.js";

const tele = window.Telegram
const canvas = document.getElementById("main-canvas");
const canvasContext = canvas.getContext("2d");
const backgroundDiv = document.getElementById("background-div");

const buttonsContainer = document.getElementById("button-container");
const menuControlButton = document.getElementById("menu-control");
const highliteButton = document.getElementById("highlite-button");
const eraserButton = document.getElementById("eraser-button");
const lineButton = document.getElementById("line-button");
const penButton = document.getElementById("pen-button");
const ellipseButton = document.getElementById("ellipse-button");

let IS_MENU_OPEN = true;
let PREV_COMMAND = undefined;
let CURR_COMMAND = undefined;

menuControlButton.onclick = () => toggleMenu();
highliteButton.onclick = () => toggleCommands("highlight");
eraserButton.onclick = () => toggleCommands("erase");
lineButton.onclick = () => toggleCommands("line");
penButton.onclick = () => toggleCommands("pen");
ellipseButton.onclick = () => toggleCommands("ellipse");

backgroundDiv.style.backgroundImage = "url(/static/uploads/uploaded_img.jpg)";
backgroundDiv.style.backgroundSize = "cover";
backgroundDiv.style.backgroundRepeat = "no-repeat";
backgroundDiv.style.width = "387px";
backgroundDiv.style.height = "387px";
backgroundDiv.style.pointerEvents = "none";

const commandsObjects = {
	"highlight": new Highlighter(highliteButton, canvas, canvasContext),
	"erase": new Eraser(eraserButton, canvas, canvasContext),
	"line": new Line(lineButton, canvas, canvasContext),
	"pen": new Pen(penButton, canvas, canvasContext)
}

function removeEventListeners() {
	if (PREV_COMMAND === undefined) {
		return
	}
	console.log(commandsObjects[PREV_COMMAND])
	Object.getOwnPropertyNames(Object.getPrototypeOf(commandsObjects[PREV_COMMAND]))
		.filter(prop_ => typeof commandsObjects[PREV_COMMAND][prop_] === 'function').forEach(method => {
			console.log(typeof method)
			if (method !== "constructor") {
				canvas.removeEventListener(method.replace("_", ""), commandsObjects[PREV_COMMAND][method]);
			}
		})
}

function toggleMenu() {
	if (IS_MENU_OPEN) {
		buttonsContainer.style.maxHeight = `${menuControlButton.offsetHeight}px`;
		buttonsContainer.style.overflow = "hidden";
		IS_MENU_OPEN = false;
		return
	}
	buttonsContainer.removeAttribute("maxHeight")
	buttonsContainer.style.overflow = "visible";
	IS_MENU_OPEN = true;
}


function toggleCommands(command) {
	PREV_COMMAND = CURR_COMMAND;
	CURR_COMMAND = command;
	if (command === "highlight") {
		removeEventListeners();
		canvas.addEventListener("mousedown", commandsObjects.highlight.mousedown);
	} else if (command === "erase") {
		removeEventListeners();
		canvas.addEventListener("mousedown", commandsObjects.erase.mousedown);
	} else if (command === "line") {
		removeEventListeners();
		canvas.addEventListener("mousedown", commandsObjects.line.mousedown);
	} else if (command === "pen") {
		removeEventListeners();
		canvas.addEventListener("mousedown", commandsObjects.pen.mousedown);
	} else if (command === "ellipse") {

	} else {
		console.error("command is not supported");
	}
}

tele.WebApp.ready();
configureMainButton({ text: "do something", color: "#2045dc ", textColor: "#ffffff", onClick: () => alert("hi") })
tele.WebApp.MainButton.show();
tele.WebApp.expand();


function configureMainButton(options) {
	tele.WebApp.MainButton.text = options.text;
	tele.WebApp.MainButton.color = options.color;
	tele.WebApp.MainButton.textColor = options.textColor;
	tele.WebApp.MainButton.onClick(options.onClick);
}
