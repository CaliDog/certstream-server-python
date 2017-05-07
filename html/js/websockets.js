var transitionEnd = 'webkitTransitionEnd otransitionend oTransitionEnd msTransitionEnd transitionend';
var animationEnd = "animationend webkitAnimationEnd oAnimationEnd MSAnimationEnd";
var randomDomains = [
    "www.blaetterteig-genussanlass.ch (SAN: blaetterteig-genussanlass.ch)",
    "whotf.org (SAN: www.whotf.org)",
    "www.kkaydesigns.com (SAN: kkaydesigns.com)",
    "suresteviajes.com (SAN: www.suresteviajes.com)",
    "www.glasslineokano.com (SAN: glasslineokano.com)",
    "u2u.com.br (SAN: autodiscover.u2u.com.br, cpanel.u2u.com.br, mail.u2u.com.br, webdisk.u2u.com.br, webmail.u2u.com.br, www.u2u.com.br)",
    "www.ewige-gegenwart.com (SAN: ewige-gegenwart.com)",
    "www.devotionextendeddayprogram.com (SAN: devotionextendeddayprogram.com)",
    "www.hifilounge.ch (SAN: hifilounge.ch)",
    "www.derwegderbotschaft.de (SAN: derwegderbotschaft.de)",
    "asktherabbi.hu (SAN: www.asktherabbi.hu)",
    "halaszbastya.hu (SAN: www.halaszbastya.hu)",
    "ncyc2013.com (SAN: mail.ncyc2013.com, www.ncyc2013.com)",
    "www.ok-tanakashouten.com (SAN: ok-tanakashouten.com)",
    "www.mueller-die-frisoere.de (SAN: mueller-die-frisoere.de)",
    "www.homeopatiatexcoco.com.mx (SAN: homeopatiatexcoco.com.mx)",
    "www.npareja2.com (SAN: npareja2.com)",
    "www.rocodoll.biz (SAN: rocodoll.biz)",
    "www.carosfutterkiste.de (SAN: carosfutterkiste.de)",
    "www.how.2u.do (SAN: how.2u.do)",
    "www.davejfb.nl (SAN: davejfb.nl, davesspacecave.nl, www.davesspacecave.nl)",
    "segitohaz.hu (SAN: www.segitohaz.hu)",
    "applnstyle.com (SAN: autodiscover.applnstyle.com, cpanel.applnstyle.com, mail.applnstyle.com, webdisk.applnstyle.com, webmail.applnstyle.com, www.applnstyle.com)",
    "marinelifecoins.kaiser-kaplaner.net (SAN: www.marinelifecoins.kaiser-kaplaner.net)",
]

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

$('.certstream-connect-button a.button').click(function(){
    $(this).attr("disabled","disabled")
    $(this).off()
    $('.websocket-indicator').removeClass().addClass('websocket-indicator connecting')
    var timer;
    socket.addEventListener('open', function(){
        $('.websocket-indicator').removeClass().addClass('websocket-indicator connected')
        $('.intro-info').html("Connection established! Waiting for events...")
        timer = setTimeout(function(){
            $('.intro-info').html("Connection established! Waiting for events... <br><b>Note:</b> CTLs usually flush in batches, so please be patient!")
        }, 5000)
    }) 
    socket.open();
    setInterval(function(){
        if (messages.length != 0){
            clearTimeout(timer);
            var message = messages.shift();
            var domains = message.data.leaf_cert.all_domains
            var cn = domains.shift()
            
            var htmlMessage = "[" + moment().format("MM/DD/YY HH:mm:ss") + "] " + cn 
            if (domains.length != 0){
                htmlMessage += " (SAN: " + domains.join(', ') + ")";
            }

            

            if($('.output-demo p').length >= 10){
                $('.output-demo p').eq(9).remove()
            }

            $('.intro-info').remove()

            var ele = $("<p class='faded-input marginless'></p>").text(htmlMessage);
            $('.output-demo').prepend(ele);
        }
    }, 100)
})


function processMessage(event) {
    var message = JSON.parse(event.data);
    if(message.message_type == "heartbeat"){

    } else {
        messages.push(message)
    }
}

// Listen for messages
socket.addEventListener('message', processMessage);

shuffle(randomDomains)
for (var i=0; i<5;i++){
    var domainLine = randomDomains[i];
    var htmlMessage = "[" + moment().subtract(5-i * 1.05, 'minutes').subtract(getRandom(0, 60), 'seconds').format("MM/DD/YY HH:mm:ss") + "] " + domainLine
    $('.output-cli').prepend($("<p class='marginless'></p>").text(htmlMessage));
}


