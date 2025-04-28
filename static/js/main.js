document.addEventListener("DOMContentLoaded", function () {
  // Инициализация Choices для мультиселекта
  const sourcesSelect = new Choices("#sources", {
    removeItemButton: true,
    placeholder: true,
    placeholderValue: "Выберите источники",
    noChoicesText: "Нет доступных вариантов",
    itemSelectText: "Нажмите для выбора",
  });

  // Инициализация flatpickr с русской локализацией и ограничениями
  const datePicker = flatpickr("#dateRange", {
    mode: "range",
    dateFormat: "Y-m-d",
    locale: "ru",
    maxDate: "today",
  });

  const form = document.getElementById("searchForm");
  const sourcesError = document.getElementById("sources-error");
  const dateRangeError = document.getElementById("dateRange-error");
  const loader = document.getElementById("loader");

  // Обработчик отправки формы
  form.addEventListener("submit", function (e) {
    let isValid = true;

    // Валидация источников
    if (document.getElementById("sources").selectedOptions.length === 0) {
      sourcesError.style.display = "block";
      isValid = false;
    }

    // Валидация дат
    if (!datePicker.input.value.trim()) {
      dateRangeError.style.display = "block";
      isValid = false;
    } 

    if (!isValid) {
      e.preventDefault();
      return; // Прекращаем выполнение если форма не валидна
    }

    loader.classList.remove("loader-hidden");
    console.log('hahaha')
  });

  // Сброс ошибок при изменении полей
  document.getElementById("sources").addEventListener("change", function () {
    sourcesError.style.display = "none";
  });

  datePicker.input.addEventListener("input", function () {
    dateRangeError.style.display = "none";
  });

  window.addEventListener("load", function () {
    loader.classList.add("loader-hidden");
  });
});
