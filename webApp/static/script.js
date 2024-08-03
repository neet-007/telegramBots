
const tele = window.Telegram

const canvas = document.getElementById("main-canvas");
const canvasContext = canvas.getContext("2d");
const backgroundDiv = document.getElementById("background-div");
console.log(canvas)
console.log(canvasContext)

let startCoordinates = { x: 0, y: 0 };
let prevRectCoords = { x1: 0, y1: 0, x2: 0, y2: 0 };

backgroundDiv.style.backgroundImage = "url(/static/uploads/uploaded_img.jpg)";
backgroundDiv.style.backgroundSize = "cover";
backgroundDiv.style.backgroundRepeat = "no-repeat";
backgroundDiv.style.width = "387px";
backgroundDiv.style.height = "387px";
backgroundDiv.style.pointerEvents = "none";

canvas.addEventListener("mousedown", handleCanvasMouseDown);

function handleCanvasMouseMove(e) {
	canvasContext.globalAlpha = 0.2;
	canvasContext.clearRect(prevRectCoords.x1, prevRectCoords.y1, prevRectCoords.x2, prevRectCoords.y2);
	prevRectCoords = { x1: startCoordinates.x, y1: startCoordinates.y, x2: e.clientX, y2: e.clientY };
	canvasContext.fillRect(startCoordinates.x, startCoordinates.y, e.clientX, e.clientY);
}

function handleCanvasMouseDownEnd(e) {
	canvas.removeEventListener("mousedown", handleCanvasMouseDownEnd);
	canvas.removeEventListener("mousemove", handleCanvasMouseMove);
}

function handleCanvasMouseDown(e) {
	startCoordinates.x = e.clientX;
	startCoordinates.y = e.clientY;
	canvas.removeEventListener("mousedown", handleCanvasMouseDown);
	canvas.addEventListener("mousemove", handleCanvasMouseMove);
	canvas.addEventListener("mousedown", handleCanvasMouseDownEnd);
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
