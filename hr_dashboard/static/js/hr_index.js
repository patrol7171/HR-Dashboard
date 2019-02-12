
//------------------------------------------------------- Forismatic API SCRIPT --------------------------------------------------------------->
function myJsonMethod(quote,author) {
  if (author == '') {
	$('#quoteInfo').html("<h4>" + quote + "</h4>" + "<p><i>- Author Unknown</i></p>");
  } else {
	$('#quoteInfo').html("<h4>" + quote + "</h4>" + "<p><i>- " + author + "</i></p>");
  }
}

