$(document).ready(function(){
    // Show the login form when the page loads
    $("#loginForm").on("submit", function(e){
      e.preventDefault();
      $.ajax({
        type: "POST",
        url: "/processlogin",
        data: $(this).serialize(),
        success: function(response){
          var data = JSON.parse(response);
          if(data.success){
            window.location.href = "/home";
          } else {
            $("#errorMsg").text("Login failed " + data.fail_count + " time(s).");
          }
        }
      });
    });
});