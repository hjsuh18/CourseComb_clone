
	for (i = 0; i < favorites.length; i++) {
		courses = JSON.parse(favorites[i][1]).join(", ");
		string = '<div class="container coursecomb">' + favorites[i][0] + " (" + courses + ")" + '<div class="overlay"> \
          <span class = "row1"> <div class = "registrar showclass" id = "'+ i + '"> </div> <div class = "reviews showclass" id = "' + i + '"> </div> <div class = "deletebutton delete-favorite" id = "' + i + '"> <span class = "text"> \
                <i class="fa fa-times" aria-hidden="true"></i> </span> </div> </span> </div>'
		$('.favorite-list').append(string);
	}


	$('.favorite-list').on('click', '.showclass', function () {
		$("#calendar").fullCalendar('removeEventSources');
		events = favorites[this.id][2];
		eventSource = [];
		for (i = 0; i < events.length; i++) {
			eventSource.push(JSON.parse(events[i]));
		}
		$("#calendar").fullCalendar('addEventSource', eventSource);

		// highlighting
		parent_element = $(this).parent().parent().parent();
		$(".coursecomb").each(function () {
			if ($(this).css("background-color") == "rgb(43, 122, 120)") {
		        $(this).css("background-color", "rgb(254, 255, 255)");
		        $(this).css("color", "rgb(23, 37, 42)");
			}
		});
		parent_element.css("background-color", "rgb(43, 122, 120)");
		parent_element.css("color", "rgb(254, 255, 255)");
	});

	// Delete a course
	$('.delete-favorite').on('click', function (e) {
		e.preventDefault();
		var parent = $(this).parent().parent().parent();
		events = favorites[this.id][2];
		var fav_delete_data = {
			deletefav: 'deletefav',
			fav_data: JSON.stringify(events),
			csrfmiddlewaretoken: csrfmiddlewaretoken
		};
		$.ajax({
			type: "POST",
			url: '/favorites/',
			data: fav_delete_data,
			success: function(data) {
				parent.remove();
			}
		});
	});

