(function () {
  'use strict';

  var measurementId = 'G-9KQZRZ21VK';
  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
  window.gtag('js', new Date());
  window.gtag('config', measurementId, {
    send_page_view: true,
    transport_type: 'beacon'
  });

  var tag = document.createElement('script');
  tag.async = true;
  tag.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(measurementId);
  document.head.appendChild(tag);

  function sendEvent(name, parameters) {
    window.gtag('event', name, Object.assign({ transport_type: 'beacon' }, parameters || {}));
  }

  document.addEventListener('click', function (event) {
    var link = event.target.closest('a[href]');
    if (!link) return;

    var href = link.getAttribute('href') || '';
    var label = (link.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 100);

    if (/getseat\.net/i.test(href)) {
      sendEvent('reservation_started', { link_url: href, link_text: label });
    } else if (/maps\.google\.com|google\.com\/maps/i.test(href)) {
      sendEvent('directions_clicked', { link_url: href, link_text: label });
    } else if (/^tel:/i.test(href)) {
      sendEvent('phone_clicked', { link_url: href, link_text: label });
    } else if (/^mailto:/i.test(href)) {
      sendEvent('email_clicked', { link_url: href, link_text: label });
    } else if (/instagram\.com/i.test(href)) {
      sendEvent('instagram_clicked', { link_url: href, link_text: label });
    } else if (/private-events\.html/i.test(href)) {
      sendEvent('private_events_viewed', { link_url: href, link_text: label });
    }
  });

  document.addEventListener('submit', function (event) {
    if (event.target && event.target.id === 'joinForm') {
      sendEvent('email_signup_started', { form_id: 'joinForm' });
    }
  });
})();
