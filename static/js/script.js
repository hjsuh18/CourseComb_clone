
  var lightpalette = ["#E0FFFF", "#D8BFD8", "#FFDEAD", "#DCDCDC", "#FFDAB9", "#BDB76B", "#E6E6FA", "#FFB6C1", "#2EC4B6", "#CD853F", "#B0C4DE"];
  var darkpalette  = ["#001f3f"];
  var schedule_data;
  var section_types = ["L", "C", "S", "U", "B", "D", "E", "F", "P"]
  
  // helper function 1
  function contains(str1, str2) {
    var i = 0;
    while (i < str1.length && i < str2.length) {
      if (str1.charAt(i) != str2.charAt(i)) {
        return false;
      }
      i++;
    }
    return true;
  }
    
  // helper function 2
  var isEqual = function (value, other) {
    // Get the value type
    var type = Object.prototype.toString.call(value);
    // If the two objects are not the same type, return false
    if (type !== Object.prototype.toString.call(other)) return false;
    // If items are not an object or array, return false
    if (['[object Array]', '[object Object]'].indexOf(type) < 0) return false;
    // Compare the length of the length of the two items
    var valueLen = type === '[object Array]' ? value.length : Object.keys(value).length;
    var otherLen = type === '[object Array]' ? other.length : Object.keys(other).length;
    if (valueLen !== otherLen) return false;
    // Compare two items
    var compare = function (item1, item2) {
      // Get the object type
      var itemType = Object.prototype.toString.call(item1);
      // If an object or array, compare recursively
      if (['[object Array]', '[object Object]'].indexOf(itemType) >= 0) {
        if (!isEqual(item1, item2)) return false;
      }
      // Otherwise, do a simple comparison
      else {
        // If the two items are not the same type, return false
        if (itemType !== Object.prototype.toString.call(item2)) return false;
        // Else if it's a function, convert to a string and compare
        // Otherwise, just compare
        if (itemType === '[object Function]') {
          if (item1.toString() !== item2.toString()) return false;
        } else {
          if (item1 !== item2) return false;
        }
      }
    };
    // Compare properties
    if (type === '[object Array]') {
      for (var i = 0; i < valueLen; i++) {
        if (compare(value[i], other[i]) === false) return false;
      }
    } else {
      for (var key in value) {
        if (value.hasOwnProperty(key)) {
          if (compare(value[key], other[key]) === false) return false;
        }
      }
    }
    // If nothing failed, return true
    return true;
  };

  // Activate tooltip
  $('body').tooltip({
    selector: '.schedule-name-input'
  });

  // Save schedule when pressed enter
  $(".save-schedule-panel").on('keyup', '#schedule_name', function (e) {
    if (e.which == 13) {
      saveSchedule();
    }
  });

  // Save schedule when clicking on arrow
  function saveSchedule () {
    calendar_data = []
    all_sources = $("#calendar").fullCalendar('getEventSources');
    for (i = 0; i < all_sources.length; i++) { 
      for (j = 0; j < all_sources[i]["rawEventDefs"].length; j++) {
        calendar_data.push(all_sources[i]["rawEventDefs"][j]);
      }
    }
    if (calendar_data.length == 0) {
      $(".save-schedule-message").empty();
      $(".save-schedule-message").append("Cannot save empty schedule");
      $(".save-schedule-message").css("color", "red");
    }
    else {
      var saveschedule_data = {
        csrfmiddlewaretoken: csrfmiddlewaretoken,
        save_schedule: 'save_schedule',
        calendar_name: $("#schedule_name").val(),
        calendar_courses: JSON.parse(schedule_data["schedule"])["names"],
        calendar_data: JSON.stringify(calendar_data)
      };
      $.ajax({
        type: "POST",
        url: '/home/',
        data: saveschedule_data,
        success: function(data) {
          $(".save-schedule-message").empty();
          if (data["message"]) {
            $(".save-schedule-message").append(data["message"]);
            $(".save-schedule-message").css("color", "green");
          }
          else if (data["error"]) {
            $(".save-schedule-message").append(data["error"]);
            $(".save-schedule-message").css("color", "red");
          }      
        }
      });
    }
  }

  // Save schedule button is clicked
  function saveScheduleButton() {
    $(".save-schedule-message").empty();
    // new_element = '<button type="button" class="btn btn-secondary createdDiv" data-toggle="tooltip" data-placement="top" title="Tooltip on top"> Tooltip on top </button>'
    new_element = "<input class = 'schedule-name-input' type='text' data-delay = '0' data-toggle='tooltip' data-placement='top' placeholder = 'Name Your Favorite' id ='schedule_name'> <i class='far fa-arrow-alt-circle-right' onclick = 'saveSchedule();'></i>"
    $(".save-schedule-message").append(new_element);
    $(".save-schedule-message").css("color", "black");
  }

  // Click on a combination
  $('body').on('click', '.coursecomb', function (e) {
   e.preventDefault();
   // create save schedule panel
   $(".save-schedule-panel").empty();
   $(".save-schedule-panel").append('<span class = "column-label">Selected Schedule:</span> \
    <span class="save-schedule-message"> </span> \
    <button class = "btn btn-primary btn-md" id="save-schedule" onclick="saveScheduleButton();">Favorite <i class="far fa-heart"></i></button>')
   $(".save-schedule-message").empty();
   // empty holder image
   $(".calendar-holder").empty();
   // show click to show precept div
   $(".precept-show").empty();
   $(".precept-show").append("Click to show precepts");
   // initilize calendar
   $("#calendar").fullCalendar({
    eventClick: function(calEvent, jsEvent, view) {
      if (calEvent["className"].indexOf("precept_render") != -1) {
        $(".save-schedule-message").empty();
                // for primary meeting
                if (calEvent["className"].indexOf("primary") != -1) {
                  title = calEvent["id"].split("-")[0];
                  all_sources = $("#calendar").fullCalendar('getEventSources');
                  precepts_display = false;
                  for (i = 0; i < all_sources.length; i++) { 
                    if (isEqual(all_sources[i]["rawEventDefs"], JSON.parse(JSON.parse(schedule_data["schedule"])[title]))) {
                      precepts_display = true;
                      var selected_precept;
                      for (j = 0; j < all_sources[i]["rawEventDefs"].length; j++) {
                        if (all_sources[i]["rawEventDefs"][j]["id"] == calEvent["id"]) {
                          selected_precept = all_sources[i]["rawEventDefs"][j];
                          temp = selected_precept["className"].split(" ");
                          temp.push("selected_class");
                          selected_precept["className"] = temp;
                          selected_precept = [selected_precept];
                        }
                      }
                      $("#calendar").fullCalendar('removeEventSource', calEvent["source"]["rawEventDefs"]);
                      $("#calendar").fullCalendar('addEventSource', selected_precept);
                    } 
                  }
                  if (precepts_display == false) {
                    $("#calendar").fullCalendar('removeEventSource', calEvent["source"]["rawEventDefs"]);
                    $("#calendar").fullCalendar('addEventSource', JSON.parse(JSON.parse(schedule_data["schedule"])[title]));
                  }
                }
                else {
                  title = calEvent["id"].split("-")[0];
                  section_type = calEvent["id"].split("-")[1][0];
                  all_sources = $("#calendar").fullCalendar('getEventSources');
                  precepts_display = false;
                  for (i = 0; i < all_sources.length; i++) { 
                    if (isEqual(all_sources[i]["rawEventDefs"], JSON.parse(schedule_data[title])[section_type])) {
                      precepts_display = true;
                      var selected_precept;
                      for (j = 0; j < all_sources[i]["rawEventDefs"].length; j++) {
                        if (all_sources[i]["rawEventDefs"][j]["id"] == calEvent["id"]) {
                          selected_precept = all_sources[i]["rawEventDefs"][j];
                          temp = selected_precept["className"];
                          selected_precept["className"] = [temp, "selected_precept"];
                          selected_precept = [selected_precept];
                        }
                      }
                      $("#calendar").fullCalendar('removeEventSource', calEvent["source"]["rawEventDefs"]);
                      $("#calendar").fullCalendar('addEventSource', selected_precept);
                    } 
                  }
                  if (precepts_display == false) {
                    $("#calendar").fullCalendar('removeEventSource', calEvent["source"]["rawEventDefs"]);
                    $("#calendar").fullCalendar('addEventSource', JSON.parse(schedule_data[title])[section_type]);
                  }
                }
              }
            },
            defaultView: 'agendaWeek',
            header: false,
            columnHeaderFormat: 'ddd',
            minTime: '08:0:00',
            maxTime: '23:00:00',
            slotDuration: '00:30:00',
            allDaySlot: false,
            weekends: false,
            height: 'parent',
            eventOverlap: false,
            timeFromat: 'H:mm',
          })
   comb_id = $(this).attr("class").split(" ")[1];
   var coursecomb_data = {
    comb_click:'comb_click',
    comb_id: comb_id
  };
  var classes;
  $.ajax({
    type: "GET",
    url: '/home/',
    data: coursecomb_data,
    success: function(data) {
      $("#calendar").fullCalendar('removeEventSources');
      all_courses = JSON.parse(JSON.parse(data["schedule"])["names"]);
      for (k = 0; k < all_courses.length; k++) {
        $("#calendar").fullCalendar('addEventSource', JSON.parse(JSON.parse(data["schedule"])[all_courses[k]]));
      }
      schedule_data = data;
      var selectedCourses = $(".coursecomb." + comb_id).text();
      // get rid of rank number at the front
      selectedCourses = selectedCourses.split(". ")[1];
      selectedCourses = selectedCourses.split(",");
      $("div#selected-coursecomb").empty();
      // $(".precept-show").empty();
      // var precepts_exist = false;
      var no_precepts = true;
      for (i = 0; i < selectedCourses.length; i++) {
        var course = selectedCourses[i].trim();
        if (data[course] != "{}") {
          // NOT SHOW CLICK TO SHOW PRECEPTS WHEN THERE ARE NO PRECEPTS
          // if (precepts_exist != true) {
          //   precepts_exist = true;
          //   $(".precept-show").append("Click to show precepts");
          // }
          no_precepts = false;
          var temp = JSON.parse(data[course]);
          var precepts;
          $("div#selected-coursecomb").append(
            $("<div/>", {"class": "col"}).append(
              $("<input class = 'course-checkbox' type = 'checkbox' name = '" + course + "' id = '" + course + "'/>" + "<label class = 'col " + i + "' id = 'precept-button' for = '" +
                course + "'>" + course + "</label>")
              )
            );
          // get colour of precept
          for (j = 0; j < section_types.length; j++){
            if (temp.hasOwnProperty(section_types[j]))
              precepts=temp[section_types[j]];
          }
          $(".col." + i).css("background-color", precepts[0].color);
        }
      }
      if (no_precepts){
        $("div#selected-coursecomb").append(
          $("<div/>", {"class": "col"}).append(
            $("<span style='color: rgb(43, 122, 120); font-size: 18px;'>There are no precepts to choose for your courses</span>")
            )
          );
      }
    }
  });
    // second column highlighting
    // this makes more sense since clicking on the highlighted one does not remove the events from calendar
    $(".coursecomb").each(function () {
      if ($(this).css("background-color") == "rgb(43, 122, 120)") {
        $(this).css("background-color", "rgb(254, 255, 255)");
        $(this).css("border-color", "rgb(23,37,42)");
        $(this).css("color", "rgb(23, 37, 42)");
      }
    });
    // $(this).css("background-color", "rgb(255, 184, 77)");
    $(this).css("background-color", "rgb(43, 122, 120)");
    $(this).css("border-color", "rgb(43, 122, 120)");
    $(this).css("color", "rgb(254, 255, 255)");
  });

  // Click on precept/labs/etc.
  $('div#selected-coursecomb').on('click', 'input[type=checkbox]', function() {
    $(".save-schedule-message").empty();
    all_sources = $("#calendar").fullCalendar('getEventSources');
    title = this.id;
    course_display = false;
    var course_remove;
    var precept_remove;
    for (i = 0; i < all_sources.length; i++) { 
      for (j = 0; j < section_types.length; j++){
        if (JSON.parse(schedule_data[title])[section_types[j]]) {
          if (isEqual(all_sources[i]["rawEventDefs"], JSON.parse(schedule_data[title])[section_types[j]])) {
            course_display = true;
            course_remove = all_sources[i]["rawEventDefs"];
            $("#calendar").fullCalendar('removeEventSource', course_remove);
          } 
        }
      }
      
      if (all_sources[i]["rawEventDefs"][0]["className"]) {
        if (all_sources[i]["rawEventDefs"][0]["className"].indexOf("selected_precept") != -1) {
          if (all_sources[i]["rawEventDefs"][0]["id"].split("-")[0] == title) {
            course_display = course_display == true ? false : true;
            precept_remove = all_sources[i]["rawEventDefs"];
            $("#calendar").fullCalendar('removeEventSource', precept_remove);
          }
        }
      }
    }
    if (course_display == false) {
      for (k = 0; k < section_types.length; k++) {
        if (JSON.parse(schedule_data[title])[section_types[k]]) {
          $("#calendar").fullCalendar('addEventSource', JSON.parse(schedule_data[title])[section_types[k]]);
        }
      }
    }
  });

  // Make filter options pop up, change entries depending on course queue content
  $('body').on('click', '.reset_filter', function(e) {
    e.preventDefault();
    var reset_filter = {
      reset_filter: 'reset_filter',
      csrfmiddlewaretoken: csrfmiddlewaretoken
    };
    $.ajax({
     type: "POST",
     url: '/home/',
     data: reset_filter,
     success: function(data) {
      // reset all form entries to default
      $("#coursenum").val('1');
      $("#ha").prop('checked', false);
      $("#sa").prop('checked', false);
      $("#stl").prop('checked', false);
      $("#stn").prop('checked', false);
      $("#ec").prop('checked', false);
      $("#em").prop('checked', false);
      $("#la").prop('checked', false);
      $("#qr").prop('checked', false);
      $("#max-dept").val('5');
      $("#no-friday-class").prop('checked', false);
      $("#no-evening-class").prop('checked', false);
      $("#after-ten-am").prop('checked', false);
      $("#full").prop('checked', false);
      $("#pdf").prop('checked', false);
      var must_have_departments = JSON.parse(data["must_have_departments"]);
      var course_priority = JSON.parse(data["course_priority"]);
      $("#must-have-departments").empty();
      $("#must-have-departments").append(must_have_departments);
      $("#course-priority").empty();
      $("#course-priority").append(course_priority);
    }
  });
  });
  // Make filter options pop up, change entries depending on course queue content
  $('body').on('click', '.create_schedule', function(e) {
    e.preventDefault();
    var filter = {
      click_filter: 'click_filter',
      csrfmiddlewaretoken: csrfmiddlewaretoken
    };
    $.ajax({
      type: "POST",
      url: '/home/',
      data: filter,
      success: function(data) {
      // load the saved course number
      var filter_coursenum = JSON.parse(data['filter_coursenum']);
      $("#coursenum").val(filter_coursenum);
      // load the saved filter distributions
      var filter_distribution = JSON.parse(data['filter_distribution']);
      if (filter_distribution != null){
        for (a = 0; a < filter_distribution.length; a++) {
          if (filter_distribution[a].localeCompare("HA") == 0){
            $("#ha").prop('checked', true);
          }
          else if (filter_distribution[a].localeCompare("SA") == 0){
            $("#sa").prop('checked', true);
          }
          else if (filter_distribution[a].localeCompare("STL") == 0){
            $("#stl").prop('checked', true);
          }
          else if (filter_distribution[a].localeCompare("STN") == 0){
            $("#stn").prop('checked', true);
          }
          else if (filter_distribution[a].localeCompare("EC") == 0){
            $("#ec").prop('checked', true);
          }
          else if (filter_distribution[a].localeCompare("EM") == 0){
            $("#em").prop('checked', true);
          }
          else if (filter_distribution[a].localeCompare("LA") == 0){
            $("#la").prop('checked', true);
          }
          else if (filter_distribution[a].localeCompare("QR") == 0){
            $("#qr").prop('checked', true);
          }
        }
      }
      
      var filter_maxdept = JSON.parse(data['filter_maxdept']);
      $("#max-dept").val(filter_maxdept);
      var filter_nofridayclass = JSON.parse(data['filter_nofridayclass']);
      $("#no-friday-class").prop('checked', filter_nofridayclass);
      var filter_noeveningclass = JSON.parse(data['filter_noeveningclass']);
      $("#no-evening-class").prop('checked', filter_noeveningclass);
      var filter_aftertenam = JSON.parse(data['filter_aftertenam']);
      $("#after-ten-am").prop('checked', filter_aftertenam);
      var filter_full = JSON.parse(data['filter_full']);
      $("#full").prop('checked', filter_full);
      var filter_pdf = JSON.parse(data['filter_pdf']);
      $("#pdf").prop('checked', filter_pdf);
      var must_have_departments = JSON.parse(data["must_have_departments"]);
      var course_priority = JSON.parse(data["course_priority"]);
      $("#must-have-departments").empty();
      $("#must-have-departments").append(must_have_departments);
      $("#course-priority").empty();
      $("#course-priority").append(course_priority);
    }
  });
  });
  // FOR ACTUAL FILTERING
  $('#filter').on('submit', function(e){
    e.preventDefault();
    $('.combqueue').empty();
    $('.combqueue').append(loading_img);

    // number of courses
    var x = $("#coursenum option:selected").text();
    
    // Must have departments
    var allDeps = [];
    $('.dep-check:checked').each(function () {
      allDeps.push($(this).val());
    });
    // distribution filter
    var distribution = [];
    if ($('#ha').is(":checked"))
      distribution.push("HA");
    if ($('#sa').is(":checked"))
      distribution.push("SA");
    if ($('#stl').is(":checked"))
      distribution.push("STL");
    if ($('#stn').is(":checked"))
      distribution.push("STN");
    if ($('#ec').is(":checked"))
      distribution.push("EC");
    if ($('#em').is(":checked"))
      distribution.push("EM");
    if ($('#la').is(":checked"))
      distribution.push("LA");
    if ($('#qr').is(":checked"))
      distribution.push("QR");
    // priority of each course
    var priority = [];
    $('.priority-select').each(function (){
      priority.push($(this).attr('id'));
      priority.push($(this).val());
    });
    // max departmentals filter
    var max_dept = $("#max_dept option:selected").text();
    var no_friday_class = false;
    if ($('#no-friday-class').is(":checked")){
      no_friday_class = true;
    }
    var no_evening_class = false;
    if ($('#no-evening-class').is(":checked")){
      no_evening_class = true;
    }
    var after_ten_am = false;
    if ($('#after-ten-am').is(":checked")){
      after_ten_am = true;
    }
    var full = false;
    if ($('#full').is(":checked")){
      full = true;
    }
    var pdf = false;
    if ($('#pdf').is(":checked"))
      pdf = true;
    var createschedule_data = {
      searchresults: 'searchresults',
      number_of_courses: x,
      depts: allDeps,
      distribution: distribution,
      priority: priority,
      max_dept: max_dept,
      no_friday_class: no_friday_class,
      no_evening_class: no_evening_class,
      after_ten_am: after_ten_am,
      full: full,
      pdf: pdf,
      csrfmiddlewaretoken: csrfmiddlewaretoken
    };
    $.ajax({
     type: "POST",
     url: '/home/',
     data: createschedule_data,
     success: function(data) {
      $("#combqueue").empty();
      if (data["course_number"]) {
        $(".combination_length").empty();
        $(".combination_length").append(0);
        $("#combqueue").append(data["course_number"]);
      }
      else if (data["no_courses"]) {
        $(".combination_length").empty();
        $(".combination_length").append(0);
        $("#combqueue").append(data["no_courses"]);
      }
      else if (data["no_combo"]) {
        $(".combination_length").empty();
        $(".combination_length").append(0);
        $("#combqueue").append(data["no_combo"]);
      }
      else if (data["filter_restrict"]) {
        $(".combination_length").empty();
        $(".combination_length").append(0);
        $("#combqueue").append(data["filter_restrict"]);
      }
      else {
        var courses_com = JSON.parse(data["courses_com"]);
        var combination_length = courses_com.length;
        $(".combination_length").empty();
        $(".combination_length").append(combination_length);
        $("#combqueue").append(courses_com);
      }
    },
    error: function(xhr, textStatus, errorThrown) {
      alert("some error");
    }
  });
    $("#filter-modal").modal("hide");
  });
  // Delete a course
  $('body').on('click', '.deleteclass', function (e) {
    e.preventDefault();
    var parent = $(this).parent().parent().parent();
    var class_delete_data = {
      deleteclass: 'deleteclass',
      registrar_id: this.id,
      csrfmiddlewaretoken: csrfmiddlewaretoken
    };
    $.ajax({
     type: "POST",
     url: '/home/',
     data: class_delete_data,
     success: function(data) {
      parent.remove();
      $(".queue_length").empty()
      $(".queue_length").append($(".coursequeue > div").length);
    }
  });
  });
  // Autocomplete
  $(function() {
    $("#courses").autocomplete({
      source: "/api/get_courses/",
      minLength: 2,
      messages: {
        noResults: '',
        results: function() {}
      },
      appendTo: '.aftersearch',
      focus: function(event, ui) { 
       event.preventDefault();
       $("#courses").val(ui.item.label);
     },
     select: function (e, ui) {
      var class_select_data = {
        addclass: 'addclass',
        class: ui.item.label,
        registrar_id: ui.item.value,
        csrfmiddlewaretoken: csrfmiddlewaretoken
      };
      e.preventDefault();
      $("#courses").val(ui.item.label);
      $.ajax({
        type: "POST",
        url: '/home/',
        data: class_select_data,
        success: function(data) {
          if (data != {}) {
            var newclass = JSON.stringify(data["newclass"]);
            var newid = data["newid"];
            var eval = data["eval"];
            var url = data["url"];
            $(".coursequeue").append(
              "<div class = 'refreshed-courses container " + newid + "'>" + JSON.parse(newclass) + 
              '<div class="overlay"> <span class = "row1"> \
              <a href="' + url + '" target="_blank"><div class = "registrar"> <span class = "text"> <i class="fa fa-info" aria-hidden="true"></i> </span> </div></a> \
              <a href="' + eval + '" target="_blank"><div class = "reviews"> <span class = "text"> <i class="fas fa-chart-pie"></i> </span> </div></a> \
              <div class = "deletebutton deleteclass" id ="' + newid + '"> <span class = "text"> <i class="fa fa-times" aria-hidden="true"></i> </span> </div> </span> </div> </div>')
              // refresh the number of courses on coursequeue
              $(".queue_length").empty();
              $(".queue_length").append($(".coursequeue > div").length);
              $("#courses").val("");
            }
          }
        });
    }
  });
  });
