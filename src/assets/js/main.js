/* Northfield Academy — progressive enhancement.
   Every page works without JS: links navigate, <details> accordions open natively,
   forms fall back to a normal POST when data-endpoint/action is set. */
(function () {
  'use strict';

  /* ---------- Mobile menu ---------- */
  var toggle = document.querySelector('[data-menu-toggle]');
  var mobileNav = document.getElementById('mobile-nav');
  if (toggle && mobileNav) {
    var setMenu = function (open) {
      toggle.setAttribute('aria-expanded', String(open));
      toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
      mobileNav.hidden = !open;
    };
    toggle.addEventListener('click', function () {
      setMenu(toggle.getAttribute('aria-expanded') !== 'true');
    });
    mobileNav.addEventListener('click', function (e) {
      if (e.target.closest('a')) setMenu(false);
    });
    mobileNav.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { setMenu(false); toggle.focus(); }
    });
    toggle.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') setMenu(false);
    });
    var mq = window.matchMedia('(min-width: 880px)');
    var onChange = function () { if (mq.matches) setMenu(false); };
    if (mq.addEventListener) mq.addEventListener('change', onChange); else mq.addListener(onChange);
  }

  /* ---------- Filters ----------
     <div data-filter-scope>
       <button data-filter="cat" data-value="All">…  (one group per key)
       <article data-item data-cat="Technology" data-timings="Weekday Evening">…
       <p data-filter-status></p> <div data-filter-empty hidden>… <button data-filter-reset>
  */
  document.querySelectorAll('[data-filter-scope]').forEach(function (scope) {
    var buttons = Array.prototype.slice.call(scope.querySelectorAll('[data-filter]'));
    var items = Array.prototype.slice.call(scope.querySelectorAll('[data-item]'));
    var status = scope.querySelector('[data-filter-status]');
    var empty = scope.querySelector('[data-filter-empty]');
    var list = scope.querySelector('[data-filter-list]');
    var active = {};
    buttons.forEach(function (b) {
      if (b.getAttribute('aria-pressed') === 'true') active[b.dataset.filter] = b.dataset.value;
    });

    var apply = function () {
      var shown = 0;
      items.forEach(function (item) {
        var ok = Object.keys(active).every(function (key) {
          var v = active[key];
          if (v === 'All' || v === 'Any') return true;
          if (key === 'cat') return item.dataset.cat === v;
          if (key === 'time') return (item.dataset.timings || '').split(' ').indexOf(v) !== -1;
          return true;
        });
        item.hidden = !ok;
        if (ok) shown++;
      });
      buttons.forEach(function (b) {
        b.setAttribute('aria-pressed', String(active[b.dataset.filter] === b.dataset.value));
      });
      if (status) {
        status.textContent = shown === items.length
          ? 'Showing all ' + items.length + ' courses'
          : 'Showing ' + shown + ' of ' + items.length + ' courses';
      }
      if (empty) empty.hidden = shown !== 0;
      if (list) list.hidden = shown === 0;
    };

    buttons.forEach(function (b) {
      b.addEventListener('click', function () { active[b.dataset.filter] = b.dataset.value; apply(); });
    });
    scope.querySelectorAll('[data-filter-reset]').forEach(function (r) {
      r.addEventListener('click', function () {
        Object.keys(active).forEach(function (k) {
          var first = scope.querySelector('[data-filter="' + k + '"]');
          active[k] = first ? first.dataset.value : 'All';
        });
        apply();
      });
    });
    apply();
  });

  /* ---------- "Enquire" buttons prefill the course select ---------- */
  document.querySelectorAll('[data-enquire-course]').forEach(function (a) {
    a.addEventListener('click', function () {
      var select = document.getElementById('enq-course');
      if (select) select.value = a.dataset.enquireCourse;
    });
  });

  /* ---------- Syllabus: expand / collapse all ---------- */
  document.querySelectorAll('[data-expand-all]').forEach(function (btn) {
    var target = document.getElementById(btn.getAttribute('aria-controls'));
    if (!target) return;
    var all = function () { return target.querySelectorAll('details'); };
    var sync = function () {
      var open = Array.prototype.every.call(all(), function (d) { return d.open; });
      btn.textContent = open ? 'Collapse all' : 'Expand all';
      btn.setAttribute('aria-expanded', String(open));
    };
    btn.addEventListener('click', function () {
      var openAll = btn.getAttribute('aria-expanded') !== 'true';
      Array.prototype.forEach.call(all(), function (d) { d.open = openAll; });
      sync();
    });
    target.addEventListener('toggle', sync, true);
    sync();
  });

  /* ---------- Enquiry forms ----------
     Set data-endpoint="https://…" on the <form> to POST JSON to your backend
     (Formspree, a serverless function, your CRM webhook…). Without it the form
     validates and shows the confirmation only — wire it up before going live. */
  document.querySelectorAll('form[data-enquiry]').forEach(function (form) {
    var wrap = form.closest('[data-enquiry-wrap]');
    var success = wrap && wrap.querySelector('[data-success]');
    var errorBox = form.querySelector('[data-error]');
    var submit = form.querySelector('[type="submit"]');

    var showError = function (msg, field) {
      errorBox.textContent = msg;
      errorBox.hidden = false;
      form.querySelectorAll('[aria-invalid]').forEach(function (f) { f.removeAttribute('aria-invalid'); });
      if (field) { field.setAttribute('aria-invalid', 'true'); field.focus(); }
    };

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var data = new FormData(form);
      var name = String(data.get('name') || '').trim();
      var phoneDigits = String(data.get('phone') || '').replace(/\D/g, '');
      var email = String(data.get('email') || '').trim();
      if (!name) return showError('Enter your name so we know who to ask for.', form.elements.name);
      if (phoneDigits.length < 10) return showError('Enter a phone number with at least 10 digits.', form.elements.phone);
      if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return showError('Check the email address, or leave it empty.', form.elements.email);
      errorBox.hidden = true;

      var done = function () {
        if (!success) return;
        var first = name.split(/\s+/)[0];
        success.querySelectorAll('[data-success-name]').forEach(function (n) { n.textContent = first; });
        var course = data.get('course');
        success.querySelectorAll('[data-success-course]').forEach(function (n) {
          n.textContent = course || 'the course that suits you';
        });
        form.hidden = true;
        success.hidden = false;
        success.focus();
      };

      var endpoint = form.dataset.endpoint;
      if (!endpoint) return done();

      submit.disabled = true;
      submit.textContent = 'Sending…';
      var payload = {};
      data.forEach(function (v, k) { payload[k] = v; });
      payload.page = location.pathname;
      fetch(endpoint, { method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body: JSON.stringify(payload) })
        .then(function (r) { if (!r.ok) throw new Error(r.status); done(); })
        .catch(function () { showError('Your enquiry did not send. Check your connection and try again, or call us.'); })
        .then(function () { submit.disabled = false; submit.textContent = submit.dataset.label; });
    });

    if (submit) submit.dataset.label = submit.textContent;

    if (success) {
      var again = success.querySelector('[data-again]');
      if (again) again.addEventListener('click', function () {
        form.reset();
        success.hidden = true;
        form.hidden = false;
        form.elements.name.focus();
      });
    }
  });

  /* ---------- Footer year ---------- */
  document.querySelectorAll('[data-year]').forEach(function (n) { n.textContent = new Date().getFullYear(); });
})();
