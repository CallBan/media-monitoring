document.addEventListener("DOMContentLoaded", function () {
  const choices = new Choices("#sources", {
    removeItemButton: true, // Показывает кнопки для удаления выбранных элементов
    placeholder: true, // Включает placeholder
    placeholderValue: "Выберите источники", // Текст placeholder
    noChoicesText: "Нет доступных вариантов", // Текст при отсутствии вариантов
    itemSelectText: "Нажмите для выбора", // Подсказка при наведении
  });

  flatpickr("#dateRange", {
    mode: "range",
    dateFormat: "Y-m-d",
    locale: "ru",
  });

  const form = document.getElementById("searchForm");

  form.addEventListener("submit", function (e) {
    let isValid = true;

    // Проверка источников
    const sources = document.getElementById("sources");
    const sourcesError = document.getElementById("sources-error");
    if (sources.selectedOptions.length === 0) {
      sourcesError.style.display = "block";
      isValid = false;
    } else {
      sourcesError.style.display = "none";
    }

    // Проверка периода
    const dateRange = document.getElementById("dateRange");
    const dateRangeError = document.getElementById("dateRange-error");
    if (!dateRange.value.trim()) {
      dateRangeError.style.display = "block";
      isValid = false;
    } else {
      dateRangeError.style.display = "none";
    }
  });

  // Убираем сообщения об ошибках при изменении полей
  document.getElementById("sources").addEventListener("change", function () {
    document.getElementById("sources-error").style.display = "none";
  });

  document.getElementById("dateRange").addEventListener("input", function () {
    document.getElementById("dateRange-error").style.display = "none";
  });
});
