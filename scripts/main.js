"use strict";
var DROP_RESULT_URL = "http://127.0.0.1:8899/checkTS/data/drop.txt";
var TELOP_RESULT_URL = "http://127.0.0.1:8899/checkTS/data/telop.txt";
function addDrops(target, completion) {
    var req = new XMLHttpRequest();
    req.open("GET", DROP_RESULT_URL, true);
    req.responseType = "json";
    req.send();
    req.onload = function () {
        if (req.response) {
            var data = req.response;
            //console.log(data)
            if ("date" in data) {
                var update = document.getElementById("update-time-drop");
                if (update) {
                    update.textContent = "Drop Update: " + data["date"];
                }
            }
            if ("data" in data) {
                data = data["data"];
                var keys = Object.keys(data).sort();
                var _loop_1 = function (key) {
                    if (data.hasOwnProperty(key)) {
                        var element_1 = data[key];
                        if (element_1.maxDrop == null) {
                            element_1.maxDrop = 0;
                        }
                        //console.log(element.maxDrop);
                        var row = document.createElement("tr");
                        var cellName = document.createElement("td");
                        cellName.textContent = key;
                        row.appendChild(cellName);
                        var cellDrop = document.createElement("td");
                        var dropDetailAnchor_1 = document.createElement("a");
                        dropDetailAnchor_1.textContent = element_1.totalDropError.toString() + "(" + element_1.maxDrop.toString() + ")";
                        if (element_1.maxDrop > 0) {
                            dropDetailAnchor_1.style.color = "red";
                        }
                        else if (element_1.totalDropError > 0) {
                            dropDetailAnchor_1.style.color = "orange";
                        }
                        dropDetailAnchor_1.href = "#drop-detail";
                        dropDetailAnchor_1.setAttribute("uk-toggle", "");
                        dropDetailAnchor_1.onclick = function (e) {
                            if (e.target === dropDetailAnchor_1) {
                                var detail_1 = document.getElementById("tbody-drop-detail");
                                if (detail_1) {
                                    while (detail_1.firstChild) {
                                        detail_1.removeChild(detail_1.firstChild);
                                    }
                                    element_1.pids.forEach(function (item) {
                                        var ro2 = document.createElement("tr");
                                        var cellPID = document.createElement("td");
                                        cellPID.textContent = item.PID;
                                        ro2.appendChild(cellPID);
                                        var cellPIDIn = document.createElement("td");
                                        cellPIDIn.textContent = item.In.toString();
                                        ro2.appendChild(cellPIDIn);
                                        var cellPIDDrop = document.createElement("td");
                                        cellPIDDrop.textContent = item.Drop.toString();
                                        ro2.appendChild(cellPIDDrop);
                                        var cellPIDScr = document.createElement("td");
                                        cellPIDScr.textContent = item.Scrambling.toString();
                                        ro2.appendChild(cellPIDScr);
                                        detail_1.appendChild(ro2);
                                    });
                                }
                                //console.log(element.pids);
                            }
                        };
                        cellDrop.appendChild(dropDetailAnchor_1);
                        row.appendChild(cellDrop);
                        var cellTelop = document.createElement("td");
                        cellTelop.textContent = "-";
                        cellTelop.classList.add("cell-telop");
                        row.appendChild(cellTelop);
                        target.appendChild(row);
                    }
                };
                for (var _i = 0, keys_1 = keys; _i < keys_1.length; _i++) {
                    var key = keys_1[_i];
                    _loop_1(key);
                }
            }
        }
        completion();
    };
}
function addTelops(target) {
    var req2 = new XMLHttpRequest();
    req2.open("GET", TELOP_RESULT_URL, true);
    req2.responseType = "json";
    req2.send();
    req2.onload = function () {
        if (req2.response) {
            var data = req2.response;
            //console.log(data)
            if ("date" in data) {
                var update = document.getElementById("update-time-telop");
                if (update) {
                    update.textContent = "Telop Update: " + data["date"];
                }
            }
            if ("data" in data) {
                data = data["data"];
                var rows = Array.prototype.slice.call(target.children);
                var _loop_2 = function (key) {
                    if (data.hasOwnProperty(key)) {
                        var dat_1 = data[key];
                        //console.log(element.maxDrop);
                        row = null;
                        for (var _i = 0, rows_1 = rows; _i < rows_1.length; _i++) {
                            var eachrow = rows_1[_i];
                            if (eachrow.firstChild && eachrow.firstChild.textContent.toLowerCase() === key.toLowerCase()) {
                                row = eachrow;
                            }
                        }
                        if (row == null) {
                            row = document.createElement("tr");
                            target.appendChild(row);
                            var cellName = document.createElement("td");
                            cellName.textContent = key;
                            row.appendChild(cellName);
                            var cellDrop = document.createElement("td");
                            cellDrop.textContent = "-";
                            row.appendChild(cellDrop);
                            cellTelop = document.createElement("td");
                            cellTelop.classList.add("cell-telop");
                            row.appendChild(cellTelop);
                        }
                        else {
                            cellTelop = row.querySelector(".cell-telop");
                        }
                        rank = 10;
                        var paths_1 = [];
                        for (var path in dat_1) {
                            if (dat_1.hasOwnProperty(path)) {
                                var frame = dat_1[path];
                                if (frame.rank < rank) {
                                    rank = frame.rank;
                                }
                                paths_1.push(path);
                            }
                        }
                        cellTelop.textContent = "";
                        var telopDetailAnchor_1 = document.createElement("a");
                        telopDetailAnchor_1.textContent = rank.toString();
                        if (rank === 0) {
                            telopDetailAnchor_1.style.color = "red";
                            row.style.backgroundColor = "pink";
                        }
                        else if (rank === 1) {
                            telopDetailAnchor_1.style.color = "orange";
                            row.style.backgroundColor = "#ffddbb";
                        }
                        telopDetailAnchor_1.href = "#telop-detail";
                        telopDetailAnchor_1.setAttribute("uk-toggle", "");
                        telopDetailAnchor_1.onclick = function (e) {
                            if (e.target === telopDetailAnchor_1) {
                                var detail_2 = document.getElementById("tbody-telop-detail");
                                if (detail_2) {
                                    while (detail_2.firstChild) {
                                        detail_2.removeChild(detail_2.firstChild);
                                    }
                                    paths_1.sort(function (a, b) {
                                        if (dat_1[a].rank < dat_1[b].rank)
                                            return -1;
                                        if (dat_1[a].rank > dat_1[b].rank)
                                            return 1;
                                        return 0;
                                    });
                                    paths_1.forEach(function (path) {
                                        var frame = dat_1[path];
                                        var ro2 = document.createElement("tr");
                                        var cellImg = document.createElement("td");
                                        cellImg.style.width = "200px";
                                        //const div = document.createElement("div");
                                        //div.setAttribute("uk-lightbox", "");
                                        cellImg.setAttribute("uk-lightbox", "");
                                        var imgAnchor = document.createElement("a");
                                        imgAnchor.href = path.replace(/\\/g, "/");
                                        var img = document.createElement("img");
                                        img.src = imgAnchor.href;
                                        imgAnchor.appendChild(img);
                                        //div.appendChild(imgAnchor);
                                        cellImg.appendChild(imgAnchor);
                                        ro2.appendChild(cellImg);
                                        var cellStr = document.createElement("td");
                                        cellStr.textContent = frame.string;
                                        if (frame.rank === 0) {
                                            cellStr.style.color = "red";
                                        }
                                        else if (frame.rank === 1) {
                                            cellStr.style.color = "orange";
                                        }
                                        cellStr.style.wordBreak = "break-all";
                                        ro2.appendChild(cellStr);
                                        detail_2.appendChild(ro2);
                                    });
                                }
                                //console.log(element.pids);
                            }
                        };
                        cellTelop.appendChild(telopDetailAnchor_1);
                    }
                };
                var row, cellTelop, rank;
                for (var key in data) {
                    _loop_2(key);
                }
            }
        }
    };
}
var tbody = document.getElementById("tbody-main");
if (tbody) {
    addDrops(tbody, function () {
        addTelops(tbody);
    });
}
//# sourceMappingURL=main.js.map