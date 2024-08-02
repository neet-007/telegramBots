
const tele = window.Telegram

let IS_SIDE_NAV_OPEN = false;
const SIDE_NAV_STATES = ["view1", "view2", "view3"];

const divChange = document.getElementById("div-change");
const button = document.getElementById("button-1");
const sideNavContainer = document.getElementById("side-nav-container");
const showNavButton = document.getElementById("side-nav-button");
const imgTag = document.createElement("img");
imgTag.setAttribute("src", `/static/uploads/uploaded_img.jpg`);

divChange.appendChild(imgTag);


for (let i = 0; i < SIDE_NAV_STATES.length; i++) {
	const li = document.createElement("li");
	li.id = `side-nav-li-${i}`;
	li.innerHTML = SIDE_NAV_STATES[i];
	li.classList.add("side-nav-li");
	sideNavContainer.appendChild(li);
};

button.onclick = changeButtom;
showNavButton.onclick = toggleNav;

tele.WebApp.ready();
configureMainButton({ text: "do something", color: "#2045dc ", textColor: "#ffffff", onClick: () => alert("hi") })
tele.WebApp.MainButton.show();
tele.WebApp.expand();


function changeButtom(e) {
	divChange.innerHTML = "changes";
}

function toggleNav() {
	if (IS_SIDE_NAV_OPEN) {
		IS_SIDE_NAV_OPEN = false;
		sideNavContainer.style.left = "0";
		return
	}
	IS_SIDE_NAV_OPEN = true;
	sideNavContainer.style.left = "-100%";
}

function configureMainButton(options) {
	tele.WebApp.MainButton.text = options.text;
	tele.WebApp.MainButton.color = options.color;
	tele.WebApp.MainButton.textColor = options.textColor;
	tele.WebApp.MainButton.onClick(options.onClick);
}
