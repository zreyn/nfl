/*
============================================================================
This file holds all the javascript needed for the page
============================================================================
*/
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

  // grab the user's guess
  var $userguess = $('#defenseBox').val();

  // determine whether the user was right
  if($userguess == event.data.play) {
    $usercorrect = true
  }


  // show the right/wrong message
  if ($usercorrect) {
    $('#right').toggle('slow', function() {
      // Animation complete.
    });
  }
  else {
    $('#wrong').toggle('slow', function() {
      // Animation complete.
    });
  }

  // show the outcome of the play
  $('#outcome').toggle('slow', function() {
    // Animation complete.
  });

  // let the server know the outcome
  $.post( "/guess", {"usercorrect": $usercorrect, "modelcorrect": $modelcorrect } );

}
