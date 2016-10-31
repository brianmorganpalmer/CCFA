var MIBC;

MIBC = {};

MIBC.config = {
  api_base: "/api/"
};

MIBC.keys = {
  ENTER: 13
};

MIBC.error = function(msg) {
  return $("#errmsg").text(msg).removeClass("hidden");
};

MIBC.noerror = function() {
  return $("#errmsg").empty().addClass("hidden");
};

MIBC.loadwrapper = function(user, proj, loadfunc) {
  if ((user == null) || (proj == null)) {
    MIBC.error("Need a User name and Project name, please");
    return;
  }
  if ($("#results").children().length > 0) {
    MIBC.clear();
  }
  $("#load_btn").attr("href", "#" + [user, proj].join("/"));
  loadfunc(user, proj);
  return MIBC.noerror();
};

MIBC.url = function(el, str, fname) {
  $(el).attr({
    href: "data:Content-type: text/plain, " + escape(str),
    download: fname
  });
};

$(document).ready(function() {
  var validator;
  MIBC._val = function(el) {
    if (el.type === "checkbox") {
      return el.checked;
    } else {
      return el.value;
    }
  };
  MIBC.load_metadata = function(user, pass) {
    $("#loading").removeClass("hidden");
    return $.get(MIBC.config.api_base + ["projects", user, pass].join("/")).done(function(data) {
      MIBC.update_form(data);
      $("#load_form > span").addClass("hidden").empty();
      return $("#load_form").fadeOut();
    }).error(function(jqxhr, status, errormsg) {
      return $("#load_form > span").text(errormsg).removeClass("hidden");
    }).always(function() {
      return $("#loading").addClass("hidden");
    });
  };
  MIBC.update_form = function(data) {
    return $("#metadata input, #metadata select").each(function(i, el) {
      var attr_arr, fields, j, row, _i, _ref;
      if (data[el.name] != null) {
        attr_arr = data[el.name];
        fields = $("[name='" + el.name + "']");
        if (fields.parent().length < attr_arr.length) {
          for (_i = 1, _ref = attr_arr.length - 1; 1 <= _ref ? _i <= _ref : _i >= _ref; 1 <= _ref ? _i++ : _i--) {
            row = MIBC.rowadd($(el).parent());
            fields.push($(row).find("[name='" + el.name + "']")[0]);
          }
        }
        j = 0;
        return fields.each(function(_, field) {
          if (field.type === "checkbox" && attr_arr[j] === "true") {
            $(field).prop("checked", true);
            $(field).change();
            return;
          }
          if (!$(field).val()) {
            $(field).val(attr_arr[j]);
            j += 1;
          }
        });
      }
    });
  };
  MIBC.generate_metadata = function() {
    var records, rows;
    records = {};
    rows = [];
    $("#metadata input[required], #metadata select[required]").each(function(i, el) {
      if (typeof records[this.name] === "undefined") {
        records[this.name] = [MIBC._val(this)];
      } else {
        records[this.name].push(MIBC._val(this));
      }
    });
    $.each(records, function(key, val) {
      rows.push([key, val.join("\t")].join("\t"));
    });
    return rows.join("\n");
  };
  MIBC.rowdel = function() {
    $(this).parents().filter(".row").remove();
  };
  MIBC.rowadd = function($row) {
    var anchor;
    anchor = $row.clone().insertAfter($row).find("a");
    anchor.on("click", MIBC.rowdel);
    anchor.children().first().removeClass("rowadd glyphicon-plus-sign").addClass("glyphicon-minus-sign");
    return anchor.parent();
  };
  validator = $("form").validate({
    debug: true,
    errorLabelContainer: "#message_box",
    wrapper: "span",
    invalidHandler: function(event, validator) {
      $("#message_box").removeClass("hidden");
    },
    successHandler: function(event, validator) {
      $(this).removeClass("btn-primary").addClass("btn-success");
    },
    rules: {
      "16s_data": {
        required: false
      },
      submit_to_sra: {
        required: false
      }
    },
    messages: {
      pi_first_name: "Please include a first name for the principle investigator",
      pi_last_name: "Please fill in the principle investigator's last name",
      pi_contact_email: "Please provide an email from the principle investigator",
      lab_name: "Please define a lab for this data submission",
      researcher_first_name: "Please fill in a first name for the researcher",
      researcher_last_name: "Please fill in a last name for the researcher",
      researcher_contact_email: "Please provide an email address for the researcher",
      study_title: "Please give your study a title",
      study_description: "Please describe the question your study is addressing",
      sample_type: "Please select a sample type",
      collection_start_date: "Please give a valid date for when data collection started",
      collection_end_date: "Please give a valid date for when data collection finished",
      geo_loc_name: "Please supply the geographic location of your sequence",
      lat_lon: "Please give the latitude and longitude of your location",
      reverse_primer: "Please fill in the reverse primer you used",
      platform: "Please fill in what platform you used for 16s sequencing",
      filename: "Please include at least one Filename"
    }
  });
  $(".rowadd").click(function() {
    return MIBC.rowadd($(this).parent().parent());
  });
  $("#metadata :checkbox").change(function() {
    var row;
    row = $("#" + this.name);
    row.toggleClass("hidden");
    return row.children().attr("required", function(idx, oldAttr) {
      return !oldAttr;
    });
  });
  $("#save_btn").click(function() {
    if ($("form").valid() || $("#save_override")[0].checked) {
      $(this).removeClass("btn-primary").addClass("btn-success");
      return MIBC.url(this, MIBC.generate_metadata(), "metadata.txt");
    } else {
      $(this).removeClass("btn-primary").addClass("btn-danger");
      return $(this).attr("href", "#");
    }
  });
  $("#load_btn").click(function() {
    var pass, user, _ref;
    if ($(this).attr("clicked") !== "true") {
      $(this).attr("clicked", true);
      return $("#load_form").fadeIn();
    } else {
      $(this).attr("clicked", false);
      _ref = $("#load_form").children().map(function() {
        return $(this).val();
      }), user = _ref[0], pass = _ref[1];
      if (user && pass) {
        return MIBC.load_metadata(user, pass);
      } else {
        return $("#load_form").fadeOut();
      }
    }
  });
});
