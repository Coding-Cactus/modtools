function resetAll() {
    document.getElementById("post").style.display = 'none';
    document.getElementById("comment").style.display = 'none';
    document.getElementById("user").style.display = 'none'			
    document.getElementById("post-infraction").style.display = 'none';
    document.getElementById("comment-infraction").style.display = 'none';
    document.getElementById("user-infraction").style.display = 'none';
    document.getElementById("auto-act-button").disabled = true;
}

function resetInfracts() {
    document.getElementById("post-infraction").style.display = 'none';
    document.getElementById("comment-infraction").style.display = 'none';
    document.getElementById("user-infraction").style.display = 'none';
    document.getElementById("auto-act-button").disabled = true;
}

document.getElementById("type-input").addEventListener("change", () => {
    resetAll();
    let type = document.getElementById("type-input").value;
    if (type !== 'empty') {
        let new_input1 = document.getElementById(type);
        new_input1.style.display = 'block';
        new_input1.style.opacity = '1';
        updateDropdown("drop-auto-action");
        new_input1 = document.getElementById(type+"-input")
        if (new_input1.value !== "") {
            new_input1.dispatchEvent(new Event('change'));
        }
        new_input1.addEventListener("change", () => {
            resetInfracts();
            let id = new_input1.value;
            if (id !== "") {
                let new_input2 = document.getElementById(type+"-infraction");
                new_input2.style.display = 'block';
                new_input2.style.opacity = '1';
                updateDropdown("drop-auto-action");
                new_input2 = document.getElementById(type+"-infraction-input")
                if (new_input2.value !== "empty") {
                    new_input2.dispatchEvent(new Event('change'));
                }
                new_input2.addEventListener("change", () => {
                    let infraction = new_input2.value;
                    if (infraction !== "empty") {
                        document.getElementById("auto-act-button").disabled = false;
                    } else {							
                        document.getElementById("auto-act-button").disabled = true;
                    }
                });
            }	else {
                updateDropdown("drop-auto-action");
            }
        });
    } else {
        updateDropdown("drop-auto-action");
    }
});

document.getElementById("auto-act-form").addEventListener("submit", (event) => {
    let url = "/auto-act";
    let request = new XMLHttpRequest();
    request.open('POST', url, true);
    request.onload = function() {
        document.getElementById("autoActResponse").innerHTML = request.responseText;
        updateDropdown("drop-auto-action");
    }
    request.send(new FormData(event.target));
    event.preventDefault();
});