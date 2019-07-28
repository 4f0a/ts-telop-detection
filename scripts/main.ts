const DROP_RESULT_URL: string = "http://127.0.0.1:8899/checkTS/data/drop.txt"
const TELOP_RESULT_URL: string = "http://127.0.0.1:8899/checkTS/data/telop.txt"

interface TSPIDErrorInfo {
	PID: string;
	In: number;
	Drop: number;
	Scrambling: number;
}

interface TSErrorInfo {
	formatError: number;
	syncError: number;
	totalDropError: number;
	totalScrambling: number;
	transportError: number;
	maxDrop: number;
	pids: TSPIDErrorInfo[];
}

interface TelopInfo {
	string: string;
	rank: number;
}

function addDrops(target: HTMLElement, completion: () => void) {
	const req = new XMLHttpRequest();
	req.open("GET", DROP_RESULT_URL, true);
	req.responseType = "json";
	req.send();
	req.onload = () => {
		if (req.response) {
			var data = req.response;
			//console.log(data)
			if ("date" in data) {
				const update = document.getElementById("update-time-drop");
				if (update) {
					update.textContent = "Drop Update: " + data["date"];
				}
			}
			if ("data" in data) {
				data = data["data"]
				const keys = Object.keys(data).sort();
				for (const key of keys) {
					if (data.hasOwnProperty(key)) {
						const element = data[key] as TSErrorInfo;
						if (element.maxDrop == null) {
							element.maxDrop = 0;
						}
						//console.log(element.maxDrop);
						const row = document.createElement("tr");
						const cellName = document.createElement("td");
						cellName.textContent = key;
						row.appendChild(cellName);
						const cellDrop = document.createElement("td");
						const dropDetailAnchor = document.createElement("a");
						dropDetailAnchor.textContent = element.totalDropError.toString() + "(" + element.maxDrop.toString() + ")";
						if (element.maxDrop > 0) {
							dropDetailAnchor.style.color = "red";
						} else if (element.totalDropError > 0) {
							dropDetailAnchor.style.color = "orange";
						}
						dropDetailAnchor.href = "#drop-detail";
						dropDetailAnchor.setAttribute("uk-toggle", "");
						dropDetailAnchor.onclick = (e: MouseEvent) => {
							if (e.target === dropDetailAnchor) {
								const detail = document.getElementById("tbody-drop-detail");
								if (detail) {
									while (detail.firstChild) {
										detail.removeChild(detail.firstChild);
									}
									element.pids.forEach((item: TSPIDErrorInfo) => {
										const ro2 = document.createElement("tr");
										const cellPID = document.createElement("td");
										cellPID.textContent = item.PID
										ro2.appendChild(cellPID);
										const cellPIDIn = document.createElement("td");
										cellPIDIn.textContent = item.In.toString();
										ro2.appendChild(cellPIDIn);
										const cellPIDDrop = document.createElement("td");
										cellPIDDrop.textContent = item.Drop.toString();
										ro2.appendChild(cellPIDDrop);
										const cellPIDScr = document.createElement("td");
										cellPIDScr.textContent = item.Scrambling.toString();
										ro2.appendChild(cellPIDScr);
										detail.appendChild(ro2);
									});
								}
								//console.log(element.pids);
							}
						};
						cellDrop.appendChild(dropDetailAnchor);
						row.appendChild(cellDrop);
						const cellTelop = document.createElement("td");
						cellTelop.textContent = "-";
						cellTelop.classList.add("cell-telop");
						row.appendChild(cellTelop);
						target.appendChild(row);
					}
				}
			}
		}
		completion();
	}
}

function addTelops(target: HTMLElement) {
	const req2 = new XMLHttpRequest();
	req2.open("GET", TELOP_RESULT_URL, true);
	req2.responseType = "json";
	req2.send();
	req2.onload = () => {
		if (req2.response) {
			var data = req2.response;
			//console.log(data)
			if ("date" in data) {
				const update = document.getElementById("update-time-telop");
				if (update) {
					update.textContent = "Telop Update: " + data["date"];
				}
			}
			if ("data" in data) {
				data = data["data"]
				const rows = Array.prototype.slice.call(target.children);
				for (const key in data) {
					if (data.hasOwnProperty(key)) {
						const dat = data[key];
						//console.log(element.maxDrop);
						var row: HTMLElement | null = null;
						for (const eachrow of rows) {
							if (eachrow.firstChild && eachrow.firstChild.textContent.toLowerCase() === key.toLowerCase()) {
								row = eachrow;
							}
						}
						var cellTelop;
						if (row == null) {
							row = document.createElement("tr");
							target.appendChild(row);
							const cellName = document.createElement("td");
							cellName.textContent = key;
							row.appendChild(cellName);
							const cellDrop = document.createElement("td");
							cellDrop.textContent = "-";
							row.appendChild(cellDrop);
							cellTelop = document.createElement("td");
							cellTelop.classList.add("cell-telop");
							row.appendChild(cellTelop);
						} else {
							cellTelop = row.querySelector(".cell-telop");
						}
						var rank = 10;
						const paths: string[] = [];
						for (const path in dat) {
							if (dat.hasOwnProperty(path)) {
								const frame = dat[path] as TelopInfo;
								if (frame.rank < rank) {
									rank = frame.rank;
								}
								paths.push(path);
							}
						}
						cellTelop.textContent = "";
						const telopDetailAnchor = document.createElement("a");
						telopDetailAnchor.textContent = rank.toString();
						if (rank === 0) {
							telopDetailAnchor.style.color = "red";
							row.style.backgroundColor = "pink";
						} else if (rank === 1) {
							telopDetailAnchor.style.color = "orange";
							row.style.backgroundColor = "#ffddbb";
						}
						telopDetailAnchor.href = "#telop-detail";
						telopDetailAnchor.setAttribute("uk-toggle", "");
						telopDetailAnchor.onclick = (e: MouseEvent) => {
							if (e.target === telopDetailAnchor) {
								const detail = document.getElementById("tbody-telop-detail");
								if (detail) {
									while (detail.firstChild) {
										detail.removeChild(detail.firstChild);
									}
									paths.sort((a: string, b: string) => {
										if(dat[a].rank < dat[b].rank) return -1;
										if(dat[a].rank > dat[b].rank) return 1;
										return 0;
									});
									paths.forEach(path => {
										const frame = dat[path] as TelopInfo;
										const ro2 = document.createElement("tr");
										const cellImg = document.createElement("td");
										cellImg.style.width = "200px";
										//const div = document.createElement("div");
										//div.setAttribute("uk-lightbox", "");
										cellImg.setAttribute("uk-lightbox", "");
										const imgAnchor = document.createElement("a");
										imgAnchor.href = path.replace(/\\/g, "/");
										const img = document.createElement("img");
										img.src = imgAnchor.href;
										imgAnchor.appendChild(img);
										//div.appendChild(imgAnchor);
										cellImg.appendChild(imgAnchor);
										ro2.appendChild(cellImg);
										const cellStr = document.createElement("td");
										cellStr.textContent = frame.string;
										if (frame.rank === 0) {
											cellStr.style.color = "red";
										} else if (frame.rank === 1) {
											cellStr.style.color = "orange";
										}
										cellStr.style.wordBreak = "break-all"
										ro2.appendChild(cellStr);
										detail.appendChild(ro2);
									});
								}
								//console.log(element.pids);
							}
						};
						cellTelop.appendChild(telopDetailAnchor);
					}
				}
			}
		}
	}
}

const tbody = document.getElementById("tbody-main");
if (tbody) {
	addDrops(tbody, () => {
		addTelops(tbody);
	});
}
