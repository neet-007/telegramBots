
const tele = window.Telegram

const canvas = document.getElementById("main-canvas");
const canvasContext = canvas.getContext("2d");
const backgroundDiv = document.getElementById("background-div");
const canvasRect = canvas.getBoundingClientRect();

console.log(canvas)
console.log(canvasContext)

let startCoordinates = { x: 0, y: 0 };
let prevRectCoords = { x1: 0, y1: 0, x2: 0, y2: 0 };
let rectsList = [];
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
	prevRectCoords = {
		x1: startCoordinates.x, y1: startCoordinates.y,
		x2: e.clientX - canvasRect.left - startCoordinates.x, y2: e.clientY - canvasRect.top - startCoordinates.y
	};
	canvasContext.fillRect(prevRectCoords.x1, prevRectCoords.y1,
		prevRectCoords.x2, prevRectCoords.y2);
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
