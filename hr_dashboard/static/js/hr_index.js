
//------------------------------------------------------- Forismatic JS --------------------------------------------------------------->
	function myJsonMethod(response) {
		  quote = response.quoteText;
		  author = response.quoteAuthor;
		  if (response.quoteAuthor == '') {
			$('#quoteInfo').html("<h5>" + quote + "</h5>" + "<p><i>- Author Unknown</i></p>");
		  } else {
			$('#quoteInfo').html("<h5>" + quote + "</h5>" + "<p><i>- " + author + "</i></p>");
		  }
	}