/**
 * NoteIt Main JavaScript
 */

// Auto-dismiss alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

// Confirm delete actions
document.addEventListener('DOMContentLoaded', function() {
    const deleteForms = document.querySelectorAll('form[onsubmit*="confirm"]');
    deleteForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            if (!confirm('Вы уверены, что хотите выполнить это действие?')) {
                e.preventDefault();
            }
        });
    });
});

// Toggle favorite with AJAX
document.addEventListener('DOMContentLoaded', function() {
    const favoriteButtons = document.querySelectorAll('[data-toggle-favorite]');
    favoriteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const documentId = this.getAttribute('data-document-id');
            const url = `/documents/${documentId}/toggle-favorite`;
            
            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const icon = this.querySelector('i');
                    if (data.is_favorite) {
                        icon.classList.remove('bi-star');
                        icon.classList.add('bi-star-fill');
                        this.classList.add('active');
                    } else {
                        icon.classList.remove('bi-star-fill');
                        icon.classList.add('bi-star');
                        this.classList.remove('active');
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    });
});

// Markdown preview (if needed in future)
function previewMarkdown(text) {
    // This can be enhanced with a markdown parser library
    return text;
}

// Search form enhancement
document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.querySelector('form[action*="search"]');
    if (searchForm) {
        const searchInput = searchForm.querySelector('input[name="query"]');
        if (searchInput && !searchInput.value) {
            searchInput.focus();
        }
    }
});

