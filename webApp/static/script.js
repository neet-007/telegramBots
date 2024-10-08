import { Highlighter } from "./highlighter.js";
import { Eraser } from "./eraser.js";
import { Line } from "./line.js";
import { Pen } from "./pen.js";
import { Ellipse } from "./ellipse.js";

const tele = window.Telegram
const canvas = document.getElementById("main-canvas");
const canvasRect = canvas.getBoundingClientRect();
/**
 *@type(CanvasRenderingContext2D)
 * */
const canvasContext = canvas.getContext("2d");
const backgroundDiv = document.getElementById("background-div");

const buttonsContainer = document.getElementById("button-container");
const buttonContainerRect = buttonsContainer.getBoundingClientRect();
const menuControlContainer = document.getElementById("menu-control-container");
const menuControlCollapseButton = document.getElementById("menu-control-collaps");
const menuControlMoveButton = document.getElementById("menu-control-move");
const highliteButton = document.getElementById("highlite-button");
const eraserButton = document.getElementById("eraser-button");
const lineButton = document.getElementById("line-button");
const penButton = document.getElementById("pen-button");
const ellipseButton = document.getElementById("ellipse-button");

let IS_MENU_OPEN = true;
let PREV_COMMAND = undefined;
let CURR_COMMAND = undefined;
const SHAPES = {
	"highlight": [[], 0.2, []],
	"line": [[], 1, []],
	"pen": [[], 1, []],
	"ellipse": [[], 0.2, []],
	"erase": [[], -1, []],
}

menuControlMoveButton.addEventListener("mousedown", handleMoveMenuDown);
menuControlCollapseButton.onclick = () => toggleMenu();
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

function handleMoveMenuDown(_) {
	menuControlMoveButton.removeEventListener("mousedown", handleMoveMenuDown);
	document.addEventListener("mousemove", handleMoveMenuMove);
	document.addEventListener("mouseup", handleMoveMenuUp);
}

function handleMoveMenuMove(e) {
	buttonsContainer.style.left = (e.clientX - buttonContainerRect.width) + "px";
	buttonsContainer.style.top = (e.clientY) + "px";
}

function handleMoveMenuUp(_) {
	document.removeEventListener("mousemove", handleMoveMenuMove);
	document.removeEventListener("mouseup", handleMoveMenuUp);
	menuControlMoveButton.addEventListener("mousedown", handleMoveMenuDown);
}

function deleteShape(command, index) {
	SHAPES[command][0].splice(index);
	canvasContext.clearRect(0, 0, canvas.width, canvas.height);
	Object.values(SHAPES).forEach(value => {
		if (value[1] === 1) {
			console.log("stroke")
			value[0].forEach(shape => {
				canvasContext.stroke(shape);
			})
		} else if (value[1] !== -1) {
			console.log("filll")
			value[0].forEach(shape => {
				canvasContext.globalAlpha = value[1];
				canvasContext.fill(shape);
				canvasContext.globalAlpha = 1.0;

			})
		} else if (command === "highlight" || command === "ellipse") {
			console.log("eraaaase")
			value[0].forEach(shape => {
				canvasContext.globalCompositeOperation = "destination-out";
				canvasContext.fill(shape);
				canvasContext.globalCompositeOperation = "source-over";
			})
		}
	})
}

const commandsObjects = {
	"highlight": new Highlighter(highliteButton, canvas, canvasContext, deleteShape, SHAPES, canvasRect),
	"erase": new Eraser(eraserButton, canvas, canvasContext, SHAPES, canvasRect),
	"line": new Line(lineButton, canvas, canvasContext, deleteShape, SHAPES, canvasRect),
	"pen": new Pen(penButton, canvas, canvasContext, SHAPES, canvasRect),
	"ellipse": new Ellipse(ellipseButton, canvas, canvasContext, deleteShape, SHAPES, canvasRect)
}

function removeEventListeners() {
	if (PREV_COMMAND === undefined) {
		return
	}

	Object.getOwnPropertyNames(Object.getPrototypeOf(commandsObjects[PREV_COMMAND]))
		.filter(prop_ => typeof commandsObjects[PREV_COMMAND][prop_] === 'function').forEach(method => {
			if (method !== "constructor") {
				canvas.removeEventListener(method.replace("_", ""), commandsObjects[PREV_COMMAND][method]);
			}
		})
}

function toggleMenu() {
	if (IS_MENU_OPEN) {
		buttonsContainer.style.maxHeight = `${menuControlContainer.offsetHeight}px`;
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
	removeEventListeners();
	if (command === "highlight") {
		canvas.addEventListener("mousedown", commandsObjects.highlight.mousedown);
	} else if (command === "erase") {
		canvas.addEventListener("mousedown", commandsObjects.erase.mousedown);
	} else if (command === "line") {
		canvas.addEventListener("mousedown", commandsObjects.line.mousedown);
	} else if (command === "pen") {
		canvas.addEventListener("mousedown", commandsObjects.pen.mousedown);
	} else if (command === "ellipse") {
		canvas.addEventListener("mousedown", commandsObjects.ellipse.mousedown);
	} else {
		console.error("command is not supported");
	}
}

tele.WebApp.ready();
configureMainButton({ text: "finish drawing", color: "#2045dc ", textColor: "#ffffff", onClick: sendBotData })
tele.WebApp.MainButton.show();
tele.WebApp.expand();


function sendBotData() {
	const image = new Image();
	image.src = "/static/uploads/uploaded_img.jpg"
	image.onload = () => {
		// Create an output canvas
		const outCanvas = document.createElement("canvas");
		outCanvas.width = image.width;
		outCanvas.height = image.height;

		const outCanvasCtx = outCanvas.getContext("2d");

		// Draw the background image onto the output canvas
		outCanvasCtx.drawImage(image, 0, 0, outCanvas.width, outCanvas.height);

		// Draw the original canvas content onto the output canvas
		outCanvasCtx.drawImage(canvas, 0, 0);

		outCanvas.toBlob(function(blob) {
			const formData = new FormData();
			formData.append('image', blob, 'image.jpeg'); // You can give the file a name

			fetch('/upload', {
				method: 'POST',
				body: formData
			})
				.then(response => response.json())
				.then(data => {
					console.log('Success:', data);
					tele.WebApp.sendData(JSON.stringify({ fileName: data.fileName }))
				})
				.catch(error => {
					console.error('Error:', error);
				});
		}, 'image/JPEG'); // Specify the desired image format
	};
}

function configureMainButton(options) {
	tele.WebApp.MainButton.text = options.text;
	tele.WebApp.MainButton.color = options.color;
	tele.WebApp.MainButton.textColor = options.textColor;
	tele.WebApp.MainButton.onClick(options.onClick);
}
