// START CHANGE-ME
// TODO: Figure out a way to do seperate this data to a different file without causing CORS issues
const VERSION = 415;
const UPDATE_DATE = "2023-02-04";
const UPDATE_ITEMS = [
  "Cleaned up code and removed some unused functions.",
  "IF THERE ARE MALFUNCTIONS, please use !dev.",
];
// END CHANGE-ME

function changelog() {
  animateNumericalValue(
    document.getElementById("version-value"),
    0,
    VERSION,
    750
  );
  document.getElementById("update-date").innerText = UPDATE_DATE;
  const update_list_container = document.getElementById(
    "update-list-container"
  );
  const update_ul = document.getElementById("update-list");
  UPDATE_ITEMS.forEach(function (value) {
    let update_li = document.createElement("li");
    update_li.className = "update-item";
    update_li.innerHTML = value;
    update_ul.appendChild(update_li);
  });
  const ul_height = update_ul.clientHeight;
  const animation_speed_ms = Math.round(1.1 * (ul_height / 10) * 1000);
  if (update_list_container.clientHeight < ul_height) {
    update_ul.classList.add("anim-list-scroll");
    //Roughly good speed, tested on 2 rows vs 10 rows
    update_ul.style.animationDuration = `${animation_speed_ms}ms`;
  }
  update_loop(animation_speed_ms);
}

changelog();
