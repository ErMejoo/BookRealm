function getCSRFToken() {
    return document.cookie.split('; ')
        .find(row => row.startsWith('csrftoken'))
        .split('=')[1];
}

$(document).ready(function(){
    $("#wishlist-btn").click(function(){
        let button = $(this);
        let bookId = button.data("book-id");

        let isInWishlist = button.text().includes("Remove");
        let url = isInWishlist 
            ? `/wishlist/remove/${bookId}/`
            : `/wishlist/add/${bookId}/`;

        $.ajax({
            url: url,
            type: "POST",
            headers: {
                "X-CSRFToken": getCSRFToken(),
                "X-Requested-With": "XMLHttpRequest"
            },
            success: function(response){
                if(response.status === "added"){
                    button.html('<i class="bi bi-bookmark-check me-1"></i>Remove from Reading List')
                          .removeClass("rr-btn-red")
                          .addClass("rr-btn-outline");
                }
                else if(response.status === "removed"){
                    button.html('<i class="bi bi-bookmark-plus me-1"></i>Add to Reading List')
                          .removeClass("rr-btn-outline")
                          .addClass("rr-btn-red");
                }
            },
            error: function(){
                alert("Something went wrong. Please try again.");
            }
        });
    });
});

$(document).ready(function(){
    $(".btn-remove-wishlist").click(function(){
        let button = $(this);
        let bookId = button.data("book-id");

        $.ajax({
            url: `/wishlist/remove/${bookId}/`,
            type: "POST",
            headers: {
                "X-CSRFToken": getCSRFToken(),
                "X-Requested-With": "XMLHttpRequest"
            },
            success: function(response){
                if(response.status === "removed"){
                    $("#wishlist-item-" + bookId).fadeOut(300, function(){ $(this).remove(); });

                    if($(".wishlist-item").length === 0){
                        $("section.px-4.py-5").html(`
                            <div class="text-center py-5">
                                <i class="bi bi-bookmark text-secondary" style="font-size: 3rem;"></i>
                                <p class="text-secondary mt-3">Your reading list is empty.</p>
                                <a href="{% url 'BookRealm:home' %}" class="btn rr-btn-red px-4 mt-2">Discover Books</a>
                            </div>
                        `);
                    }
                }
            },
            error: function(){
                alert("Could not remove the book. Please try again.");
            }
        });
    });
});