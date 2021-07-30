switchBtn = document.getElementById("switch")
jBtn = document.getElementById("japanese")
bBtn = document.getElementById("bulgarian")
mBtn = document.getElementById("music")

backBtn = document.getElementById("back")
checkBtn = document.getElementById("checkBtn")
tickBtn = document.getElementById("tick")
crossBtn = document.getElementById("cross")

switchBtn.onclick = switchDirection
jBtn.onclick = function() {categoryPressed(jBtn.id, "japanese.csv")}
bBtn.onclick = function() {categoryPressed(bBtn.id, "bulgarian.csv")}
mBtn.onclick = function() {categoryPressed(mBtn.id, "music.csv")}

backBtn.onclick = returnToLanding
checkBtn.onclick = checkAnswer
tickBtn.onclick = answerRight
crossBtn.onclick = answerWrong

var reversed = false
var selectedCat = null
var selectedSec = null
var selectedCsv = null

var tests = new Object();
var test = [];
var testItem = null;

var testSize = 0;
var wrongAnswers = 0;

function switchDirection() {
    reversed = !reversed;
    $("#switch").fadeOut(200, function() {
        $("#switch").text("Q " + (reversed ? "←" : "→") + " A");
        // $("#switch").css("transform", "rotate(" + (reversed ? "180" : "0") + "deg)");
        $("#switch").fadeIn(200);
    });
    loadSections(selectedCsv);
}

function scoreName(csvName, secName, reversed) {
    return "scores/" + csvName + "/" + secName + (reversed ? "<" : ">")
}

function categoryPressed(btnId, csvName) {
    selectedCsv = csvName;
    if (btnId == selectedCat) {
        $("#" + btnId).animate({top: "5px"}, 100);
        $("#" + btnId).animate({top: "10px"}, 100);
    } else {
        selectedCat = btnId

        $("#japanese").animate({top: "0px"}, 200);
        $("#bulgarian").animate({top: "0px"}, 200);
        $("#music").animate({top: "0px"}, 200);
        $("#" + btnId).animate({top: "10px"}, {duration: 200, queue: false});

        loadSections(csvName)
    }
}

function loadSections(csvName) {
    $(".sections").empty();
    
    $.get("data/" + csvName, function(csvData) {
        data = $.csv.toObjects(csvData);
        tests = new Object();

        var first = true;
        var currentSec = null;

        $.each(data, function(index, value) {
            if (value["name"] != null) {
                currentSec = value["name"]
                tests[currentSec] = [value];

                var score = localStorage.getItem(scoreName(csvName, currentSec, reversed));

                if (score == null) {
                    score = "-";
                } else {
                    score = parseFloat(score);
                    score = Math.min(score, 1);
                    score = Math.max(score, 0);
                    score = Math.floor(score * 100);
                }

                if (!first) {
                    $("<hr>").appendTo(".sections");
                }
                first = false;

                var btn = $("<button />", {
                    "class": "sectionBtn",
                    "text": currentSec,
                    click: function() {
                        selectedSec = value["name"]
                        $("#landing").hide();
                        $("#testing").show();
                        document.getElementById("secTitle").innerHTML = selectedSec
                        startTest();
                    }
                })
                btn.append(
                    $("<span />", {
                        "class": "sectionSpan",
                        "text": score + "%"
                    })
                )
                btn.appendTo(".sections");
            } else {
                tests[currentSec].push(value)
            }
        });
    });
}

function startTest() {
    test = tests[selectedSec];

    testSize = test.length;
    wrongAnswers = 0;
    nextQuestion();
}

function nextQuestion() {
    if (test.length == 0) {
        $("#question").text(":D");
        $("#answer").text("Learnt!");
        $("#furi").text("");

        $("#checkBtn").hide();
        $("#response").hide();

        score = testSize / (testSize + wrongAnswers)
        localStorage.setItem(scoreName(selectedCsv, selectedSec, reversed), score);
    } else {
        prevItem = testItem;

        var all_same = true;
        for (const item of test) {
            if (item["question"] != test[0]["question"]) {
                all_same = false;
            }
        }

        if (all_same) {
            itemIndex = 0;
            testItem = test[itemIndex];
        } else {
            while (testItem == prevItem) {
                itemIndex = Math.floor(Math.random()*test.length);
                testItem = test[itemIndex]
            }
        }

        test.splice(itemIndex, 1)

        var question = testItem["question"]
        var answer = testItem["answer"]

        if (reversed) {
            $("#question").text("")
            $("#answer").text(answer)
        } else {
            $("#question").text(question)
            $("#answer").text("")
        }

        $("#furi").text("")

        $("#checkBtn").show()
        $("#response").hide()
    }
}

function checkAnswer() {
    var question = testItem["question"]
    var answer = testItem["answer"]
    var furigana = testItem["furigana"] ?? ""

    if (reversed) {
        $("#question").text(question)
    } else {
        $("#answer").text(answer)
    }

    $("#furi").text(furigana)

    $("#checkBtn").hide()
    $("#response").show()
}

function answerRight() {
    nextQuestion();
}

function answerWrong() {
    wrongAnswers += 1;
    test.push(testItem);
    test.push(testItem);
    nextQuestion();
}

function returnToLanding() {
    selectedSec = null;
    $("#landing").show();
    $("#testing").hide();
    loadSections(selectedCsv);
}

$( document ).ready(function() {
});