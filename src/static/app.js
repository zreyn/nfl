/*
============================================================================
This file holds all the javascript needed for the page
============================================================================
*/

function display_accuracy() {
  $('#accuracy').load('/get_accuracy');
}

function evaluate(event) {

  // deactivate the buttons
  $('#passButton').prop('disabled', true);
  $('#rushButton').prop('disabled', true);
  $('#kickButton').prop('disabled', true);

  // keep track of whether the user and/or model was correct
  var $modelcorrect = false
  var $usercorrect = false

  // show the model's prediction
  $('#prediction').toggle('slow', function() {
    // Animation complete.
  });

  // determine whether the model was right
  if(event.data.play_pred == event.data.play) {
    $modelcorrect = true
  }

  // show the right/wrong message
  if ($modelcorrect) {
    $('#model_right').toggle('slow', function() {
      // Animation complete.
    });
    updateCookie("ModelRight", 1)
    updateCookie("ModelTotal", 1)
  }
  else {
    $('#model_wrong').toggle('slow', function() {
      // Animation complete.
    });
    updateCookie("ModelRight", 0)
    updateCookie("ModelTotal", 1)
  }

  // determine whether the user was right
  if(event.data.user_pred == event.data.play) {
    $usercorrect = true
  }

  // show the right/wrong message and update the cookies
  if ($usercorrect) {
    $('#user_right').toggle('slow', function() {
      // Animation complete.
    });
    updateCookie("UserRight", 1)
    updateCookie("UserTotal", 1)
  }
  else {
    $('#user_wrong').toggle('slow', function() {
      // Animation complete.
    });
    updateCookie("UserRight", 0)
    updateCookie("UserTotal", 1)
  }

  // show the outcome of the play
  $('#outcome').toggle('slow', function() {
    // Animation complete.
  });


  // let the server know the outcome
  $.ajax({
           type: "POST",
           url: "/guess",
           contentType: "application/json",
           dataType: "json",
           data: JSON.stringify({
             "actual_play": event.data.play,
             "user_guess": event.data.user_pred,
             "model_guess": event.data.play_pred}),
           success: display_accuracy()
       });
}

function updateCookie(cname, cvalue) {
  var value = getCookie(cname);
    if (value == "") {
      setCookie(cname, cvalue, 7);
    } else {
      var count = parseInt(cvalue);
      var val = parseInt(value);
      setCookie(cname, count+val, 7);
    }
}

function setCookie(cname, cvalue, exdays) {
    var d = new Date();
    d.setTime(d.getTime() + (exdays*24*60*60*1000));
    var expires = "expires="+d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}
