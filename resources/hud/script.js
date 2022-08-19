function get_random_id() {
  // Don't use this for cryptography :)
  return `${Date.now()}${Math.random()}`;
}
function type_writer(message, element) {
  /*
    TODO: Recode with `window.requestAnimationFrame()`
    https://developer.mozilla.org/en-US/docs/Web/API/window/requestAnimationFrame
  */
  speed = 400 / message.length;
  let i = 0;
  function _type_writer() {
    if (i < message.length) {
      element.innerHTML += message.charAt(i);
      i++;
      setTimeout(_type_writer, speed);
    }
  }
  _type_writer();
}

function add_pie_timer(parent, time) {
  // In tests, not very accurate if time below 1.
  // Increase interval_amount to allow lower, more accurate times
  // at the cost of smoother animation.
  const xmlns = "http://www.w3.org/2000/svg";

  const interval_amount = 1.5;
  const total_iterations = 360 / interval_amount;
  const time_ms = time * 1000;
  // We want total_iterations to take time_ms, so we should
  const fps = time_ms / total_iterations;
  console.log(fps);
  let timer_container = document.createElementNS(xmlns, "svg");
  let timer_child = document.createElementNS(xmlns, "path");
  timer_child.setAttribute("fill", "white");
  timer_container.appendChild(timer_child);
  parent.appendChild(timer_container);

  const size = 30;
  timer_container.setAttribute("width", size);
  timer_container.setAttribute("height", size);

  let theta = 0;
  let radius = size / 2;
  timer_child.setAttribute(
    "transform",
    "translate(" + radius + "," + radius + ")"
  );
  /*
    TODO: Recode with `window.requestAnimationFrame()`
    https://developer.mozilla.org/en-US/docs/Web/API/window/requestAnimationFrame
  */
  (function animate() {
    let not_last = true;
    if (theta < 360) {
      theta += interval_amount;
    } else {
      theta = 359.999;
      not_last = false;
    }
    let x = Math.sin((theta * Math.PI) / 180) * radius;
    let y = Math.cos((theta * Math.PI) / 180) * -radius;
    let d =
      "M0,0 v" +
      -radius +
      "A" +
      radius +
      "," +
      radius +
      " 1 " +
      (theta > 180 ? 1 : 0) +
      ",1 " +
      x +
      "," +
      y +
      "z";
    timer_child.setAttribute("d", d);
    if (not_last) {
      setTimeout(animate, fps);
    }
  })();
}

function show_ping(message) {
  const id = get_random_id();

  let ping_text = document.createElement("div");
  ping_text.className = "default-type";
  // ping_text.innerText = message;
  ping_text.id = `ping-text-${id}`;

  let ping_container = document.createElement("div");
  ping_container.className = "big-popup-container anim-ping-popup";
  ping_container.id = `ping-container-${id}`;
  ping_container.appendChild(ping_text);

  const main_container = document.getElementById("flex-main-container");
  main_container.appendChild(ping_container);
  type_writer(message, ping_text);
  setTimeout(function () {
    ping_text.classList.add("anim-action-blink");
    var audio = new Audio("autoaimon.mp3");
    audio.play();
    setTimeout(function () {
      ping_container.classList.add("anim-shrink-fade");
      setTimeout(function () {
        ping_container.remove();
      }, 600);
    }, 2000);
  }, 500);
}

function show_timed_popup(message, time) {
  const id = get_random_id();

  let ping_text = document.createElement("div");
  ping_text.className = "default-type";
  ping_text.id = `ping-text-${id}`;

  let ping_row = document.createElement("div");
  ping_row.className = "popup-row";
  ping_row.id = `ping-row-${id}`;
  ping_row.appendChild(ping_text);

  let ping_container = document.createElement("div");
  ping_container.className = "big-popup-container anim-ping-popup";
  ping_container.id = `ping-container-${id}`;
  ping_container.appendChild(ping_row);

  const main_container = document.getElementById("flex-main-container");
  main_container.appendChild(ping_container);

  type_writer(message, ping_text);

  add_pie_timer(ping_row, time);

  const fade_in_time = 500;
  const fade_out_time = 200;
  setTimeout(function () {
    ping_text.classList.add("anim-action-blink");
    setTimeout(function () {
      ping_container.classList.add("anim-quick-shrink-up-fade");
      setTimeout(function () {
        ping_container.remove();
      }, fade_out_time);
    }, time * 1000 - fade_in_time);
  }, fade_in_time);
}

function activate_hud_error(show_error) {
  let visibility = show_error ? "visible" : "hidden";
  document.getElementById("system-error").style.visibility = visibility;
  document.getElementById("hud-connection-loss").style.visibility = visibility;
  if (show_error) {
    document.getElementById("hw-stats-cpu-temp-value").innerText = "ERR";
    document.getElementById("hw-stats-cpu-load-value").innerText = "ERR";
  }
}

function animateNumericalValue(obj, start, end, duration) {
  // https://css-tricks.com/animating-number-counters/
  let startTimestamp = null;
  const step = (timestamp) => {
    if (!startTimestamp) startTimestamp = timestamp;
    const progress = Math.min((timestamp - startTimestamp) / duration, 1);
    const current_val = Math.floor(progress * (end - start) + start);
    const current_val_padded = current_val.toString().padStart(2, "0"); // Leading zero if single digit
    obj.innerHTML = current_val_padded;
    if (progress < 1) {
      window.requestAnimationFrame(step);
    }
  };
  window.requestAnimationFrame(step);
}

function update_hw_stat(obj, new_hw_stat) {
  const new_hw_val_unrounded = parseFloat(new_hw_stat);
  if (isNaN(new_hw_val_unrounded)) {
    console.error(`Unparseable Value: ${new_hw_stat}`);
    obj.innerText = "ERR";
    return;
  }
  const new_hw_val = Math.round(new_hw_val_unrounded);
  const old_hw_stat = obj.innerText;
  let old_hw_val = parseInt(old_hw_stat);
  old_hw_val = isNaN(old_hw_val) ? 0 : old_hw_val;

  const animation_speed = old_hw_val == 0 ? 750 : 250;

  animateNumericalValue(obj, old_hw_val, new_hw_val, animation_speed);
}

function update_hw_stats(data) {
  let temperature_obj = document.getElementById("hw-stats-cpu-temp-value");
  let load_obj = document.getElementById("hw-stats-cpu-load-value");

  // try {
  //   data_obj = JSON.parse(data);
  // } catch {
  //   console.error(`[HW Stats] Unable to parse JSON data: ${data}`);
  //   temperature_obj.innerText = "ERR";
  //   load_obj.innerText = "ERR";
  //   return;
  // }

  data_obj = data;

  update_hw_stat(temperature_obj, data_obj.cpu_temp ?? null);
  update_hw_stat(load_obj, data_obj.cpu_load ?? null);
}

function connect() {
  let socket = new WebSocket("ws://127.0.0.1:8080");
  let connection_established = false;
  socket.onopen = function (e) {
    console.log("[WS] Connection established");
    connection_established = true;
    activate_hud_error(false);
    setTimeout(function () {
      // sanity
      activate_hud_error(false);
    }, 500);
  };

  socket.onmessage = function (event) {
    console.log(`[WS] Data received from server: ${event.data}`);
    if (event.data == "ping") {
      show_ping("PING RECEIVED");
      return true;
    }
    // Try to json parse, return on fail
    try {
      message_obj = JSON.parse(event.data);
    } catch {
      console.error(`[WS] Unable to parse JSON data: ${event.data}`);
      return false;
    }

    /*Handle actions per message type*/
    let message_data = message_obj["value"];
    switch (message_obj["type"]) {
      case "temp_log": {
        update_temp_log(message_data["cpu"], message_data["gpu"]);
        break;
      }
      case "timed_message": {
        show_timed_popup(
          message_data["message"],
          message_data["seconds"] / 1000
        );
        break;
      }
      case "system_monitor_update": {
        update_hw_stats(message_data["data"]);
        break;
      }

      default:
        console.error(`[WS] Unknown message type: ${event.data}`);
        break;
    }
  };

  socket.onclose = function (event) {
    if (event.wasClean) {
      console.log(
        `[WS] Connection closed cleanly, code=${event.code} reason=${event.reason}`
      );
    } else {
      if (connection_established) {
        console.log("[WS] Connection died");
      } else {
        console.log("[WS] Failed to connect, retrying...");
      }
    }
    activate_hud_error(true);
    setTimeout(function () {
      connect();
    }, 250);
  };

  socket.onerror = function (error) {
    if (connection_established) {
      console.log(`[WS] ${error.message}`);
    }
  };
}

function clock() {
  const epoch = new Date("2021-03-27 00:00:00");
  const seconds_to_days_multiplier = 1000 * 3600 * 24;
  setInterval(function () {
    const current_datetime = new Date();
    const am_pm = current_datetime.getHours() <= 11 ? "AM" : "PM";
    const modulo_hour = current_datetime.getHours() % 12;
    const hour_twelve = (modulo_hour == 0 ? 12 : modulo_hour)
      .toString()
      .padStart(2, "0");
    const minutes = current_datetime.getMinutes().toString().padStart(2, "0");
    const seconds = current_datetime.getSeconds().toString().padStart(2, "0");
    const time_str = `${hour_twelve}:${minutes}:${seconds} ${am_pm}`;
    const day = Math.floor(
      (current_datetime - epoch) / seconds_to_days_multiplier
    )
      .toString()
      .padStart(3, "0");
    document.getElementById("clock-text").innerText = time_str;
    document.getElementById("date-value").innerText = day;
  }, 1000);
}

function update_loop(animation_speed_ms) {
  const fade_in_time = 300;
  const couple_loops_time = animation_speed_ms * 3 - fade_in_time;
  const hidden_time = animation_speed_ms * 5; // 12 = A 15-second changelog stays hidden for 3 minutes
  const update_container = document.getElementById("update-container");
  const help_container = document.getElementById("help-container");
  function core() {
    setTimeout(function () {
      console.log("[CHANGELOG] Done grow, removing");
      update_container.classList.remove("anim-grow");
      setTimeout(function () {
        console.log("[CHANGELOG] Started shrink");
        update_container.classList.add("anim-shrink");
        help_container.classList.remove("anim-shrink");
        help_container.classList.add("anim-grow");
        setTimeout(function () {
          console.log("[CHANGELOG] Removing shrink, adding grow");
          help_container.classList.remove("anim-grow");
          help_container.classList.add("anim-shrink");
          update_container.classList.remove("anim-shrink");
          update_container.classList.add("anim-grow");
        }, hidden_time);
      }, couple_loops_time);
    }, fade_in_time);
  }
  core();
  setInterval(function () {
    console.log(
      "[CHANGELOG] Loop complete, changelog visible, queueing shrink for later"
    );
    core();
  }, fade_in_time + couple_loops_time + hidden_time);
}

function changelog() {
  // START CHANGE-ME
  const VERSION = 411;
  const UPDATE_DATE = "2022-08-19";
  const UPDATE_ITEMS = [
    "Added HUD core",
    "Replaced some OBS elements with HUD elements",
    "Upgraded hardware monitoring system",
  ];
  // END CHANGE-ME
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

function main() {
  clock();
  connect();
  changelog();
}
main();
