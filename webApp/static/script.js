
const tele = window.Telegram

const canvas = document.getElementById("main-canvas");
const canvasContext = canvas.getContext("2d");
const backgroundDiv = document.getElementById("background-div");
const canvasRect = canvas.getBoundingClientRect();

const buttonsContainer = document.getElementById("button-container");
const menuControlButton = document.getElementById("menu-control");
const highliteButton = document.getElementById("highlite-button");
const eraserButton = document.getElementById("eraser-button");
const lineButton = document.getElementById("line-button");
const penButton = document.getElementById("pen-button");
const ellipseButton = document.getElementById("ellipse-button");

let IS_MENU_OPEN = true;

menuControlButton.onclick = () => toggleCommands("menu");
highliteButton.onclick = () => toggleCommands("highlite");
eraserButton.onclick = () => toggleCommands("erase");
lineButton.onclick = () => toggleCommands("line");
penButton.onclick = () => toggleCommands("pen");
ellipseButton.onclick = () => toggleCommands("ellipse");


console.log(canvas)
console.log(canvasContext)

let startCoordinates = { x: 0, y: 0 };
let prevRectCoords = { x1: 0, y1: 0, x2: 0, y2: 0 };
let prevLineCoords = { x: 0, y: 0 };
let rectsList = [];
backgroundDiv.style.backgroundImage = "url(/static/uploads/uploaded_img.jpg)";
backgroundDiv.style.backgroundSize = "cover";
backgroundDiv.style.backgroundRepeat = "no-repeat";
backgroundDiv.style.width = "387px";
backgroundDiv.style.height = "387px";
backgroundDiv.style.pointerEvents = "none";

canvas.addEventListener("mousedown", handleCanvasMouseDown);

function toggleCommands(command) {
	if (command === "highlite") {
		canvas.removeEventListener("mousedown", handleCanvasMouseDownErase);
		canvas.addEventListener("mousedown", handleCanvasMouseDown);
	} else if (command === "erase") {
		canvas.removeEventListener("mousedown", handleCanvasMouseDownLine);
		canvas.removeEventListener("mousedown", handleCanvasMouseDownLineAdd);
		canvas.removeEventListener("mousemove", handleCanvasMouseMoveLine);
		canvas.removeEventListener("mousedown", handleCanvasMouseDown);
		canvas.removeEventListener("mousemove", handleCanvasMouseMove);
		canvas.addEventListener("mousedown", handleCanvasMouseDownErase);
	} else if (command === "line") {
		canvas.removeEventListener("mousedown", handleCanvasMouseDownErase);
		canvas.removeEventListener("mousedown", handleCanvasMouseDown);
		canvas.removeEventListener("mousemove", handleCanvasMouseMove);
		canvas.removeEventListener("mousemove", handleCanvasMouseMoveErase);
		canvas.addEventListener("mousedown", handleCanvasMouseDownLine);
	} else if (command === "pen") {
		canvas.removeEventListener("mousedown", handleCanvasMouseDownLine);
		canvas.removeEventListener("mousedown", handleCanvasMouseDownLineAdd);
		canvas.removeEventListener("mousemove", handleCanvasMouseMoveLine);
		canvas.removeEventListener("mousedown", handleCanvasMouseDown);
		canvas.removeEventListener("mousemove", handleCanvasMouseMove);
		canvas.removeEventListener("mousedown", handleCanvasMouseDownEnd);
		canvas.removeEventListener("mousedown", handleCanvasMouseDownErase);
		canvas.removeEventListener("mousemove", handleCanvasMouseMoveErase);
		canvas.removeEventListener("mouseup", handleCanvasMouseUpErase);
		canvas.addEventListener("mousedown", handleCanvasMouseDownPen);
	} else if (command === "ellipse") {

	} else {
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
}

function handleCanvasMouseMove(e) {
	canvasContext.globalAlpha = 0.2;
	canvasContext.clearRect(prevRectCoords.x1, prevRectCoords.y1, prevRectCoords.x2, prevRectCoords.y2);
	prevRectCoords = {
		x1: startCoordinates.x, y1: startCoordinates.y,
		x2: e.clientX - canvasRect.left - startCoordinates.x, y2: e.clientY - canvasRect.top - startCoordinates.y
	};
	canvasContext.fillRect(prevRectCoords.x1, prevRectCoords.y1,
		prevRectCoords.x2, prevRectCoords.y2);
	canvasContext.globalAlpha = 1.0;
}

function handleCanvasMouseMoveErase(e) {
	canvasContext.clearRect(e.clientX - canvasRect.left, e.clientY - canvasRect.top, 50, 50);
}

function handleCanvasMouseMoveLine(e) {
	canvasContext.clearRect(0, prevLineCoords.y - 1, canvas.width, 2);
	canvasContext.globalAlpha = 0.2;
	canvasContext.lineTo(e.clientX - canvasRect.left, e.clientY - canvasRect.top);
	canvasContext.globalAlpha = 1.0;
	canvasContext.stroke();
}

function handleCanvasMouseMovePen(e) {
	canvasContext.lineTo(e.clientX - canvasRect.left, e.clientY - canvasRect.top);
	canvasContext.stroke();
}

function handleCanvasMouseUpErase(_) {
	canvas.removeEventListener("mouseup", handleCanvasMouseUpErase);
	canvas.removeEventListener("mousemove", handleCanvasMouseMoveErase);
	canvas.addEventListener("mousedown", handleCanvasMouseDownErase);
}

function handleCanvasMouseUpPen(_) {
	canvas.removeEventListener("mouseup", handleCanvasMouseUpPen);
	canvas.removeEventListener("mousemove", handleCanvasMouseMovePen);
	canvas.addEventListener("mousedown", handleCanvasMouseDownPen);
}

function handleCanvasMouseDownEnd(_) {
	rectsList.push({
		x1: prevRectCoords.x1, y1: prevRectCoords.y1,
		x2: prevRectCoords.x2, y2: prevRectCoords.y2
	});
	console.log(rectsList);
	canvas.removeEventListener("mousedown", handleCanvasMouseDownEnd);
	canvas.removeEventListener("mousemove", handleCanvasMouseMove);
	canvas.addEventListener("mousedown", handleCanvasMouseDown);
	prevRectCoords = { x1: 0, y1: 0, x2: 0, y2: 0 };
}

function handleCanvasMouseDown(e) {
	startCoordinates.x = e.clientX - canvasRect.left;
	startCoordinates.y = e.clientY - canvasRect.top;
	canvas.removeEventListener("mousedown", handleCanvasMouseDown);
	canvas.addEventListener("mousemove", handleCanvasMouseMove);
	canvas.addEventListener("mousedown", handleCanvasMouseDownEnd);
}

function handleCanvasMouseDownErase(e) {
	canvasContext.clearRect(e.clientX - canvasRect.left, e.clientY - canvasRect.top, 50, 50);
	canvas.removeEventListener("mousedown", handleCanvasMouseDownErase);
	canvas.addEventListener("mousemove", handleCanvasMouseMoveErase);
	canvas.addEventListener("mouseup", handleCanvasMouseUpErase);
}

function handleCanvasMouseDownLine(e) {
	canvasContext.beginPath();
	canvasContext.moveTo(e.clientX - canvasRect.left, e.clientY - canvasRect.top);
	canvasContext.lineWidth = 0.4;
	canvas.removeEventListener("mousedown", handleCanvasMouseDownLine);
	canvas.addEventListener("mousemove", handleCanvasMouseMoveLine);
	canvas.addEventListener("mousedown", handleCanvasMouseDownLineAdd);
}

function handleCanvasMouseDownLineAdd(e) {
	canvasContext.clearRect(0, prevLineCoords.y - 1, canvas.width, 2);
	prevLineCoords = { x: e.clientX - canvasRect.left, y: e.clientY - canvasRect.top };
	canvasContext.lineTo(prevLineCoords.x, prevLineCoords.y);
	canvasContext.stroke();
	canvasContext.moveTo(prevLineCoords.x, prevLineCoords.y);
	canvasContext.closePath();
	canvas.removeEventListener("mousemove", handleCanvasMouseMoveLine);
	canvas.removeEventListener("mousedown", handleCanvasMouseDownLineAdd);
	canvas.addEventListener("mousedown", handleCanvasMouseDownLine);
}

function handleCanvasMouseDownPen(e) {
	canvasContext.beginPath();
	canvasContext.moveTo(e.clientX - canvasRect.left, e.clientY - canvasRect.top);
	canvas.removeEventListener("mousedown", handleCanvasMouseDownPen);
	canvas.addEventListener("mousemove", handleCanvasMouseMovePen);
	canvas.addEventListener("mouseup", handleCanvasMouseUpPen);
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
