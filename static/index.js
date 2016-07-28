$(function() {
    context = document.getElementById('canvas').getContext("2d");
    var clickX = new Array();
    var clickY = new Array();
    var clickDrag = new Array();
    var clickColor = new Array();
    var outlineImage = new Image();
    outlineImage.src = "annotation/monet.png"
    outlineImage.onload = function () {
        context.drawImage(outlineImage, 0, 0, 512, 384);
    }
    var paint;

    var colorRed = "#ff0000";

    $('input[type=radio][name=color]').change(function() {
        curColor = this.value
    });

    $('input[type=radio][name=style]').change(function() {
        clickX = new Array();
        clickY = new Array();
        clickDrag = new Array();
        clickColor = new Array();
        outlineImage.src = "annotation/" + this.value + ".png";
    });

    var curColor = colorRed;

    function addClick(x, y, dragging)
    {
      clickX.push(x);
      clickY.push(y);
      clickDrag.push(dragging);
      clickColor.push(curColor);
    }
    function redraw(){
      context.clearRect(0, 0, context.canvas.width, context.canvas.height); // Clears the canvas
      context.drawImage(outlineImage, 0, 0, 512, 384);


      context.lineJoin = "round";
      context.lineWidth = 20;

      for(var i=0; i < clickX.length; i++) {
        context.beginPath();
        if(clickDrag[i] && i){
          context.moveTo(clickX[i-1], clickY[i-1]);
         }else{
           context.moveTo(clickX[i]-1, clickY[i]);
         }
         context.lineTo(clickX[i], clickY[i]);
         context.closePath();
         context.strokeStyle = clickColor[i];
         context.stroke();
      }
    }
    $('#canvas').mousedown(function(e){
        var mouseX = e.pageX - this.offsetLeft - $(this).parent().offset().left;
        var mouseY = e.pageY - this.offsetTop - $(this).parent().offset().top ;
        var offsetL = this.offsetLeft + $(this).parent().offset().left - 15;
        var offsetT = this.offsetTop + $(this).parent().offset().top;

        paint = true;
        addClick(e.pageX - offsetL, e.pageY - offsetT);
        redraw();
    });
    $('#canvas').mousemove(function(e){
        if(paint){
            var offsetL = this.offsetLeft + $(this).parent().offset().left - 15;
            var offsetT = this.offsetTop + $(this).parent().offset().top;
            addClick(e.pageX - offsetL, e.pageY - offsetT, true);
            redraw();
        }
    });
    $('#canvas').mouseup(function(e){
      paint = false;
    });
    $('#canvas').mouseleave(function(e){
      paint = false;
    });

    function showResult(imageUrl) {
        $("#resultImage").attr("src", imageUrl)
    }

    function poll(filename) {
            var poll_interval=0;

            $.ajax({
                    url: "/ready/" + filename,
                    type: 'GET',
                    dataType: 'json',
                    success: function(data) {
                            showResult(data.url);
                            $('#submitButton').button('reset');
                            poll_interval=0;
                    },
                    error: function () {
                            poll_interval=500;
                            setTimeout(function() {poll(filename)}, poll_interval);
                    },
            });
    }


    $('#submitButton').click(function(e) {
        var formData = new FormData();
        var $btn = $(this).button('loading');
        document.getElementById('canvas').toBlob(function(blob){
            // var img = context.getImageData(0, 0, 512, 384)
            // let file = new File(img.data, "image.png", {type : 'image/png'})
            formData.append("image", blob, "image.jpg");
            formData.append("style", $('input[type=radio][name=style]:checked').val())
            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/upload', true);
            xhr.onload = function () {
              if (xhr.status === 200) {
                var data = JSON.parse(xhr.responseText);
                poll(data.uid);
              } else {
                alert('An error occurred!');
              }
            };
            xhr.send(formData);
        }, "image/jpeg", 1)
    })
});
