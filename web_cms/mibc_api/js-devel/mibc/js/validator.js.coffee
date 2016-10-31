
# from MIBC: MIBC

$(document).ready ->

  MIBC.load_validation = (user, proj) ->
    $("#loading").removeClass("hidden")
    $.get MIBC.config.api_base + ["projects", user, proj, "validate"].join "/"
      .done (data) ->
        MIBC.display_results data
        MIBC.noerror()
      .error (jqxhr, status, errormsg) ->
        MIBC.error errormsg
      .always ->
        $("#loading").addClass("hidden")

  MIBC.clear = ->
    $("#results").empty()
    $("#status").addClass "hidden"

  MIBC.display_results = (data) ->
    window.MIBCdata = data
    allclear = true
    for report in data
      [status, message] = report
      if status is not true
        allclear = false
        $("#results").append $("#error_tpl").clone().text(message)
    if allclear is true
      $("#status")
        .removeClass("hidden btn-danger")
        .addClass("btn-success")
      $("#status span").removeClass("glyphicon-thumbs-down")
        .addClass("glyphicon-thumbs-up")
    else
      $("#status")
        .removeClass("hidden btn-success")
        .addClass("btn-danger")
      $("#status span").removeClass("glyphicon-thumbs-up")
        .addClass("glyphicon-thumbs-down")


  $("#load_btn").click ->
    [user, proj] = ( $(query).val() for query in ["#load_usr", "#load_proj"] )
    MIBC.loadwrapper user, proj, MIBC.load_validation

  if window.location.hash?
    [user, proj] = window.location.hash.replace("#", "").split "/"
    if user? and proj?
      MIBC.loadwrapper user, proj, MIBC.load_validation
    



