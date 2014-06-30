function validateForm() {
    var x = document.forms["login_form"]["email"].value;
    var atpos = x.indexOf("@");
    var dotpos = x.lastIndexOf(".");
    var y = document.forms["login_form"]["pass"].value;

    if (x == null || x== "") {
        alert("Please fill the Username/Email field.");
        return false;
    }
    if (atpos< 1 || dotpos<atpos+2 || dotpos+2>=x.length) {
        alert("Not a valid username/e-mail address.");
        return false;
    }
    if (y == null || y == "") {
        alert("Please fill the Password field.");
        return false;
    }
    
}

function validateLogin () {
    var x = document.forms["login_form"]["email"].value;
    var y = document.forms["login_form"]["pass"].value;
    
    if (x == "anuragmathur1311@gmail.com" && y =="abcd1234") {
        return;
    } else if (x == "anuragmathur1311@gmail.com" && y !="abcd1234") {
        alert("Password Incorrect");
        return false;
    } else if (x != "anuragmathur1311@gmail.com" && y =="abcd1234") {
        alert("Username Incorrect");
        return false;
    } else {
        alert("Username and Password Incorrect");
        return false;
    }
}