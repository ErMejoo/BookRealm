$(document).ready(function() {
    $('#follow-btn').click(function(e) {
        e.preventDefault();
        let $btn = $(this);
        let userId = $btn.data('user-id');
        let isFollowing = $btn.hasClass('rr-btn-outline');
        let url = isFollowing
            ? `/unfollow/${userId}/`
            : `/follow/${userId}/`;

        $.ajax({type: "POST",
            url: url,
            headers: {'X-CSRFToken': $('meta[name="csrf-token"]').attr('content')},
            success: function(response) {
                if (isFollowing) {
                    $btn.removeClass('rr-btn-outline').addClass('rr-btn-red');
                    $btn.html('<i class="bi bi-person-plus me-1"></i>Follow Author');
                } else {
                    $btn.removeClass('rr-btn-red').addClass('rr-btn-outline');
                    $btn.html('<i class="bi bi-person-dash me-1"></i>Unfollow');
                }
            },
            error: function() {
                alert('Error processing request. Please try again.');
            }
        });
    });
});