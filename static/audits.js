function change_page(forwards) {
    let next_page
    if (forwards) {
        next_page = Number(document.getElementById("page-num").innerHTML) + 1
    } else {
        next_page = Number(document.getElementById("page-num").innerHTML) - 1
    }
    let url = "/audits";
    let request = new XMLHttpRequest();
    request.open('POST', url, true);
    request.onload = function() {
        document.getElementById("audits").innerHTML = request.responseText;
        settings = document.getElementById('settings')
        if (settings !== null) {
            document.getElementById("creator-input").value = document.getElementById("creator-setting").innerHTML;
            document.getElementById("actionType-input").value = document.getElementById("actionType-setting").innerHTML;
            document.getElementById("model-input").value = document.getElementById("model-setting").innerHTML;
            document.getElementById("order-input").value = document.getElementById("order-setting").innerHTML;
            document.getElementById("page-input").value = document.getElementById("page-setting").innerHTML;
        }
        updateDropdown("drop-audits");
        document.getElementById("audit-settings-button").addEventListener('click', () => {
            a();
        });
        document.getElementById("audits-forward").addEventListener('click', () => {change_page(true)});
        if (next_page > 1) {
            document.getElementById("audits-backward").addEventListener('click', () => {change_page(false)});
        }
    };
    document.getElementById("page-input").value = next_page;
    settings = document.getElementById('settings')
    if (settings !== null) {
        document.getElementById("creator-input").value = document.getElementById("creator-setting").innerHTML;
        document.getElementById("actionType-input").value = document.getElementById("actionType-setting").innerHTML;
        document.getElementById("model-input").value = document.getElementById("model-setting").innerHTML;
        document.getElementById("order-input").value = document.getElementById("order-setting").innerHTML;
    }
    form = document.getElementById("audit-settings-form")
    request.send(new FormData(form));
    document.getElementById("audits").innerHTML = "<p style='text-align: center;'>Retrieving audits</p><div class='loader'></div>";
    updateDropdown("drop-audits");
}

function a() {		
    document.getElementById("audit-settings-button").style.opacity = "0";
    document.getElementById("audit-settings").style.opacity = "1";
    document.getElementById("audit-settings").style.display = 'block';
    document.getElementById("audit-settings-button").style.display = 'none';
    updateDropdown("drop-audits");					
    document.getElementById("audit-settings-form").addEventListener("submit", (event) => {
        let url = "/audits";
        let request = new XMLHttpRequest();
        request.open('POST', url, true);
        request.onload = function() {
            document.getElementById("audits").innerHTML = request.responseText;
            updateDropdown("drop-audits");
            settings = document.getElementById('settings')
            if (settings !== null) {
                document.getElementById("creator-input").value = document.getElementById("creator-setting").innerHTML;
                document.getElementById("actionType-input").value = document.getElementById("actionType-setting").innerHTML;
                document.getElementById("model-input").value = document.getElementById("model-setting").innerHTML;
                document.getElementById("order-input").value = document.getElementById("order-setting").innerHTML;
                document.getElementById("page-input").value = document.getElementById("page-setting").innerHTML;
            }
            document.getElementById("audit-settings-button").addEventListener('click', () => {
                a();
            });
            page = Number(document.getElementById("page-num").innerHTML)
            document.getElementById("audits-forward").addEventListener('click', () => {change_page(true)});
            if (page > 1) {
                document.getElementById("audits-backward").addEventListener('click', () => {change_page(false)});
            }
        };
        request.send(new FormData(event.target));
        event.preventDefault();
        document.getElementById("audits").innerHTML = "<p style='text-align: center;'>Retrieving audits</p><div class='loader'></div>";
        updateDropdown("drop-audits");
    });
}


function audits() {
    if (!clicked) {
        clicked = true;
        let xhr = new XMLHttpRequest();
        xhr.open("GET", '/audits', true);
        xhr.onload = function() {
            document.getElementById('audits').innerHTML = this.responseText;
            updateDropdown("drop-audits");
            document.getElementById("audit-settings-button").addEventListener('click', () => {
                a();
            });
            document.getElementById("audits-forward").addEventListener('click', () => {change_page(true)});
        }
        xhr.send();
    }			
}
var clicked = false;
document.getElementById("drop-audits").addEventListener("click", audits);