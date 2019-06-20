
$("form").submit(function (e) { // Устанавливаем событие отправки для формы с id=form
    e.preventDefault();
    var form_data = $(this).serialize(); // Собираем все данные из формы
    $.ajax({
        type: "POST", // Метод отправки
        url: "/cmd", // Путь до php файла отправителя
        data: form_data,
        success: function (data) { // если запрос успешен вызываем функцию
            $("#alerttext").innerText=data;
            $("#toast").toast("show");
            // setTimeout(()=>$('#toast').toast("hide"),4000);
            alert(data); // добавлем текстовое содержимое в элемент с классом .myClass
        },
        error: function (data) {
            alert(data.responseText);
        }
    });
});

