/*
  Stylesheet

  Author: Milind Agarwal

  This is the custom JS for all the templates for this application.

  */

  $any_push_files = []
function getCookie(cname) {
  var name = cname + "=";
  var decodedCookie = decodeURIComponent(document.cookie);
  var ca = decodedCookie.split(';');
  for(var i = 0; i <ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}
$(document).keypress(
  function(event){
    if (event.which == '13') {
      event.preventDefault();
    }
});



$(document).ready(function() {

  var len = $('.height').length
  for (var l = 0; l < len; l = l + 1) {
    $('.height')[l].style.height = "27em"
  }

  $("video source").each(function() {
    var sourceFile = $(this).attr("data-src");
    $(this).attr("src", sourceFile);
    var video = this.parentElement;
    video.load();
    // uncomment if video is not autoplay
    //video.play();
  });


});

$(document).ready(function() {
  // Add minus icon for collapse element which is open by default
  $(".collapse.show").each(function() {
    $(this).prev(".card-header").find(".fa").addClass("fa-minus").removeClass("fa-plus");
  });

  // Toggle plus minus icon on show hide of collapse element
  $(".collapse").on('show.bs.collapse', function() {
    $(this).prev(".card-header").find(".fa").removeClass("fa-plus").addClass("fa-minus");
  }).on('hide.bs.collapse', function() {
    $(this).prev(".card-header").find(".fa").removeClass("fa-minus").addClass("fa-plus");
  });


});


// PATHWAY ANALYSIS CODE . .
var storedFilesGeneMania = [];

// sleep time expects milliseconds
function sleep(time) {
  return new Promise((resolve) => setTimeout(resolve, time));
}

$(document).ready(function() {

  $('#genemaniabutton').on('click', function() {

    console.log("div gene mania button clicked")

    // var form_data = new FormData($('#genemaniaform')[0]);
    var data = new FormData();

    storedFilesGeneMania.forEach(function(file, i) {
      data.append('genemaniafile', file);
    });

    console.log(storedFilesGeneMania)
    // send ajax POST request to start background job
    $.ajax({
      type: 'POST',
      url: '/genemania',
      data: data,
      cache: false,
      processData: false,
      contentType: false,
      success: function(data, status, request) {
        $('.inprogress').css('display', 'none');
        $('.completed').css('display', 'inline');
        // $('#download_cleanbutton').css('display', 'inline')

        console.log("Hi!!! :) :) You got this! ")
        // Parse the response gene list here.
        append = 'human/' + data

        // And then generate the appropriate URL for it. // Embed it in the iframe src.
        $('#pathwayIFRAME')[0].src = 'http://genemania.org/search/' + append
        console.log($('#pathwayIFRAME')[0].src)
      },
      error: function() {
        alert('Unexpected error');
      }

    });

  });
});


$(document).ready(function() {
  var selDiv = "";

  $("body").on('click', '.genemaniaicon', function(e) {
    console.log("Trash icon clicked. ")
    var file = $(e.currentTarget)["0"].parentNode.innerText
    console.log(file)
    for (var i = 0; i < storedFilesGeneMania.length; i++) {
      // There's whitespace at the end of these stupid files. Please make sure
      // use trim() otherwise your string equality won't work even if comparing
      // 'identical' strings.
      if (storedFilesGeneMania[i].name.trim() == file.trim()) {
        // Not being called at the moment.
        console.log(file)
        storedFilesGeneMania.splice(i, 1);
        break;
      }
      console.log(i)
    }

    $(this)['0'].parentElement.remove();
    console.log(storedFilesGeneMania);
  });
  //
  //
  $("#genemaniaupload").on('change', function(e) {
    $('.alert-danger').css('display', 'none');
    storedFilesGeneMania = []
    console.log("We're in here/ ")
    var files = e.target.files
    var filesArr = Array.prototype.slice.call(files);
    var input = document.getElementById('genemaniaupload');
    var output = document.getElementById('genemaniaFileList');
    // output.innerHTML = '<ul>';
    // var urls = []
    for (var i = 0; i < input.files.length; ++i) {
      // This is the File Object that I can create the URL of.
      f = input.files.item(i);
      storedFilesGeneMania.push(f);
      output.innerHTML += '<li>' + f.name + ' <i class= "fas fa-trash-alt genemaniaicon"></i>' + '</li>';

      if (['csv', 'xlsx'].indexOf(f.name.split('.')[f.name.split('.').length - 1]) < 0) {
        $('.alert-danger').css('display', '');
      }

    }
    output.innerHTML += '</ul><br>';
  });
  //
});
// //



// IGV PART OF THE CODE. I wrote this.. .
// Global iterator.
var i = 0
// var line_split
var len_file
var packet_length
// var split_me
// var read
// var name

var mask
var perc = 0
var storedFilesIGV = [];
var trackFileList = []
var dataIGV = null
var searches = []

$(document).ready(() => {
  var pathname = window.location.pathname;
  $('.alert-danger').css('display', 'none');
  if (pathname == "/visualize") {
    document.body.style.zoom = "90%"
    $('#onuploaddiv').css('display', 'none');
    $('.progress-after').css('visibility', 'hidden');
    $('.card').css('visibility', 'hidden');
  }

  if (pathname == "/") {
    document.body.style.zoom = "75%"

  }


  if (pathname == '/genemania') {
    document.body.style.zoom = "75%"
  }

  if (pathname == '/ancestry') {
    $('.alert-danger').css('display', 'none');
  }
});

// sleep time expects milliseconds
function sleep(time) {
  return new Promise((resolve) => setTimeout(resolve, time));
}

$(document).ready(function() {

  var pathname = window.location.pathname;
  if (pathname == "/visualize") {

  $('.completed').css('display', 'none');
  $('.showmorelink').css('display', 'none');
  $('.statush6').css('visibility', 'visible');

  $('#igvloadingprogress')[0].style.width = "2%"

  $('#igvbutton').on('click', function() {

    console.log("div igv button clicked")
    $('.card').css('visibility', 'hidden');
    $('#onuploaddiv').css('display', 'none');
    $('#downloadAnchor').css('display', 'none');
    $('#yesbutton').css('display', 'none');
    $('#nobutton').css('display', 'none');
    $('#maybebutton').css('display', 'none');
    $('.progress-after').css('visibility', 'hidden');
    $('.statush6').css('visibility', 'visible');
    $('.completed').css('display', 'none');
    $('.notstarted').css('display', 'none');
    $('.inprogress').css('display', 'inline');

    $('.igvloadingprogress')[0].style.display = ""
    $('#igvloadingprogress')[0].style.width = "100%"




    // var form_data = new FormData($('#igvform')[0][1]);
    var data = new FormData();

    storedFilesIGV.forEach(function(file, i) {
      data.append('igvfile', file);
    });

    console.log(storedFilesIGV)
    // send ajax POST request to start background job
    $.ajax({
      type: 'POST',
      url: '/visualize',
      data: data,
      cache: false,
      processData: false,
      contentType: false,
      success: function(data, status, request) {
        // $('.inprogress').css('display', 'none');
        // $('#download_cleanbutton').css('display', 'inline')
        $('.igvloadingprogress')[0].style.display = "none"


        console.log("IGV button clicked")
        console.log("Hi!!! :) :) You got this! ")
        $('#progress').css('width', 0 + '%')

        $('.card').css('visibility', 'visible');

        $('#onuploaddiv').css('display', 'inline');
        $('#downloadAnchor').css('display', 'none');

        $('.statush6').css('visibility', 'hidden');
        $('#yesbutton').css('display', 'inline');
        $('#nobutton').css('display', 'inline');
        $('#onuploaddiv h5').css('display', 'inline')
        $('#maybebutton').css('display', 'inline');


        $('.progress-after').css('visibility', 'visible');


        // Need to build in a slight pause herem or when reader object is ready.
        // The 0th row is the column header of the CSV file.
        console.log("Loaded!")

        // Collapse the uploader.
        $('.showmorelink')[0].click()
        $('.showmorelink').css('display', 'inline');

        // Change the SRC of the iframe.
        $('#iframeID')[0].src = './static/igvjs_viewer.html'

        // Usage!
        // sleep(500).then(() => {
        //   // line_split = read.result.split("\n")
        // len_file = line_split.length
        //   // split_me = line_split[0].split(',')
        //   // This is the max value of my iterator.
        //
        mask = []
        //   // Resetting the iterator every time we upload a new file.
        i = 0
        perc = 0
        // var x = JSON.parse(data)
        // dataIGV = JSON.parse(x['packet'])
        // console.log(x['len_file'])
        // len_file = x['len_file']
        // packet_length = dataIGV.length
        // Manual add:

        $('#iframeID').load(function() {
          len_file = $('#iframeID').contents().find('tbody tr').length
          packet_length = len_file
          console.log(len_file)
          console.log("NEw code being executed. ")
          // Make everything invisible except 0.
          for (var p = 1; p < len_file; p = p + 1) {
            $('#iframeID').contents().find('tbody tr')[p].style.display = "none"
          }

        });



        //   // update(i)
        //
        //   // console.log('chr' + dataIGV[i][0] + ':' + dataIGV[i][1] + '-' + dataIGV[i][2])
        //   var search = 'chr' + dataIGV[i][0] + ':' + dataIGV[i][1] + '-' + dataIGV[i][2]
        //   console.log(search)
        //   searches.push(search)
        //   $('#iframeID').contents().find('.igv-search-container input')[0].value = search
        //   $('#iframeID').contents().find('.igv-search-container div').click()
        //   // console.log(i)
        // });
      },
      error: function() {
        alert('Unexpected error');
      }

    });


    console.log("Code here will get executed, becuase AJAX is asynchronous..")

    });

}

});


function updateThePage() {

  $.ajax({
    type: 'POST',
    url: '/igvBatch',
    data: mask,
    cache: false,
    processData: false,
    contentType: false,
    success: function(data, status, request) {
      $('.inprogress').css('display', 'none');
      $('.completed').css('display', 'inline');
      // $('#download_cleanbutton').css('display', 'inline')

      console.log("BATCH: New packet stream coming in")
      console.log("Hi!!! :) :) You got this! ")

      // Change the SRC of the iframe.

      mask = []
      // Resetting the iterator every time we upload a new file.
      i = 0
      perc = 0

      // console.log(x['len_file'])
      // len_file = x['len_file']

      packet_length = 1

      dataIGV = JSON.parse(data)
      len = dataIGV['len_file']

      if (len == 0) {
        console.log("You ate all the packets :)) No more data left. ")
        $('#yesbutton').css('display', 'none')
        $('#nobutton').css('display', 'none')
        $('#maybebutton').css('display', 'none')
        $('#onuploaddiv h5').css('display', 'none')
        $('#downloadAnchor').css('display', 'inline')
      } else {
        $('#iframeID')[0].src = './static/igvjs_viewer.html'
      }



    },

    error: function() {
      alert('Unexpected error');
    }

  });
  // Make an AJAX request here to ASK FOR MORE.
  // Send as data: mask
  // Response: either more data, in which case 'go to' the appropriate location in code.
  // Else if response is "DONE", in that case. Just offer the download link, because the file will have been generated already



  console.log("Leaving the update function")
}

$(document).ready(function() {

  $('#yesbutton').on('click', function() {

    // True
    mask.push("YES")
    perc += 1
    var t = perc * 100 / (len_file - 1)
    console.log(t)

    $('#progress').css('width', t + '%')


    console.log("Yes button clicked! ")
    // Freeing up memory from variant we don't need anymore.

    // delete dataIGV[i]
    i = i + 1
    // $('#iframeID')[0].src = './static/igvjs_viewer.html'

    if (i == packet_length) {
      console.log(i)
      // updateThePage()
      console.log("Borderline")

      updateThePage()
    } else {
      console.log(i)

      // JS magic..
      $('#iframeID').contents().find('tbody tr')[i - 1].style.display = "none"
      $('#iframeID').contents().find('tbody tr')[i].style.display = ""
      $('#iframeID').contents().find('tbody tr')[i].children[0].click()


      // var search = 'chr' + dataIGV[i][0] + ':' + dataIGV[i][1] + '-' + dataIGV[i][2]
      // console.log(search)
      // searches.push(search)
      // $('#iframeID').contents().find('.igv-search-container input')[0].value = search
      // $('#iframeID').contents().find('.igv-search-container div').click()
    }



  });

  $('#nobutton').on('click', function() {
    // False
    mask.push("NO")
    perc += 1
    var t = perc * 100 / (len_file - 1)
    $('#progress').css('width', t + '%')

    console.log("No button clicked! ")
    // Freeing up memory from variant we don't need anymore.
    // delete dataIGV[i]
    i = i + 1
    // $('#iframeID')[0].src = './static/igvjs_viewer.html'

    if (i == packet_length) {
      console.log(i)
      console.log("Borderline")
      updateThePage()
    } else {
      console.log(i)
      $('#iframeID').contents().find('tbody tr')[i - 1].style.display = "none"
      $('#iframeID').contents().find('tbody tr')[i].style.display = ""
      $('#iframeID').contents().find('tbody tr')[i].children[0].click()

      // var search = 'chr' + dataIGV[i][0] + ':' + dataIGV[i][1] + '-' + dataIGV[i][2]
      // console.log(search)
      // searches.push(search)
      // $('#iframeID').contents().find('.igv-search-container input')[0].value = search
      // $('#iframeID').contents().find('.igv-search-container div').click()
    }

  });

  $('#maybebutton').on('click', function() {
    console.log("Maybe button was clicked even though process was executing in background... this is promising :))")
    // False

    // Push MAYBE or " " BLANK, or SKIP
    mask.push("MAYBE")
    perc += 1
    var t = perc * 100 / (len_file - 1)
    $('#progress').css('width', t + '%')

    console.log("Maybe button clicked! ")
    // Freeing up memory from variant we don't need anymore.
    // delete dataIGV[i]
    i = i + 1
    // $('#iframeID')[0].src = './static/igvjs_viewer.html'

    if (i == packet_length) {
      console.log(i)
      console.log("Borderline")
      updateThePage()
    } else {

      console.log(i)
      $('#iframeID').contents().find('tbody tr')[i - 1].style.display = "none"
      $('#iframeID').contents().find('tbody tr')[i].style.display = ""
      $('#iframeID').contents().find('tbody tr')[i].children[0].click()


      // var search = 'chr' + dataIGV[i][0] + ':' + dataIGV[i][1] + '-' + dataIGV[i][2]
      // console.log(search)
      // searches.push(search)
      // $('#iframeID').contents().find('.igv-search-container input')[0].value = search
      // $('#iframeID').contents().find('.igv-search-container div').click()
    }

  });

});

$(document).ready(function() {
  $('#downloadAnchor').on('click', function() {

    console.log("Triggering a click now.....")
    // $('#downloadAnchor').click()

    console.log("Download button clicked!")

    // Download the appropriate file as CSV.

    $.ajax({
      type: 'POST',
      url: '/downloadIGV',
      success: function(data, status, request) {
        console.log(searches)
        length = data.length
        for (i = 0; i < data.length; i++) {
          file_data = data[i][1]
          file_name = data[i][0]
          parsed_data = Papa.unparse(file_data)
          download(parsed_data, file_name, "text/csv")
        }
      }
    });






  })
});

$(document).ready(function() {
  var selDiv = "";

  $("body").on('click', '.igvicon', function(e) {
    console.log("Trash icon clicked. ")
    var file = $(e.currentTarget)["0"].parentNode.innerText
    console.log(file)
    for (var i = 0; i < storedFilesIGV.length; i++) {
      // There's whitespace at the end of these stupid files. Please make sure
      // use trim() otherwise your string equality won't work even if comparing
      // 'identical' strings.
      if (storedFilesIGV[i].name.trim() == file.trim()) {
        // Not being called at the moment.
        console.log(file)
        storedFilesIGV.splice(i, 1);
        break;
      }
      console.log(i)
    }

    $(this)['0'].parentElement.remove();
    console.log(storedFilesIGV);
  });
  //
  //
  $("#igvupload").on('change', function(e) {
    $('.alert-danger').css('display', 'none');

    storedFilesIGV = []
    console.log("We're in here/ ")
    var files = e.target.files
    var filesArr = Array.prototype.slice.call(files);
    var input = document.getElementById('igvupload');
    var output = document.getElementById('igvFileList');
    output.innerHTML = '<ul>';
    // var urls = []
    for (var i = 0; i < input.files.length; ++i) {
      // This is the File Object that I can create the URL of.
      f = input.files.item(i);
      storedFilesIGV.push(f);
      output.innerHTML += '<li>' + f.name + ' <i class= "fas fa-trash-alt igvicon"></i>' + '</li>';

      if (['csv', 'xlsx'].indexOf(f.name.split('.')[f.name.split('.').length - 1]) < 0) {
        $('.alertFile').css('display', '');
      }

    }
    output.innerHTML += '</ul><br>';
  });
  //
  //
});
// //

$(document).ready(function() {

  $('#trackbutton').on('click', function() {
    $.ajax({
      type: 'POST',
      url: '/selecttrack',
      success: function(data, status, request) {
        trackFileList = []
        // Here, read from the file with all the paths
        console.log(data['data'])
        var output = document.getElementById('trackFileList');
        // Display these in a div as a list
        output.innerHTML = '<ul>';
        $('.alert-danger').css('display', 'none');

        for (var k = 0; k < data['data'].length; k = k + 1) {
          var temp = data['data'][k].split('/').slice(-1)[0]
          trackFileList.push(temp)
          output.innerHTML += '<li>' + temp + '</li>';

          if (['bam', 'cram'].indexOf(temp.split('.')[temp.split('.').length - 1]) < 0) {
            $('.alert-danger').css('display', '');
          }
        }
        output.innerHTML += '</ul><br>';

        // If you add a little trash icon, then you can directly modify that file in your sandbox.

        console.log("Track paths have been saved. ")

      }
    });
  });
});

// TRYING TO WRITE A GENERIC PROGRESS BAR METHOD..
function update_progress(status_url) {
    // send GET request to status URL
    $.getJSON(status_url, function(data) {
      console.log("In the update_progress methods..... ")
        // update UI
        console.log(data)
        percent = parseInt(data['current']*100/ data['total']);

        $('.progress-bar')[0].style.width = "" + percent + "%";

        // $(status_div.childNodes[1]).text(percent + '%');
        // $(status_div.childNodes[2]).text(data['status']);
        if (data['state'] != 'PENDING' && data['state'] != 'PROGRESS') {
            if ('result' in data) {

                // The task was completed!!!
                var pathname = window.location.pathname;
                if (pathname == "/clean"){
                  console.log("Pathname was clean. Making buttons visible. ")
                  $('.inprogress').css('display', 'none');
                  $('#download_cleanbutton').css('display', 'inline');
                  $('#push_cleanbutton').css('display', 'inline');
                  $('.completed').css('display', 'inline');
                }

                else if (pathname == "/annotate"){
                  console.log("Pathname was annotate. Making buttons visible. ")
                  $('.inprogress').css('display', 'none');
                  $('.completed').css('display', 'inline');
                  $('#download_annotatebutton').css('display', 'inline');
                  $('#push_annotatebutton').css('display', 'inline');
                }

                else if (pathname == "/filtering") {
                  $('.inprogress').css('display', 'none');
                  $('.completed').css('display', 'inline');
                  $('#download_filterbutton').css('display', 'inline');
                  $('#push_filterbutton').css('display', 'inline')
                }

                else if (pathname == "/modes") {
                  $('.inprogress').css('display', 'none');
                  $('.completed').css('display', 'inline');
                  $('#download_modesbutton').css('display', 'inline')
                  $('#push_modesbutton').css('display', 'inline')
                }

                else if (pathname == '/unbiasedcohort') {
                  $('.inprogress').css('display', 'none');
                  $('.completed').css('display', 'inline');
                  $('#download_unbiasedcohortbutton').css('display', 'inline')
                }

                else if (pathname == '/biasedcohort') {
                  $('.inprogress').css('display', 'none');
                  $('.completed').css('display', 'inline');
                  $('#download_biasedcohortbutton').css('display', 'inline')
                }

                else if (pathname == '/gen_blacklist') {
                  $('.inprogress').css('display', 'none');
                  $('.completed').css('display', 'inline');
                  $('#download_gen_blacklistbutton').css('display', 'inline')
                }

                else if  (pathname == '/apply_blacklist') {
                  $('.inprogress').css('display', 'none');
                  $('.completed').css('display', 'inline');
                  $('#download_apply_blacklistbutton').css('display', 'inline')
                }

                else if  (pathname == '/onevcf') {
                  $('.inprogress').css('display', 'none');
                  $('.completed').css('display', 'inline');
                  $('#download_onevcfbutton').css('display', 'inline');
                  $('#push_onevcfbutton').css('display', 'inline');
                }

                else if  (pathname == '/twovcf') {
                  $('.inprogress').css('display', 'none');
                  $('.completed').css('display', 'inline');
                  $('#download_twovcfbutton').css('display', 'inline');
                  $('#push_twovcfbutton').css('display', 'inline');
                }

                else if (pathname == '/ancestry') {
                  $('.inprogress').css('display', 'none');
                  $('.completed').css('display', 'inline');
                  $('#rightDiv').css('opacity', '1');
                  $('#rightDiv').css('pointer-events', 'inherit');
                }

            }
            else {
              var pathname = window.location.pathname;
              if (pathname == "/ancestry"){
                    console.log('common marker error occurred.')
                    $('.inprogress').css('display', 'none');
                    $('.firstalert').css('display', '');

                   if (data['err'] == -2) {
                    // Some other error occured.
                    $('.inprogress').css('display', 'none');
                    $('.secondalert').css('display', '');
                  }


              }



                // something unexpected happened
                // check the path,  and then display an error message accordingly.
                // $(status_div.childNodes[3]).text('Result: ' + data['state']);
            }
        }
        else {
            if ($('.progress-bar')[0].style.width > 70) {
              $('.starter').addClass('secondalert').removeClass('firstalert')
              $('.starter2').addClass('firstalert').removeClass('secondalert')
            }

            else {

              $('.starter').removeClass('secondalert').addClass('firstalert')
              $('.starter2').addClass('secondalert').removeClass('firstalert')

            }
            // rerun in 2 seconds
            setTimeout(function() {
                update_progress(status_url);
            }, 2000);
        }
    });
}

//
// ONE VCF ANNOVAR CODE..
//
$(document).ready(function() {

  var pathname = window.location.pathname;
  if (pathname == "/onevcf"){

      var selDiv = "";
      var storedFiles = [];

      var form = document.getElementById("onevcfform");
      $('#download_onevcfbutton').css('display', 'none');
      $('#push_onevcfbutton').css('display', 'none')

      $('.completed').css('display', 'none');
      $('.custommargin h6').css('display', 'inline');


      $("div #onevcfbutton").on('click', function() {
        $('#download_onevcfbutton').css('display', 'none')
        $('#push_onevcfbutton').css('display', 'none')
        $('.completed').css('display', 'none');
        $('.notstarted').css('display', 'none');
        $('.inprogress').css('display', 'inline');


        console.log("button clicked")

        var form_data = new FormData($('#onevcfform')[0]);
        var data = new FormData();

        storedFiles.forEach(function(file, i) {
          data.append('file' + i, file);
        });
        // send ajax POST request to start background job
        $.ajax({
          type: 'POST',
          url: '/onevcf',
          data: data,
          cache: false,
          processData: false,
          contentType: false,
          success: function(data, status, request) {

            console.log("AJAX call returned from one VCF")
            status_url = request.getResponseHeader('Location');
            update_progress(status_url);
            $('.inprogress').css('display', 'none');


          },
          error: function() {
            alert('Unexpected error');
          }
        });
      });
      // End of onclick method for the submit

      // $("div #download_onevcfbutton").on('click', function() {
      //   $.ajax({
      //     type: 'GET',
      //     url: '/downloadonevcf',
      //     success: function(data, status, request) {
      //       length = data.length
      //       console.log(length)
      //       data = new Blob(data)
      //
      //       var a = document.createElement('a');
      //       var url = window.URL.createObjectURL(data);
      //       a.href = url;
      //       a.download = 'annovar_results.zip';
      //       document.body.append(a);
      //       a.click();
      //       a.remove();
      //       window.URL.revokeObjectURL(url);
      //   }
      //
      //       // console.log(data)
      //       // for (i = 0; i < length; i++) {
      //       //   file_data = data[i][1]
      //       //   file_name = data[i][0]
      //       //   // parsed_data = Papa.unparse(file_data)
      //       //   // download(parsed_data, file_name, "text/csv")
      //       //   download(file_data, file_name)
      //       // }
      //     // }
      //   });
      // });



      // End of onclick method for the download
      $("div #push_onevcfbutton").on('click', function() {
        $.ajax({
          type: 'POST',
          url: '/push',
          async:false,
          success: function(data, status, request) {

            $any_push_files = []

            data = JSON.parse(data)
            length = data.length;
            console.log(data)

            for (var q = 0; q < length; q++) {
              console.log(data[q])
              $any_push_files.push(data[q]);
            }
            // Close the unordered list.
            console.log($any_push_files)

            // Clearing my cookie.
            document.cookie = "any_push_files=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
            console.log(document.cookie)
            var d = new Date();
            exdays = 1
            d.setTime(d.getTime() + (exdays*24*60*60*1000));
            var expires = "expires="+ d.toUTCString();

            document.cookie = 'any_push_files=' + $any_push_files.toString() + ';' + expires + ";path=/;"
            console.log("We reset the cookie.. ")
            console.log(document.cookie)
          }
        });
      });

      $("body").on('click', '.onevcficon', function(e) {
        var file = $(e.currentTarget)["0"].parentNode.innerText
        console.log(file)
        for (var i = 0; i < storedFiles.length; i++) {
          // There's whitespace at the end of these stupid files. Please make sure
          // use trim() otherwise your string equality won't work even if comparing
          // 'identical' strings.
          if (storedFiles[i].name.trim() == file.trim()) {
            // Not being called at the moment.
            console.log(file)
            storedFiles.splice(i, 1);
            break;
          }
          console.log(i)
        }

        $(this)['0'].parentElement.remove();
        console.log(storedFiles);
      });


      $("#onevcfupload").on('change', function(e) {
        $('.alert-danger').css('display', 'none');

        var files = e.target.files
        var filesArr = Array.prototype.slice.call(files);
        var input = document.getElementById('onevcfupload');
        var output = document.getElementById('onevcfFileList');
        // output.innerHTML = '<ul>';
        for (var i = 0; i < input.files.length; ++i) {
          f = input.files.item(i);
          storedFiles.push(f);
          output.innerHTML += '<li>' + f.name + ' <i class= "fas fa-trash-alt onevcficon"></i>' + '</li>';

          if (['vcf'].indexOf(f.name.split('.')[f.name.split('.').length - 1]) < 0) {
            $('.alert-danger').css('display', '');
          }

        }
        // output.innerHTML += '</ul><br>';
      });
}
});




//
// TWO VCF ANNOVAR CODE..
//
$(document).ready(function() {

  var pathname = window.location.pathname;
  if (pathname == "/twovcf"){

      var selDiv = "";
      var storedFiles = [];

      var form = document.getElementById("twovcfform");
      $('#download_twovcfbutton').css('display', 'none');
      $('#push_twovcfbutton').css('display', 'none')

      $('.completed').css('display', 'none');
      $('.custommargin h6').css('display', 'inline');


      $("div #twovcfbutton").on('click', function() {
        $('#download_twovcfbutton').css('display', 'none')
        $('#push_twovcfbutton').css('display', 'none')
        $('.completed').css('display', 'none');
        $('.notstarted').css('display', 'none');
        $('.inprogress').css('display', 'inline');


        console.log("button clicked")

        var form_data = new FormData($('#twovcfform')[0]);
        var data = new FormData();

        storedFiles.forEach(function(file, i) {
          data.append('file' + i, file);
        });
        // send ajax POST request to start background job
        $.ajax({
          type: 'POST',
          url: '/twovcf',
          data: data,
          cache: false,
          processData: false,
          contentType: false,
          success: function(data, status, request) {

            console.log("AJAX call returned from one VCF")
            status_url = request.getResponseHeader('Location');
            update_progress(status_url);
            // $('.inprogress').css('display', 'none');


          },
          error: function() {
            alert('Unexpected error');
          }
        });
      });
      // End of onclick method for the submit

      $("div #download_twovcfbutton").on('click', function() {
        $.ajax({
          type: 'POST',
          url: '/downloadtwovcf',
          success: function(data, status, request) {
            length = data.length
            for (i = 0; i < length; i++) {
              file_data = data[i][1]
              file_name = data[i][0]
              parsed_data = Papa.unparse(file_data)
              download(parsed_data, file_name, "text/csv")
            }
          }
        });
      });
      // End of onclick method for the download
      $("div #push_twovcfbutton").on('click', function() {
        $.ajax({
          type: 'POST',
          url: '/push',
          async:false,
          success: function(data, status, request) {

            $any_push_files = []

            data = JSON.parse(data)
            length = data.length;
            console.log(data)

            for (var q = 0; q < length; q++) {
              console.log(data[q])
              $any_push_files.push(data[q]);
            }
            // Close the unordered list.
            console.log($any_push_files)

            // Clearing my cookie.
            document.cookie = "any_push_files=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
            console.log(document.cookie)
            var d = new Date();
            exdays = 1
            d.setTime(d.getTime() + (exdays*24*60*60*1000));
            var expires = "expires="+ d.toUTCString();

            document.cookie = 'any_push_files=' + $any_push_files.toString() + ';' + expires + ";path=/;"
            console.log("We reset the cookie.. ")
            console.log(document.cookie)
          }
        });
      });

      $("body").on('click', '.twovcficon', function(e) {
        var file = $(e.currentTarget)["0"].parentNode.innerText
        console.log(file)
        for (var i = 0; i < storedFiles.length; i++) {
          // There's whitespace at the end of these stupid files. Please make sure
          // use trim() otherwise your string equality won't work even if comparing
          // 'identical' strings.
          if (storedFiles[i].name.trim() == file.trim()) {
            // Not being called at the moment.
            console.log(file)
            storedFiles.splice(i, 1);
            break;
          }
          console.log(i)
        }

        $(this)['0'].parentElement.remove();
        console.log(storedFiles);
      });


      $("#twovcfupload").on('change', function(e) {
        $('.alert-danger').css('display', 'none');

        var files = e.target.files
        var filesArr = Array.prototype.slice.call(files);
        var input = document.getElementById('twovcfupload');
        var output = document.getElementById('twovcfFileList');
        // output.innerHTML = '<ul>';
        for (var i = 0; i < input.files.length; ++i) {
          f = input.files.item(i);
          storedFiles.push(f);
          output.innerHTML += '<li>' + f.name + ' <i class= "fas fa-trash-alt twovcficon"></i>' + '</li>';

          if (['vcf'].indexOf(f.name.split('.')[f.name.split('.').length - 1]) < 0) {
            $('.alert-danger').css('display', '');
          }

        }
        // output.innerHTML += '</ul><br>';
      });
}
});


// CLEANING AND PREFILTERING CODE
//
//
$(document).ready(function() {

  var pathname = window.location.pathname;
  if (pathname == "/clean"){

      var selDiv = "";
      var storedFiles = [];

      var form = document.getElementById("cleanform");
      $('#download_cleanbutton').css('display', 'none');
      $('#push_cleanbutton').css('display', 'none')

      $('.completed').css('display', 'none');
      $('.custommargin h6').css('display', 'inline');


      var mycookie = getCookie('any_push_files')
      console.log(mycookie)
      $any_push_files = mycookie.split(',');
      console.log($any_push_files)

      var push_length = $any_push_files.length
      // some analysis has been done, and this is being pushed to.
      if (push_length != 0 && $any_push_files != "") {
        var output = document.getElementById('cleanPushFileList');
        for (var q = 0; q < push_length; q++) {
          output.innerHTML += '<li>' + $any_push_files[q] + '</li>';
        }
      }



      $("div #cleanbutton").on('click', function() {
        $('#download_cleanbutton').css('display', 'none')
        $('#push_cleanbutton').css('display', 'none')
        $('.completed').css('display', 'none');
        $('.notstarted').css('display', 'none');
        $('.inprogress').css('display', 'inline');


        console.log("button clicked")

        var form_data = new FormData($('#cleanform')[0]);
        var data = new FormData();

        storedFiles.forEach(function(file, i) {
          data.append('file' + i, file);
        });

        include = []
        for (var k = 0; k < 11; k++) {
          include.push($('.form-check-input')[k].checked)
        }

        data.append('include', include)
        // send ajax POST request to start background job
        $.ajax({
          type: 'POST',
          url: '/clean',
          data: data,
          cache: false,
          processData: false,
          contentType: false,
          success: function(data, status, request) {

            status_url = request.getResponseHeader('Location');
            update_progress(status_url);

            // $('.inprogress').css('display', 'none');


          },
          error: function() {
            alert('Unexpected error');
          }
        });
      });
      // End of onclick method for the submit

      $("div #download_cleanbutton").on('click', function() {
        $.ajax({
          type: 'POST',
          url: '/downloadclean',
          success: function(data, status, request) {

            length = data.length
            for (i = 0; i < length; i++) {
              file_data = data[i][1]
              file_name = data[i][0]
              parsed_data = Papa.unparse(file_data)
              download(parsed_data, file_name, "text/csv")
            }
          }
        });
      });
      // End of onclick method for the download
      $("div #push_cleanbutton").on('click', function() {
        $.ajax({
          type: 'POST',
          url: '/push',
          async:false,
          success: function(data, status, request) {

            $any_push_files = []

            data = JSON.parse(data)
            length = data.length;
            console.log(data)

            for (var q = 0; q < length; q++) {
              console.log(data[q])
              $any_push_files.push(data[q]);
            }
            // Close the unordered list.
            console.log($any_push_files)

            // Clearing my cookie.
            document.cookie = "any_push_files=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
            console.log(document.cookie)
            var d = new Date();
            exdays = 1
            d.setTime(d.getTime() + (exdays*24*60*60*1000));
            var expires = "expires="+ d.toUTCString();

            document.cookie = 'any_push_files=' + $any_push_files.toString() + ';' + expires + ";path=/;"
            console.log("We reset the cookie.. ")
            console.log(document.cookie)
          }
        });
      });

      $("body").on('click', '.cleanicon', function(e) {
        var file = $(e.currentTarget)["0"].parentNode.innerText
        console.log(file)
        for (var i = 0; i < storedFiles.length; i++) {
          // There's whitespace at the end of these stupid files. Please make sure
          // use trim() otherwise your string equality won't work even if comparing
          // 'identical' strings.
          if (storedFiles[i].name.trim() == file.trim()) {
            // Not being called at the moment.
            console.log(file)
            storedFiles.splice(i, 1);
            break;
          }
          console.log(i)
        }

        $(this)['0'].parentElement.remove();
        console.log(storedFiles);
      });


      $("#cleanupload").on('change', function(e) {
        $('.alert-danger').css('display', 'none');

        $('#cleanPushFileList').empty()
        // Also clear the cookies. set it to an expired date.
        document.cookie = "any_push_files=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";

        var files = e.target.files
        var filesArr = Array.prototype.slice.call(files);
        var input = document.getElementById('cleanupload');
        var output = document.getElementById('cleanFileList');
        // output.innerHTML = '<ul>';
        for (var i = 0; i < input.files.length; ++i) {
          f = input.files.item(i);
          storedFiles.push(f);
          output.innerHTML += '<li>' + f.name + ' <i class= "fas fa-trash-alt cleanicon"></i>' + '</li>';
          if (['csv', 'xlsx'].indexOf(f.name.split('.')[f.name.split('.').length - 1]) < 0) {
            $('.alert-danger').css('display', '');
          }
        }
        // output.innerHTML += '</ul><br>';
      });
}
});


//
// ANNOTATION CODE.
//
$(document).ready(function() {

  var pathname = window.location.pathname;
  if (pathname == "/annotate"){
        var storedFiles_anno = [];
        var form = document.getElementById("annotateform");
        $('#download_annotatebutton').css('display', 'none');
        $('#push_annotatebutton').css('display', 'none')

        $('.completed').css('display', 'none');


        var mycookie = getCookie('any_push_files')
        console.log(mycookie)
        $any_push_files = mycookie.split(',');
        console.log($any_push_files)

        var push_length = $any_push_files.length
        // some analysis has been done, and this is being pushed to.
        if (push_length != 0 && $any_push_files != "") {
          var output = document.getElementById('annotatePushFileList');
          for (var q = 0; q < push_length; q++) {
            output.innerHTML += '<li>' + $any_push_files[q] + '</li>';
          }
        }

        $("div #annotatebutton").on('click', function() {
          $('#download_annotatebutton').css('display', 'none')
          $('#push_annotatebutton').css('display', 'none')

          $('.completed').css('display', 'none');
          $('.notstarted').css('display', 'none');
          $('.inprogress').css('display', 'inline');


          console.log("button clicked")

          var form_data = new FormData($('#annotateform')[0]);

          // send ajax POST request to start background job
          $.ajax({
            type: 'POST',
            url: '/annotate',
            data: form_data,
            cache: false,
            processData: false,
            contentType: false,
            success: function(data, status, request) {

              status_url = request.getResponseHeader('Location');
              update_progress(status_url);

              // $('.inprogress').css('display', 'none');

            },
            error: function() {
              alert('Unexpected error');
            }
          });
        });
        // End of onclick method for the submit

        $("div #download_annotatebutton").on('click', function() {
          $.ajax({
            type: 'POST',
            url: '/downloadannotate',
            success: function(data, status, request) {

              length = data.length
              for (i = 0; i < data.length; i++) {
                file_data = data[i][1]
                file_name = data[i][0]
                parsed_data = Papa.unparse(file_data)
                download(parsed_data, file_name, "text/csv")
              }
            }
          });
        });

        // End of onclick method for the download
        $("div #push_annotatebutton").on('click', function() {
          $.ajax({
            type: 'POST',
            url: '/push',
            async:false,
            success: function(data, status, request) {

              $any_push_files = []

              data = JSON.parse(data)
              length = data.length;
              console.log(data)

              for (var q = 0; q < length; q++) {
                console.log(data[q])
                $any_push_files.push(data[q]);
              }
              // Close the unordered list.
              console.log($any_push_files)

              // Clearing my cookie.
              document.cookie = "any_push_files=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
              console.log(document.cookie)
              var d = new Date();
              exdays = 1
              d.setTime(d.getTime() + (exdays*24*60*60*1000));
              var expires = "expires="+ d.toUTCString();

              document.cookie = 'any_push_files=' + $any_push_files.toString() + ';' + expires + ";path=/;"
              console.log("We reset the cookie.. ")
              console.log(document.cookie)
            }
          });
        });


        $("body").on('click', '.annotateicon', function(e) {
          var file = $(e.currentTarget)["0"].parentNode.innerText
          console.log(file)
          for (var i = 0; i < storedFiles_anno.length; i++) {
            // There's whitespace at the end of these stupid files. Please make sure
            // use trim() otherwise your string equality won't work even if comparing
            // 'identical' strings.
            if (storedFiles_anno[i].name.trim() == file.trim()) {
              // Not being called at the moment.
              console.log(file)
              storedFiles_anno.splice(i, 1);
              break;
            }
            console.log(i)
          }

          $(this)['0'].parentElement.remove();
          console.log(storedFiles_anno);
        });


        $("#annotateupload").on('change', function(e) {
          $('.alert-danger').css('display', 'none');


          // Clear what the user can see.
          $('#annotatePushFileList').empty()
          // Also clear the cookies. set it to an expired date.
          document.cookie = "any_push_files=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";


          var files = e.target.files
          var filesArr = Array.prototype.slice.call(files);
          var input = document.getElementById('annotateupload');
          var output = document.getElementById('annotateFileList');
          // output.innerHTML = '<ul>';
          for (var i = 0; i < input.files.length; ++i) {
            f = input.files.item(i);
            storedFiles_anno.push(f);
            output.innerHTML += '<li>' + f.name + ' <i class= "fas fa-trash-alt annotateicon"></i>' + '</li>';
            if (['csv', 'xlsx'].indexOf(f.name.split('.')[f.name.split('.').length - 1]) < 0) {
              $('.alert-danger').css('display', '');
            }

          }
          // output.innerHTML += '</ul><br>';
        });
    }
});


//
// FILTERING CODE.
//
$(document).ready(function() {
  var pathname = window.location.pathname;
  if (pathname == "/filtering") {
      var storedFiles_filter = [];
      var form = document.getElementById("filterform");
      $('#download_filterbutton').css('display', 'none');
      $('#push_filterbutton').css('display', 'none');




      var rangeSlider = function(){
        var slider = $('.range-slider'),
        range = $('.range-slider__range'),
        value = $('.range-slider__value');

        slider.each(function(){

          value.each(function(){
            var value = $(this).prev().attr('value');
            $(this).html(value);
          });

          range.on('input', function(){
            $('.range-slider__value')[0].value = this.value;
            // $(this).next(value).html(this.value);
          });

          value.on('change textInput input', function(){
            $('.range-slider__range')[0].value = this.value
          })
        });
      };

      rangeSlider();

      $('#maf_threshold')[0].style.width = "13em"
      $('#value')[0].style.width = "5em"

      // We decided to not have the user input GDI thresholds anymore.
      // Not wanting to change the server side code, I decided not to display the
      // input element. Therfore, the "user never enters a GDI value", and my code can handle that.
      $('#gdiRowElement').css('display', 'none');

      $('.completed').css('display', 'none');
      console.log("I'm here bro.. ")

      var mycookie = getCookie('any_push_files')
      console.log(mycookie)
      $any_push_files = mycookie.split(',');
      console.log($any_push_files)

      var push_length = $any_push_files.length
      // some analysis has been done, and this is being pushed to.
      if (push_length != 0 && $any_push_files != "") {
        var output = document.getElementById('filterPushFileList');
        // output.innerHTML = '<ul>';
        for (var q = 0; q < push_length; q++) {
          output.innerHTML += '<li>' + $any_push_files[q] + '</li>';
        }
      }

      $("div #filterbutton").on('click', function() {
        $('#download_filterbutton').css('display', 'none');
        $('#push_filterbutton').css('display', 'none')

        $('.completed').css('display', 'none');
        $('.notstarted').css('display', 'none');
        $('.inprogress').css('display', 'inline');

        console.log("button clicked")

        var form_data = new FormData($('#filterform')[0]);

        // send ajax POST request to start background job
        $.ajax({
          type: 'POST',
          url: '/filtering',
          data: form_data,
          cache: false,
          processData: false,
          contentType: false,
          success: function(data, status, request) {

            status_url = request.getResponseHeader('Location');
            update_progress(status_url);

            // $('.inprogress').css('display', 'none');



          },
          error: function() {
            alert('Unexpected error');
          }
        });
      });
      // End of onclick method for the submit

      $("div #download_filterbutton").on('click', function() {
        $.ajax({
          type: 'POST',
          url: '/downloadfilter',
          success: function(data, status, request) {

            length = data.length
            for (i = 0; i < data.length; i++) {
              file_data = data[i][1]
              file_name = data[i][0]
              parsed_data = Papa.unparse(file_data)
              download(parsed_data, file_name, "text/csv")
            }
          }
        });
      });
      // End of onclick method for the download
      $("div #push_filterbutton").on('click', function() {
        $.ajax({
          type: 'POST',
          url: '/push',
          async:false,
          success: function(data, status, request) {

            $any_push_files = []

            data = JSON.parse(data)
            length = data.length;
            console.log(data)
            console.log(status)
            console.log(request)
            console.log(length)
            // Create an unordered list in the appropriate location
            // output.innerHTML += '</ul><br>';
            for (var q = 0; q < length; q++) {
              console.log(data[q])
              $any_push_files.push(data[q]);
            }
            // Close the unordered list.
            console.log($any_push_files)

            // Clearing my cookie.
            document.cookie = "any_push_files=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
            console.log(document.cookie)
            var d = new Date();
            exdays = 1
            d.setTime(d.getTime() + (exdays*24*60*60*1000));
            var expires = "expires="+ d.toUTCString();

            document.cookie = 'any_push_files=' + $any_push_files.toString() + ';' + expires + ";path=/;"
            console.log("We reset the cookie.. ")
            console.log(document.cookie)
          }
        });
      });


      $("body").on('click', '.filtericon', function(e) {
        var file = $(e.currentTarget)["0"].parentNode.innerText
        console.log(file)
        for (var i = 0; i < storedFiles_filter.length; i++) {
          // There's whitespace at the end of these stupid files. Please make sure
          // use trim() otherwise your string equality won't work even if comparing
          // 'identical' strings.
          if (storedFiles_filter[i].name.trim() == file.trim()) {
            // Not being called at the moment.
            console.log(file)
            storedFiles_filter.splice(i, 1);
            break;
          }
          console.log(i)
        }

        $(this)['0'].parentElement.remove();
        console.log(storedFiles_filter);
      });


      $("#filterupload").on('change', function(e) {
        $('.alert-danger').css('display', 'none');


        // Clear what the user can see.
        $('#filterPushFileList').empty()
        // Also clear the cookies. set it to an expired date.
        document.cookie = "any_push_files=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";


        var files = e.target.files
        var filesArr = Array.prototype.slice.call(files);
        var input = document.getElementById('filterupload');
        var output = document.getElementById('filterFileList');
        // output.innerHTML = '<ul>';
        for (var i = 0; i < input.files.length; ++i) {
          f = input.files.item(i);
          storedFiles_filter.push(f);
          output.innerHTML += '<li>' + f.name + ' <i class= "fas fa-trash-alt filtericon"></i>' + '</li>';
          if (['csv', 'xlsx'].indexOf(f.name.split('.')[f.name.split('.').length - 1]) < 0) {
            $('.alert-danger').css('display', '');
          }
        }
        // output.innerHTML += '</ul><br>';
      });
  }
});


//MODES OF INHERITANCE code//
//
//
$(document).ready(function() {

  var pathname = window.location.pathname;
  if (pathname == "/modes") {

    var selDiv_modes = "";
    var storedFiles_modes = [];

    var form = document.getElementById("modesform");
    $('#download_modesbutton').css('display', 'none');
    $('#push_modesbutton').css('display', 'none')

    $('.completed').css('display', 'none');

    $('.extraoptions').css('visibility', 'hidden');
    console.log("I'm here bro.. ")

    var mycookie = getCookie('any_push_files')
    console.log(mycookie)
    $any_push_files = mycookie.split(',');
    console.log($any_push_files)

    var push_length = $any_push_files.length
    // some analysis has been done, and this is being pushed to.
    if (push_length != 0 && $any_push_files != "") {
      var output = document.getElementById('modesPushFileList');
      // output.innerHTML = '<ul>';
      for (var q = 0; q < push_length; q++) {
        output.innerHTML += '<li>' + $any_push_files[q] + '<select name="x"><option value="het">Heterozygous</option><option value="hom">Homozygous</option><option value="absent">Absent</option><option value="any">Any</option><option value="hetabs" >Heterozygous or Absent</option></select>' +
          '</li>';
      }
      $('.extraoptions').css('visibility', 'visible');

    }


    $("div #modesbutton").on('click', function() {

      $('#download_modesbutton').css('display', 'none')
      $('#push_modesbutton').css('display', 'none')
      $('.completed').css('display', 'none');
      $('.notstarted').css('display', 'none');
      $('.inprogress').css('display', 'inline');

      console.log("button clicked")

      var form_data = new FormData($('#modesform')[0]);
      var data = new FormData();

      storedFiles_modes.forEach(function(file, i) {
        data.append('file' + i, file);
      });

      zyg = []
      zyg.push($('select')[0].value)
      len = $('select').length
      others = []
      for (j = 1; j < len; j++) {
        others.push($('select')[j].value)
      }
      zyg.push(others)
      data.append('zyg', zyg)
      console.log(zyg)
      // console.log(data)

      // For X-recessive
      bool1 = $(".form-check")[1].children[0].checked
      // $(".form-check")[1].children[1].innerText

      // For compound heterozygous
      bool2 = $(".form-check")[0].children[0].checked

      if (bool2 == true) {
        patient_ix = parseInt($("#compHetPatient")[0].value)
      }
      else {
        patient_ix = -1
      }
      // $(".form-check")[0].children[1].innerText

      // For HGNC Gene Name
      bool3 = $(".form-check")[2].children[0].checked

      // X-recessive first, then compound het.
      configs = [bool1, bool2, bool3, patient_ix]

      data.append('config', configs)

      // send ajax POST request to start background job
      $.ajax({
        type: 'POST',
        url: '/modes',
        data: data,
        cache: false,
        processData: false,
        contentType: false,
        success: function(data, status, request) {


          status_url = request.getResponseHeader('Location');
          update_progress(status_url);


          // $('.inprogress').css('display', 'none');



        },
        error: function() {
          alert('Unexpected error');
        }
      });
    });
    // End of onclick method for the submit

    $("div #download_modesbutton").on('click', function() {
      $.ajax({
        type: 'POST',
        url: '/downloadmodes',
        success: function(data, status, request) {

          length = data.length
          for (i = 0; i < data.length; i++) {
            file_data = data[i][1]
            file_name = data[i][0]
            parsed_data = Papa.unparse(file_data)
            download(parsed_data, file_name, "text/csv")
            break;
          }
        }
      });
    });
    // End of onclick method for the download

    $("body").on('click', '.modesicon', function(e) {
      var file = $(e.currentTarget)["0"].parentNode.innerText
      console.log(file)
      for (var i = 0; i < storedFiles_modes.length; i++) {
        // There's whitespace at the end of these stupid files. Please make sure
        // use trim() otherwise your string equality won't work even if comparing
        // 'identical' strings.
        if (storedFiles_modes[i].name.trim() == file.trim()) {
          // Not being called at the moment.
          console.log(file)
          storedFiles_modes.splice(i, 1);
          break;
        }
        console.log(i)
      }

      $(this)['0'].parentElement.remove();
      console.log(storedFiles_modes);
    });


    $("#check1")[0].addEventListener('change', (event) => {
      if ($(".form-check")[0].children[0].checked == true) {

        innerHTML = "<br>Choose index patient: <br><select id='compHetPatient' name='select_patient'>"

        for (var file_num = 0; file_num < $('#modesPushFileList li').length; file_num++) {
          val = $('#modesPushFileList li')[file_num].innerText.split('\n')[0]
          text = "<option value=" + file_num + ">" + val  + "</option>"
          innerHTML += text
        }

        for (var file_num = 0; file_num < $('#modesFileList li').length; file_num++) {
          val = $('#modesFileList li')[file_num].innerText.split('\n')[0]
          text = "<option value=" + file_num + ">" + val  + "</option>"
          innerHTML += text
        }

        innerHTML += "</select>"
        $('p.text-muted')[1].innerHTML += innerHTML
      }

      else {
        innerHTML = "<p class='text-muted'>Currently, the program <b> only supports compound heterozygous analyses for trios.</b></p>"
        $('p.text-muted')[1].innerHTML = innerHTML

      }
    });


    $("#modesupload").on('change', function(e) {
      $('.alert-danger').css('display', 'none');


      // Clear what the user can see.
      $('#modesPushFileList').empty()
      // Also clear the cookies. set it to an expired date.
      document.cookie = "any_push_files=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";

      var files = e.target.files
      var filesArr = Array.prototype.slice.call(files);
      var input = document.getElementById('modesupload');
      var output = document.getElementById('modesFileList');
      // output.innerHTML = '<ul>';
      for (var i = 0; i < input.files.length; ++i) {
        f = input.files.item(i);
        storedFiles_modes.push(f);
        output.innerHTML += '<li>' + f.name + '<select name="x"><option value="het">Heterozygous</option><option value="hom">Homozygous</option><option value="absent">Absent</option><option value="any">Any</option><option value="hetabs" >Heterozygous or Absent</option></select>' +
          ' <i class= "fas fa-trash-alt modesicon"></i>' + '</li>';

        if (['csv', 'xlsx'].indexOf(f.name.split('.')[f.name.split('.').length - 1]) < 0) {
          $('.alert-danger').css('display', '');
        }
      }

      $('.extraoptions').css('visibility', 'visible');
      // output.innerHTML += '</ul><br>';
    });

  }
});


//
// UNBIASED COHORT ANALYSIS
//
//
$(document).ready(function() {




  var pathname = window.location.pathname;
  if (pathname == "/unbiasedcohort"){
      var selDiv = "";
      var storedFiles_unbiased = [];

      var form = document.getElementById("unbiasedcohortform");
      $('#download_unbiasedcohortbutton').css('display', 'none')
      $('.completed').css('display', 'none');
      $('#unbiasedcohortFileList')[0].style.display = "none"

      var rangeSlider = function(){
        var slider = $('.range-slider'),
        range = $('.range-slider__range'),
        value = $('.range-slider__value');

        slider.each(function(){

          value.each(function(){
            var value = $(this).prev().attr('value');
            $(this).html(value);
          });

          range.on('input', function(){
            $('.range-slider__value')[0].value = this.value;
            // $(this).next(value).html(this.value);
          });

          value.on('change textInput input', function(){
            $('.range-slider__range')[0].value = this.value
          })
        });
      };

      rangeSlider();
  }

  $("div #unbiasedcohortbutton").on('click', function() {
    $('#download_unbiasedcohortbutton').css('display', 'none')
    $('.completed').css('display', 'none');
    $('.notstarted').css('display', 'none');
    $('.inprogress').css('display', 'inline');

    console.log("button clicked")

    var form_data = new FormData($('#unbiasedcohortform')[0]);
    var data = new FormData();

    storedFiles_unbiased.forEach(function(file, i) {
      data.append('file' + i, file);
    });

    threshold =
    data.append('mafThreshunbcohort', $('#mafThresholdunbcohort')[0].value)
    data.append('mafColumnsSel', $('#sel_unbiased')[0].value)

    // send ajax POST request to start background job
    $.ajax({
      type: 'POST',
      url: '/unbiasedcohort',
      data: data,
      cache: false,
      processData: false,
      contentType: false,
      success: function(data, status, request) {

        status_url = request.getResponseHeader('Location');
        update_progress(status_url);

        // $('.inprogress').css('display', 'none');


      },
      error: function() {
        alert('Unexpected error');
      }
    });
  });
  // End of onclick method for the submit

  $("div #download_unbiasedcohortbutton").on('click', function() {
    $.ajax({
      type: 'POST',
      url: '/downloadunbiasedcohort',
      success: function(data, status, request) {

        length = data.length
        for (i = 0; i < data.length; i++) {
          file_data = data[i][1]
          file_name = data[i][0]
          parsed_data = Papa.unparse(file_data)
          download(parsed_data, file_name, "text/csv")
        }
      }
    });
  });
  // End of onclick method for the download

  $("body").on('click', '.unbiasedcohorticon', function(e) {
    var file = $(e.currentTarget)["0"].parentNode.innerText
    console.log(file)
    for (var i = 0; i < storedFiles_unbiased.length; i++) {
      // There's whitespace at the end of these stupid files. Please make sure
      // use trim() otherwise your string equality won't work even if comparing
      // 'identical' strings.
      if (storedFiles_unbiased[i].name.trim() == file.trim()) {
        // Not being called at the moment.
        console.log(file)
        storedFiles_unbiased.splice(i, 1);
        break;
      }
      console.log(i)
    }

    $(this)['0'].parentElement.remove();
    console.log(storedFiles_unbiased);
  });


  $("#unbiasedcohortupload").on('change', function(e) {
    $('.alert-danger').css('display', 'none');

    var files = e.target.files
    var filesArr = Array.prototype.slice.call(files);
    $('#unbiasedcohortFileList')[0].style.display = ""
    var input = document.getElementById('unbiasedcohortupload');
    var output = document.getElementById('unbiasedcohortFileList');
    // output.innerHTML = '<ul>';
    for (var i = 0; i < input.files.length; ++i) {
      f = input.files.item(i);
      storedFiles_unbiased.push(f);
      output.innerHTML += '<li>' + f.name + ' <i class= "fas fa-trash-alt unbiasedcohorticon"></i>' + '</li>';

      if (['csv', 'xlsx'].indexOf(f.name.split('.')[f.name.split('.').length - 1]) < 0) {
        $('.alert-danger').css('display', '');
      }

    }
    // output.innerHTML += '</ul><br>';
  });

});



//
// BIASED COHORT ANALYSIS
//
//
$(document).ready(function() {
  var pathname = window.location.pathname;
  if (pathname == "/biasedcohort"){
      var selDiv = "";
      var storedFiles_biased = [];

      var form = document.getElementById("biasedcohortform");
      $('#download_biasedcohortbutton').css('display', 'none')
      $('.completed').css('display', 'none');

      $('#biasedcohortFileList')[0].style.display = "none"


      var rangeSlider = function(){
        var slider = $('.range-slider'),
        range = $('.range-slider__range'),
        value = $('.range-slider__value');

        slider.each(function(){

          value.each(function(){
            var value = $(this).prev().attr('value');
            $(this).html(value);
          });

          range.on('input', function(){
            $('.range-slider__value')[0].value = this.value;
            // $(this).next(value).html(this.value);
          });

          value.on('change textInput input', function(){
            $('.range-slider__range')[0].value = this.value
          })
        });
      };

      rangeSlider();

    }

  $("div #biasedcohortbutton").on('click', function() {
    $('#download_biasedcohortbutton').css('display', 'none')
    $('.completed').css('display', 'none');
    $('.notstarted').css('display', 'none');
    $('.inprogress').css('display', 'inline');

    console.log("button clicked")

    var form_data = new FormData($('#biasedcohortform')[0]);


    // send ajax POST request to start background job
    $.ajax({
      type: 'POST',
      url: '/biasedcohort',
      data: form_data,
      cache: false,
      processData: false,
      contentType: false,
      success: function(data, status, request) {
        status_url = request.getResponseHeader('Location');
        update_progress(status_url);

        // $('.inprogress').css('display', 'none');


      },
      error: function() {
        alert('Unexpected error');
      }
    });
  });
  // End of onclick method for the submit

  $("div #download_biasedcohortbutton").on('click', function() {
    $.ajax({
      type: 'POST',
      url: '/downloadbiasedcohort',
      success: function(data, status, request) {

        length = data.length
        for (i = 0; i < data.length; i++) {
          file_data = data[i][1]
          file_name = data[i][0]
          parsed_data = Papa.unparse(file_data)
          download(parsed_data, file_name, "text/csv")
        }
      }
    });
  });
  // End of onclick method for the download

  $("body").on('click', '.biasedcohorticon', function(e) {
    var file = $(e.currentTarget)["0"].parentNode.innerText
    console.log(file)
    for (var i = 0; i < storedFiles_biased.length; i++) {
      // There's whitespace at the end of these stupid files. Please make sure
      // use trim() otherwise your string equality won't work even if comparing
      // 'identical' strings.
      if (storedFiles_biased[i].name.trim() == file.trim()) {
        // Not being called at the moment.
        console.log(file)
        storedFiles_biased.splice(i, 1);
        break;
      }
      console.log(i)
    }

    $(this)['0'].parentElement.remove();
    console.log(storedFiles_biased);
  });


  $("#biasedcohortupload").on('change', function(e) {
    $('.alert-danger').css('display', 'none');

    var files = e.target.files
    var filesArr = Array.prototype.slice.call(files);

    $('#biasedcohortFileList')[0].style.display = ""

    var input = document.getElementById('biasedcohortupload');
    var output = document.getElementById('biasedcohortFileList');
    // output.innerHTML = '<ul>';
    for (var i = 0; i < input.files.length; ++i) {
      f = input.files.item(i);
      storedFiles_biased.push(f);
      output.innerHTML += '<li>' + f.name + ' <i class= "fas fa-trash-alt biasedcohorticon"></i>' + '</li>';
      if (['csv', 'xlsx'].indexOf(f.name.split('.')[f.name.split('.').length - 1]) < 0) {
        $('.alert-danger').css('display', '');
      }
    }
    // output.innerHTML += '</ul><br>';
  });

});


//
// KINSHIP AND SEX INFERENCE CODE
//
//
$(document).ready(function() {
  var selDiv = "";
  var storedFiles = [];

  var form = document.getElementById("kinsexform");
  $('#download_kinsexbutton').css('display', 'none')
  $('.completed').css('display', 'none');
  $('.x_chr_explain').css('display', 'none');
  $('.y_chr_explain').css('display', 'none');

  $('#checkbox_X').on('change', function() {
    tempvar = $('#checkbox_X')[0].checked
    if (tempvar == true) {
      $('.x_chr_explain').css('display', 'inline');
    } else {
      $('.x_chr_explain').css('display', 'none');
    }

  });

  $('#checkbox_Y').on('change', function() {
    tempvar = $('#checkbox_Y')[0].checked
    if (tempvar == true) {
      $('.y_chr_explain').css('display', 'inline');
    } else {
      $('.y_chr_explain').css('display', 'none');
    }

  });



  $("div #kinsexbutton").on('click', function() {
    $('#download_kinsexbutton').css('display', 'none')
    $('.completed').css('display', 'none');
    $('.notstarted').css('display', 'none');
    $('.inprogress').css('display', 'inline');

    console.log("button clicked")

    var form_data = new FormData($('#kinsexform')[0]);

    x_chr = $('#checkbox_X')[0].checked
    y_chr = $('#checkbox_Y')[0].checked

    format = $('#fileFormat_PLINK_SEX')[0].value

    var data = new FormData();

    storedFiles.forEach(function(file, i) {
      data.append('file' + i, file);
    });

    data.append('x_check', x_chr)
    data.append('y_check', y_chr)
    data.append('format', format)

    // send ajax POST request to start background job
    $.ajax({
      type: 'POST',
      url: '/kinsex',
      data: data,
      cache: false,
      processData: false,
      contentType: false,
      success: function(data, status, request) {
        $('.inprogress').css('display', 'none');
        $('.completed').css('display', 'inline');
        $('#download_kinsexbutton').css('display', 'inline')

      },
      error: function() {
        alert('Unexpected error');
      }
    });
  });
  // End of onclick method for the submit

  $("div #download_kinsexbutton").on('click', function() {
    $.ajax({
      type: 'POST',
      url: '/downloadkinsex',
      success: function(data, status, request) {

        length = data.length
        for (i = 0; i < data.length; i++) {
          file_data = data[i][1]
          file_name = data[i][0]
          parsed_data = Papa.unparse(file_data)
          download(parsed_data, file_name, "text/csv")
        }
      }
    });
  });
  // End of onclick method for the download

  $("body").on('click', '.kinsexicon', function(e) {
    var file = $(e.currentTarget)["0"].parentNode.innerText
    console.log(file)
    for (var i = 0; i < storedFiles.length; i++) {
      // There's whitespace at the end of these stupid files. Please make sure
      // use trim() otherwise your string equality won't work even if comparing
      // 'identical' strings.
      if (storedFiles[i].name.trim() == file.trim()) {
        // Not being called at the moment.
        console.log(file)
        storedFiles.splice(i, 1);
        break;
      }
      console.log(i)
    }

    $(this)['0'].parentElement.remove();
    console.log(storedFiles);
  });


  $("#kinsexupload").on('change', function(e) {
    $('.alert-danger').css('display', 'none');

    var files = e.target.files
    var filesArr = Array.prototype.slice.call(files);
    var input = document.getElementById('kinsexupload');
    var output = document.getElementById('kinsexFileList');
    // output.innerHTML = '<ul>';
    extensions = []
    for (var i = 0; i < input.files.length; ++i) {
      f = input.files.item(i);
      storedFiles.push(f);
      output.innerHTML += '<li>' + f.name + ' <i class= "fas fa-trash-alt kinsexicon"></i>' + '</li>';
      extensions.push(f.name.split('.')[f.name.split('.').length - 1])
    }

    ped_map = ['ped', 'map']
    bed_bim = ['bed', 'bim', 'fam']

    y = extensions
    if (y.length == 2) {
      num = 0

      for (var i = 0; i < y.length; i++) {
        if (ped_map.indexOf(y[i]) >=0) {
          num++
        }
        else {
          num = -5
        }
      }

      if (num < 0) {
        $('.alert-danger').css('display', '');

      }
    }

    else if (y.length == 3) {
      num = 0
      for (var i = 0; i < y.length; i++) {
        if (bed_bim.indexOf(y[i]) >=0) {
          num++
        }
        else {
          num = -5
        }
      }

      if (num < 0) {
        $('.alert-danger').css('display', '');
      }
    }

    else {
      $('.alert-danger').css('display', '');
    }




    // output.innerHTML += '</ul><br>';
  });

});



//
//
// ANCESTRY CODE --->
//
//

$(document).ready(function() {
  var selDiv = "";
  var storedFiles = [];

  var form = document.getElementById("ancestryform");
  // $('#download_ancestrybutton').css('display', 'none')
  $('.completed').css('display', 'none');
  $('#axis_controls').css('display', 'none');

  $('.starter').removeClass('secondalert').addClass('firstalert')
  $('.starter2').addClass('secondalert').removeClass('firstalert')

  $('.firstalert').css('display', 'none');
  $('.secondalert').css('display', 'none');

  $("div #ancestrybutton").on('click', function() {
    // $('#download_ancestrybutton').css('display', 'none')
    $('.completed').css('display', 'none');
    $('.notstarted').css('display', 'none');
    $('.inprogress').css('display', 'inline');

    $('.starter').removeClass('secondalert').addClass('firstalert')
    $('.starter2').addClass('secondalert').removeClass('firstalert')

    console.log("button clicked")

    var form_data = new FormData($('#ancestryform')[0]);

    format = $('#fileFormat_PLINK_ANCESTRY')[0].value

    var data = new FormData();

    storedFiles.forEach(function(file, i) {
      data.append('file' + i, file);
    });

    data.append('format', format)

    // send ajax POST request to start background job
    $.ajax({
      type: 'POST',
      url: '/ancestry',
      data: data,
      cache: false,
      processData: false,
      contentType: false,
      success: function(data, status, request) {
        console.log(data)

        console.log("AJAX call returned from one VCF")
        status_url = request.getResponseHeader('Location');
        update_progress(status_url);
        // $('.inprogress').css('display', 'none');


      },
      error: function() {
        $('.inprogress').css('display', 'none');
        $('.secondalert').css('display', '');
        }
    });
  });

  $("body").on('click', '.ancestryicon', function(e) {
    var file = $(e.currentTarget)["0"].parentNode.innerText
    console.log(file)
    for (var i = 0; i < storedFiles.length; i++) {
      // There's whitespace at the end of these stupid files. Please make sure
      // use trim() otherwise your string equality won't work even if comparing
      // 'identical' strings.
      if (storedFiles[i].name.trim() == file.trim()) {
        // Not being called at the moment.
        console.log(file)
        storedFiles.splice(i, 1);
        break;
      }
      console.log(i)
    }

    $(this)['0'].parentElement.remove();
    console.log(storedFiles);
  });


  $("#ancestryupload").on('change', function(e) {
    $('.zeroalert').css('display', 'none');

    var files = e.target.files
    var filesArr = Array.prototype.slice.call(files);
    var input = document.getElementById('ancestryupload');
    var output = document.getElementById('ancestryFileList');
    // output.innerHTML = '<ul>';
    extensions = []
    for (var i = 0; i < input.files.length; ++i) {
      f = input.files.item(i);
      storedFiles.push(f);
      output.innerHTML += '<li>' + f.name + ' <i class= "fas fa-trash-alt ancestryicon"></i>' + '</li>';
      extensions.push(f.name.split('.')[f.name.split('.').length - 1])

    }

    ped_map = ['ped', 'map']
    bed_bim = ['bed', 'bim', 'fam']

    y = extensions
    if (y.length == 2) {
      num = 0

      for (var i = 0; i < y.length; i++) {
        if (ped_map.indexOf(y[i]) >=0) {
          num++
        }
        else {
          num = -5
        }
      }

      if (num < 0) {
        $('.zeroalert').css('display', '');

      }
    }

    else if (y.length == 3) {
      num = 0
      for (var i = 0; i < y.length; i++) {
        if (bed_bim.indexOf(y[i]) >=0) {
          num++
        }
        else {
          num = -5
        }
      }

      if (num < 0) {
        $('.zeroalert').css('display', '');
      }
    }

    else {
      $('.zeroalert').css('display', '');
    }

    // output.innerHTML += '</ul><br>';
  });

});

$(document).ready(function() {

  var form = document.getElementById("pcaform");
  $('.completed').css('display', 'none');


  $("div #pcabutton").on('click', function() {
    // $('#download_ancestrybutton').css('display', 'none')
    $('.completed').css('display', 'none');
    $('.notstarted').css('display', 'none');
    $('.inprogress').css('display', 'inline');
    $('.alert-danger').css('display', 'none');

    $('#sample_img').css('display', 'none')

    console.log("button clicked")

    var data = new FormData($('#pcaform')[0]);
    // Will form data have everything I need

    // send ajax POST request to start background job
    $.ajax({
      type: 'POST',
      url: '/pca',
      data: data,
      cache: false,
      processData: false,
      contentType: false,
      success: function(data, status, request) {

        if (-1 == parseInt(data)) {
          $('.inprogress').css('display', 'none');
          $('.secondalert').css('display', '');
        }

        else {
          $('.inprogress').css('display', 'none');
          $('.completed').css('display', 'inline');
          $('#axis_controls').css('display', 'inline');
          $('#plot_iframe')[0].src = './static/temp-plot.html'
        }


      },
      error: function() {
        alert('Unexpected error');
      }
    });
  });

});

$(document).ready(function() {

  $("#refresh_button").on('click', function() {

    console.log("refresh button clicked")
    // Read off the input values
    var x_ax = $('#pc1_val')[0].value
    var y_ax = $('#pc2_val')[0].value

    // Use them to call a python subprocess and regenerate the temp-plot.HTML
    data = {
      'x': x_ax,
      'y': y_ax
    }
    // Re-embed :)

    // send ajax POST request to start background job
    $.ajax({
      type: 'POST',
      url: '/refresh',
      data: JSON.stringify(data),
      cache: false,
      processData: false,
      contentType: "application/json; charset=utf-8",
      success: function(data, status, request) {
        $('#plot_iframe')[0].src = './static/temp-plot.html'
      },
      error: function() {
        alert('Unexpected error');
      }
    });
  });
});

// Do this if user selects 1000G dataset, and you need to display the table.
$(document).ready(function() {

  // $('#1000G_pops').css('display','none');
  /// CHANGE THESE OPACITIES AND POINTER ACTIONS BACK-- WHEN THERE IS PROCESSED DATA EXISTING.
  var pathname = window.location.pathname;
  if (pathname == "/ancestry") {
    $('#rightDiv').css('opacity', '0.2');
    $('#rightDiv').css('pointer-events', 'none');
    $('#sample_img').css('opacity', '0.3');

    // INITIAL VIEW:
    $("#checkbox_ALL")[0].checked = true
    $('.popcheck').each(function() {
      $(this)[0].checked = true;
      $(this)[0].disabled = true;
    });



    $('#fileFormat_PLINK_ANCESTRY_DB').change(function() {
      if ($('#fileFormat_PLINK_ANCESTRY_DB')[0].value == "1000 Genomes Project") {
        console.log('Twas true')

        $('#1000G_pops').css('display', 'inline')
        $("#checkbox_ALL")[0].checked = true
        $('.popcheck').each(function() {
          $(this)[0].checked = true;
          $(this)[0].disabled = true;
        })
      } else {
        $('#1000G_pops').css('display', 'none')

      }
    });

    $("#checkbox_ALL").click(function() {
      if ($(this).is(':checked') == false) {
        $('.popcheck').each(function() {
          $(this)[0].checked = false;
          $(this)[0].disabled = false;
        })

      } else {
        $('.popcheck').each(function() {
          $(this)[0].checked = true;
          $(this)[0].disabled = true;
        })
      }
    });

  }
});



//
// BLACKLIST GENERATION
//
//

$(document).ready(function() {
  var selDiv = "";
  var storedFiles_gen_blacklist = [];

  var pathname = window.location.pathname;

  if (pathname == '/gen_blacklist') {
    console.log("In here :)) ")

    var form = document.getElementById("gen_blacklistform");
    $('#download_gen_blacklistbutton').css('display', "none")
    $('.completed').css('display', 'none');

    var rangeSlider = function(){
      var slider = $('.range-slider'),
      range = $('.range-slider__range'),
      value = $('.range-slider__value');

      slider.each(function(){

        value.each(function(){
          var value = $(this).prev().attr('value');
          $(this).html(value);
        });

        range.on('input', function(){
          $('.range-slider__value')[0].value = this.value;
          // $(this).next(value).html(this.value);
        });

        value.on('change textInput input', function(){
          $('.range-slider__range')[0].value = this.value
        })
      });
    };

    rangeSlider();


    $("div #gen_blacklistbutton").on('click', function() {
      $('#download_gen_blacklistbutton').css('display', 'none')
      $('.completed').css('display', 'none');
      $('.notstarted').css('display', 'none');
      $('.inprogress').css('display', 'inline');

      console.log("button clicked")

      var form_data = new FormData($('#gen_blacklistform')[0]);
      var data = new FormData();

      storedFiles_gen_blacklist.forEach(function(file, i) {
        data.append('file' + i, file);
      });

      // Also append the cutoff thing to it.
      data.append('cutoff', $("#cutoff_gen_blacklist")[0].value)
      console.log("Triggered after clicking submit. ")

      // send ajax POST request to start background job
      $.ajax({
        type: 'POST',
        url: '/gen_blacklist',
        data: data,
        cache: false,
        processData: false,
        contentType: false,
        success: function(data, status, request) {
          status_url = request.getResponseHeader('Location');
          update_progress(status_url);

          // $('.inprogress').css('display', 'none');


        },
        error: function() {
          alert('Unexpected error');
        }
      });
    });


    // End of onclick method for the submit

    $("div #download_gen_blacklistbutton").on('click', function() {
      $.ajax({
        type: 'POST',
        url: '/downloadgen_blacklist',
        success: function(data, status, request) {

          length = data.length
          for (i = 0; i < data.length; i++) {
            file_data = data[i][1]
            file_name = data[i][0]
            parsed_data = Papa.unparse(file_data)
            download(parsed_data, file_name, "text/csv")
          }
        }
      });
    });
    // End of onclick method for the download

    $("body").on('click', '.gen_blacklisticon', function(e) {
      console.log("Triggered after clicking trash icon! ")


      var file = $(e.currentTarget)["0"].parentNode.innerText
      console.log(file)
      for (var i = 0; i < storedFiles_gen_blacklist.length; i++) {
        // There's whitespace at the end of these stupid files. Please make sure
        // use trim() otherwise your string equality won't work even if comparing
        // 'identical' strings.
        if (storedFiles_gen_blacklist[i].name.trim() == file.trim()) {
          // Not being called at the moment.
          console.log(file)
          storedFiles_gen_blacklist.splice(i, 1);


          break;
        }
        console.log(i)
      }

      $(this)['0'].parentElement.remove();
    });


    $("#gen_blacklistupload").on('change', function(e) {
      $('.alert-danger').css('display', 'none');

      console.log("Blacklist adds")
      var files = e.target.files
      var filesArr = Array.prototype.slice.call(files);
      var input = document.getElementById('gen_blacklistupload');
      var output = document.getElementById('gen_blacklistFileList');
      // output.innerHTML = '<ul>';
      for (var i = 0; i < input.files.length; ++i) {
        f = input.files.item(i);
        storedFiles_gen_blacklist.push(f);
        output.innerHTML += '<li>' + f.name + ' <i class= "fas fa-trash-alt gen_blacklisticon"></i>' + '</li>';
        if (['csv', 'xlsx'].indexOf(f.name.split('.')[f.name.split('.').length - 1]) < 0) {
          $('.alert-danger').css('display', '');
        }
      }
      // output.innerHTML += '</ul><br>';
    });

  }
});


//
// BLACKLIST FILTER APPLY
//
//

$(document).ready(function() {
  var selDiv = "";
  var storedFiles_apply_blacklist = [];
  var storedFiles_ref = []

  var pathname = window.location.pathname;

  if (pathname == '/apply_blacklist') {
    console.log("In apply blacklist method!  :)) ")

    var form = document.getElementById("apply_blacklistform");
    $('#download_apply_blacklistbutton').css('display', 'none')
    $('.completed').css('display', 'none');

    $("div #apply_blacklistbutton").on('click', function() {
      $('#download_apply_blacklistbutton').css('display', 'none')
      $('.completed').css('display', 'none');
      $('.notstarted').css('display', 'none');
      $('.inprogress').css('display', 'inline');

      console.log("button clicked")

      var form_data = new FormData($('#apply_blacklistform')[0]);
      var data = new FormData();

      storedFiles_apply_blacklist.forEach(function(file, i) {
        data.append('file' + i, file);
      });

      storedFiles_ref.forEach(function(file, i) {
        data.append('blacklist', file)
      });

      // Also append the cutoff thing to it.
      data.append('checkSort', $("#checkSort")[0].checked)
      console.log("Triggered after clicking submit. ")

      // send ajax POST request to start background job
      $.ajax({
        type: 'POST',
        url: '/apply_blacklist',
        data: data,
        cache: false,
        processData: false,
        contentType: false,
        success: function(data, status, request) {
          status_url = request.getResponseHeader('Location');
          update_progress(status_url);

          // $('.inprogress').css('display', 'none');


        },
        error: function() {
          alert('Unexpected error');
        }
      });
    });


    // End of onclick method for the submit

    $("div #download_apply_blacklistbutton").on('click', function() {
      $.ajax({
        type: 'POST',
        url: '/downloadapply_blacklist',
        success: function(data, status, request) {
          console.log(data)
          length = data.length
          for (i = 0; i < data.length; i++) {
            file_data = data[i][1]
            file_name = data[i][0]

            parsed_data = Papa.unparse(file_data)
            download(parsed_data, file_name, "text/csv")
          }

        }
      });
    });
    // End of onclick method for the download

    $("body").on('click', '.apply_blacklisticon', function(e) {
      console.log("Triggered after clicking trash icon! ")


      var file = $(e.currentTarget)["0"].parentNode.innerText
      console.log(file)
      for (var i = 0; i < storedFiles_apply_blacklist.length; i++) {
        // There's whitespace at the end of these stupid files. Please make sure
        // use trim() otherwise your string equality won't work even if comparing
        // 'identical' strings.
        if (storedFiles_apply_blacklist[i].name.trim() == file.trim()) {
          // Not being called at the moment.
          console.log(file)
          storedFiles_apply_blacklist.splice(i, 1);
          break;
        }
        console.log(i)
      }

      $(this)['0'].parentElement.remove();
    });


    $("#apply_blacklistupload").on('change', function(e) {
      $('.alert2').css('display', 'none');

      console.log("Blacklist adds")
      var files = e.target.files
      var filesArr = Array.prototype.slice.call(files);
      var input = document.getElementById('apply_blacklistupload');
      var output = document.getElementById('apply_blacklistFileList');
      // output.innerHTML = '<ul>';
      for (var i = 0; i < input.files.length; ++i) {
        f = input.files.item(i);
        storedFiles_apply_blacklist.push(f);
        output.innerHTML += '<li>' + f.name + ' <i class= "fas fa-trash-alt apply_blacklisticon"></i>' + '</li>';
        if (['csv', 'xlsx'].indexOf(f.name.split('.')[f.name.split('.').length - 1]) < 0) {
          $('.alert2').css('display', '');
        }
      }
      // output.innerHTML += '</ul><br>';
    });





    $("body").on('click', '.apply_blacklistreficon', function(e) {
      console.log("Triggered after clicking trash icon! ")


      var file = $(e.currentTarget)["0"].parentNode.innerText
      console.log(file)
      for (var i = 0; i < storedFiles_ref.length; i++) {
        // There's whitespace at the end of these stupid files. Please make sure
        // use trim() otherwise your string equality won't work even if comparing
        // 'identical' strings.
        if (storedFiles_ref[i].name.trim() == file.trim()) {
          // Not being called at the moment.
          console.log(file)
          storedFiles_ref.splice(i, 1);
          break;
        }
        console.log(i)
      }

      $(this)['0'].parentElement.remove();
    });


    $("#apply_blacklistrefupload").on('change', function(e) {
      $('.alert1').css('display', 'none');
      console.log("Blacklist adds")
      var files = e.target.files
      var filesArr = Array.prototype.slice.call(files);
      var input = document.getElementById('apply_blacklistrefupload');
      var output = document.getElementById('apply_blacklistrefFileList');
      // output.innerHTML = '<ul>';
      for (var i = 0; i < input.files.length; ++i) {
        f = input.files.item(i);
        storedFiles_ref.push(f);
        output.innerHTML += '<li>' + f.name + ' <i class= "fas fa-trash-alt apply_blacklistreficon"></i>' + '</li>';
        if (['csv', 'xlsx'].indexOf(f.name.split('.')[f.name.split('.').length - 1]) < 0) {
          $('.alert1').css('display', '');
        }
      }
      // output.innerHTML += '</ul><br>';
    });




  }
});
