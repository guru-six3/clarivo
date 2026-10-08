// The browser only displays results. Python performs every FAQ match.
const conversation = document.querySelector('#conversation');
const form = document.querySelector('#chat-form');
const input = document.querySelector('#question');
const send = document.querySelector('#send');
const status = document.querySelector('#request-status');
const welcome = document.querySelector('#welcome').cloneNode(true);
let busy = false;

function element(tag, className, text) {
  const node = document.createElement(tag);
  node.className = className;
  if (text !== undefined) node.textContent = text; // Never render user text as HTML.
  return node;
}
function prettyDate(iso) {
  return new Date(`${iso}T12:00:00`).toLocaleDateString('en-IN', {day:'numeric', month:'short', year:'numeric'});
}
function scrollToLatest() { conversation.scrollTop = conversation.scrollHeight; }

async function ask(question) {
  if (busy || !question.trim()) return;
  busy = true;
  send.disabled = true;
  document.querySelector('#reset').disabled = true;
  input.value = '';
  document.querySelector('#welcome')?.remove();
  conversation.append(element('div', 'message user', question));
  scrollToLatest();
  status.textContent = 'Finding the closest FAQ…';
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 10000);
  try {
    const response = await fetch('/api/chat', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({question}), signal:controller.signal});
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Request failed.');
    const message = element('div', 'message bot');
    const meta = element('div', 'bot-meta');
    meta.append(element('span', 'bot-avatar', '✦'), element('span', '', result.matched ? `CLARIVO · ${result.topic.toUpperCase()}` : 'CLARIVO · LET’S TRY ANOTHER QUESTION'));
    message.append(meta, element('p', '', result.answer));
    if (result.event) {
      const card = element('div', 'answer-event');
      const detail = element('div', '');
      detail.append(element('span', '', 'SAMPLE DATE'), element('strong', '', result.event.status));
      card.append(detail, element('span', '', `${result.event.label} · ${prettyDate(result.event.date)}`));
      message.append(card);
    }
    message.append(element('span', 'related-label', result.matched ? 'YOU MAY ALSO WANT TO ASK' : 'TRY ONE OF THESE'));
    const related = element('div', 'related');
    result.suggestions.forEach(suggestion => {
      const button = element('button', '', suggestion.question);
      button.type = 'button';
      button.dataset.question = suggestion.question;
      related.append(button);
    });
    message.append(related);
    conversation.append(message);
    status.textContent = '';
  } catch (error) {
    conversation.append(element('div', 'message bot', 'The examination desk is unavailable. Please check that the local server is running and try again.'));
    input.value = question;
    status.textContent = 'Your question has been restored so you can retry.';
  } finally {
    clearTimeout(timeout);
    busy = false;
    send.disabled = false;
    document.querySelector('#reset').disabled = false;
    scrollToLatest();
    input.focus();
  }
}
form.addEventListener('submit', event => {event.preventDefault(); ask(input.value.trim());});
conversation.addEventListener('click', event => {
  const button = event.target.closest('button[data-question]');
  if (button) ask(button.dataset.question);
});
document.querySelector('#reset').addEventListener('click', () => {
  conversation.replaceChildren(welcome.cloneNode(true));
  status.textContent = '';
  input.value = '';
  input.focus();
});

async function loadCalendar() {
  try {
    const response = await fetch('/api/calendar');
    if (!response.ok) throw new Error('Calendar unavailable');
    const data = await response.json();
    const events = document.querySelector('#events');
    events.replaceChildren();
    data.events.sort((a,b) => a.date.localeCompare(b.date)).forEach(event => {
      const date = new Date(`${event.date}T12:00:00`);
      const row = element('div', 'event');
      const stamp = element('div', 'event-date');
      stamp.append(element('small', '', date.toLocaleDateString('en-IN',{month:'short'}).toUpperCase()), element('strong', '', String(date.getDate())));
      const detail = element('div', '');
      detail.append(element('p', 'event-label', event.label), element('span', 'event-status', event.status));
      row.append(stamp, detail);
      events.append(row);
    });
    document.querySelector('#local-date').textContent = `As of ${prettyDate(data.today)} · ${data.timezone}`;
  } catch {
    document.querySelector('#events').textContent = 'Calendar unavailable. Refresh after starting the server.';
  }
}
loadCalendar();
// Refresh dates if this page remains open across midnight.
setInterval(loadCalendar, 60000);
