
const tele = window.Telegram

const canvas = document.getElementById("main-canvas");
const canvasContext = canvas.getContext("2d");

console.log(canvas)
console.log(canvasContext)

const imgObject = new Image();
imgObject.src = "/static/uploads/uploaded_img.jpg";

imgObject.onload = function() {
	canvasContext.drawImage(imgObject, 0, 0, canvas.offsetWidth, canvas.offsetHeight);
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
