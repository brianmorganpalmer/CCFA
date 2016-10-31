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
  var proj, user, _ref;
  MIBC.load_validation = function(user, proj) {
    $("#loading").removeClass("hidden");
    return $.get(MIBC.config.api_base + ["projects", user, proj, "validate"].join("/")).done(function(data) {
      MIBC.display_results(data);
      return MIBC.noerror();
    }).error(function(jqxhr, status, errormsg) {
      return MIBC.error(errormsg);
    }).always(function() {
      return $("#loading").addClass("hidden");
    });
  };
  MIBC.clear = function() {
    $("#results").empty();
    return $("#status").addClass("hidden");
  };
  MIBC.display_results = function(data) {
    var allclear, message, report, status, _i, _len;
    window.MIBCdata = data;
    allclear = true;
    for (_i = 0, _len = data.length; _i < _len; _i++) {
      report = data[_i];
      status = report[0], message = report[1];
      if (status === !true) {
        allclear = false;
        $("#results").append($("#error_tpl").clone().text(message));
      }
    }
    if (allclear === true) {
      $("#status").removeClass("hidden btn-danger").addClass("btn-success");
      return $("#status span").removeClass("glyphicon-thumbs-down").addClass("glyphicon-thumbs-up");
    } else {
      $("#status").removeClass("hidden btn-success").addClass("btn-danger");
      return $("#status span").removeClass("glyphicon-thumbs-up").addClass("glyphicon-thumbs-down");
    }
  };
  $("#load_btn").click(function() {
    var proj, query, user, _ref;
    _ref = (function() {
      var _i, _len, _ref, _results;
      _ref = ["#load_usr", "#load_proj"];
      _results = [];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        query = _ref[_i];
        _results.push($(query).val());
      }
      return _results;
    })(), user = _ref[0], proj = _ref[1];
    return MIBC.loadwrapper(user, proj, MIBC.load_validation);
  });
  if (window.location.hash != null) {
    _ref = window.location.hash.replace("#", "").split("/"), user = _ref[0], proj = _ref[1];
    if ((user != null) && (proj != null)) {
      return MIBC.loadwrapper(user, proj, MIBC.load_validation);
    }
  }
});
