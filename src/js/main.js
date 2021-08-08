jBtn = document.getElementById("japanese")
bBtn = document.getElementById("bulgarian")
mBtn = document.getElementById("music")

backBtn = document.getElementById("back")
checkBtn = document.getElementById("checkBtn")
tickBtn = document.getElementById("tick")
crossBtn = document.getElementById("cross")

jBtn.onclick = function() {categoryPressed(jBtn.id, ["japanese.csv", "j6000.csv"])}
bBtn.onclick = function() {categoryPressed(bBtn.id, ["bulgarian.csv"])}
mBtn.onclick = function() {categoryPressed(mBtn.id, ["music.csv"])}

backBtn.onclick = returnToLanding
checkBtn.onclick = checkAnswer
tickBtn.onclick = answerRight
crossBtn.onclick = answerWrong

var reversed = false;
var selectedCat = null;
var selectedSec = null;
var selectedCsv = null;
var selectedCsvs = null;

var tests = new Object();
var test = [];
var testItem = null;

var testSize = 0;
var wrongAnswers = 0;

var scrollPos = 0;

function scoreName(csvName, secName, reversed) {
    return "scores/" + csvName + "/" + secName + (reversed ? "<" : ">")
}

function dateName(csvName, secName, reversed) {
    return "scores/" + csvName + "/" + secName + (reversed ? "<" : ">") + "day"
}

function categoryPressed(btnId, csvNames) {
    scrollPos = $(window).scrollTop()
    selectedCsvs = csvNames;
    if (btnId == selectedCat) {
        $("#" + btnId).animate({top: "5px"}, 100);
        $("#" + btnId).animate({top: "10px"}, 100);
    } else {
        selectedCat = btnId

        $("#japanese").animate({top: "0px"}, 200);
        $("#bulgarian").animate({top: "0px"}, 200);
        $("#music").animate({top: "0px"}, 200);
        $("#" + btnId).animate({top: "10px"}, {duration: 200, queue: false});

        loadSections(csvNames)
    }
}

function parseScore(score) {
    if (score == null) {
        score = "-";
    } else {
        score = parseFloat(score);
        score = Math.floor(score * 100) + "%";
    }

    return score
}

function getDateDiff(date) {
    var diff = "";
    if (date != null) {
        diff = "Day " + Math.floor((new Date() - new Date(date)) / (1000 * 3600 * 24));
    }

    return diff
}

function loadSections(csvNames) {
    $(".sections").empty();
    
    tests = new Object();

    var first = true;
    var currentSec = null;

    $.each(csvNames, function(index, csvName) {
        $.get("data/" + csvName, function(csvData) {
            data = $.csv.toObjects(csvData);

            $.each(data, function(index, value) {
                if (value["name"] != null) {
                    currentSec = value["name"]
                    tests[currentSec] = [value];

                    var scoreA = parseScore(localStorage.getItem(scoreName(csvName, currentSec, true)));
                    var scoreB = parseScore(localStorage.getItem(scoreName(csvName, currentSec, false)));
                    
                    var diffA = getDateDiff(localStorage.getItem(dateName(csvName, currentSec, true)));
                    var diffB = getDateDiff(localStorage.getItem(dateName(csvName, currentSec, false)));

                    if (!first) {
                        $("<hr>").appendTo(".sections");
                    }
                    first = false;

                    var sectionDiv = $("<div />", {
                        "class": "sectionDiv",
                    });

                    leftBtn = $("<button />", {
                        "class": "sectionBtn",
                        "text": scoreA,
                        click: function() {
                            selectedCsv = csvName;
                            selectedSec = value["name"]
                            reversed = true;
                            startTest();
                        }
                    });

                    leftBtn.append(
                        $("<span />", {
                            "class": "daySpan",
                            "text": diffA
                        })
                    );

                    sectionDiv.append(leftBtn);

                    sectionDiv.append(
                        $("<span />", {
                            "class": "sectionSpan",
                            "text": currentSec
                        }
                    ));

                    rightBtn = $("<button />", {
                        "class": "sectionBtn",
                        css : {
                            "text-align": "right"
                        },
                        click: function() {
                            selectedCsv = csvName;
                            selectedSec = value["name"]
                            reversed = false;
                            startTest();
                        }
                    });

                    rightBtn.append(
                        $("<span />", {
                            "class": "daySpan",
                            "text": diffB
                        })
                    );
                    
                    rightBtn.append(
                        $("<span />", {
                            "text": scoreB
                        })
                    );

                    sectionDiv.append(rightBtn);

                    sectionDiv.appendTo(".sections").ready(
                        function() {
                            $(window).scrollTop(scrollPos);
                            console.log(scrollPos, $(window).scrollTop());
                        }
                    );
                } else {
                    tests[currentSec].push(value)
                }
            });
        });
    });
}

function startTest() {
    scrollPos = $(window).scrollTop()
    console.log(scrollPos)
    $("#landing").hide();
    $("#testing").show();
    document.getElementById("secTitle").innerHTML = selectedSec

	if (reversed) {
        test = [];
        for (var testItem of tests[selectedSec]) {
            answers = testItem["answer"].split(", ");
            furis =  testItem["furi"].split(", ");
            for (var i = 0; i < answers.length; i++) {
                test.push({
                    "question": testItem["question"],
                    "answer": answers[i],
                    "furi": furis[i]
                });
            }
        }
    } else {
        test = tests[selectedSec];
    }

    testSize = test.length;
    wrongAnswers = 0;
    nextQuestion();
}

function nextQuestion() {
    if (test.length == 0) {
        $("#question").text(":D");
        $("#answer").text("Learnt!");

        $("#checkBtn").hide();
        $("#response").hide();

        score = testSize / (testSize + wrongAnswers)
        localStorage.setItem(scoreName(selectedCsv, selectedSec, reversed), score);

        var today = new Date();
        var dd = String(today.getDate()).padStart(2, "0");
        var mm = String(today.getMonth() + 1).padStart(2, "0"); //January is 0!
        var yyyy = today.getFullYear();

        today = mm + "/" + dd + "/" + yyyy;

        localStorage.setItem(dateName(selectedCsv, selectedSec, reversed), today);
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

        $("#checkBtn").show()
        $("#response").hide()
    }
}

function checkAnswer() {
    var question = testItem["question"]
    var answer = testItem["answer"]
    var furigana = testItem["furi"] ?? answer

    if (furigana == "") {
        furigana = answer
    }

    if (reversed) {
        $("#question").text(question)
    }

    $("#answer").html(furigana)

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
    loadSections(selectedCsvs);
}

$( document ).ready(function() {
});