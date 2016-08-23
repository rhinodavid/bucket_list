$(function(){
  $('#btnSignUp').click(function(e){
    e.preventDefault();
    $.ajax({
      url: '/signUp',
      data: $('form').serialize(),
      type: 'POST',
      success: function(response) {
        console.log(response);
      },
      error: function(error) {
        console.log(error);
      }
    });
  });
});