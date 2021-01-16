function admin_ban(event) {
    if (confirm("This will ban the user and delete all of their posts, are you sure that you wish to do this?")) {
        let url = "/admin-ban";
        let request = new XMLHttpRequest();
        request.open('POST', url, true);
        request.onload = function() {
    console.log(request.responseText);
            document.getElementById("adminBanResponse").innerHTML = request.responseText;
            updateDropdown("admin-ban-title");
        };
        request.send(new FormData(event.target));
    }		
    event.preventDefault();
}
document.getElementById("admin-ban-form").addEventListener("submit", admin_ban);