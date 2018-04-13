const var dists = ["HA", "LA", "SA", "EC", "EM", "QR", "STL", "STN"]

for (i = 0; i < dists.length; i++) {
	var box = document.createElement("div");
	box.className = "form-check form-check-inline";
	box.id = dists[i]
	var input = document.createElement("input");
	input.className = "form-check-input";
	input.type = "checkbox"
	input.id = 
	var node = document.createTextNode(dists[i]);
	par.appendChild(node);

	document.getElementById("distribution").appendChild(box);
}