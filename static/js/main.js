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
});
