<template>
    <div class="main-wrapper">
        <!-- <top-panel></top-panel> -->
        <section class="section top-panel">
            <div class="container">
                <div class="columns">
                    <div class="column"></div>
                    <div class="column splash">
                        <h1 class="title animated fadeInDown">
                            CERTSTREAM
                        </h1>
                        <h2 class="subtitle animated fadeIn slow delayed">
                            Real-time <a href="https://www.certificate-transparency.org/what-is-ct">certificate transparency log</a> update stream.
                            <br>
                            See SSL certificates as they're issued in real time.
                        </h2>
                        <a @click="scrollDown" class="button learn-more animated fadeIn slow delayed">Learn More </i></a>
                    </div>
                </div>
            </div>
        </section>

        <img id="rolling-transition" class="transition" src="../assets/rolling-transition.png">

        <!-- <intro-panel></intro-panel> -->
        <section class="section intro-panel" id="intro-panel">
            <div class="container has-text-centered">
                <div class="columns">
                    <div class="column has-text-centered">
                        <img class="overview" src="../assets/certstream-overview.png">
                    </div>
                    <div class="column right-column">
                        <p class="title">TL;DR</p>
                        <p class="content">
                            CertStream is an intelligence feed that gives you real-time updates from the <a
                                href="https://www.certificate-transparency.org/what-is-ct">Certificate
                            Transparency Log network</a>, allowing you to use it as a building block to make tools that react to new certificates being
                            issued in real time. We do all the hard work of watching, aggregating, and parsing the transparency logs, and give you super simple
                            libraries that enable you to do awesome things with minimal effort.
                            <br><br>
                            It's our way of saying "thank you" to the amazing security community in general, as well as a
                            good way to give people a taste of the sort of intelligence feeds that are powering our flagship
                            product - <a href="https://phishfinder.io" target="_blank">PhishFinder</a>.
                        </p>
                    </div>
                </div>
            </div>
        </section>

        <feed-watcher></feed-watcher>

        <!-- <get-started-panel></get-started-panel> -->
        <section class="section get-started-panel">
            <div class="container has-text-centered get-started-content">
                <p class="title">GET STARTED</p>
                <div class="container has-text-centered">
                    <div class="columns">
                        <div class="column">
                            <div class="content-section">
                                <h2 id="install" class="small-title">Install CertStream</h2>
                                <p class="white-text">
                                    CertStream is hosted <a href="https://github.com/search?q=org%3ACaliDog+certstream">on Github</a> and we currently have libraries for <a href="https://github.com/CaliDog/certstream-python">Python</a>, <a href="https://github.com/CaliDog/certstream-js">Javascript</a>, <a href="https://github.com/CaliDog/certstream-go">Go</a>, and <a href="https://github.com/CaliDog/certstream-java">Java</a>.
                                    These libraries are intended to lower the barrier of entry to interacting with the <a href="https://www.certificate-transparency.org/what-is-ct">Certificate Transparency Log</a> network so you can craft simple but powerful analytics tools with just a few lines of code!
                                </p>
                                <div class="columns language-buttons">
                                    <div class="python column" :class="{active: activeLanguage == 'python'}" @mouseover="setLanguage('python')">
                                        <i :class="{colored: activeLanguage == 'python'}" class="devicon-python-plain"></i>
                                        <a target="_blank" href="https://github.com/CaliDog/certstream-python">Python</a>
                                    </div>

                                    <div class="javascript column" :class="{active: activeLanguage == 'javascript'}" @mouseover="setLanguage('javascript')">
                                        <i :class="{colored: activeLanguage == 'javascript'}" class="devicon-javascript-plain"></i>
                                        <a target="_blank" href="https://github.com/CaliDog/certstream-js">JavaScript</a>
                                    </div>

                                    <div class="go column" :class="{active: activeLanguage == 'go'}" @mouseover="setLanguage('go')">
                                        <i :class="{colored: activeLanguage == 'go'}" class="devicon-go-plain"></i>
                                        <a target="_blank" href="https://github.com/CaliDog/certstream-go">Go</a>
                                    </div>

                                    <div class="java column" :class="{active: activeLanguage == 'java'}" @mouseover="setLanguage('java')">
                                        <i :class="{colored: activeLanguage == 'java'}" class="devicon-java-plain"></i>
                                        <a target="_blank" href="https://github.com/CaliDog/certstream-java">Java</a>
                                    </div>
                                </div>
                                <div class="typer-wrapper">
                                    <p :class="{active: activeLanguage !== null && activeLanguage != 'java'}" class="content typer-content">
                                        <span class="dollar">$</span>
                                        <span class="typer"></span>
                                        <span ref="clipboard" @click="showToolTip" @mouseleave="hideToolTip" v-tooltip.top-center="{content: 'Copied to your clipboard!', trigger: 'manual', hide: 1000}" class="copy">
                                            <i class="fa fa-clipboard" aria-hidden="true"></i>
                                        </span>
                                    </p>
                                </div>

                            </div>
                            <div class="content-section cli-example">
                                <h2 id="cli" class="small-title">CertStream CLI</h2>

                                <p class="white-text">
                                    Installing the CLI is easy, all you have to do is <a @click="showPipInstructions">install the python library</a> and run it like any other program. It can be used to emit certificate data in a number of forms to be processed by other command line utilities (or just for storage). Pipe it into grep, sed, awk, jq, or any other utility to send alerts, gather statistics, or slice and dice certs as you want!
                                </p>

                                <div class="columns demo-gifs">
                                    <div class="column">
                                        <div class="columns demo-selector-wrapper">
                                            <div :class="{active: activeDemo.name == 'basic'}" @mouseover="setActiveDemo('basic')" class="column">
                                                <div class="demo-selector">
                                                    <p>Basic output</p>
                                                </div>
                                            </div>
                                            <div :class="{active: activeDemo.name == 'full'}" @mouseover="setActiveDemo('full')" class="column">
                                                <div class="demo-selector">
                                                    <p>Full SAN output</p>
                                                </div>
                                            </div>
                                            <div :class="{active: activeDemo.name == 'json'}" @mouseover="setActiveDemo('json')" class="column">
                                                <div class="demo-selector">
                                                    <p>JSON output mode + JQ</p>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="demo-data-wrapper">
                                            <div class="command-wrapper">
                                                <p class="content typer-content">
                                                    <span class="dollar">$</span> <span class="demo-typer"></span>
                                                </p>
                                            </div>
                                            <div class="section-wrapper">
                                                <img @click="showExampleModal('basic')" class="demo-gif" :src="activeDemo.image">
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- <data-structures></data-structures> -->
        <section class="section data-structures">
            <div class="container has-text-centered data-structures-content">
                <p class="title">SIMPLE(ISH) DATA</p>
                <div class="container has-text-centered">
                    <div class="columns">
                        <div class="column subsection-wrapper heartbeat-subsection">
                            <h2 class="small-title">Heartbeat Messsages</h2>
                            <div class="json-tree-wrapper">
                                <json-tree :data="heartbeat" :options="{maxDepth: 3}"></json-tree>
                            </div>
                        </div>
                    </div>
                    <div class="columns">
                        <div class="column subsection-wrapper update-subsection">
                            <h2 class="small-title">Certificate Update</h2>
                            <p>If you prefer the raw data blob, there's a live example <a target="_blank" href="https://certstream.calidog.io/example.json">here</a></p>
                            <div class="json-tree-wrapper">
                                <json-tree :data="exampleMessage" :level="3"></json-tree>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- <footer></footer> -->
        <section class="section footer">
            <div class="container has-text-centered">
                <div class="container has-text-centered">
                    <img class="doghead" src="../assets/doghead.png">
                    <p>Made with love by Cali Dog Security</p>
                    <span class="icons">
                        <a target="_blank" href="https://medium.com/cali-dog-security">
                            <i class="fa fa-medium" aria-hidden="true"></i>
                        </a>
                        <a target="_blank" href="https://github.com/calidog">
                            <i class="fa fa-github" aria-hidden="true"></i>
                        </a>
                    </span>
                    <p>© 2017 Cali Dog Security</p>
                </div>
            </div>
        </section>
    </div>
</template>


<script>
    import FeedWatcher from "./FeedWatcher.vue"
    import Vue from "vue"

    import VTooltip from 'v-tooltip'
    import VueScrollTo from 'vue-scrollto'
    import JsonTree from 'vue-json-tree'

    Vue.use(VTooltip);
    Vue.use(VueScrollTo);

    import Typed from 'typed.js';

    let heartbeat = {
        "message_type": "heartbeat",
        "timestamp": 1509613330.63217
    };

    let exampleMessage = {
        "message_type": "certificate_update",
        "data": {
            "update_type": "PreCertEntry",
                "leaf_cert": {
                "subject": {
                    "aggregated": "/jurisdictionC=JP/serialNumber=0110-01-029641/businessCategory=Private Organization/C=JP/ST=Tokyo/L=Shibuya-ku/O=Railway Information Systems Co.,Ltd./OU=Marketing And Planning Div.2 Marketing And Development Dept./CN=cor-trl.jrsystem.jp",
                        "C": "JP",
                        "ST": "Tokyo",
                        "L": "Shibuya-ku",
                        "O": "Railway Information Systems Co.,Ltd.",
                        "OU": "Marketing And Planning Div.2 Marketing And Development Dept.",
                        "CN": "cor-trl.jrsystem.jp"
                },
                "extensions": {
                    "basicConstraints": "CA:FALSE",
                        "certificatePolicies": "Policy: 1.3.6.1.4.1.6334.1.100.1\n  CPS: https://www.cybertrust.ne.jp/ssl/repository/index.html\nPolicy: 2.23.140.1.1\n",
                        "authorityInfoAccess": "OCSP - URI:http://sureseries-ocsp.cybertrust.ne.jp/OcspServer\nCA Issuers - URI:http://sureseries-crl.cybertrust.ne.jp/SureServer/2021_ev/ctjevcag2_sha256.crt\n",
                        "subjectAltName": "DNS:cor-trl.jrsystem.jp",
                        "ct_precert_poison": "NULL",
                        "keyUsage": "Digital Signature, Key Encipherment",
                        "extendedKeyUsage": "TLS Web Server Authentication, TLS Web Client Authentication",
                        "authorityKeyIdentifier": "keyid:91:43:05:EC:B4:6A:15:4F:DC:E1:EE:86:56:5C:11:D0:2A:2B:8D:5F\n",
                        "crlDistributionPoints": "\nFull Name:\n  URI:http://sureseries-crl.cybertrust.ne.jp/SureServer/2021_ev/cdp.crl\n",
                        "subjectKeyIdentifier": "0E:86:5F:55:9E:61:D5:F4:CA:E4:4B:46:76:FF:87:A8:56:D4:F1:70"
                },
                "not_before": 1509608474.0,
                    "not_after": 1517497140.0,
                    "as_der": "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",
                    "all_domains": [
                    "cor-trl.jrsystem.jp"
                ]
            },
            "chain": [
                {
                    "subject": {
                        "aggregated": "/C=JP/O=Cybertrust Japan Co., Ltd./CN=Cybertrust Japan EV CA G2",
                        "C": "JP",
                        "ST": null,
                        "L": null,
                        "O": "Cybertrust Japan Co., Ltd.",
                        "OU": null,
                        "CN": "Cybertrust Japan EV CA G2"
                    },
                    "extensions": {
                        "keyUsage": "Certificate Sign, CRL Sign",
                        "basicConstraints": "CA:TRUE, pathlen:0",
                        "subjectKeyIdentifier": "91:43:05:EC:B4:6A:15:4F:DC:E1:EE:86:56:5C:11:D0:2A:2B:8D:5F",
                        "certificatePolicies": "Policy: 1.3.6.1.4.1.6334.1.100.1\n  CPS: http://cybertrust.omniroot.com/repository\n",
                        "crlDistributionPoints": "\nFull Name:\n  URI:http://crl.omniroot.com/ctglobal.crl\n",
                        "authorityInfoAccess": "OCSP - URI:http://ocsp.omniroot.com/evssl\n",
                        "authorityKeyIdentifier": "keyid:B6:08:7B:0D:7A:CC:AC:20:4C:86:56:32:5E:CF:AB:6E:85:2D:70:57\n"
                    },
                    "not_before": 1393401600.0,
                    "not_after": 1575964800.0,
                    "as_der": "MIIERTCCAy2gAwIBAgILBAAAAAABRG4ZUuYwDQYJKoZIhvcNAQELBQAwOzEYMBYGA1UEChMPQ3liZXJ0cnVzdCwgSW5jMR8wHQYDVQQDExZDeWJlcnRydXN0IEdsb2JhbCBSb290MB4XDTE0MDIyNjA4MDAwMFoXDTE5MTIxMDA4MDAwMFowVjELMAkGA1UEBhMCSlAxIzAhBgNVBAoTGkN5YmVydHJ1c3QgSmFwYW4gQ28uLCBMdGQuMSIwIAYDVQQDExlDeWJlcnRydXN0IEphcGFuIEVWIENBIEcyMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEArCKKisPZ9Q65mENR+uZiufhKz1jxO27rMNvjs8t53jg3VDa06k/sZPEyUaqyKb7W5l2TfDGhrppzvNWT/IEiHHEO6/IYqWwLAaoH3NrxKVH7ZKuzUGWom/OOEuK3ApF6h9YF8Ar8gXy2kHxlaZzi+K+hstgEqGnrXqIOYdQRriqFKroRaAETF0yx28Z9Bfl9HB8UPoS4c8EZp4a1I747G2+AxXL+ViR3Jedj2eLHMZC9Gx07uRhTFDVpHfdsSVIR5/xg3VP8JpSfp0ul0lMq9OpfDlgDazK4ecb0pkTh73NG4nvqpHlOo02HeYRgh4QEsuotbzg5xv7G23zwZpdjyQIDAQABo4IBLTCCASkwDgYDVR0PAQH/BAQDAgEGMBIGA1UdEwEB/wQIMAYBAf8CAQAwHQYDVR0OBBYEFJFDBey0ahVP3OHuhlZcEdAqK41fMFAGA1UdIARJMEcwRQYKKwYBBAGxPgFkATA3MDUGCCsGAQUFBwIBFilodHRwOi8vY3liZXJ0cnVzdC5vbW5pcm9vdC5jb20vcmVwb3NpdG9yeTA1BgNVHR8ELjAsMCqgKKAmhiRodHRwOi8vY3JsLm9tbmlyb290LmNvbS9jdGdsb2JhbC5jcmwwOgYIKwYBBQUHAQEELjAsMCoGCCsGAQUFBzABhh5odHRwOi8vb2NzcC5vbW5pcm9vdC5jb20vZXZzc2wwHwYDVR0jBBgwFoAUtgh7DXrMrCBMhlYyXs+rboUtcFcwDQYJKoZIhvcNAQELBQADggEBAA0gyrDmAxSDnyRrYZpl6ic+O6fMKz0vG1cxgOsJbzlm77U8wBroT77atZrcf5CXh26dTKovZaMYCYXw1y/p/IVCg9NQqt1wt0PYhNAvCOL00dyfW4qztVOgCrMtCOMLy2XGlHTjxKA0A56hj6nTtQuwM+kXV4nJzsbPpn/b7BcEtqgAlNSM1CoAn8CxHMi6vtYyAPm5CTpa0VAhkCBa6MJwkvf89Q6ugwmwXtTFcDCcoCywmpDMxCYlFjXEUIDYHU4mlWEjXaElUusqbucq5qfj2Hg/cpitpE9sZ00O6XWRGLdxyrnayanqzlwyafYYWSgzTrrtxddsMz9A/VA46JY="
                },
                {
                    "subject": {
                        "aggregated": "/O=Cybertrust, Inc/CN=Cybertrust Global Root",
                        "C": null,
                        "ST": null,
                        "L": null,
                        "O": "Cybertrust, Inc",
                        "OU": null,
                        "CN": "Cybertrust Global Root"
                    },
                    "extensions": {
                        "keyUsage": "Certificate Sign, CRL Sign",
                        "basicConstraints": "CA:TRUE",
                        "subjectKeyIdentifier": "B6:08:7B:0D:7A:CC:AC:20:4C:86:56:32:5E:CF:AB:6E:85:2D:70:57",
                        "crlDistributionPoints": "\nFull Name:\n  URI:http://www2.public-trust.com/crl/ct/ctroot.crl\n",
                        "authorityKeyIdentifier": "keyid:B6:08:7B:0D:7A:CC:AC:20:4C:86:56:32:5E:CF:AB:6E:85:2D:70:57\n"
                    },
                    "not_before": 1166169600.0,
                    "not_after": 1639555200.0,
                    "as_der": "MIIDoTCCAomgAwIBAgILBAAAAAABD4WqLUgwDQYJKoZIhvcNAQEFBQAwOzEYMBYGA1UEChMPQ3liZXJ0cnVzdCwgSW5jMR8wHQYDVQQDExZDeWJlcnRydXN0IEdsb2JhbCBSb290MB4XDTA2MTIxNTA4MDAwMFoXDTIxMTIxNTA4MDAwMFowOzEYMBYGA1UEChMPQ3liZXJ0cnVzdCwgSW5jMR8wHQYDVQQDExZDeWJlcnRydXN0IEdsb2JhbCBSb290MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA+Mi8vRRQZhP/8NN57CPytxrHjoXxEnOmGaoQ25yiZXRadz5RfVb23CO21O1fWLE3TdVJDm71aofW0ozSJ8bi/zafmGWgE07GKmSb1ZASzxQG9Dvj1Ci+6A74q05IlG2OlTEQXO2iLb3VOm2yHLtgwEZLAfVJrn5GitB0jaEMAs7u/OePuGtm839EAL9mJRQr3RAwHQeWP032a7iPt3sMpTjr3kfb1V05/Iin89cqdPHoWqI7n1C6poxFNcJQZZXcY4Lv3b93TZxiyWNzFtApD0mpSPCzqrdsxacwOUBdrsTiXSZT8M4cIwhhqJQZugRiQOwfOHB3EgZxpzAYXSUnpQIDAQABo4GlMIGiMA4GA1UdDwEB/wQEAwIBBjAPBgNVHRMBAf8EBTADAQH/MB0GA1UdDgQWBBS2CHsNesysIEyGVjJez6tuhS1wVzA/BgNVHR8EODA2MDSgMqAwhi5odHRwOi8vd3d3Mi5wdWJsaWMtdHJ1c3QuY29tL2NybC9jdC9jdHJvb3QuY3JsMB8GA1UdIwQYMBaAFLYIew16zKwgTIZWMl7Pq26FLXBXMA0GCSqGSIb3DQEBBQUAA4IBAQBW7wojoFROlZfJ+InaRcHUowAl9B8Tq7ejhVhpwjCt2BWKLePJzYFa+HMjWqd8BfP9IjsO0QbE2zZMcwSO5bAi5MXzLqXZI+O4Tkogp24CJJ8iYGd7ix1yCcUxXOl5n4BHPa2hCwcUPUf/A2kaDAtE52Mlp3+yybh2hO0j9n0Hq0V+09+zv+mKts2oomcrUtW3ZfA5TGOgkXmTUg9U3YO7n9GPp1Nzw8v/MOx8BLjYRB+TX3EJIrduPuocA06dGiBh+4E37F78CkWr1+cXVdCg6mCbpvbjjFspwgZgFJ0tl0ypkxWdYcQBX0jWWL1WMRJOEcgh4LMRkWXbtKaIOM5V"
                }
            ],
                "cert_index": 166946722,
                "seen": 1509613630.389911,
                "source": {
                "url": "ct.googleapis.com/pilot",
                    "name": "Google 'Pilot' log"
            }
        }
    };

    export default {
        name: 'frontpage',
        data() {
            return {
                activeLanguage: null,
                activeDemo: {},
                typer: null,
                languages: {
                    python: {install: "pip install certstream"},
                    javascript: {install: "npm install certstream"},
                    go: {install: "go get github.com/CaliDog/certstream-go"},
                    java: {install: "<a href='https://github.com/calidog/certstream-java#installing' target='_blank'>Click Here</a> for instructions (because Java 😓 ️)"},
                },
                demos: {
                    "basic": {
                        name: "basic",
                        command: "certstream",
                        image: require("../assets/demo1.gif")
                    },
                    "full": {
                        name: "full",
                        command: "certstream --full",
                        image: require("../assets/demo2.gif")
                    },
                    "json": {
                        name: "json",
                        command: "certstream --json | jq -r '.data | [.source.url, (.cert_index|tostring), .leaf_cert.subject.aggregated] | join(\",\")'",
                        image: require("../assets/demo3.gif")
                    }
                },
                heartbeat: heartbeat,
                exampleMessage: exampleMessage

            }
        },
        mounted() {
            this.typer = new Typed('.typer', {
                strings: ["Select a language above"],
                showCursor: false,
            });
            this.demoTyper = new Typed('.demo-typer', {
                strings: ["certstream"],
                showCursor: false,
            })
            this.activeDemo = this.demos['basic']
        },
        methods: {
            scrollDown (){
                this.$scrollTo("#intro-panel", 500);
            },
            setActiveDemo (demoName){
                if (this.demos[demoName] == this.activeDemo){return}

                this.activeDemo = this.demos[demoName];
                this.demoTyper.strings = [this.activeDemo.command];

                this.demoTyper.reset();
            },
            showPipInstructions(){
                this.$scrollTo("#install", 500);
                this.setLanguage("python");
            },
            showToolTip(){
                this.$refs.clipboard._tooltip.show();
                this.copyToClipboard(this.languages[this.activeLanguage].install);
            },
            hideToolTip(){
                setTimeout(this.$refs.clipboard._tooltip.hide, 1000)
            },
            setLanguage(lang) {
                if (this.activeLanguage === lang){return}

                this.activeLanguage = lang;

                this.typer.strings = [this.languages[lang].install];

                this.typer.reset();
            },
            copyToClipboard(text) {
                if (window.clipboardData && window.clipboardData.setData) {
                    // IE specific code path to prevent textarea being shown while dialog is visible.
                    return clipboardData.setData("Text", text);

                } else if (document.queryCommandSupported && document.queryCommandSupported("copy")) {
                    var textarea = document.createElement("textarea");
                    textarea.textContent = text;
                    textarea.style.position = "fixed";  // Prevent scrolling to bottom of page in MS Edge.
                    document.body.appendChild(textarea);
                    textarea.select();
                    try {
                        return document.execCommand("copy");  // Security exception may be thrown by some browsers.
                    } catch (ex) {
                        console.warn("Copy to clipboard failed.", ex);
                        return false;
                    } finally {
                        document.body.removeChild(textarea);
                    }
                }
            }
        },
        components: {
            FeedWatcher,
            JsonTree
        }
    }
</script>

<style lang="scss">

    @import url('../lib/json-tree.css');

    body {
        line-height: 1.8;
    }

    .splash{
        margin-top: -20vh;
    }

    @media screen and (max-width:768px) and (min-width:0px) {
        html{
            font-size: 12px;
        }
        a{
            border-bottom: 1px solid rgb(236, 240, 241) !important;
        }
        .main-wrapper{
            overflow: hidden;
        }
        .column.splash{
            text-align: center;
        }
        .typer-content{
            margin: 0;
        }
        .demo-selector-wrapper{
            .column{
                margin: 0 !important;
                .demo-selector{
                    border-radius: 0 !important;
                }
            }
        }
        .data-structures-content{
            padding: 10px !important;
        }
    }

    @media screen and (max-width:930px){
        .get-started-panel{
            padding: 0;
            .get-started-content{
                padding-right: 10px !important;
                padding-left: 10px !important;
            }
        }
        .title{
            font-size: 3rem !important;
        }
    }
    @media screen and (max-width:1155px) {
        .get-started-panel, .data-structures{
            padding-right: 0 !important;
            padding-left: 0 !important;
        }

    }


        .footer{
        color: #555555;
        background: #D7E7D4;
        font-weight: 700;
        padding-bottom: 3rem;
        .doghead{
            width: 111px;
            margin: 10px;
        }
        .icons{
            font-size: 26px;
            margin-bottom: 10px;
            display: block;
            a{
                padding: 10px;
                color: #555555;
                &:hover{
                    color: #1E82C8;
                }
            }
        }
    }


    .button.learn-more{
        background: #1AAF5D;
        border: none;
        padding: 14px 60px;
        border-radius: 50px;
        display: inline;
        color: #ECF0F1;
        font-weight: 700;
        font-size: 1.125rem;
        &:hover{
            box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.2);
        }
        &:active{
            box-shadow: none;
        }
    }

    .cli-example{
        .columns{
            margin: 0;
        }
        .demo-gifs{
            color: #ECF0F1;

            .demo-gif{
                width: 100%;
                max-width: 100%;
                height: 100%;
                max-height: 100%;
                border-radius: 4px;
            }

            .demo-data-wrapper{
                background: #217C4B;
                margin-top: 30px;
                padding: 30px 20px 20px;
                border-radius: 4px;
            }

            .demo-selector-wrapper{
                margin-top: 30px;
                margin-bottom: 20px;
            }

            .command-wrapper{
                margin: 0;
            }

            .columns > .column.active .demo-selector{
                background: rgba(47, 49, 51, 1);
            }

            .demo-selector-wrapper .column{
                margin-right: 30px;
                &:last-child{
                    margin-right: 0;
                }
            }

            .demo-selector{
                background: rgba(47, 49, 51, 0.8);
                font-weight: 700;
                border-radius: 4px;
                padding: 1rem;
            }
            .column{
                text-align: center;
                padding: 0;
            }
            .dollar{
                opacity: 1 !important;
            }
            .typer-content{
                width: 100% !important;
                margin-bottom: 20px;
                display: inline-block;
                text-align: left;
            }
        }
    }

    .top-panel {
        @media screen and (max-width:768px) and (min-width:0px) {
            height: 90vh;
            background-attachment: scroll;
            .container .columns .column:first-child{
                display: none;
            }
            .subtitle, .title{
                text-align: center;
            }
        }

        background: url('../assets/certstream-bg.png') no-repeat center center fixed;
        background-size: cover;
        background-position-y: 0;

        display: flex;
        align-content: center;
        justify-content: center;
        height: 100vh;

        .container{
            margin: 0;
            width: 100%;
            display: flex;
            align-content: center;
            justify-content: center;
            .columns{
                width: 100%;
                display: flex;
                justify-content: center;
                align-items: center;
            }
        }

        .title {
            font-size: 4rem;
            color: #ECF0F1;
            margin-bottom: 48px;
        }

        .subtitle {
            font-weight: 700;
            font-size: 1.25rem;
            color: #ECF0F1;
            line-height: 1.6;
            margin-bottom: 2.5rem;
            a{
                color: #ECF0F1;
                border-bottom: 1px solid transparent;
                transition: all .5s;
                border-bottom: 1px dashed #ECF0F1;
                &:hover{
                    border-bottom: 1px solid #ECF0F1;
                }
            }
        }

    }

    .transition {
        display: block;
        margin-top: -80px;
        min-width: 100%;
    }

    .small-title {
        font-weight: 700;
        font-size: 1.125rem;
        color: #ECF0F1;
    }

    .content-section{
        margin-bottom: 80px;
    }

    .mobile-only-disclaimer{
        display: none;
    }

    .data-structures{
        .subsection-wrapper{
            width: 100%;

            &.heartbeat-subsection{
                margin-top: 20px;
                margin-bottom: 45px;
                h2{
                    margin-bottom: 20px;
                }
            }

            &>p{
                color: #ECF0F1;
                padding: 5px 0 20px;
                a{
                    font-weight: 600;
                }
            }
        }

        .json-tree{
            font-size: .9rem !important;
        }
        .json-tree-root{

            background: #333;
            color: #ECF0F1;
            min-width: 0;
            .json-tree-paired, .json-tree-row:hover{
                background-color: #3e3e3e;
            }
            .json-tree{
                color: #ECF0F1;
                .json-tree-value-number{
                    color: #1E82C8;
                }
                .json-tree-value-string{
                    color: #c66c66;
                }
            }

        }

        .data-structures-content{
            padding: 1rem 140px;
        }
        .content{
            padding: 13px 20px;
            background: #2E3032;
            border-radius: 2px;
        }
    }

    .intro-panel, .get-started-panel, .data-structures {
        &.data-structures{
            background: #179D53 !important;
        }
        background: #1AAF5D;
        padding: 75px 100px 64px 100px;

        @media screen and (max-width:768px) and (min-width:0px) {
            padding: 7rem 2.5rem;
            .overview{
                margin-top: 0 !important;
            }
            .title{
                text-align: center;
                font-size: 2.5rem !important;
            }
            .content{
                font-size: 1.5rem !important;
            }
        }

        .right-column{
            margin-top: 60px;
        }

        img.overview {
            margin-top: -1rem;
            max-height: 585px;
            max-width: 90vw;
            width: auto;
            height: auto;
        }

        .column {
            text-align: left;
        }

        .title {
            font-size: 1.5rem;
            color: #ECF0F1;
            letter-spacing: 2px;
        }

        .white-text{
            color: #ECF0F1;
            padding: 20px 1px 30px 1px;
        }
        .typer-wrapper{
            padding: 30px 20px;
            background: #217C4B;
            border-radius: 4px;
        }
        .content {
            font-size: 1rem;
            color: #ECF0F1;
            &.typer-content{
                margin-left: auto;
                margin-right: auto;
                position: relative;
                overflow: hidden;
                background: #ECECEC !important;
                color: #333 !important;
                a{
                    color: #333 !important;
                    border-bottom: 1px solid #333;
                    &:hover{
                        border-bottom: 2px solid #333;
                    }
                }
                &.active {
                    text-align: left;
                    span.dollar, span.copy{
                        opacity: 1
                    }
                    span.copy{
                        right: 0;
                        &:hover{
                            i{
                                color: #1AAF5D;
                            }
                        }
                    }
                }
                span.dollar, span.copy{
                    transition: all .25s;
                    opacity: 0;
                }
                span.dollar{
                    color: #c66c66;
                }
                span.copy{
                    cursor: pointer;
                    background: rgb(236, 240, 241);
                    color: #333;
                    position: absolute;
                    right: -2.6rem;
                    top: 0;
                    padding: 0.8rem;
                }
                span{
                    font-weight: 700
                }
            }
        }

        a {
            color: #ECF0F1;
            font-weight: 700;
            transition: border-bottom .25s;
            border-bottom: 1px solid rgba(236, 240, 241, .5);

            &:hover {
                border-bottom: 1px solid rgba(236, 240, 241, 1);
            }

        }
    }

    .get-started-panel{
        .column{
            max-width: 100%;
        }

        @media screen and (max-width:768px) and (min-width:0px) {
            padding: 0;
            .get-started-content{
                padding: 0 !important;
                p.title:first-child{
                    display: none;
                }
                .small-title{
                    font-size: 2.5rem !important;
                    text-align: center;
                }
                p.content{
                    font-size: 1.3rem !important;
                }
                p.typer-content{
                    max-width: 100%;
                    span.copy{
                        display: none;
                    }
                }
                .language-buttons .column{
                    margin-right: 0;
                    border-bottom: 1px solid #333;
                    border-radius: 0;
                    &:first-child{
                        border-top: 1px solid #333;
                    }
                }
            }
            .white-text{
                font-size: 1.5rem;
                padding: 1.5rem 2.5rem;
            }
            .mobile-only-disclaimer{
                display: block;
            }
        }

        padding-top: 100px;

        .language-buttons{
            max-width: 100%;
            margin: 25px auto 20px;
            .column{
                background: rgba(47, 49, 51, .8);
                transition: all .5s;
                color: #ecf0f1;
                font-weight: 700;
                font-size: 1.125rem;
                margin-right: 30px;
                display: flex;
                justify-content: center;
                align-items: center;
                flex-direction: row;
                text-align: center;
                position: relative;
                border-radius: 4px;

                &:last-child{
                    margin-right: 0;
                }
                i{
                    font-size: 2rem;
                    padding-right: 1rem;
                    transition: color .5s;
                    &:not(.colored){
                        color: #ecf0f1;
                    }
                }
                &.active{
                    background: rgba(47, 49, 51, 1);
                }
                &.go i.colored{
                    color: #7FC6E8;
                }
            }
        }

        p.title{
            padding-bottom: 60px;
        }
        .get-started-content{
            padding: 0 140px;
            .content{
                padding: 13px 20px;
                background: #2E3032;
                border-radius: 2px;
            }
        }
    }

    .demo-panel {
        @media screen and (max-width:768px) and (min-width:0px) {
            display: none;
        }
        background: #D7E7D4;
        display: flex;
        justify-content: center;
        flex-direction: column;
        align-items: center;
        padding-top: 90px;
        padding-bottom: 45px;

        .call-to-action {
            font-size: 1.5rem;
            color: #555555;
            font-weight: 700;
            p{
                letter-spacing: 2px;
            }
        }

        .connect-button{
            margin-top: -5px;
            margin-bottom: 40px;

            a.button {
                width: auto;
                height: auto;
                padding: 20px 42px;
                background: #1E82C8;
                border-radius: 4px;
                font-size: 1rem;
                color: #ECF0F1;
                font-weight: 700;
            }
        }
    }

    .slow {
        animation-duration: 3s;
    }

    .delayed {
        animation-delay: 1s;
    }

</style>
