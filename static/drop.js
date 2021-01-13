function initialise() {
	let drops = document.querySelectorAll("div.drop-title");
	drops.forEach( drop => {
		let sibling = drop.nextElementSibling;
		let child = sibling.firstElementChild;
		sibling.dataset.height = getComputedStyle(child).getPropertyValue('height');
	});
}

function updateDropdown(id) {
	let sibling = document.getElementById(id).nextElementSibling;
	let child = sibling.firstElementChild;
	sibling.dataset.height = getComputedStyle(child).getPropertyValue('height');
	sibling.style.height = sibling.dataset.height;
}

document.addEventListener('DOMContentLoaded', () => {
	let initialised = false;
	let drops = document.querySelectorAll("div.drop-title");
	drops.forEach( drop => {
		let sibling = drop.nextElementSibling;
		sibling.style.height = "0px";
		drop.addEventListener("click", () => {
			if (!initialised) {
				initialise();
				initialised = false;
			}
			if (sibling.style.height !== "0px") {
				sibling.style.height = "0px";
				sibling.style.opacity = "0";
			} else {
				sibling.style.height = sibling.dataset.height;
				sibling.style.opacity = "1";
			}
		});
	});
});


function resize() {
	initialise();
	let drops = document.querySelectorAll("div.drop-title");
	drops.forEach( drop => {
		let sibling = drop.nextElementSibling;
		if (sibling.style.height === "0px") {
				sibling.style.height = "0px";
				sibling.style.opacity = "0";
			} else {
				sibling.style.height = sibling.dataset.height;
				sibling.style.opacity = "1";
			}
	});
}

window.addEventListener('resize', resize);