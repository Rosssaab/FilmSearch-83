document.addEventListener('DOMContentLoaded', function() {
    var searchForm = document.getElementById('searchForm');
    var searchResults = document.getElementById('searchResults');
    var loadMoreBtn = document.getElementById('loadMoreBtn');
    var resetButton = document.getElementById('resetButton');

    function attachEventListeners() {
        if (searchForm) {
            searchForm.addEventListener('submit', handleSearch);
        }

        if (loadMoreBtn) {
            loadMoreBtn.addEventListener('click', loadMore);
        }

        if (resetButton) {
            resetButton.addEventListener('click', resetSearch);
        }

        // Attach other event listeners (e.g., for trailer buttons)
        attachTrailerListeners();
    }

    function handleSearch(e) {
        e.preventDefault();
        console.log("Form submitted");  // Debug log

        fetch(searchForm.action, {
            method: searchForm.method,
            body: new FormData(searchForm)
        })
        .then(response => response.text())
        .then(html => {
            console.log("Response received");  // Debug log
            document.body.innerHTML = html;
            attachEventListeners();
            toggleResetButton();
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    function loadMore() {
        var page = parseInt(this.getAttribute('data-page'));
        var formData = new FormData(searchForm);
        formData.append('page', page);

        console.log("Loading more movies, page:", page);  // Debug log

        fetch('/load_more', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log("Received data:", data);  // Debug log
            if (data.movies && data.movies.length > 0) {
                var movieList = document.getElementById('movieList');
                data.movies.forEach(movie => {
                    var movieCard = createMovieCard(movie);
                    movieList.appendChild(movieCard);
                });

                if (page < data.total_pages) {
                    loadMoreBtn.setAttribute('data-page', page + 1);
                } else {
                    loadMoreBtn.style.display = 'none';
                }

                attachEventListeners();
            } else {
                console.log("No more movies found");  // Debug log
                loadMoreBtn.style.display = 'none';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            loadMoreBtn.style.display = 'none';
        });
    }

    function resetSearch() {
        if (searchForm) searchForm.reset();
        if (searchResults) searchResults.style.display = 'none';
        toggleResetButton();
    }

    function toggleResetButton() {
        if (resetButton) {
            if (searchResults && searchResults.style.display !== 'none') {
                resetButton.style.display = 'block';
            } else {
                resetButton.style.display = 'none';
            }
        }
    }

    function createMovieCard(movie) {
        // ... (keep the existing createMovieCard function)
    }

    function attachTrailerListeners() {
        document.querySelectorAll('.watch-trailer').forEach(function(button) {
            button.addEventListener('click', function() {
                var trailerKey = this.getAttribute('data-trailer-key');
                var trailerModal = document.getElementById('trailerModal');
                var iframe = trailerModal.querySelector('iframe');
                if (trailerKey) {
                    iframe.src = `https://www.youtube.com/embed/${trailerKey}`;
                    console.log('Setting iframe src to:', iframe.src); // Debug log
                } else {
                    console.log('No trailer key found'); // Debug log
                }
            });
        });

        var trailerModal = document.getElementById('trailerModal');
        trailerModal.addEventListener('hidden.bs.modal', function () {
            var iframe = this.querySelector('iframe');
            iframe.src = '';
        });
    }

    // Initial attachment of event listeners
    attachEventListeners();
    toggleResetButton();
});