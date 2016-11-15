/*
============================================================================
This file holds all the javascript needed for the page
============================================================================
*/

function display_accuracy(){
  $('#accuracy').load('/get_accuracy');
}

function evaluate(event){

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
  }
  else {
    $('#model_wrong').toggle('slow', function() {
      // Animation complete.
    });
  }

  // determine whether the user was right
  if(event.data.user_pred == event.data.play) {
    $usercorrect = true
  }

  // show the right/wrong message
  if ($usercorrect) {
    $('#user_right').toggle('slow', function() {
      // Animation complete.
    });
  }
  else {
    $('#user_wrong').toggle('slow', function() {
      // Animation complete.
    });
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
