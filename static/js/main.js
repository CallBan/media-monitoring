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

    // Валидация
    if (document.getElementById("sources").selectedOptions.length === 0) {
        sourcesError.style.display = "block";
        isValid = false;
    }
    if (!datePicker.input.value.trim()) {
        dateRangeError.style.display = "block";
        isValid = false;
    }

    if (!isValid) {
        e.preventDefault();
        return;
    }

    // Показываем элементы
    loader.classList.remove("loader-hidden");
    document.getElementById("progress-container").classList.add("show");
    document.getElementById("status").classList.add("show");

    // Очищаем предыдущие результаты
    document.getElementById("results").innerHTML = "";
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

// Обработка сжатия списка документов
function toggleSection(id) {
  const section = document.getElementById("section-" + id);
  if (section.style.display === "none") {
    section.style.display = "block";
  } else {
    section.style.display = "none";
  }
}

// Связь сервер-фронт, статус бар о работе парсера
const eventSource = new EventSource("/stream");

        eventSource.onmessage = function(e) {
            const data = JSON.parse(e.data);

            // Обновляем основные поля

            totalSources = data.len_sources;

            // Обновляем прогресс-бар и статус
            if (data.idx !== undefined && totalSources > 0) {
                const progress = Math.round((data.idx / totalSources) * 100);
                document.getElementById('progress-bar').style.width = `${progress}%`;
                document.getElementById('progress-bar').textContent = `${progress}%`;

                // Добавляем анимацию при изменении прогресса
                document.getElementById('progress-bar').classList.add('animate');
                setTimeout(() => {
                    document.getElementById('progress-bar').classList.remove('animate');
                }, 500);

                document.getElementById('status').textContent =
                    `Обработка ${data.name} ${data.idx} из ${totalSources} (${progress}%)`;
            }
        };

        eventSource.onerror = function() {
            eventSource.close();
            document.getElementById('status').textContent = "Соединение закрыто";
            document.getElementById('progress-bar').style.backgroundColor = "#e74c3c";
        };