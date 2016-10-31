# from MIBC: MIBC

$(document).ready ->

  MIBC.load_efosuggestion = ->
    $("#loading").removeClass("hidden")
    url = MIBC.config.api_base + "utilities/efosuggest"
    data = JSON.stringify
      data: MIBC.extract_from_dom()[0].map (val, idx) ->
        [idx, val]

    $.ajax
        url:  url
        data: data
        type: "POST"
        dataType: "json"
      .done (data) ->
        MIBC.display_suggestions data
        MIBC.noerror()
      .error (jqxhr, status, errormsg) ->
        MIBC.error errormsg
      .always ->
        $("#loading").addClass("hidden")

  MIBC.load_efovalidation = ->
    $("#loading").removeClass("hidden")
    url = MIBC.config.api_base + "utilities/efovalidate"
    data = [].concat.apply [], MIBC.extract_from_dom()
    data = JSON.stringify
      data: data.map (val, idx) ->
        [idx, val]

    $.ajax
        url:  url
        data: data
        type: "POST"
        dataType: "json"
      .done (data) ->
        MIBC.display_validation data
        MIBC.noerror()
      .error (jqxhr, status, errormsg) ->
        MIBC.error errormsg
      .always ->
        $("#loading").addClass("hidden")

  MIBC.load_samplemeta = (user, proj) ->
    $("#loading").removeClass("hidden")
    $.get MIBC.config.api_base + ["projects", user, proj].join "/"
      .done (data) ->
        MIBC.display_samplemeta data
        MIBC.noerror()
      .error (jqxhr, status, errormsg) ->
        MIBC.error errormsg
      .always ->
        $("#loading").addClass("hidden")

  MIBC.clear = ->
    $("#results").empty()

  MIBC.extract_from_dom = ->
    ( (field.innerText for field in row.children) \
      for row in $("#results tr").get() )

  MIBC.serialize = (arr) ->
    rows = ( row.join('\t') for row in arr )
    rows.join('\n')

  MIBC.display_suggestions = (data) ->
   allchildren = $("#results tr").children()
   for [idx, suggestion] in data
     continue if suggestion[1].length is 0
     menulist = $('<ul class="nav nav-pills nav-stacked" />').append(
        ('<li><a id="'+s[0]+'">'+s[1]+'('+s[0]+')'+'</a></li>' \
        for s in suggestion).join("")
     )
     menulist.on "click", "a", ->
        MIBC.suggestion_choose(this)
     $(allchildren[idx]).append menulist

  MIBC.display_validation = (data) ->
   allchildren = $("#results tr").children()
   for [idx, result] in data
     if result[1] is true
       $(allchildren[idx]).wrapInner '<span class="label label-success"></span>'
     else
       $(allchildren[idx]).wrapInner '<span class="label label-danger"></span>'

  MIBC.display_samplemeta = (data) ->
    window.MIBCdata = data
    $("#results").append "<tr><th>" \
                         + data.map_headers.join("</th><th>") \
                         + "</th></tr>"
                 .append ( "<tr><td>"+row.join("</td><td>")+"</td></tr>" \
                           for row in data.map ).join("")

  MIBC.suggestion_choose = (el) ->
    v = el.id
    $(el).parent().parent().parent()
      .empty()
      .text(v)
    
  MIBC.finish_edit = (el) ->
    v = el.value
    $(el).parent()
      .empty()
      .text(v)
      .removeClass("in_edit")
      .click(MIBC.start_edit)

  MIBC.start_edit = ->
    return if $(this).hasClass "in_edit" 
    t = this.innerText
    $(this).empty().append( $("<input>").attr(
        type:  "text"
        value: t
        width: "100%"
      ).on(
        blur: ->
          MIBC.finish_edit(this)
        keyup: ->
          MIBC.finish_edit(this) if event.which is MIBC.keys.ENTER
      )
    ).addClass("in_edit")

  $("#load_btn").click ->
    [user, proj] = ( $(query).val() for query in ["#load_usr", "#load_proj"] )
    MIBC.loadwrapper user, proj, MIBC.load_samplemeta

  $("#validate_btn").click ->
    this.href = window.location.hash
    if $("#results td").length < 1
      MIBC.error "Please load a project first"
      return
    MIBC.load_efovalidation()
    MIBC.noerror()

  $("#suggest_btn").click ->
    this.href = window.location.hash
    if $("#results td").length < 1
      MIBC.error "Please load a project first"
      return
    MIBC.load_efosuggestion()
    MIBC.noerror()

  $("#save_btn").click ->
    a = MIBC.extract_from_dom()
    MIBC.url this, MIBC.serialize(a), "map.txt"

  $("#results").on "click", "td", MIBC.start_edit

  if window.location.hash?
    [user, proj] = window.location.hash.replace("#", "").split "/"
    if user? and proj?
      MIBC.loadwrapper user, proj, MIBC.load_samplemeta
