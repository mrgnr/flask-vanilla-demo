function toggleSubnav(subnav, open) {
  if (open) {
    subnav.classList.add("is-active");
  } else {
    subnav.classList.remove("is-active");
  }

  const toggle = subnav.querySelector(".p-subnav__toggle");

  if (toggle) {
    const dropdown = document.getElementById(
      toggle.getAttribute("aria-controls")
    );

    if (dropdown) {
      dropdown.setAttribute("aria-hidden", open ? false : true);
    }
  }
}

function closeAllSubnavs() {
  const subnavs = document.querySelectorAll(".p-subnav");
  for (var i = 0, l = subnavs.length; i < l; i++) {
    toggleSubnav(subnavs[i], false);
  }
}

function setupSubnavToggle(subnavToggle) {
  subnavToggle.addEventListener("click", function (event) {
    event.preventDefault();
    event.stopPropagation();

    const subnav = subnavToggle.parentElement;
    const isActive = subnav.classList.contains("is-active");

    closeAllSubnavs();
    if (!isActive) {
      toggleSubnav(subnav, true);
    }
  });
}

const subnavToggles = document.querySelectorAll(".p-subnav__toggle");

for (var i = 0, l = subnavToggles.length; i < l; i++) {
  setupSubnavToggle(subnavToggles[i]);
}

document.addEventListener("click", function (event) {
  const target = event.target;

  if (target.closest) {
    if (
      !target.closest(".p-subnav__toggle)" && !target.closest(".p-sub__item"))
    ) {
      closeAllSubnavs();
    }
  }
});

function initSearchResetButtons(selector) {
  var resetButtons = [].slice.call(document.querySelectorAll(selector));

  resetButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      var input = button.parentNode.querySelector("input");
      input.focus();
    });
  });
}

initSearchResetButtons(".p-search-box__reset");
