/* === TWITTERLY APP JS === */

const CSRF_TOKEN = document.cookie.split('; ')
  .find(r => r.startsWith('csrftoken='))
  ?.split('=')[1] || '';

// ==================== CHARACTER COUNTER ====================
function setupCharCounter(textarea, counter, limit = 280) {
  if (!textarea || !counter) return;
  textarea.addEventListener('input', () => {
    const remaining = limit - textarea.value.length;
    counter.textContent = remaining;
    counter.className = 'char-counter';
    if (remaining <= 20) counter.classList.add('warning');
    if (remaining < 0) counter.classList.add('danger');
  });
}

document.querySelectorAll('.tweet-textarea, #tweet-content, #modalTweetContent').forEach(el => {
  const counter = el.closest('form')?.querySelector('.char-counter');
  if (counter) setupCharCounter(el, counter, 280);
});

// ==================== IMAGE PREVIEW ====================
const modalImage = document.getElementById('modalTweetImage');
const preview = document.getElementById('imagePreview');
const previewContainer = document.getElementById('imagePreviewContainer');

if (modalImage) {
  modalImage.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file && preview && previewContainer) {
      const reader = new FileReader();
      reader.onload = (ev) => {
        preview.src = ev.target.result;
        previewContainer.classList.remove('d-none');
      };
      reader.readAsDataURL(file);
    }
  });
}

// ==================== AJAX LIKE ====================
async function toggleLike(btn, tweetId) {
  const icon = btn.querySelector('i');
  const countEl = btn.querySelector('.count');
  try {
    const res = await fetch(`/tweet/${tweetId}/like/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': CSRF_TOKEN, 'Content-Type': 'application/json' }
    });
    const data = await res.json();
    if (data.is_liked) {
      btn.classList.add('liked');
      icon.classList.replace('far', 'fas');
    } else {
      btn.classList.remove('liked');
      icon.classList.replace('fas', 'far');
    }
    if (countEl) countEl.textContent = data.likes_count || '';
  } catch (err) { console.error(err); }
}

// ==================== AJAX RETWEET ====================
async function toggleRetweet(btn, tweetId) {
  const icon = btn.querySelector('i');
  const countEl = btn.querySelector('.count');
  try {
    const res = await fetch(`/tweet/${tweetId}/retweet/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': CSRF_TOKEN, 'Content-Type': 'application/json' }
    });
    const data = await res.json();
    if (data.is_retweeted) {
      btn.classList.add('retweeted');
    } else {
      btn.classList.remove('retweeted');
    }
    if (countEl) countEl.textContent = data.retweets_count || '';
  } catch (err) { console.error(err); }
}

// ==================== AJAX BOOKMARK ====================
async function toggleBookmark(btn, tweetId) {
  const icon = btn.querySelector('i');
  try {
    const res = await fetch(`/tweet/${tweetId}/bookmark/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': CSRF_TOKEN, 'Content-Type': 'application/json' }
    });
    const data = await res.json();
    if (data.is_bookmarked) {
      btn.classList.add('bookmarked');
      icon.classList.replace('far', 'fas');
    } else {
      btn.classList.remove('bookmarked');
      icon.classList.replace('fas', 'far');
    }
  } catch (err) { console.error(err); }
}

// ==================== AJAX FOLLOW ====================
async function toggleFollow(btn, username) {
  try {
    const res = await fetch(`/accounts/${username}/follow/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': CSRF_TOKEN, 'Content-Type': 'application/json' }
    });
    const data = await res.json();
    if (data.is_following) {
      btn.textContent = 'Following';
      btn.classList.add('following');
    } else {
      btn.textContent = 'Follow';
      btn.classList.remove('following');
    }
    const followerCount = document.querySelector('.followers-count');
    if (followerCount && data.followers_count !== undefined) {
      followerCount.textContent = data.followers_count;
    }
  } catch (err) { console.error(err); }
}

// ==================== ADMIN BLOCK TOGGLE ====================
async function toggleBlock(btn, userId) {
  if (!confirm('Are you sure you want to toggle block status for this user?')) return;
  try {
    const res = await fetch(`/admin-portal/users/${userId}/toggle-block/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': CSRF_TOKEN, 'Content-Type': 'application/json' }
    });
    const data = await res.json();
    if (data.is_blocked) {
      btn.textContent = 'Unblock';
      btn.classList.replace('btn-danger', 'btn-success');
    } else {
      btn.textContent = 'Block';
      btn.classList.replace('btn-success', 'btn-danger');
    }
  } catch (err) { console.error(err); }
}

// ==================== AUTO-DISMISS TOASTS ====================
setTimeout(() => {
  document.querySelectorAll('.toast.show').forEach(t => {
    try { new bootstrap.Toast(t).hide(); } catch(e) {}
  });
}, 4000);

// ==================== TWEET CARD CLICK ====================
document.querySelectorAll('.tweet-card[data-tweet-id]').forEach(card => {
  card.addEventListener('click', (e) => {
    if (e.target.closest('a, button, form')) return;
    const id = card.dataset.tweetId;
    window.location.href = `/tweet/${id}/`;
  });
});
