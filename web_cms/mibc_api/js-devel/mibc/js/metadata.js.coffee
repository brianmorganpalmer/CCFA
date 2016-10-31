
# from MIBC: MIBC

$(document).ready ->

  MIBC._val = (el) ->
    (if el.type is "checkbox" then el.checked else el.value)

  MIBC.load_metadata = (user, pass) ->
    $("#loading").removeClass("hidden")
    $.get MIBC.config.api_base + ["projects", user, pass].join "/"
      .done (data) ->
        MIBC.update_form data
        $("#load_form > span").addClass("hidden").empty()
        $("#load_form").fadeOut()
      .error (jqxhr, status, errormsg) ->
        $("#load_form > span").text(errormsg).removeClass("hidden")
      .always ->
        $("#loading").addClass("hidden")

  MIBC.update_form = (data) ->
    $("#metadata input, #metadata select").each (i, el) ->
      if data[el.name]?
        attr_arr = data[el.name]
        fields = $("[name='"+el.name+"']")
        if fields.parent().length < attr_arr.length
          for [1..attr_arr.length-1]
            row = MIBC.rowadd $(el).parent()
            fields.push $(row).find("[name='"+el.name+"']")[0]
        j = 0
        fields.each (_, field) ->
          if field.type is "checkbox" and attr_arr[j] is "true"
            $(field).prop "checked", true
            $(field).change()
            return
          if not $(field).val()
            $(field).val attr_arr[j]
            j += 1
            return
          
  MIBC.generate_metadata = ->
    records = {}
    rows = []
    $("#metadata input[required], #metadata select[required]").each (i, el) ->
      if typeof (records[@name]) is "undefined"
        records[@name] = [MIBC._val(this)]
      else
        records[@name].push MIBC._val(this)
      return

    $.each records, (key, val) ->
      rows.push [
        key
        val.join("\t")
      ].join("\t")
      return

    rows.join "\n"

  MIBC.rowdel = ->
    $(this).parents().filter(".row").remove()
    return

  MIBC.rowadd = ($row) ->
    anchor = $row.clone().insertAfter($row).find("a")
    anchor.on "click", MIBC.rowdel
    anchor.children().first()
      .removeClass("rowadd glyphicon-plus-sign")
      .addClass "glyphicon-minus-sign"
    return anchor.parent()

  
  # Validation logic
  validator = $("form").validate(
    debug: true
    errorLabelContainer: "#message_box"
    wrapper: "span"
    invalidHandler: (event, validator) ->
      $("#message_box").removeClass "hidden"
      return

    successHandler: (event, validator) ->
      $(this).removeClass("btn-primary").addClass "btn-success"
      return

    rules:
      "16s_data":
        required: false

      submit_to_sra:
        required: false

    messages:
      pi_first_name: "Please include a first name for the principle investigator"
      pi_last_name: "Please fill in the principle investigator's last name"
      pi_contact_email: "Please provide an email from the principle investigator"
      lab_name: "Please define a lab for this data submission"
      researcher_first_name: "Please fill in a first name for the researcher"
      researcher_last_name: "Please fill in a last name for the researcher"
      researcher_contact_email: "Please provide an email address for the researcher"
      study_title: "Please give your study a title"
      study_description: "Please describe the question your study is addressing"
      sample_type: "Please select a sample type"
      collection_start_date: "Please give a valid date for when data collection started"
      collection_end_date: "Please give a valid date for when data collection finished"
      geo_loc_name: "Please supply the geographic location of your sequence"
      lat_lon: "Please give the latitude and longitude of your location"
      reverse_primer: "Please fill in the reverse primer you used"
      platform: "Please fill in what platform you used for 16s sequencing"
      filename: "Please include at least one Filename"
  )
  
  # Event listeners
  $(".rowadd").click ->
    MIBC.rowadd $(this).parent().parent()

  $("#metadata :checkbox").change ->
    row = $("#" + @name)
    row.toggleClass "hidden"
    row.children().attr "required", (idx, oldAttr) ->
      not oldAttr

  $("#save_btn").click ->
    if $("form").valid() or $("#save_override")[0].checked
      $(this).removeClass("btn-primary").addClass "btn-success"
      MIBC.url this, MIBC.generate_metadata(), "metadata.txt"
    else
      $(this).removeClass("btn-primary").addClass "btn-danger"
      $(this).attr "href", "#"

  $("#load_btn").click ->
    if $(this).attr("clicked") isnt "true"
      $(this).attr("clicked", true)
      $("#load_form").fadeIn()
    else
      $(this).attr("clicked", false)
      [user, pass] = $("#load_form").children().map ->
        $(this).val()
      if user and pass
        MIBC.load_metadata user, pass
      else
        $("#load_form").fadeOut()
      
  return

