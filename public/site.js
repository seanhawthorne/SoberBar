(() => {
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const header = document.getElementById('siteHeader');
  const progressBar = document.getElementById('scrollProgress');
  const menuToggle = document.getElementById('menuToggle');
  const mobileNav = document.getElementById('mobileNav');
  const mobileLinks = document.querySelectorAll('[data-mobile-link]');
  const heroParallax = document.querySelectorAll('[data-parallax]');
  const revealItems = document.querySelectorAll('.reveal');
  const faqItems = document.querySelectorAll('.faq-item');
  const form = document.getElementById('softOpeningForm');
  const formPanel = document.getElementById('join');
  const formSuccess = document.getElementById('formSuccess');
  const submitButton = document.getElementById('submitInvitation');

  const setScrollState = () => {
    const scrollY = window.scrollY || window.pageYOffset;
    header?.classList.toggle('scrolled', scrollY > 24);

    const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
    const progress = scrollHeight > 0 ? Math.min((scrollY / scrollHeight) * 100, 100) : 0;
    if (progressBar) progressBar.style.width = `${progress}%`;

    if (!reducedMotion) {
      heroParallax.forEach((item) => {
        const depth = Number(item.dataset.parallax || 0);
        item.style.setProperty('--parallax-shift', `${Math.max(scrollY * -depth / 900, -depth)}px`);
      });
    }
  };

  const closeMenu = () => {
    if (!menuToggle || !mobileNav) return;
    menuToggle.setAttribute('aria-expanded', 'false');
    mobileNav.classList.remove('open');
    mobileNav.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  };

  const openMenu = () => {
    if (!menuToggle || !mobileNav) return;
    menuToggle.setAttribute('aria-expanded', 'true');
    mobileNav.classList.add('open');
    mobileNav.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
  };

  menuToggle?.addEventListener('click', () => {
    const expanded = menuToggle.getAttribute('aria-expanded') === 'true';
    expanded ? closeMenu() : openMenu();
  });

  mobileLinks.forEach((link) => link.addEventListener('click', closeMenu));

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') closeMenu();
  });

  if (!reducedMotion && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        const delay = Number(entry.target.dataset.delay || 0);
        window.setTimeout(() => entry.target.classList.add('visible'), delay);
        observer.unobserve(entry.target);
      });
    }, { threshold: 0.18, rootMargin: '0px 0px -8% 0px' });

    revealItems.forEach((item, index) => {
      item.dataset.delay = item.dataset.delay || String((index % 6) * 70);
      observer.observe(item);
    });
  } else {
    revealItems.forEach((item) => item.classList.add('visible'));
  }

  faqItems.forEach((item) => {
    const trigger = item.querySelector('.faq-trigger');
    const panel = item.querySelector('.faq-panel');
    trigger?.addEventListener('click', () => {
      const isOpen = item.classList.contains('open');
      faqItems.forEach((current) => {
        current.classList.remove('open');
        current.querySelector('.faq-trigger')?.setAttribute('aria-expanded', 'false');
        current.querySelector('.faq-panel')?.setAttribute('aria-hidden', 'true');
      });
      if (!isOpen) {
        item.classList.add('open');
        trigger.setAttribute('aria-expanded', 'true');
        panel?.setAttribute('aria-hidden', 'false');
      }
    });
  });

  const validators = {
    name: (value) => value.trim().length >= 2 ? '' : 'Please enter your full name.',
    email: (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim()) ? '' : 'Please enter a valid email address.',
    instagram: (value) => /^[A-Za-z0-9._]{1,30}$/.test(value.trim().replace(/^@/, '')) ? '' : 'Use a valid Instagram handle without spaces.'
  };

  const setFieldError = (field, message) => {
    const errorNode = document.querySelector(`[data-error-for="${field.name}"]`);
    field.setAttribute('aria-invalid', message ? 'true' : 'false');
    if (errorNode) errorNode.textContent = message;
  };

  const validateField = (field) => {
    const validator = validators[field.name];
    if (!validator) return '';
    const message = validator(field.value);
    setFieldError(field, message);
    return message;
  };

  form?.querySelectorAll('input').forEach((field) => {
    field.addEventListener('blur', () => validateField(field));
    field.addEventListener('input', () => {
      if (field.getAttribute('aria-invalid') === 'true') validateField(field);
    });
  });

  form?.addEventListener('submit', (event) => {
    event.preventDefault();
    const fields = Array.from(form.querySelectorAll('input'));
    const errors = fields.map(validateField).filter(Boolean);

    if (errors.length) {
      fields.find((field) => field.getAttribute('aria-invalid') === 'true')?.focus();
      return;
    }

    const name = form.name.value.trim();
    const email = form.email.value.trim();
    const instagram = form.instagram.value.trim().replace(/^@/, '');

    submitButton?.setAttribute('disabled', 'true');
    submitButton?.setAttribute('aria-busy', 'true');
    if (submitButton) {
      submitButton.innerHTML = '<span class="loading-indicator">Saving your invitation</span>';
    }

    window.setTimeout(() => {
      const entries = JSON.parse(localStorage.getItem('soberBarSignups') || '[]');
      entries.push({
        name,
        email,
        instagram,
        timestamp: new Date().toISOString()
      });
      localStorage.setItem('soberBarSignups', JSON.stringify(entries));
      console.log('Soft opening signup:', { name, email, instagram });

      form.reset();
      formPanel?.setAttribute('hidden', 'hidden');
      formSuccess?.classList.add('visible');
      formSuccess?.removeAttribute('hidden');
      formSuccess?.scrollIntoView({ behavior: reducedMotion ? 'auto' : 'smooth', block: 'center' });
    }, reducedMotion ? 0 : 650);
  });

  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener('click', (event) => {
      const href = anchor.getAttribute('href');
      if (!href || href === '#') return;
      const target = document.querySelector(href);
      if (!target) return;
      event.preventDefault();
      const top = target.getBoundingClientRect().top + window.scrollY - 78;
      window.scrollTo({ top, behavior: reducedMotion ? 'auto' : 'smooth' });
    });
  });

  window.addEventListener('scroll', setScrollState, { passive: true });
  window.addEventListener('resize', setScrollState);
  setScrollState();
})();
