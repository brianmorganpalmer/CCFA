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
  MIBC.load_efosuggestion = function() {
    var data, url;
    $("#loading").removeClass("hidden");
    url = MIBC.config.api_base + "utilities/efosuggest";
    data = JSON.stringify({
      data: MIBC.extract_from_dom()[0].map(function(val, idx) {
        return [idx, val];
      })
    });
    return $.ajax({
      url: url,
      data: data,
      type: "POST",
      dataType: "json"
    }).done(function(data) {
      MIBC.display_suggestions(data);
      return MIBC.noerror();
    }).error(function(jqxhr, status, errormsg) {
      return MIBC.error(errormsg);
    }).always(function() {
      return $("#loading").addClass("hidden");
    });
  };
  MIBC.load_efovalidation = function() {
    var data, url;
    $("#loading").removeClass("hidden");
    url = MIBC.config.api_base + "utilities/efovalidate";
    data = [].concat.apply([], MIBC.extract_from_dom());
    data = JSON.stringify({
      data: data.map(function(val, idx) {
        return [idx, val];
      })
    });
    return $.ajax({
      url: url,
      data: data,
      type: "POST",
      dataType: "json"
    }).done(function(data) {
      MIBC.display_validation(data);
      return MIBC.noerror();
    }).error(function(jqxhr, status, errormsg) {
      return MIBC.error(errormsg);
    }).always(function() {
      return $("#loading").addClass("hidden");
    });
  };
  MIBC.load_samplemeta = function(user, proj) {
    $("#loading").removeClass("hidden");
    return $.get(MIBC.config.api_base + ["projects", user, proj].join("/")).done(function(data) {
      MIBC.display_samplemeta(data);
      return MIBC.noerror();
    }).error(function(jqxhr, status, errormsg) {
      return MIBC.error(errormsg);
    }).always(function() {
      return $("#loading").addClass("hidden");
    });
  };
  MIBC.clear = function() {
    return $("#results").empty();
  };
  MIBC.extract_from_dom = function() {
    var field, row, _i, _len, _ref, _results;
    _ref = $("#results tr").get();
    _results = [];
    for (_i = 0, _len = _ref.length; _i < _len; _i++) {
      row = _ref[_i];
      _results.push((function() {
        var _j, _len1, _ref1, _results1;
        _ref1 = row.children;
        _results1 = [];
        for (_j = 0, _len1 = _ref1.length; _j < _len1; _j++) {
          field = _ref1[_j];
          _results1.push(field.innerText);
        }
        return _results1;
      })());
    }
    return _results;
  };
  MIBC.serialize = function(arr) {
    var row, rows;
    rows = (function() {
      var _i, _len, _results;
      _results = [];
      for (_i = 0, _len = arr.length; _i < _len; _i++) {
        row = arr[_i];
        _results.push(row.join('\t'));
      }
      return _results;
    })();
    return rows.join('\n');
  };
  MIBC.display_suggestions = function(data) {
    var allchildren, idx, menulist, s, suggestion, _i, _len, _ref, _results;
    allchildren = $("#results tr").children();
    _results = [];
    for (_i = 0, _len = data.length; _i < _len; _i++) {
      _ref = data[_i], idx = _ref[0], suggestion = _ref[1];
      if (suggestion[1].length === 0) {
        continue;
      }
      menulist = $('<ul class="nav nav-pills nav-stacked" />').append(((function() {
        var _j, _len1, _results1;
        _results1 = [];
        for (_j = 0, _len1 = suggestion.length; _j < _len1; _j++) {
          s = suggestion[_j];
          _results1.push('<li><a id="' + s[0] + '">' + s[1] + '(' + s[0] + ')' + '</a></li>');
        }
        return _results1;
      })()).join(""));
      menulist.on("click", "a", function() {
        return MIBC.suggestion_choose(this);
      });
      _results.push($(allchildren[idx]).append(menulist));
    }
    return _results;
  };
  MIBC.display_validation = function(data) {
    var allchildren, idx, result, _i, _len, _ref, _results;
    allchildren = $("#results tr").children();
    _results = [];
    for (_i = 0, _len = data.length; _i < _len; _i++) {
      _ref = data[_i], idx = _ref[0], result = _ref[1];
      if (result[1] === true) {
        _results.push($(allchildren[idx]).wrapInner('<span class="label label-success"></span>'));
      } else {
        _results.push($(allchildren[idx]).wrapInner('<span class="label label-danger"></span>'));
      }
    }
    return _results;
  };
  MIBC.display_samplemeta = function(data) {
    var row;
    window.MIBCdata = data;
    return $("#results").append("<tr><th>" + data.map_headers.join("</th><th>") + "</th></tr>").append(((function() {
      var _i, _len, _ref, _results;
      _ref = data.map;
      _results = [];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        row = _ref[_i];
        _results.push("<tr><td>" + row.join("</td><td>") + "</td></tr>");
      }
      return _results;
    })()).join(""));
  };
  MIBC.suggestion_choose = function(el) {
    var v;
    v = el.id;
    return $(el).parent().parent().parent().empty().text(v);
  };
  MIBC.finish_edit = function(el) {
    var v;
    v = el.value;
    return $(el).parent().empty().text(v).removeClass("in_edit").click(MIBC.start_edit);
  };
  MIBC.start_edit = function() {
    var t;
    if ($(this).hasClass("in_edit")) {
      return;
    }
    t = this.innerText;
    return $(this).empty().append($("<input>").attr({
      type: "text",
      value: t,
      width: "100%"
    }).on({
      blur: function() {
        return MIBC.finish_edit(this);
      },
      keyup: function() {
        if (event.which === MIBC.keys.ENTER) {
          return MIBC.finish_edit(this);
        }
      }
    })).addClass("in_edit");
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
    return MIBC.loadwrapper(user, proj, MIBC.load_samplemeta);
  });
  $("#validate_btn").click(function() {
    this.href = window.location.hash;
    if ($("#results td").length < 1) {
      MIBC.error("Please load a project first");
      return;
    }
    MIBC.load_efovalidation();
    return MIBC.noerror();
  });
  $("#suggest_btn").click(function() {
    this.href = window.location.hash;
    if ($("#results td").length < 1) {
      MIBC.error("Please load a project first");
      return;
    }
    MIBC.load_efosuggestion();
    return MIBC.noerror();
  });
  $("#save_btn").click(function() {
    var a;
    a = MIBC.extract_from_dom();
    return MIBC.url(this, MIBC.serialize(a), "map.txt");
  });
  $("#results").on("click", "td", MIBC.start_edit);
  if (window.location.hash != null) {
    _ref = window.location.hash.replace("#", "").split("/"), user = _ref[0], proj = _ref[1];
    if ((user != null) && (proj != null)) {
      return MIBC.loadwrapper(user, proj, MIBC.load_samplemeta);
    }
  }
});
