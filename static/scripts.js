$(document).ready(function() {
    $(".expand-icon").on("click", function() {
        var recipe = $(this).closest('.recipe');
        recipe.css("max-height", "none");
        recipe.find(".expand-icon").css("display", "none");
        recipe.find(".close-icon").css("display", "block");
        recipe.find("p:last-child").css("display", "block");
    });

    $(".close-icon").on("click", function() {
        var recipe = $(this).closest('.recipe');
        recipe.css("max-height", "400px");
        recipe.find(".expand-icon").css("display", "block");
        recipe.find(".close-icon").css("display", "none");
        recipe.find("p:last-child").css("display", "none");
    });
});



document.querySelectorAll('.recipe').forEach(function(recipe) {
    var expandIcon = recipe.querySelector('.expand-icon');
    var closeIcon = recipe.querySelector('.close-icon');
    var fullText = recipe.querySelector('p:last-child');

    expandIcon.addEventListener('click', function() {
        fullText.style.display = 'block';
        expandIcon.style.display = 'none';
        closeIcon.style.display = 'block';
    });

    closeIcon.addEventListener('click', function() {
        fullText.style.display = 'none';
        expandIcon.style.display = 'block';
        closeIcon.style.display = 'none';
    });
});
