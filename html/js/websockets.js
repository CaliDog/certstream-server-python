var transitionEnd = 'webkitTransitionEnd otransitionend oTransitionEnd msTransitionEnd transitionend';
var animationEnd = "animationend webkitAnimationEnd oAnimationEnd MSAnimationEnd";

function shuffle(array) {
  var currentIndex = array.length, temporaryValue, randomIndex;

  // While there remain elements to shuffle...
  while (0 !== currentIndex) {

    // Pick a remaining element...
    randomIndex = Math.floor(Math.random() * currentIndex);
    currentIndex -= 1;

    // And swap it with the current element.
    temporaryValue = array[currentIndex];
    array[currentIndex] = array[randomIndex];
    array[randomIndex] = temporaryValue;
  }

  return array;
}

function getRandom(min, max) {
  return Math.random() * (max - min) + min;
}

var URL = "wss://certstream.calidog.io/"
var OPTIONS = {
    debug: false, 
    automaticOpen: false
}

var socket = new ReconnectingWebSocket(URL, null, OPTIONS);

var messages = [];

window.all_timers = [];

$('.certstream-connect-button a.button').click(function(){
    $(this).attr("disabled","disabled")
    $(this).off()
    $('.websocket-indicator').removeClass().addClass('websocket-indicator connecting')
    var timer;
    socket.addEventListener('open', function(){
        $('.websocket-indicator').removeClass().addClass('websocket-indicator connected')
        $('.intro-info').html("Connection established! Waiting for events...")
        timer = setTimeout(function(){
            if (!window.certstream_latest){return;}

            var certstream_messages = window.certstream_latest.messages;

            for(var i=0;i<certstream_messages.length;i++){
                var messageTimer = setTimeout(function(index) {    
                  processMessage({"data": JSON.stringify(certstream_messages[index])});
                }, i * getRandom(0, 2500), i); 
                window.all_timers.push(messageTimer);
            }

        }, 3000)
    }) 
    socket.open();
    setInterval(function(){
        if (messages.length != 0){
            clearTimeout(timer);
            for (var i=0; i<window.all_timers;i++){
                clearTimeout(window.all_timers[i])
            }
            var message = messages.shift();
            var domains = message.data.leaf_cert.all_domains
            var htmlMessage = formatTimeForEvent(message)

            if($('.output-demo p').length >= 10){
                $('.output-demo p').eq(9).remove()
            }

            $('.intro-info').remove()

            var ele = $("<p class='faded-input marginless'></p>").text(htmlMessage);
            $('.output-demo').prepend(ele);
        }
    }, 100)
})

//$.getJSON("/latest.json", function( data ) {
$.getJSON("/latest.json", function( data ) {
  window.certstream_latest = data
  for(var i=0;i<Math.min(5, window.certstream_latest.messages.length);i++){

    $('.output-cli').prepend($("<p class='marginless'></p>").text(formatTimeForEvent(window.certstream_latest.messages[i])));
  }
});

function formatTimeForEvent(event){
    var domains = event.data.leaf_cert.all_domains
    var cn = domains[0]

    var message = "[" + moment.unix(event.data.seen).format("MM/DD/YY HH:mm:ss") + "] " + cn 
    if (domains.length != 0){
        message += " (SAN: " + domains.slice(1).join(', ') + ")";
    }
    return message
}

function processMessage(event) {
    var message = JSON.parse(event.data);
    if(message.message_type == "heartbeat"){

    } else {
        messages.push(message)
    }
}

// Listen for messages
socket.addEventListener('message', processMessage);

$.getJSON('/example.json', function(responseJSON){
    var formatter = new JSONFormatter(responseJSON, 4, {
        hoverPreviewEnabled: true,
        theme: 'light'

    })
    $('#json-parsed').append(formatter.render())
})

